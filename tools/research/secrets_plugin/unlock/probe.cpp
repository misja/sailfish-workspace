// Protected-key callback through real Secrets/PasswordAgent; no password provider.
#include "SecretsPass.h"
#include <QtCore/QCoreApplication>
#include <QtCore/QFile>
#include <QtCore/QFileInfo>
#include <QtCore/QSaveFile>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonArray>
#include <unistd.h>
#include <cstdio>
#include <stdexcept>
static QByteArray read(const QString &path) {
    QFile f(path);if(!f.open(QIODevice::ReadOnly))throw std::runtime_error("Fixture read failed");
    return f.readAll();
}
template<typename F>bool refused(F action) {
    try{action();}catch(const std::exception&){return true;}return false;
}
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);if(argc!=2)return 2;
    const QString configPath=QString::fromLocal8Bit(argv[1]);
    const QString root=QFileInfo(configPath).absolutePath();
    const auto config=QJsonDocument::fromJson(read(configPath)).object();
    QJsonObject checks,observations;
    observations["consumerPid"]=static_cast<int>(getpid());
    observations["daemonPid"]=config.value("daemonPid");
    auto trace=[&]{return QJsonDocument::fromJson(read(root+"/agent-trace.json")).object();};
    auto count=[&] {
        int n=0;for(const auto &value:trace().value("events").toArray())
            if(value.toObject().value("kind")=="prompt")++n;
        return n;
    };
    auto phase=[&](const QString &name,const QString &action) {
        QJsonObject c;c["phase"]=name;c["action"]=action;
        const QByteArray data=QJsonDocument(c).toJson();
        QSaveFile f(root+"/agent-control.json");f.setDirectWriteFallback(false);
        if(!f.open(QIODevice::WriteOnly)||f.write(data)!=data.size()||!f.commit())
            throw std::runtime_error("Cannot set fixture phase");
    };
    try {
        const QString plugin="org.sailfishos.crypto.plugin.rnp.test";
        const Sailfish::Crypto::Key::Identifier key(config.value("aSub").toString(),
            config.value("aId").toString(),plugin);
        SecretsPassHelper helper(config.value("store").toString().toStdString(),plugin,key);
        auto file=helper.getPassFile("entry.gpg");
        const std::string plain=read(config.value("text").toString()).toStdString();
        const QByteArray before=read(config.value("entry").toString());
        checks["standard-agent-registered"]=trace().value("ready").toBool();
        checks["second-registration-refused"]=trace().value("duplicateRegistrationRejected").toBool();
        auto attempt=[&](const QString &name,const QString &action,bool success) {
            phase(name,action);const int previous=count();
            const bool failed=refused([&]{file->decrypt();});
            checks[name]=success?(!failed&&file->getDecrypted()==plain)
                :(failed&&file->getDecrypted().empty());
            checks[name+"-prompted"]=count()>previous;
            checks[name+"-cipher-unchanged"]=read(config.value("entry").toString())==before;
        };
        attempt("protected-success","correct",true);
        attempt("wrong-password","wrong",false);
        phase("totp-success","correct");int previous=count();
        checks["protected-totp"]=selectedTotp(*file,59)=="94287082";
        checks["protected-totp-prompted"]=count()>previous;
        attempt("cancel-after-success","cancel",false);
        attempt("empty-response","empty",false);
        attempt("oversize-response","oversize",false);
        for(const QString &name:{QString("wrong"),QString("symmetric")}) {
            phase(name+"-no-prompt","correct");previous=count();
            file->setFullPath(helper.entryPath((name+".gpg").toStdString()));
            checks[name+"-refused"]=refused([&]{file->decrypt();})&&file->getDecrypted().empty();
            checks[name+"-no-prompt"]=count()==previous;
        }
        file->setFullPath(helper.entryPath("entry.gpg"));
        attempt("success-after-refusals","correct",true);
        attempt("agent-disconnect","disconnect",false);
        phase("agent-unavailable","correct");previous=count();
        checks["unavailable-agent-refused"]=refused([&]{file->decrypt();})&&file->getDecrypted().empty();
        checks["unavailable-agent-no-prompt"]=count()==previous;
        bool foreign=true,masked=true,instruction=true,daemonOnly=true;int prompts=0,denied=0;
        for(const auto &value:trace().value("events").toArray()) {
            const QJsonObject event=value.toObject();
            if(event.value("kind")=="foreign-validation") {
                ++denied;foreign=foreign&&event.value("denied").toBool();
            }
            if(event.value("kind")=="prompt") {
                ++prompts;masked=masked&&event.value("echo").toInt()==2;
                instruction=instruction&&event.value("instruction").toString().contains(config.value("aSub").toString().right(8))
                    &&event.value("instruction").toString().contains("decrypt");
                daemonOnly=daemonOnly&&event.value("callerPid").toInt()==config.value("daemonPid").toInt();
            }
        }
        checks["foreign-validation-refused"]=prompts>0&&denied==prompts&&foreign;
        checks["password-echo-mode"]=prompts>0&&masked;
        checks["correct-private-key-instruction"]=prompts>0&&instruction;
        // Observation, not an authorization promise about the original consumer.
        observations["agentCallerPidMatchesDaemon"]=daemonOnly;
        observations["promptCount"]=prompts;
        observations["agentTrace"]=trace();
        observations["consumer_maps"]=QString::fromUtf8(read("/proc/self/maps"));
    } catch(const std::exception &error) {
        observations["error"]=QString::fromUtf8(error.what());checks["completed"]=false;
    }
    bool pass=!checks.isEmpty();for(auto it=checks.begin();it!=checks.end();++it)pass=pass&&it.value().toBool();
    QJsonObject report;report["checks"]=checks;report["observations"]=observations;report["status"]=pass?"pass":"fail";
    const QByteArray out=QJsonDocument(report).toJson();fwrite(out.constData(),1,out.size(),stdout);
    return pass?0:1;
}
