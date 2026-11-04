// Original adapter code: GPL-3.0-or-later.
#include "SecretsPass.h"
#include "GpgIdManage.h"
#include "totp.h"
#include "Base32.h"
#include <Crypto/storedkeyidentifiersrequest.h>
#include <Crypto/storedkeyrequest.h>
#include <Crypto/encryptrequest.h>
#include <Crypto/decryptrequest.h>
#include <QtCore/QFile>
#include <QtCore/QSaveFile>
#include <QtCore/QSharedPointer>
#include <QtCore/QVariant>
#include <QtCore/QRegularExpression>
#include <stdexcept>
#include <limits>
#include <utility>

using namespace Sailfish::Crypto;
namespace {
[[noreturn]] void unsupported()
{
    throw std::runtime_error("Operation is outside the selected-entry Secrets adapter");
}
void require(const Result &result)
{
    if (result.code() != Result::Succeeded)
        throw std::runtime_error("Sailfish Crypto request failed");
}
QByteArray bytes(const std::string &s)
{
    if (s.size() > static_cast<size_t>(std::numeric_limits<int>::max()))
        throw std::runtime_error("Entry exceeds QByteArray capacity");
    return QByteArray(s.data(), static_cast<int>(s.size()));
}
QByteArray readCipher(const std::string &path)
{
    QFile input(QString::fromStdString(path));
    if (!input.open(QIODevice::ReadOnly))
        throw std::runtime_error("Cannot open encrypted entry");
    const QByteArray data = input.readAll();
    if (input.error() != QFileDevice::NoError)
        throw std::runtime_error("Cannot read complete encrypted entry");
    return data;
}
void saveCipher(const std::string &path, const QByteArray &cipher)
{
    QSaveFile output(QString::fromStdString(path));
    output.setDirectWriteFallback(false);
    if (!output.open(QIODevice::WriteOnly))
        throw std::runtime_error("Cannot open atomic ciphertext output");
    if (output.write(cipher) != cipher.size()) {
        output.cancelWriting();
        throw std::runtime_error("Cannot write complete ciphertext");
    }
    if (!output.commit())
        throw std::runtime_error("Cannot commit ciphertext");
}
class SecretsPassFile final : public InterfacePassFile
{
public:
    SecretsPassFile(SecretsPassHelper &helper, std::string path) : m_helper(helper)
    {
        fullPath = m_helper.entryPath(path);
    }
    void decrypt() override
    {
        // Failure after an earlier success must not expose stale plaintext.
        decrypted.clear();
        decryptedSignedBy.clear();
        const QByteArray plain = m_helper.decryptBytes(readCipher(m_helper.entryPath(fullPath)));
        decrypted.assign(plain.constData(), static_cast<size_t>(plain.size()));
    }
    void encrypt(std::string plain, std::vector<std::string> recipients, bool sign) override
    {
        if (sign)
            unsupported();
        const QByteArray cipher = m_helper.encryptBytes(plain, recipients);
        saveCipher(m_helper.entryPath(fullPath), cipher);
        decrypted.swap(plain);
        decryptedSignedBy.clear();
    }
    void encryptStringToFile(std::string plain, std::string destination,
                             std::vector<std::string> recipients, bool sign) override
    {
        if (sign)
            unsupported();
        const QByteArray cipher = m_helper.encryptBytes(plain, recipients);
        saveCipher(m_helper.entryPath(destination), cipher);
    }
    void encryptFileToFile(std::string, std::string, std::vector<std::string>, bool) override
    { unsupported(); }
    void dectyptFileNameToFileName(std::string, std::string) override
    { unsupported(); }
    void reEncryptFile(std::string, std::vector<std::string>, bool) override
    { unsupported(); }
    std::vector<GpgKeys> listKeys(std::string pattern = "", bool secretOnly = false) override
    { return m_helper.listKeys(std::move(pattern), secretOnly); }
    bool getIsRnPgp() override
    { unsupported(); } // The legacy two-engine tag cannot describe this API adapter.
private:
    SecretsPassHelper &m_helper;
};
}

