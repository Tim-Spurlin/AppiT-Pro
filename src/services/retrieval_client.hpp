#pragma once

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonArray>
#include <QVariantMap>
#include <QVariantList>
#include <QTimer>
#include <QUrl>
#include <memory>

namespace haasp {
namespace services {

/**
 * @brief Client for HAASP Hybrid Retrieval Service
 * 
 * Provides C++/QML interface to the Python-based retrieval service
 * Features:
 * - Async HTTP communication with the retrieval API
 * - Semantic, fuzzy, and graph search capabilities
 * - RAG (Retrieval-Augmented Generation) queries
 * - Conversation memory management
 * - Real-time status monitoring
 */
class RetrievalClient : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)
    Q_PROPERTY(QString serviceUrl READ serviceUrl WRITE setServiceUrl NOTIFY serviceUrlChanged)
    Q_PROPERTY(QVariantMap statistics READ statistics NOTIFY statisticsChanged)

public:
    explicit RetrievalClient(QObject *parent = nullptr);
    ~RetrievalClient() override;

    // Connection management
    bool isConnected() const { return m_connected; }
    QString serviceUrl() const { return m_serviceUrl; }
    void setServiceUrl(const QString& url);

    // Statistics
    QVariantMap statistics() const { return m_statistics; }

    // QML-accessible methods
    Q_INVOKABLE void connectToService();
    Q_INVOKABLE void disconnectFromService();
    
    Q_INVOKABLE void addDocument(const QString& docId, const QString& content, 
                                const QString& filePath = "", const QString& language = "",
                                const QVariantMap& metadata = QVariantMap());
    
    Q_INVOKABLE void performSearch(const QString& query, int k = 10, 
                                  const QString& mode = "all", const QString& pilotId = "");
    
    Q_INVOKABLE void performRAGQuery(const QString& query, int k = 10,
                                    const QString& taskType = "general", const QString& pilotId = "");
    
    Q_INVOKABLE void addConversation(const QString& pilotId, const QString& utterance, 
                                    const QString& speaker = "user");
    
    Q_INVOKABLE void getConversationHistory(const QString& pilotId, int limit = 20);
    
    Q_INVOKABLE void triggerReindex(bool force = false);
    Q_INVOKABLE void refreshStatistics();

public slots:
    void onNetworkReplyFinished();
    void onStatisticsTimer();

signals:
    void connectedChanged();
    void serviceUrlChanged();
    void statisticsChanged();
    
    // Search results
    void searchCompleted(const QVariantList& results, const QString& query);
    void searchFailed(const QString& error, const QString& query);
    
    // RAG results
    void ragResponseReceived(const QString& response, const QVariantList& sources, const QString& query);
    void ragFailed(const QString& error, const QString& query);
    
    // Conversation
    void conversationAdded(const QString& pilotId, bool success);
    void conversationHistoryReceived(const QString& pilotId, const QVariantList& messages);
    
    // System events
    void documentAdded(const QString& docId, bool success);
    void reindexStarted();
    void reindexCompleted();
    void serviceStatusChanged(const QString& status);

private slots:
    void handleSearchResponse(QNetworkReply* reply, const QString& originalQuery);
    void handleRAGResponse(QNetworkReply* reply, const QString& originalQuery);
    void handleConversationResponse(QNetworkReply* reply, const QString& pilotId);
    void handleStatisticsResponse(QNetworkReply* reply);

private:
    // HTTP client
    std::unique_ptr<QNetworkAccessManager> m_networkManager;
    
    // Connection state
    bool m_connected = false;
    QString m_serviceUrl = "http://127.0.0.1:8000";
    QVariantMap m_statistics;
    
    // Active requests tracking
    QHash<QNetworkReply*, QString> m_activeRequests;
    
    // Statistics timer
    QTimer* m_statisticsTimer;
    
    // Helper methods
    QNetworkReply* sendPostRequest(const QString& endpoint, const QJsonObject& data);
    QNetworkReply* sendGetRequest(const QString& endpoint);
    void processResponse(QNetworkReply* reply, std::function<void(const QJsonObject&)> handler);
    void emitError(const QString& operation, const QString& error);
};

} // namespace services
} // namespace haasp