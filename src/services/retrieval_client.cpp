#include "retrieval_client.hpp"
#include <QNetworkRequest>
#include <QHttpMultiPart>
#include <QTimer>
#include <QDebug>
#include <QJsonParseError>
#include <functional>

namespace haasp {
namespace services {

RetrievalClient::RetrievalClient(QObject *parent)
    : QObject(parent)
    , m_networkManager(std::make_unique<QNetworkAccessManager>(this))
    , m_statisticsTimer(new QTimer(this))
{
    // Setup statistics refresh timer
    m_statisticsTimer->setInterval(10000); // 10 seconds
    connect(m_statisticsTimer, &QTimer::timeout, this, &RetrievalClient::onStatisticsTimer);
    
    qDebug() << "RetrievalClient initialized";
}

RetrievalClient::~RetrievalClient() = default;

void RetrievalClient::setServiceUrl(const QString& url)
{
    if (m_serviceUrl != url) {
        m_serviceUrl = url;
        emit serviceUrlChanged();
        
        // Reconnect if we were previously connected
        if (m_connected) {
            connectToService();
        }
    }
}

void RetrievalClient::connectToService()
{
    qDebug() << "Connecting to retrieval service at" << m_serviceUrl;
    
    // Test connection with health check
    QNetworkReply* reply = sendGetRequest("/");
    
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        reply->deleteLater();
        
        if (reply->error() == QNetworkReply::NoError) {
            QJsonParseError parseError;
            QJsonDocument doc = QJsonDocument::fromJson(reply->readAll(), &parseError);
            
            if (parseError.error == QJsonParseError::NoError) {
                QJsonObject response = doc.object();
                
                if (response["status"].toString() == "running") {
                    m_connected = true;
                    m_statisticsTimer->start();
                    emit connectedChanged();
                    emit serviceStatusChanged("connected");
                    
                    qDebug() << "✅ Connected to retrieval service";
                    
                    // Get initial statistics
                    refreshStatistics();
                } else {
                    m_connected = false;
                    emit connectedChanged();
                    emit serviceStatusChanged("service_not_ready");
                }
            } else {
                qDebug() << "Invalid JSON response from service";
                m_connected = false;
                emit connectedChanged();
                emit serviceStatusChanged("invalid_response");
            }
        } else {
            qDebug() << "Failed to connect to retrieval service:" << reply->errorString();
            m_connected = false;
            emit connectedChanged();
            emit serviceStatusChanged("connection_failed");
        }
    });
}

void RetrievalClient::onNetworkReplyFinished()
{
    QNetworkReply* reply = qobject_cast<QNetworkReply*>(sender());
    if (!reply) {
        qWarning() << "Invalid reply object in onNetworkReplyFinished";
        return;
    }
    
    reply->deleteLater();
    
    if (reply->error() != QNetworkReply::NoError) {
        qWarning() << "Network error:" << reply->errorString();
        return;
    }
    
    // Handle successful reply - could process response data here if needed
    qDebug() << "Network reply finished successfully";
}

void RetrievalClient::disconnectFromService()
{
    m_connected = false;
    m_statisticsTimer->stop();
    
    // Cancel active requests
    for (auto reply : m_activeRequests.keys()) {
        reply->abort();
        reply->deleteLater();
    }
    m_activeRequests.clear();
    
    emit connectedChanged();
    emit serviceStatusChanged("disconnected");
    
    qDebug() << "Disconnected from retrieval service";
}