SecretsPassHelper::SecretsPassHelper(const std::string &root, const QString &plugin,
                                     const Key::Identifier &privateKey)
    : m_root(std::filesystem::canonical(root).string()), m_plugin(plugin), m_private(privateKey)
{
    if (!std::filesystem::is_directory(m_root))
        throw std::runtime_error("Store root is not a directory");
}
std::string SecretsPassHelper::entryPath(const std::string &path) const
{
    if (path.empty())
        throw std::runtime_error("An entry path is required");
    const std::filesystem::path root(m_root);
    const std::filesystem::path candidate = std::filesystem::weakly_canonical(
        std::filesystem::path(path).is_absolute() ? std::filesystem::path(path) : root / path);
    auto a = root.begin(), b = candidate.begin();
    for (; a != root.end(); ++a, ++b) {
        if (b == candidate.end() || *a != *b)
            throw std::runtime_error("Selected entry is outside the store");
    }
    if (b == candidate.end())
        throw std::runtime_error("Selected entry is the store directory");
    return candidate.string();
}
std::unique_ptr<InterfacePassFile> SecretsPassHelper::getPassFile(std::string path)
{
    return std::unique_ptr<InterfacePassFile>(new SecretsPassFile(*this, std::move(path)));
}
void SecretsPassHelper::loadCatalog()
{
    if (m_catalogLoaded)
        return;
    StoredKeyIdentifiersRequest request;
    request.setManager(&m_manager);
    request.setStoragePluginName(m_plugin);
    request.startRequest();
    request.waitForFinished();
    require(request.result());
    QVector<Key> catalog;
    for (const Key::Identifier &identifier : request.identifiers()) {
        StoredKeyRequest metadata;
        metadata.setManager(&m_manager);
        metadata.setIdentifier(identifier);
        metadata.setKeyComponents(Key::MetaData);
        metadata.startRequest();
        metadata.waitForFinished();
        require(metadata.result());
        if (metadata.storedKey().identifier() != identifier)
            throw std::runtime_error("Stored-key metadata identifier mismatch");
        catalog.append(metadata.storedKey());
    }
    m_catalog.swap(catalog);
    m_catalogLoaded = true;
}
std::vector<GpgKeys> SecretsPassHelper::listKeys(std::string pattern, bool secretOnly)
{
    if (secretOnly)
        unsupported(); // Public Decrypt metadata is not evidence of secret availability.
    loadCatalog();
    const QString query = QString::fromStdString(pattern);
    const QRegularExpression hex(QStringLiteral("^[0-9a-fA-F]+$"));
    std::vector<GpgKeys> result;
    for (const Key &key : m_catalog) {
        // This pinned plugin groups a primary and its subkeys under the primary keyid.
        const bool primary = key.name().endsWith(key.collectionName(), Qt::CaseInsensitive);
        bool match = query.isEmpty() && primary;
        if (!query.isEmpty()) {
            match = key.name().compare(query, Qt::CaseInsensitive) == 0;
            if (hex.match(query).hasMatch() && (query.size() == 8 || query.size() == 16))
                match = match || key.name().endsWith(query, Qt::CaseInsensitive);
            if (!hex.match(query).hasMatch() && primary)
                match = match || key.filterData().value("User-Emails").contains(query, Qt::CaseInsensitive);
        }
        if (!match)
            continue;
        GpgKeys row{};
        row.keyid = key.name().toStdString(); // Full fingerprint, never a fabricated public key.
        row.name = key.filterData().value("User-Emails").toStdString();
        row.foundUsingPattern = pattern;
        row.can_encrypt = key.operations().testFlag(CryptoManager::OperationEncrypt);
        result.push_back(std::move(row));
    }
    return result;
}
Key SecretsPassHelper::publicKey(const std::string &fingerprint)
{
    loadCatalog();
    QVector<Key::Identifier> found;
    for (const Key &key : m_catalog) {
        if (key.name().compare(QString::fromStdString(fingerprint), Qt::CaseInsensitive) == 0)
            found.append(key.identifier());
    }
    if (found.size() != 1)
        throw std::runtime_error("Recipient fingerprint is unresolved or ambiguous");
    StoredKeyRequest request;
    request.setManager(&m_manager);
    request.setIdentifier(found.first());
    request.setKeyComponents(Key::MetaData | Key::PublicKeyData);
    request.startRequest();
    request.waitForFinished();
    require(request.result());
    const Key key = request.storedKey();
    if (key.identifier() != found.first() || key.publicKey().isEmpty()
        || !key.privateKey().isEmpty() || !key.secretKey().isEmpty())
        throw std::runtime_error("Public recipient data is invalid");
    return key;
}
std::vector<std::string> SecretsPassHelper::recipientsFor(const std::string &entry)
{
    GpgIdManage policy(entryPath(entry), m_root, *this);
    policy.ensureValidGpgIdFile();
    return policy.encryptTo;
}
QByteArray SecretsPassHelper::encryptBytes(const std::string &plain,
                                          const std::vector<std::string> &recipients)
{
    if (recipients.empty())
        throw std::runtime_error("No recipients");
    QVector<Key> keys;
    for (const std::string &fingerprint : recipients)
        keys.append(publicKey(fingerprint)); // Resolve/export every recipient before encrypt/write.
    QVariantList additional;
    for (int i = 1; i < keys.size(); ++i) {
        QVariantMap item;
        item.insert("fingerprint", keys[i].name());
        item.insert("publicKey", keys[i].publicKey());
        additional.append(item);
    }
    EncryptRequest request;
    request.setManager(&m_manager);
    request.setCryptoPluginName(m_plugin);
    request.setKey(keys.first());
    request.setData(bytes(plain));
    request.setBlockMode(CryptoManager::BlockModeUnknown);
    request.setPadding(CryptoManager::EncryptionPaddingNone);
    QVariantMap parameters;
    parameters.insert("With-Armor", false);
    if (!additional.isEmpty())
        parameters.insert("org.sailfishos.crypto.rnp.additionalRecipients", additional);
    request.setCustomParameters(parameters);
    request.startRequest();
    request.waitForFinished();
    require(request.result());
    if (request.ciphertext().isEmpty())
        throw std::runtime_error("No encrypted output");
    return request.ciphertext();
}
QByteArray SecretsPassHelper::decryptBytes(const QByteArray &cipher)
{
    if (m_private.name().isEmpty() || m_private.storagePluginName() != m_plugin)
        throw std::runtime_error("An explicit private-key reference is required");
    Key reference;
    reference.setIdentifier(m_private);
    DecryptRequest request;
    request.setManager(&m_manager);
    request.setCryptoPluginName(m_plugin);
    request.setKey(reference);
    request.setData(cipher);
    request.setBlockMode(CryptoManager::BlockModeUnknown);
    request.setPadding(CryptoManager::EncryptionPaddingNone);
    request.startRequest();
    request.waitForFinished();
    require(request.result());
    return request.plaintext();
}
void SecretsPassHelper::setCtxSigners(std::vector<std::string>) { unsupported(); }
void SecretsPassHelper::exportPublicKey(const std::string &, const std::string &) { unsupported(); }
void SecretsPassHelper::importPublicKey(const std::string &, bool) { unsupported(); }
void SecretsPassHelper::trustPublicKey(const std::string &) { unsupported(); }
void SecretsPassHelper::setPasswordCallback(std::function<std::string(std::string)>) { unsupported(); }

QString selectedTotp(InterfacePassFile &file, quint64 timestamp)
{
    file.decrypt();
    const std::string &entry = file.getDecrypted();
    const QString text = QString::fromUtf8(entry.data(), static_cast<int>(entry.size()));
    for (const QString &line : text.split('\n')) {
        if (!line.startsWith(QStringLiteral("otpauth://")))
            continue;
        if (!line.startsWith(QStringLiteral("otpauth://totp/")))
            unsupported(); // HOTP requires a separately reviewed counter-update path.
        const auto settings = Totp::parseSettings(line);
        if (Base32::decode(Base32::sanitizeInput(settings->key.toLatin1())).isNull())
            throw std::runtime_error("Invalid OTP key");
        return Totp::generateTotp(settings, timestamp);
    }
    throw std::runtime_error("Selected entry has no OTP URI");
}
