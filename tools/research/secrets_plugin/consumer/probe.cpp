// Synthetic SDK consumer checks; published RFC6238 Appendix B vectors only.
#include "SecretsPass.h"
#include "GpgIdManage.h"
#include "FileSearch.h"
#include <QtCore/QCoreApplication>
#include <QtCore/QFile>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonArray>
#include <QtCore/QCryptographicHash>
#include <set>
#include <cstdio>
#include <stdexcept>

static QByteArray read(const QString &path)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly))
        throw std::runtime_error("Fixture read failed");
    return file.readAll();
}
template<typename F> bool refused(F action)
{
    try { action(); } catch (const std::exception &) { return true; }
    return false;
}
static std::set<std::string> keys(const std::vector<std::string> &v)
{
    return {v.begin(), v.end()};
}
int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    if (argc != 2) return 2;
    const QJsonObject config = QJsonDocument::fromJson(read(QString::fromLocal8Bit(argv[1]))).object();
    QJsonObject checks, observations;
    const QString plugin = QStringLiteral("org.sailfishos.crypto.plugin.rnp.test");
    const std::string root = config.value("store").toString().toStdString();
    auto reference = [&](const QString &tag) {
        return Sailfish::Crypto::Key::Identifier(config.value(tag+"Sub").toString(),
                                                config.value(tag+"Id").toString(), plugin);
    };
    try {
        SecretsPassHelper a(root, plugin, reference("a")), b(root, plugin, reference("b"));
        const std::string original = read(config.value("text").toString()).toStdString();
        const std::string updated = read(config.value("updatedText").toString()).toStdString();
        const std::string afp = config.value("aPrimary").toString().toStdString();
        const std::string bfp = config.value("bPrimary").toString().toStdString();
        checks["root-policy"] = keys(a.recipientsFor("root.gpg")) == std::set<std::string>{afp};
        checks["inherited-policy"] = keys(a.recipientsFor("child/inherited.gpg")) == std::set<std::string>{afp};
        checks["nested-policy-replaces-root"] = keys(a.recipientsFor("nested/entry.gpg")) == std::set<std::string>{bfp};
        checks["multiple-policy"] = keys(a.recipientsFor("multi/entry.gpg")) == std::set<std::string>{afp,bfp};
        checks["unresolved-policy-refused"] = refused([&]{a.recipientsFor("unresolved/entry.gpg");});
        checks["ambiguous-policy-refused"] = refused([&]{a.recipientsFor("ambiguous/entry.gpg");});
        checks["empty-policy-refused"] = refused([&]{a.recipientsFor("empty/entry.gpg");});
        SecretsPassHelper noPolicy(config.value("missingRoot").toString().toStdString(), plugin, reference("a"));
        checks["missing-policy-refused"] = refused([&]{noPolicy.recipientsFor("entry.gpg");});
        const QString unreadable = QString::fromStdString(root)+"/unreadable/.gpg-id";
        const bool unreadableMode = QFile::setPermissions(unreadable, QFile::Permissions());
        const bool policyRefused = refused([&]{a.recipientsFor("unreadable/entry.gpg");});
        const bool policyRestored = QFile::setPermissions(unreadable, QFile::ReadOwner|QFile::WriteOwner);
        checks["unreadable-policy-refused"] = unreadableMode && policyRefused && policyRestored;

        const QString guardPath = QString::fromStdString(root)+"/unresolved/entry.gpg";
        const QByteArray guardBefore = read(guardPath);
        auto guard = a.getPassFile("unresolved/entry.gpg"); guard->decrypt();
        const bool guardRefused = refused([&] {
            const auto recipients = a.recipientsFor("unresolved/entry.gpg");
            guard->encrypt(updated, recipients, false);
        });
        checks["unresolved-save-preserves-cipher-and-cache"] = guardRefused
            && read(guardPath)==guardBefore && guard->getDecrypted()==original;

        for (const auto &item : std::vector<std::pair<std::string,SecretsPassHelper*>>{
                {"root.gpg",&a},{"child/inherited.gpg",&a},{"nested/entry.gpg",&b},{"multi/entry.gpg",&a}}) {
            auto file = item.second->getPassFile(item.first);
            file->decrypt();
            checks[QString::fromStdString(item.first)+"-read"] = file->getDecrypted()==original;
            const auto recipients = item.second->recipientsFor(item.first);
            // The interface pointer must dispatch the new virtual save seam.
            file->encrypt(updated, recipients, false);
            checks[QString::fromStdString(item.first)+"-committed-cache"] = file->getDecrypted()==updated;
            auto fresh = item.second->getPassFile(item.first); fresh->decrypt();
            checks[QString::fromStdString(item.first)+"-fresh-read"] = fresh->getDecrypted()==updated;
        }
        auto multiB=b.getPassFile("multi/entry.gpg");multiB->decrypt();
        checks["second-recipient-store-read"] = multiB->getDecrypted()==updated;

        const QString blockedPath = QString::fromStdString(root)+"/blocked/entry.gpg";
        auto blocked=a.getPassFile("blocked/entry.gpg");blocked->decrypt();
        const QByteArray beforeBlocked=read(blockedPath);
        const auto blockedRecipients=a.recipientsFor("blocked/entry.gpg");
        const QString blockedDir=QString::fromStdString(root)+"/blocked";
        const bool blockedMode=QFile::setPermissions(blockedDir,QFile::ReadOwner|QFile::ExeOwner);
        const bool saveRefused=refused([&]{blocked->encrypt(updated,blockedRecipients,false);});
        const bool blockedRestored=QFile::setPermissions(blockedDir,QFile::ReadOwner|QFile::WriteOwner|QFile::ExeOwner);
        checks["failed-save-preserves-cipher-and-cache"] = blockedMode&&saveRefused&&blockedRestored
            &&read(blockedPath)==beforeBlocked&&blocked->getDecrypted()==original;
        observations["failed-save-case"] = "parent read/execute only; existing file still writable; QSaveFile fallback disabled";

        auto stale=a.getPassFile("root.gpg");stale->decrypt();
        const bool hadPlain=stale->getDecrypted()==updated;
        stale->setFullPath(a.entryPath("nested/entry.gpg"));
        checks["wrong-private-no-stale-cache"] = hadPlain&&refused([&]{stale->decrypt();})&&stale->getDecrypted().empty();
        stale->setFullPath(a.entryPath("corrupt.gpg"));
        checks["corrupt-cipher-refused"] = refused([&]{stale->decrypt();})&&stale->getDecrypted().empty();
        checks["outside-entry-refused"] = refused([&]{a.getPassFile(config.value("outside").toString().toStdString());});
        stale->setFullPath(config.value("outside").toString().toStdString());
        checks["changed-path-outside-refused"] = refused([&]{stale->decrypt();})&&stale->getDecrypted().empty();
        checks["symlink-outside-refused"] = refused([&]{a.getPassFile("escape.gpg");});
        checks["secret-enumeration-not-fabricated"] = refused([&]{a.listKeys("",true);});

        // Existing FileSearch performs the walk; no replacement store walker.
        FileSearch search;
        std::set<std::string> listed;
        search.searchDown(root,".*",{},".*",[](const std::string&){return true;},
            [&](const std::string &path){
                if(std::filesystem::path(path).extension()==".gpg") listed.insert(path);
            });
        checks["existing-file-search"] = listed.count(a.entryPath("root.gpg"))
            &&listed.count(a.entryPath("child/inherited.gpg"))&&listed.count(a.entryPath("multi/entry.gpg"));

        // Expected data from https://www.rfc-editor.org/rfc/rfc6238.html#appendix-B
        const quint64 times[]={59,1111111109,1111111111,1234567890,2000000000,20000000000ULL};
        const char *algorithms[]={"sha1","sha256","sha512"};
        const char *expected[][3]={
            {"94287082","46119246","90693936"},{"07081804","68084774","25091201"},
            {"14050471","67062674","99943326"},{"89005924","91819424","93441116"},
            {"69279037","90698825","38618901"},{"65353130","77737706","47863826"}};
        for(int algorithm=0;algorithm<3;++algorithm) {
            auto otp=a.getPassFile(std::string("otp/")+algorithms[algorithm]+".gpg");
            for(int row=0;row<6;++row)
                checks[QString("rfc6238-%1-%2").arg(algorithms[algorithm]).arg(times[row])]
                    = selectedTotp(*otp,times[row])==QString::fromLatin1(expected[row][algorithm]);
        }
        observations["consumer_maps"]=QString::fromUtf8(read("/proc/self/maps"));
    } catch(const std::exception &error) {
        observations["error"]=QString::fromUtf8(error.what());
        checks["completed"]=false;
    }
    bool pass=!checks.isEmpty();
    for(auto it=checks.begin();it!=checks.end();++it)pass=pass&&it.value().toBool();
    QJsonObject report;report["status"]=pass?"pass":"fail";report["checks"]=checks;report["observations"]=observations;
    const QByteArray output=QJsonDocument(report).toJson();
    fwrite(output.constData(),1,output.size(),stdout);
    return pass?0:1;
}
