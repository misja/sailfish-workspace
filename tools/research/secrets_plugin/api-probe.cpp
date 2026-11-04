// Synthetic SDK public-API fixture. No direct plugin calls.
#include <Crypto/cryptomanager.h>
#include <Crypto/storedkeyrequest.h>
#include <Crypto/encryptrequest.h>
#include <Crypto/decryptrequest.h>
#include <QtCore/QCoreApplication>
#include <QtCore/QFile>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <cstdio>
using namespace Sailfish::Crypto;
static QByteArray read(const QString &path) {
    QFile file(path);
    return file.open(QIODevice::ReadOnly) ? file.readAll() : QByteArray();
}
static bool write(const QString &path, const QByteArray &bytes) {
    QFile file(path);
    return file.open(QIODevice::WriteOnly) && file.write(bytes) == bytes.size();
}
static const QString plugin = QStringLiteral("org.sailfishos.crypto.plugin.rnp.test");
static const QString extraName = QStringLiteral("org.sailfishos.crypto.rnp.additionalRecipients");
int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    if (argc != 2) return 2;
    QJsonObject c = QJsonDocument::fromJson(read(QString::fromLocal8Bit(argv[1]))).object();
    QJsonObject checks, errors;
    CryptoManager manager;
    auto identifier = [&](const QString &tag, const QString &field) {
        return Key::Identifier(c.value(tag + field).toString(), c.value(tag + "Id").toString(), plugin);
    };
    auto load = [&](const QString &tag) {
        StoredKeyRequest request;
        request.setManager(&manager);
        request.setIdentifier(identifier(tag, "Primary"));
        request.setKeyComponents(Key::MetaData | Key::PublicKeyData);
        request.startRequest(); request.waitForFinished();
        Key key = request.storedKey();
        checks.insert(tag + "-public-export", request.result().code() == Result::Succeeded
            && key.identifier() == identifier(tag, "Primary") && !key.publicKey().isEmpty()
            && key.privateKey().isEmpty() && key.secretKey().isEmpty());
        errors.insert(tag + "-export", request.result().errorMessage());
        return key;
    };
    Key a = load("a"), b = load("b");
    StoredKeyRequest secret;
    secret.setManager(&manager); secret.setIdentifier(identifier("a", "Primary"));
    secret.setKeyComponents(Key::PrivateKeyData);
    secret.startRequest(); secret.waitForFinished();
    checks.insert("private-export-refused", secret.result().code() == Result::Failed
        && secret.storedKey().privateKey().isEmpty() && secret.storedKey().secretKey().isEmpty());
    Key::Identifier missing = identifier("a", "Primary"); missing.setName(QString(40, '1'));
    StoredKeyRequest absent;
    absent.setManager(&manager); absent.setIdentifier(missing); absent.setKeyComponents(Key::PublicKeyData);
    absent.startRequest(); absent.waitForFinished();
    checks.insert("missing-public-key-refused", absent.result().code() == Result::Failed
        && absent.storedKey().publicKey().isEmpty());
    const QByteArray text = read(c.value("text").toString());
    auto payload = [](const Key &key) {
        QVariantMap item;
        item.insert("fingerprint", key.name()); item.insert("publicKey", key.publicKey());
        return item;
    };
    EncryptRequest encrypt;
    encrypt.setManager(&manager); encrypt.setCryptoPluginName(plugin);
    encrypt.setPadding(CryptoManager::EncryptionPaddingNone);
    encrypt.setBlockMode(CryptoManager::BlockModeUnknown);
    encrypt.setData(text);
    auto perform = [&](const QString &label, const Key &main, const QVariant &extras, bool good) {
        encrypt.setKey(main);
        QVariantMap parameters; parameters.insert("With-Armor", false);
        if (extras.isValid()) parameters.insert(extraName, extras);
        encrypt.setCustomParameters(parameters);
        encrypt.startRequest(); encrypt.waitForFinished();
        const bool success = encrypt.result().code() == Result::Succeeded;
        checks.insert(label, good ? success && !encrypt.ciphertext().isEmpty()
                                 : encrypt.result().code() == Result::Failed && encrypt.ciphertext().isEmpty());
        errors.insert(label, encrypt.result().errorMessage());
        return encrypt.ciphertext();
    };
    const QVariantList additional = QVariantList() << payload(b);
    const QByteArray multi = perform("two-public-recipients", a, additional, true);
    checks.insert("cipher-written", write(c.value("cipherOut").toString(), multi));
    perform("malformed-list-refused", a, QString("not a list"), false);
    perform("reference-extra-refused", a, QVariantList() << QVariantMap{{"fingerprint", b.name()}}, false);
    QVariantMap wrong = payload(b); wrong["fingerprint"] = a.name();
    perform("cross-payload-fingerprint-refused", a, QVariantList() << wrong, false);
    QVariantMap bad = payload(b); bad["publicKey"] = QByteArray("not a public key");
    perform("invalid-packet-refused", a, QVariantList() << bad, false);
    QVariantMap empty = payload(b); empty["publicKey"] = QByteArray();
    perform("missing-packet-refused", a, QVariantList() << empty, false);
    QVariantMap privatePayload = payload(b);
    privatePayload["publicKey"] = read(c.value("bSecretPayload").toString());
    perform("secret-packet-extra-refused", a, QVariantList() << privatePayload, false);
    Key secretMain = a; secretMain.setPublicKey(read(c.value("aSecretPayload").toString()));
    perform("secret-packet-main-refused", secretMain, additional, false);
    Key shortFp = a; shortFp.setName(a.name().right(16));
    perform("keyid-is-not-fingerprint", shortFp, additional, false);
    Key rawPrivate = a; rawPrivate.setPrivateKey("synthetic marker");
    perform("raw-private-component-refused", rawPrivate, additional, false);
    const QByteArray again = perform("success-after-refusals", a, additional, true);
    checks.insert("second-cipher-written", write(c.value("cipherAgain").toString(), again));
    // Existing stored-reference single-recipient route traverses native metadata prechecks.
    Key reference; reference.setIdentifier(identifier("a", "Primary"));
    const QByteArray single = perform("stored-reference-encryption", reference, QVariant(), true);
    checks.insert("single-cipher-written", write(c.value("singleOut").toString(), single));
    for (const QString &tag : {QString("a"), QString("b")}) {
        Key key; key.setIdentifier(identifier(tag, "Sub"));
        DecryptRequest decrypt;
        decrypt.setManager(&manager); decrypt.setCryptoPluginName(plugin); decrypt.setKey(key);
        decrypt.setData(multi); decrypt.setPadding(CryptoManager::EncryptionPaddingNone);
        decrypt.setBlockMode(CryptoManager::BlockModeUnknown);
        decrypt.startRequest(); decrypt.waitForFinished();
        checks.insert(tag + "-stored-subkey-decrypt", decrypt.result().code() == Result::Succeeded
            && decrypt.plaintext() == text);
        errors.insert(tag + "-decrypt", decrypt.result().errorMessage());
    }
    Key bRef; bRef.setIdentifier(identifier("b", "Sub"));
    DecryptRequest wrongKey;
    wrongKey.setManager(&manager); wrongKey.setCryptoPluginName(plugin); wrongKey.setKey(bRef);
    wrongKey.setData(single); wrongKey.setPadding(CryptoManager::EncryptionPaddingNone);
    wrongKey.startRequest(); wrongKey.waitForFinished();
    checks.insert("wrong-stored-private-key-refused", wrongKey.result().code() == Result::Failed
        && wrongKey.plaintext().isEmpty());
    bool pass = true;
    for (auto it = checks.begin(); it != checks.end(); ++it) pass = pass && it.value().toBool();
    QJsonObject report; report["checks"] = checks; report["errors"] = errors;
    report["status"] = pass ? "pass" : "fail";
    const QByteArray json = QJsonDocument(report).toJson();
    fwrite(json.constData(), 1, json.size(), stdout);
    return pass ? 0 : 1;
}