void RetrievalClient::addDocument(const QString& docId, const QString& content,
                                 const QString& filePath, const QString& language,
                                 const QVariantMap& metadata)
{
    if (!m_connected) {
        emit documentAdded(docId, false);
        return;
    }
    
    QJsonObject request;
    request["doc_id"] = docId;
    request["content"] = content;
    request["file_path"] = filePath;
    request["language"] = language;
    request["metadata"] = QJsonObject::fromVariantMap(metadata);
    
    QNetworkReply* reply = sendPostRequest("/documents", request);
    
    connect(reply, &QNetworkReply::finished, this, [this, reply, docId]() {
        reply->deleteLater();
        
        if (reply->error() == QNetworkReply::NoError) {
            QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
            QJsonObject response = doc.object();
            
            bool success = response["status"].toString() == "success";
            emit documentAdded(docId, success);
            
            qDebug() << "Document" << docId << (success ? "added successfully" : "failed to add");
        } else {
            emit documentAdded(docId, false);
            qDebug() << "Failed to add document:" << reply->errorString();
        }
    });
}

void RetrievalClient::performSearch(const QString& query, int k, const QString& mode, const QString& pilotId)
{
    if (!m_connected) {
        emit searchFailed("Service not connected", query);
        return;
    }
    
    QJsonObject request;
    request["query"] = query;
    request["k"] = k;
    request["mode"] = mode;
    if (!pilotId.isEmpty()) {
        request["pilot_id"] = pilotId;
    }
    request["include_conversation"] = true;
    
    QNetworkReply* reply = sendPostRequest("/search", request);
    m_activeRequests[reply] = query;
    
    connect(reply, &QNetworkReply::finished, this, [this, reply, query]() {
        handleSearchResponse(reply, query);
    });
    
    qDebug() << "Performing search:" << query;
}

void RetrievalClient::performRAGQuery(const QString& query, int k, const QString& taskType, const QString& pilotId)
{
    if (!m_connected) {
        emit ragFailed("Service not connected", query);
        return;
    }
    
    QJsonObject request;
    request["query"] = query;
    request["k"] = k;
    request["task_type"] = taskType;
    if (!pilotId.isEmpty()) {
        request["pilot_id"] = pilotId;
    }
    request["include_sources"] = true;
    
    QNetworkReply* reply = sendPostRequest("/rag", request);
    m_activeRequests[reply] = query;
    
    connect(reply, &QNetworkReply::finished, this, [this, reply, query]() {
        handleRAGResponse(reply, query);
    });
    
    qDebug() << "Performing RAG query:" << query;
}

void RetrievalClient::addConversation(const QString& pilotId, const QString& utterance, const QString& speaker)
{
    if (!m_connected) {
        emit conversationAdded(pilotId, false);
        return;
    }
    
    QJsonObject request;
    request["pilot_id"] = pilotId;
    request["utterance"] = utterance;
    request["speaker"] = speaker;
    
    QNetworkReply* reply = sendPostRequest("/conversations", request);
    
    connect(reply, &QNetworkReply::finished, this, [this, reply, pilotId]() {
        handleConversationResponse(reply, pilotId);
    });
}

void RetrievalClient::getConversationHistory(const QString& pilotId, int limit)
{
    if (!m_connected) {
        emit conversationHistoryReceived(pilotId, QVariantList());
        return;
    }
    
    QString endpoint = QString("/conversations/%1?limit=%2").arg(pilotId).arg(limit);
    QNetworkReply* reply = sendGetRequest(endpoint);
    
    connect(reply, &QNetworkReply::finished, this, [this, reply, pilotId]() {
        reply->deleteLater();
        
        if (reply->error() == QNetworkReply::NoError) {
            QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
            QJsonObject response = doc.object();
            
            QJsonArray messages = response["messages"].toArray();
            QVariantList messagesList;
            
            for (const QJsonValue& msg : messages) {
                messagesList.append(msg.toObject().toVariantMap());
            }
            
            emit conversationHistoryReceived(pilotId, messagesList);
        } else {
            emit conversationHistoryReceived(pilotId, QVariantList());
        }
    });
}

void RetrievalClient::triggerReindex(bool force)
{
    if (!m_connected) {
        return;
    }
    
    QString endpoint = QString("/reindex?force=%1").arg(force ? "true" : "false");
    QNetworkReply* reply = sendPostRequest("/reindex", QJsonObject());
    
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        reply->deleteLater();
        
        if (reply->error() == QNetworkReply::NoError) {
            emit reindexStarted();
            qDebug() << "Reindexing started";
        }
    });
}

