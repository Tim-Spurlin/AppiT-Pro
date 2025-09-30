#include "ai_oracle.hpp"
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonObject>
#include <QJsonArray>
#include <QEventLoop>
#include <QDebug>
#include <QDir>
#include <QFile>

namespace haasp {

AiOracle::AiOracle(QObject *parent) : QObject(parent) {
    m_network = new QNetworkAccessManager(this);
    loadApiKeys();
}

AiOracle::~AiOracle() {
    delete m_network;
}

void AiOracle::loadApiKeys() {
    QFile envFile(QDir::currentPath() + "/../.env");
    if (envFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream in(&envFile);
        while (!in.atEnd()) {
            QString line = in.readLine().trimmed();
            if (line.startsWith("GROK_API_KEY=")) {
                m_grokApiKey = line.mid(13);
            } else if (line.startsWith("QWEN_API_KEY=")) {
                m_qwenApiKey = line.mid(12);
            }
        }
        envFile.close();
    }

    if (m_grokApiKey.isEmpty() && m_qwenApiKey.isEmpty()) {
        qWarning() << "No AI API keys found in .env file";
    }
}

void AiOracle::generateCode(const QString &prompt, const QString &language) {
    if (m_grokApiKey.isEmpty() && m_qwenApiKey.isEmpty()) {
        emit errorOccurred("No API keys configured");
        return;
    }

    QString systemPrompt = QString("You are an expert software engineer. Generate high-quality, production-ready %1 code. "
                                   "Follow best practices, include proper error handling, and ensure the code is sophisticated and efficient. "
                                   "Only return the code without explanations.").arg(language);

    QJsonObject payload;
    payload["model"] = "grok-beta"; // or appropriate model
    payload["messages"] = QJsonArray({
        QJsonObject{{"role", "system"}, {"content", systemPrompt}},
        QJsonObject{{"role", "user"}, {"content", prompt}}
    });
    payload["temperature"] = 0.1; // Low temperature for deterministic, high-quality code

    if (!m_grokApiKey.isEmpty()) {
        callGrokApi("chat/completions", payload);
    } else {
        callQwenApi("chat/completions", payload);
    }
}

void AiOracle::getSuggestions(const QString &context) {
    QString prompt = QString("Analyze this code context and provide intelligent suggestions for improvement: %1").arg(context);
    generateCode(prompt, "suggestions");
}

void AiOracle::analyzeCode(const QString &code) {
    QString prompt = QString("Perform a comprehensive code analysis on the following code. "
                           "Identify potential bugs, performance issues, security vulnerabilities, "
                           "and suggest improvements: %1").arg(code);
    generateCode(prompt, "analysis");
}

void AiOracle::refactorCode(const QString &code, const QString &requirements) {
    QString prompt = QString("Refactor the following code according to these requirements: %1\n\nCode: %2").arg(requirements, code);
    generateCode(prompt, "refactored");
}

void AiOracle::callGrokApi(const QString &endpoint, const QJsonObject &payload) {
    QNetworkRequest request(QUrl("https://api.x.ai/v1/" + endpoint));
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", QString("Bearer %1").arg(m_grokApiKey).toUtf8());

    QNetworkReply *reply = m_network->post(request, QJsonDocument(payload).toJson());
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
            QString code = extractCodeFromResponse(doc);
            emit codeGenerated(code, "cpp"); // Default to cpp, could detect
        } else {
            emit errorOccurred(reply->errorString());
        }
        reply->deleteLater();
    });
}

void AiOracle::callQwenApi(const QString &endpoint, const QJsonObject &payload) {
    QNetworkRequest request(QUrl("https://api.qwen.ai/v1/" + endpoint)); // Hypothetical endpoint
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", QString("Bearer %1").arg(m_qwenApiKey).toUtf8());

    QNetworkReply *reply = m_network->post(request, QJsonDocument(payload).toJson());
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
            QString code = extractCodeFromResponse(doc);
            emit codeGenerated(code, "cpp");
        } else {
            emit errorOccurred(reply->errorString());
        }
        reply->deleteLater();
    });
}

QString AiOracle::extractCodeFromResponse(const QJsonDocument &doc) {
    QJsonObject obj = doc.object();
    QJsonArray choices = obj["choices"].toArray();
    if (!choices.isEmpty()) {
        QJsonObject choice = choices[0].toObject();
        QJsonObject message = choice["message"].toObject();
        return message["content"].toString();
    }
    return QString();
}

} // namespace haasp