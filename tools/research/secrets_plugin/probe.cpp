// SPDX-License-Identifier: GPL-3.0-or-later
// Synthetic direct-class fixture. Never loads an existing daemon.
#include <QCoreApplication>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTextStream>
#include <utility>
#include <cstring>
#include <rnp/rnp_err.h>
#include "rnp_p.h"
#include "rnpffi.h"
#include "rnpkeys.h"
using Key = Sailfish::Crypto::Key;
using Result = Sailfish::Crypto::Result;
using Manager = Sailfish::Crypto::CryptoManager;
class Fixture : public RnpFfi, public RnpKeys {
public:
    explicit Fixture(Rnp *engine) : RnpFfi(engine), RnpKeys(engine) {}
    QString name() const override { return QStringLiteral("org.sailfishos.crypto.plugin.rnp.test"); }
    QString displayName() const override { return QStringLiteral("Synthetic RNP fixture"); }
    int version() const override { return 1; }
};
static QByteArray read(const QString &path) {
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) qFatal("fixture input unavailable");
    return file.readAll();
}
static bool write(const QString &path, const QByteArray &bytes) {
    QFile file(path);
    return file.open(QIODevice::WriteOnly) && file.write(bytes) == bytes.size() && file.flush();
}
struct PasswordState { QByteArray password; QStringList requested; bool refuse = false; };
static bool provider(rnp_ffi_t, void *context, rnp_key_handle_t key,
                     const char *, char *buffer, size_t size) {
    auto *state = static_cast<PasswordState *>(context);
    if (!key) {
        // Deliberately willing: the scoped plugin must block this before forwarding.
        state->requested.append(QStringLiteral("<symmetric>"));
    } else {
        char *fp = nullptr;
        if (rnp_key_get_fprint(key, &fp) != RNP_SUCCESS || !fp) return false;
        state->requested.append(QString::fromLatin1(fp));
        rnp_buffer_destroy(fp);
    }
    if (state->refuse || static_cast<size_t>(state->password.size()) >= size) return false;
    memcpy(buffer, state->password.constData(), state->password.size());
    buffer[state->password.size()] = '\0';
    return true;
}
static Key reference(const QJsonObject &config, const QString &field, const QString &plugin) {
    Key key;
    key.setName(config.value(field).toString());
    key.setCollectionName(config.value("aId").toString());
    key.setStoragePluginName(plugin);
    return key;
}
static Result decrypt(Fixture &plugin, const QByteArray &cipher, const Key &key, QByteArray *plain) {
    Manager::VerificationStatus status = Manager::VerificationStatusUnknown;
    return plugin.RnpFfi::decrypt(cipher, QByteArray(), key, Manager::BlockModeUnknown,
        Manager::EncryptionPaddingNone, QByteArray(), QByteArray(), QVariantMap(), plain, &status);
}
static bool unsupported(const Result &result) {
    return result.code() == Result::Failed && result.errorCode() == Result::OperationNotSupportedError;
}
int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    if (argc != 3) return 2;
    const QString profile = QString::fromLocal8Bit(argv[1]);
    const QJsonObject config = QJsonDocument::fromJson(read(QString::fromLocal8Bit(argv[2]))).object();
    QJsonObject checks;
    QJsonObject observations;
    {
        Rnp engine(Rnp::GPG_COMPAT);
        Fixture plugin(&engine);
        PasswordState passwords;
#if PLUGIN_CORRECTED
        passwords.password = read(config.value("passwordFile").toString()).trimmed();
        checks.insert("provider", engine.setPasswordProvider(provider, &passwords));
#endif
        Key a = reference(config, "aPrimary", plugin.name());
        const QByteArray text = read(config.value("text").toString());
        QByteArray plain;
        if (profile == "control") {
            Key output;
            Sailfish::Crypto::KeyPairGenerationParameters generation;
            Sailfish::Crypto::KeyDerivationParameters derivation;
            checks.insert("generate-unsupported", unsupported(plugin.RnpFfi::generateKey(
                Key(), generation, derivation, QVariantMap(), &output)));
            checks.insert("generate-store-unsupported", unsupported(plugin.RnpFfi::generateAndStoreKey(
                a, generation, derivation, QVariantMap(), &output)));
            checks.insert("import-unsupported", unsupported(plugin.RnpFfi::importKey(
                QByteArray("not a key"), QByteArray(), QVariantMap(), &output)));
            checks.insert("import-store-unsupported", unsupported(plugin.RnpFfi::importAndStoreKey(
                QByteArray("not a key"), a, QByteArray(), QVariantMap(), &output)));
            checks.insert("private-export-unsupported", unsupported(plugin.RnpFfi::storedKey(
                a.identifier(), Key::PrivateKeyData, QVariantMap(), &output)));
            Result metadata = plugin.RnpFfi::storedKey(a.identifier(), Key::MetaData, QVariantMap(), &output);
            checks.insert("metadata-valid-reference", metadata.code() == Result::Succeeded
                && output.identifier() == a.identifier() && output.publicKey().isEmpty()
                && output.privateKey().isEmpty() && output.secretKey().isEmpty());
            Rnp::Key native = engine.publicKeyring().key(a);
            Key converted = native.toCryptoKey(plugin.name());
            checks.insert("metadata-no-fabricated-bytes", converted.publicKey().isEmpty()
                && converted.privateKey().isEmpty() && converted.secretKey().isEmpty());
            Result good = decrypt(plugin, read(config.value("aCipher").toString()), a, &plain);
            checks.insert("own-key-roundtrip", good.code() == Result::Succeeded && plain == text);
            Result wrong = decrypt(plugin, read(config.value("bCipher").toString()), a, &plain);
            checks.insert("other-primary-refused", wrong.code() == Result::Failed && plain.isEmpty());
            observations.insert("other-key-result-success", wrong.code() == Result::Succeeded);
            observations.insert("other-key-plaintext-exact", plain == text);
            Key raw = a; raw.setPrivateKey("fabricated marker");
            checks.insert("raw-private-refused", unsupported(decrypt(plugin,
                read(config.value("bCipher").toString()), raw, &plain)));
            raw = a; raw.setSecretKey("fabricated marker");
            checks.insert("raw-secret-refused", unsupported(decrypt(plugin,
                read(config.value("bCipher").toString()), raw, &plain)));
            raw = a; raw.setPrivateKey("fabricated marker");
            QByteArray signature, encrypted, authenticationTag;
            checks.insert("raw-sign-refused", unsupported(plugin.RnpFfi::sign(text, raw,
                Manager::SignaturePaddingNone, Manager::DigestUnknown, QVariantMap(), &signature)));
            checks.insert("raw-encrypt-refused", unsupported(plugin.RnpFfi::encrypt(text, QByteArray(), raw,
                Manager::BlockModeUnknown, Manager::EncryptionPaddingNone, QByteArray(),
                QVariantMap(), &encrypted, &authenticationTag)));
            Manager::VerificationStatus verification = Manager::VerificationStatusUnknown;
            checks.insert("raw-verify-refused", unsupported(plugin.RnpFfi::verify(QByteArray("dummy signature"),
                text, raw, Manager::SignaturePaddingNone, Manager::DigestUnknown, QVariantMap(), &verification)));
            checks.insert("software-crypto", plugin.RnpFfi::encryptionType()
                == Sailfish::Crypto::CryptoPlugin::SoftwareEncryption);
            checks.insert("software-storage", plugin.RnpKeys::encryptionType()
                == Sailfish::Secrets::EncryptionPlugin::SoftwareEncryption);
            // Last: pristine control may mutate only its synthetic ring copy.
            auto removed = plugin.RnpKeys::removeSecret(a.collectionName(), a.name());
            checks.insert("delete-unsupported", removed.code() == Sailfish::Secrets::Result::Failed
                && removed.errorCode() == Sailfish::Secrets::Result::OperationNotSupportedError);
        } else if (profile == "protected") {
#if PLUGIN_CORRECTED
            Key sub = reference(config, "aSub", plugin.name());
            Key sibling = reference(config, "aSibling", plugin.name());
            Key signing = reference(config, "aSigning", plugin.name());
            auto exactCallback = [&](const Key &key) { return passwords.requested == (QStringList() << key.name()); };
            passwords.requested.clear();
            Result good = decrypt(plugin, read(config.value("subCipher").toString()), sub, &plain);
            checks.insert("protected-subkey", good.code() == Result::Succeeded && plain == text && exactCallback(sub));
            for (const QString &field : {"siblingCipher", "aCipher", "bCipher"}) {
                passwords.requested.clear();
                Result wrong = decrypt(plugin, read(config.value(field).toString()), sub, &plain);
                checks.insert(field + "-refused-before-private-use",
                    wrong.code() == Result::Failed && plain.isEmpty() && passwords.requested.isEmpty());
            }
            passwords.requested.clear();
            Result primary = decrypt(plugin, read(config.value("aCipher").toString()), a, &plain);
            checks.insert("exact-primary", primary.code() == Result::Succeeded && plain == text && exactCallback(a));
            passwords.requested.clear();
            Result noFamily = decrypt(plugin, read(config.value("subCipher").toString()), a, &plain);
            checks.insert("primary-not-family-authority", noFamily.code() == Result::Failed
                && plain.isEmpty() && passwords.requested.isEmpty());
            passwords.refuse = true; passwords.requested.clear();
            Result refused = decrypt(plugin, read(config.value("subCipher").toString()), sub, &plain);
            checks.insert("refusal-after-success", refused.code() == Result::Failed && plain.isEmpty() && exactCallback(sub));
            passwords.refuse = false; passwords.requested.clear();
            Result empty = decrypt(plugin, read(config.value("emptyCipher").toString()), sub, &plain);
            checks.insert("empty-plaintext", empty.code() == Result::Succeeded && plain.isEmpty() && exactCallback(sub));
            checks.insert("public-ring-for-public-validation", engine.publicKeyring().isValid());
            passwords.requested.clear();
            QByteArray symmetric = read(config.value("symmetricCipher").toString());
            checks.insert("symmetric-fixture-native-positive", engine.decrypt(symmetric) == text
                && passwords.requested == (QStringList() << QStringLiteral("<symmetric>")));
            passwords.requested.clear();
            Result noSymmetric = decrypt(plugin, symmetric, sub, &plain);
            checks.insert("symmetric-fallback-refused", noSymmetric.code() == Result::Failed
                && plain.isEmpty() && passwords.requested.isEmpty());
            passwords.requested.clear();
            QByteArray signedOnly = read(config.value("signedOnly").toString());
            checks.insert("signed-only-native-positive", engine.decrypt(signedOnly) == text
                && passwords.requested.isEmpty());
            passwords.requested.clear();
            Result noUnsignedEncryption = decrypt(plugin, signedOnly, sub, &plain);
            checks.insert("signed-only-not-keyed-decryption", noUnsignedEncryption.code() == Result::Failed
                && plain.isEmpty() && passwords.requested.isEmpty());
            Rnp::Key owned = engine.publicKeyring().key(sub);
            checks.insert("returned-subkey-parent", owned.keyid() == a.collectionName()
                && owned.toCryptoKey(plugin.name()).identifier() == sub.identifier());
            Rnp::Key moved = engine.publicKeyring().key(sibling);
            moved = std::move(owned);
            checks.insert("move-ownership", !owned.isValid() && moved.fingerprint() == sub.name()
                && moved.keyid() == a.collectionName());
            moved = std::move(moved);
            checks.insert("self-move", moved.isValid() && moved.keyid() == a.collectionName());
            for (int i = 0; i < 32; ++i)
                moved = engine.publicKeyring().key((i % 2) ? sibling : sub);
            checks.insert("repeated-move", moved.fingerprint() == sibling.name() && moved.keyid() == a.collectionName());
            passwords.requested.clear();
            QByteArray signature;
            Result signedResult = plugin.RnpFfi::sign(text, signing, Manager::SignaturePaddingNone,
                Manager::DigestUnknown, QVariantMap(), &signature);
            checks.insert("exact-sign-subkey", signedResult.code() == Result::Succeeded
                && !signature.isEmpty() && exactCallback(signing));
            checks.insert("signature-written", write(config.value("signatureOut").toString(), signature));
            passwords.requested.clear();
            Result disallowed = plugin.RnpFfi::sign(text, sub, Manager::SignaturePaddingNone,
                Manager::DigestUnknown, QVariantMap(), &signature);
            checks.insert("encryption-key-not-primary-signing", disallowed.code() == Result::Failed
                && signature.isEmpty() && passwords.requested.isEmpty());
            QByteArray cipher, tag;
            Result encrypted = plugin.RnpFfi::encrypt(text, QByteArray(), sub, Manager::BlockModeUnknown,
                Manager::EncryptionPaddingNone, QByteArray(), QVariantMap(), &cipher, &tag);
            checks.insert("public-encryption", encrypted.code() == Result::Succeeded && !cipher.isEmpty());
            checks.insert("cipher-written", write(config.value("cipherOut").toString(), cipher));
#else
            return 2;
#endif
        } else return 2;
        if (!passwords.password.isEmpty())
            rnp_buffer_clear(passwords.password.data(), passwords.password.size());
    }
    bool passed = !checks.isEmpty();
    for (auto i = checks.constBegin(); i != checks.constEnd(); ++i) passed = passed && i.value().toBool();
    QJsonObject result;
    result.insert("status", passed ? "pass" : "fail");
    result.insert("profile", profile);
    result.insert("checks", checks);
    result.insert("observations", observations);
    QTextStream(stdout) << QJsonDocument(result).toJson(QJsonDocument::Compact) << '\n';
    return passed ? 0 : 1;
}
