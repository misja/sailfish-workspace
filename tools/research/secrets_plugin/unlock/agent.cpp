// Scripted UI endpoint ONLY, using the stock PasswordAgent interface.
// Original fixture code: GPL-3.0-or-later. Never used with real passwords.
#include <QtCore/QCoreApplication>
#include <QtCore/QFile>
#include <QtCore/QSaveFile>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonArray>
#include <QtCore/QTimer>
#include <QtDBus/QDBusConnection>
#include <QtDBus/QDBusContext>
#include <QtDBus/QDBusMessage>
#include <QtDBus/QDBusObjectPath>
#include <QtDBus/QDBusPendingCallWatcher>
#include <QtDBus/QDBusReply>
#include <QtDBus/QDBusError>
#include <QtCore/QVariant>
#include <QtCore/QFileInfo>
#include <QtCore/QDir>
#include <unistd.h>
#include <utility>
#include <cstdio>

static QByteArray read(const QString &path) {
    QFile f(path);
    return f.open(QIODevice::ReadOnly)?f.readAll():QByteArray();
}
static QDBusMessage authority(const QString &method,const QVariantList &arguments) {
    auto call=QDBusMessage::createMethodCall(QString(),"/org/sailfishos/Security/PasswordAuthority",
                                            "org.sailfishos.Security.PasswordAuthority",method);
    call.setArguments(arguments);
    return call;
}
class SessionAgent final : public QObject, protected QDBusContext {
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface","org.sailfishos.Security.PasswordAgent")
public:
    SessionAgent(QString root,const QDBusConnection &connection,const QDBusConnection &foreign)
        : m_root(std::move(root)),m_connection(connection),m_foreign(foreign) {}
    bool ready(bool duplicateRejected) {
        m_state["ready"]=true;
        m_state["duplicateRegistrationRejected"]=duplicateRejected;
        return persist();
    }
public Q_SLOTS:
    void QueryPassword(const QString &cookie,const QString &messageText,const QVariantMap &properties) {
        setDelayedReply(true);
        const QDBusMessage query=message();
        const QDBusConnection replyConnection=connection();
        const QJsonObject control=QJsonDocument::fromJson(read(m_root+"/agent-control.json")).object();
        const QString phase=control.value("phase").toString(),action=control.value("action").toString();
        QJsonObject event;
        event["kind"]="prompt";event["phase"]=phase;event["action"]=action;
        event["callerPid"]=static_cast<int>(properties.value("applicationPid").toUInt());
        event["echo"]=properties.value("echo").toInt();
        event["allowedCharacters"]=properties.value("allowedCharacters").toInt();
        event["instruction"]=properties.value("enterCurrentPasswordText").toString();
        event["message"]=messageText;
        append(event);
        // A different connection must not validate even a known live cookie.
        auto *foreign=new QDBusPendingCallWatcher(m_foreign.asyncCall(authority(
            "ValidatePassword",{cookie,QStringLiteral("unauthorized synthetic value")}),10000),this);
        connect(foreign,&QDBusPendingCallWatcher::finished,this,
            [=](QDBusPendingCallWatcher *watcher) {
                const bool denied=watcher->isError()
                    &&watcher->error().type()==QDBusError::AccessDenied;
                watcher->deleteLater();
                QJsonObject checked;checked["kind"]="foreign-validation";checked["phase"]=phase;
                checked["denied"]=denied;append(checked);
                if(!denied) {
                    replyConnection.send(query.createErrorReply(QDBusError::AccessDenied,""));
                    return;
                }
                if(action=="disconnect") {
                    QJsonObject gone;gone["kind"]="agent-disconnect";gone["phase"]=phase;append(gone);
                    QCoreApplication::quit();
                    return;
                }
                if(action=="cancel") {
                    replyConnection.send(query.createErrorReply(
                        "org.sailfishos.Security.Error.Canceled",QString()));
                    return;
                }
                QByteArray input;
                if(action=="correct") {
                    input=read(m_root+"/fixture-password");
                    if(input.endsWith('\n'))input.chop(1);
                } else if(action=="wrong") input="wrong synthetic fixture password";
                else if(action=="oversize") input=QByteArray(8192,'x');
                else if(action!="empty") {
                    replyConnection.send(query.createErrorReply(
                        QDBusError::Failed,"Unknown synthetic response mode"));
                    return;
                }
                // No password is logged or returned by QueryPassword. Native
                // PasswordAgent holds the input after this standard method call.
                auto *validated=new QDBusPendingCallWatcher(m_connection.asyncCall(authority(
                    "ValidatePassword",{cookie,QString::fromUtf8(input)}),10000),this);
                connect(validated,&QDBusPendingCallWatcher::finished,this,
                    [=](QDBusPendingCallWatcher *result) {
                        const bool success=!result->isError();
                        QJsonObject done;done["kind"]="validation";done["phase"]=phase;
                        done["acceptedByAuthority"]=success;append(done);
                        if(success)replyConnection.send(query.createReply());
                        else replyConnection.send(query.createErrorReply(QDBusError::Failed,
                            "Native password authority refused fixture response"));
                        result->deleteLater();
                    });
            });
    }
    void Cancel(const QString &) {
        QJsonObject event;event["kind"]="authority-cancel";append(event);
    }
private:
    void append(const QJsonObject &event) {
        m_events.append(event);persist();
    }
    bool persist() {
        m_state["events"]=m_events;
        QSaveFile f(m_root+"/agent-trace.json");
        f.setDirectWriteFallback(false);
        const QByteArray data=QJsonDocument(m_state).toJson();
        return f.open(QIODevice::WriteOnly)&&f.write(data)==data.size()&&f.commit();
    }
    QString m_root;
    QDBusConnection m_connection,m_foreign;
    QJsonArray m_events;
    QJsonObject m_state;
};
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);
    if(argc!=2)return 2;
    const QString root=QFileInfo(QString::fromLocal8Bit(argv[1])).canonicalFilePath();
    const QFileInfo info(root);
    if(!info.isDir()||info.dir().absolutePath()!="/home/ubuntu"
        ||!info.fileName().startsWith("sailfish-rnp-api-fixture-")
        ||info.ownerId()!=static_cast<uint>(geteuid()))return 2;
    const QString address="unix:path="+root+"/runtime/sailfishsecretsd/p2pSocket-agent";
    auto connection=QDBusConnection::connectToPeer(address,"fixture-session-agent");
    auto foreign=QDBusConnection::connectToPeer(address,"fixture-foreign-agent");
    if(!connection.isConnected()||!foreign.isConnected())return 3;
    SessionAgent agent(root,connection,foreign);
    if(!connection.registerObject("/fixture/PasswordAgent",&agent,QDBusConnection::ExportAllSlots))return 4;
    const auto first=connection.call(authority("RegisterSessionAgent",
        {QVariant::fromValue(QDBusObjectPath("/fixture/PasswordAgent"))}),QDBus::Block,10000);
    if(first.type()==QDBusMessage::ErrorMessage)return 5;
    const auto duplicate=foreign.call(authority("RegisterSessionAgent",
        {QVariant::fromValue(QDBusObjectPath("/fixture/OtherAgent"))}),QDBus::Block,10000);
    const bool refused=duplicate.type()==QDBusMessage::ErrorMessage
        &&duplicate.errorName()=="org.sailfishos.Security.Error.ExistingAgent";
    if(!agent.ready(refused))return 6;
    return app.exec();
}
#include "agent.moc"
