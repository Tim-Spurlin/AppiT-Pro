#pragma once

#include <QObject>
#include <QString>
#include <QVariantMap>
#include <QDateTime>

namespace haasp {

class QuantumConduit : public QObject
{
    Q_OBJECT

public:
    explicit QuantumConduit(QObject *parent = nullptr);

public slots:
    void routeMessage(const QString &message);

signals:
    void messageRouted(const QString &message);
    void synthesisCompleted(const QVariantMap &result);
};

} // namespace haasp
