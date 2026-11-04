// Original adapter code: GPL-3.0-or-later. Upstream interfaces retain their notices.
#pragma once
#include "InterfacePassHelper.h"
#include <Crypto/cryptomanager.h>
#include <Crypto/key.h>
#include <QtCore/QVector>
#include <filesystem>

class SecretsPassHelper final : public InterfaceLibgpgfactory
{
public:
    SecretsPassHelper(const std::string &storeRoot, const QString &plugin,
                      const Sailfish::Crypto::Key::Identifier &privateKey);
    SecretsPassHelper(const SecretsPassHelper &) = delete;
    SecretsPassHelper &operator=(const SecretsPassHelper &) = delete;
    std::unique_ptr<InterfacePassFile> getPassFile(std::string path) override;
    std::vector<GpgKeys> listKeys(std::string pattern = "", bool secretOnly = false) override;
    std::vector<std::string> recipientsFor(const std::string &entry);
    std::string entryPath(const std::string &path) const;
    const std::string &storeRoot() const { return m_root; }
    QByteArray encryptBytes(const std::string &plain, const std::vector<std::string> &recipients);
    QByteArray decryptBytes(const QByteArray &cipher);
    void setCtxSigners(std::vector<std::string>) override;
    void exportPublicKey(const std::string &, const std::string &) override;
    void importPublicKey(const std::string &, bool) override;
    void trustPublicKey(const std::string &) override;
    void setPasswordCallback(std::function<std::string(std::string)>) override;
private:
    void loadCatalog();
    Sailfish::Crypto::Key publicKey(const std::string &fingerprint);
    Sailfish::Crypto::CryptoManager m_manager;
    std::string m_root;
    QString m_plugin;
    Sailfish::Crypto::Key::Identifier m_private;
    QVector<Sailfish::Crypto::Key> m_catalog;
    bool m_catalogLoaded = false;
};

// Decrypt selected entry and pass its first OTP URI to the pinned QtTotp code.
// No URI parser, Base32 codec, HMAC or clock implementation is introduced here.
QString selectedTotp(InterfacePassFile &file, quint64 timestamp);
