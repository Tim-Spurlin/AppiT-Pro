#include "pilot_orchestrator.hpp"
#include <QDir>
#include <QStandardPaths>
#include <QDebug>

namespace haasp {

PilotOrchestrator::PilotOrchestrator(QObject *parent)
    : QObject(parent), m_healthTimer(new QTimer(this))
{
    connect(m_healthTimer, &QTimer::timeout, this, &PilotOrchestrator::checkPilotHealth);
    m_healthTimer->start(30000); // Check every 30 seconds
}

PilotOrchestrator::~PilotOrchestrator()
{
    // Stop all pilots
    for (auto it = m_pilots.begin(); it != m_pilots.end(); ++it) {
        if (it->process && it->process->state() == QProcess::Running) {
            it->process->terminate();
            it->process->waitForFinished(5000);
        }
    }
}

void PilotOrchestrator::startPilot(const QString &pilotName)
{
    if (m_pilots.contains(pilotName)) {
        qWarning() << "Pilot already running:" << pilotName;
        return;
    }

    setupPilotProcess(pilotName);

    PilotProcess &pilot = m_pilots[pilotName];
    pilot.process->start();

    if (pilot.process->waitForStarted(5000)) {
        pilot.active = true;
        pilot.startTime = QDateTime::currentDateTime();
        emit pilotStarted(pilotName);
        qDebug() << "Started pilot:" << pilotName;
    } else {
        emit pilotError(pilotName, "Failed to start pilot process");
        qWarning() << "Failed to start pilot:" << pilotName;
    }
}

void PilotOrchestrator::stopPilot(const QString &pilotName)
{
    if (!m_pilots.contains(pilotName)) {
        return;
    }

    PilotProcess &pilot = m_pilots[pilotName];
    if (pilot.process && pilot.process->state() == QProcess::Running) {
        pilot.process->terminate();
        pilot.process->waitForFinished(5000);

        if (pilot.process->state() == QProcess::Running) {
            pilot.process->kill();
        }
    }

    pilot.active = false;
    emit pilotStopped(pilotName);
    qDebug() << "Stopped pilot:" << pilotName;
}

void PilotOrchestrator::sendMessage(const QString &pilotName, const QString &message)
{
    if (!m_pilots.contains(pilotName)) {
        emit pilotError(pilotName, "Pilot not found");
        return;
    }

    PilotProcess &pilot = m_pilots[pilotName];
    if (pilot.process && pilot.active) {
        pilot.process->write((message + "\n").toUtf8());
    }
}

QStringList PilotOrchestrator::getActivePilots() const
{
    QStringList active;
    for (auto it = m_pilots.begin(); it != m_pilots.end(); ++it) {
        if (it->active) {
            active.append(it->name);
        }
    }
    return active;
}

QVariantMap PilotOrchestrator::getPilotStatus(const QString &pilotName) const
{
    QVariantMap status;
    status["name"] = pilotName;
    status["active"] = false;
    status["uptime"] = 0;
    status["memory_usage"] = 0;

    if (m_pilots.contains(pilotName)) {
        const PilotProcess &pilot = m_pilots[pilotName];
        status["active"] = pilot.active;
        if (pilot.active && pilot.startTime.isValid()) {
            status["uptime"] = pilot.startTime.secsTo(QDateTime::currentDateTime());
        }
        // Memory usage would require platform-specific code
    }

    return status;
}

void PilotOrchestrator::onPilotFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    QProcess *process = qobject_cast<QProcess*>(sender());
    if (!process) return;

    QString pilotName;
    for (auto it = m_pilots.begin(); it != m_pilots.end(); ++it) {
        if (it->process == process) {
            pilotName = it->name;
            it->active = false;
            break;
        }
    }

    if (!pilotName.isEmpty()) {
        if (exitStatus == QProcess::CrashExit) {
            emit pilotError(pilotName, "Pilot crashed");
        } else if (exitCode != 0) {
            emit pilotError(pilotName, QString("Pilot exited with code %1").arg(exitCode));
        }
        emit pilotStopped(pilotName);
        qDebug() << "Pilot finished:" << pilotName << "exit code:" << exitCode;
    }
}

void PilotOrchestrator::onPilotReadyRead()
{
    QProcess *process = qobject_cast<QProcess*>(sender());
    if (!process) return;

    QString pilotName;
    for (auto it = m_pilots.begin(); it != m_pilots.end(); ++it) {
        if (it->process == process) {
            pilotName = it->name;
            break;
        }
    }

    if (!pilotName.isEmpty()) {
        QByteArray data = process->readAllStandardOutput();
        QString message = QString::fromUtf8(data).trimmed();

        if (!message.isEmpty()) {
            emit pilotMessage(pilotName, message);
        }

        // Also check stderr
        data = process->readAllStandardError();
        if (!data.isEmpty()) {
            QString error = QString::fromUtf8(data).trimmed();
            emit pilotError(pilotName, error);
        }
    }
}

void PilotOrchestrator::checkPilotHealth()
{
    for (auto it = m_pilots.begin(); it != m_pilots.end(); ++it) {
        if (it->active && it->process) {
            if (it->process->state() != QProcess::Running) {
                it->active = false;
                emit pilotError(it->name, "Pilot process died unexpectedly");
                emit pilotStopped(it->name);
            }
        }
    }
}

void PilotOrchestrator::setupPilotProcess(const QString &pilotName)
{
    PilotProcess pilot;
    pilot.name = pilotName;
    pilot.process = new QProcess(this);
    pilot.active = false;

    connect(pilot.process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &PilotOrchestrator::onPilotFinished);
    connect(pilot.process, &QProcess::readyReadStandardOutput,
            this, &PilotOrchestrator::onPilotReadyRead);
    connect(pilot.process, &QProcess::readyReadStandardError,
            this, &PilotOrchestrator::onPilotReadyRead);

    QString scriptPath = getPilotScriptPath(pilotName);
    if (!scriptPath.isEmpty()) {
        pilot.process->setProgram("python3");
        pilot.process->setArguments({scriptPath});
    }

    m_pilots[pilotName] = pilot;
}

QString PilotOrchestrator::getPilotScriptPath(const QString &pilotName) const
{
    QString basePath = QDir::currentPath() + "/pilots/";
    QString scriptPath = basePath + pilotName + ".py";

    if (QFile::exists(scriptPath)) {
        return scriptPath;
    }

    return QString(); // Not found
}

} // namespace haasp