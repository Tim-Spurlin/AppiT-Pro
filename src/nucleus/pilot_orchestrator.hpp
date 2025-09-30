#pragma once

#include <QObject>
#include <QProcess>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTimer>

namespace haasp {

class PilotOrchestrator : public QObject {
    Q_OBJECT

public:
    explicit PilotOrchestrator(QObject *parent = nullptr);
    ~PilotOrchestrator();

    Q_INVOKABLE void startPilot(const QString &pilotName);
    Q_INVOKABLE void stopPilot(const QString &pilotName);
    Q_INVOKABLE void sendMessage(const QString &pilotName, const QString &message);
    Q_INVOKABLE QStringList getActivePilots() const;
    Q_INVOKABLE QVariantMap getPilotStatus(const QString &pilotName) const;

signals:
    void pilotStarted(const QString &pilotName);
    void pilotStopped(const QString &pilotName);
    void pilotMessage(const QString &pilotName, const QString &message);
    void pilotError(const QString &pilotName, const QString &error);

private slots:
    void onPilotFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onPilotReadyRead();
    void checkPilotHealth();

private:
    struct PilotProcess {
        QProcess *process;
        QString name;
        bool active;
        QDateTime startTime;
    };

    QMap<QString, PilotProcess> m_pilots;
    QTimer *m_healthTimer;

    void setupPilotProcess(const QString &pilotName);
    QString getPilotScriptPath(const QString &pilotName) const;
};

} // namespace haasp