void RetrievalClient::refreshStatistics()
{
    if (!m_connected) {
        return;
    }
    
    QNetworkReply* reply = sendGetRequest("/statistics");
    
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        handleStatisticsResponse(reply);
    });
}

void RetrievalClient::onStatisticsTimer()
{
    refreshStatistics();
}

// Private methods

QNetworkReply* RetrievalClient::sendPostRequest(const QString& endpoint, const QJsonObject& data)
{
    QUrl url(m_serviceUrl + endpoint);
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    
    QJsonDocument doc(data);
    return m_networkManager->post(request, doc.toJson());
}

QNetworkReply* RetrievalClient::sendGetRequest(const QString& endpoint)
{
    QUrl url(m_serviceUrl + endpoint);
    QNetworkRequest request(url);
    
    return m_networkManager->get(request);
}

void RetrievalClient::handleSearchResponse(QNetworkReply* reply, const QString& originalQuery)
{
    reply->deleteLater();
    m_activeRequests.remove(reply);
    
    if (reply->error() == QNetworkReply::NoError) {
        QJsonParseError parseError;
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll(), &parseError);
        
        if (parseError.error == QJsonParseError::NoError) {
            QJsonObject response = doc.object();
            
            // Extract results based on mode
            QVariantList results;
            
            if (response.contains("fused_results")) {
                QJsonArray fusedResults = response["fused_results"].toArray();
                for (const QJsonValue& result : fusedResults) {
                    results.append(result.toObject().toVariantMap());
                }
            } else {
                // Fallback to vector results
                QJsonArray vectorResults = response["vector_results"].toArray();
                for (const QJsonValue& result : vectorResults) {
                    results.append(result.toObject().toVariantMap());
                }
            }
            
            emit searchCompleted(results, originalQuery);
            qDebug() << "Search completed with" << results.size() << "results";
        } else {
            emit searchFailed("Invalid JSON response", originalQuery);
        }
    } else {
        emit searchFailed(reply->errorString(), originalQuery);
    }
}

void RetrievalClient::handleRAGResponse(QNetworkReply* reply, const QString& originalQuery)
{
    reply->deleteLater();
    m_activeRequests.remove(reply);
    
    if (reply->error() == QNetworkReply::NoError) {
        QJsonParseError parseError;
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll(), &parseError);
        
        if (parseError.error == QJsonParseError::NoError) {
            QJsonObject response = doc.object();
            
            QString aiResponse = response["response"].toString();
            
            // Extract sources
            QVariantList sources;
            if (response.contains("generation")) {
                QJsonObject generation = response["generation"].toObject();
                QJsonArray sourcesArray = generation["sources"].toArray();
                
                for (const QJsonValue& source : sourcesArray) {
                    sources.append(source.toString());
                }
            }
            
            emit ragResponseReceived(aiResponse, sources, originalQuery);
            qDebug() << "RAG response received for query:" << originalQuery;
        } else {
            emit ragFailed("Invalid JSON response", originalQuery);
        }
    } else {
        emit ragFailed(reply->errorString(), originalQuery);
    }
}

void RetrievalClient::handleConversationResponse(QNetworkReply* reply, const QString& pilotId)
{
    reply->deleteLater();
    
    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject response = doc.object();
        
        bool success = response["added"].toBool();
        emit conversationAdded(pilotId, success);
    } else {
        emit conversationAdded(pilotId, false);
    }
}

void RetrievalClient::handleStatisticsResponse(QNetworkReply* reply)
{
    reply->deleteLater();
    
    if (reply->error() == QNetworkReply::NoError) {
        QJsonParseError parseError;
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll(), &parseError);
        
        if (parseError.error == QJsonParseError::NoError) {
            m_statistics = doc.object().toVariantMap();
            emit statisticsChanged();
        }
    }
}

} // namespace services
} // namespace haasp