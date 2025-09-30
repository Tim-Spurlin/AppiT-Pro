#pragma once

#include <QObject>
#include <QNetworkAccessManager>
#include <QJsonDocument>
#include <QFile>
#include <QTextStream>

namespace haasp {

class AiOracle : public QObject {
    Q_OBJECT

public:
    explicit AiOracle(QObject *parent = nullptr);
    ~AiOracle();

signals:
    void codeGenerated(const QString &code, const QString &language);
    void suggestionReceived(const QString &suggestion);
    void errorOccurred(const QString &error);

public slots:
    void generateCode(const QString &prompt, const QString &language = "cpp");
    void getSuggestions(const QString &context);
    void analyzeCode(const QString &code);
    void refactorCode(const QString &code, const QString &requirements);

private:
    QNetworkAccessManager *m_network;
    QString m_grokApiKey;
    QString m_qwenApiKey;

    void loadApiKeys();
    void callGrokApi(const QString &endpoint, const QJsonObject &payload);
    void callQwenApi(const QString &endpoint, const QJsonObject &payload);
    QString extractCodeFromResponse(const QJsonDocument &doc);
};

} // namespace haasp