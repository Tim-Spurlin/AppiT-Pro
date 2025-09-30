#pragma once

#include <QObject>
#include <QString>
#include <QVariantMap>
#include <QVariantList>
#include <QDateTime>
#include <QTimer>

#include <git2.h>
#include <memory>

namespace haasp {

/**
 * @brief GitService provides libgit2-based Git operations and analytics
 * 
 * Integrates repository management with HAASP's synthesis pipeline,
 * providing code intelligence, change impact analysis, and automated
 * quality assessment.
 * 
 * Security features:
 * - GPG/SSH verification enforced
 * - Secure token storage via KWallet/libsecret
 * - AppArmor process isolation
 * - Pre-commit secret scanning
 */
class GitService : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString currentRepo READ currentRepo NOTIFY currentRepoChanged)
    Q_PROPERTY(QString currentBranch READ currentBranch NOTIFY currentBranchChanged) 
    Q_PROPERTY(bool hasChanges READ hasChanges NOTIFY statusChanged)
    Q_PROPERTY(int ahead READ ahead NOTIFY statusChanged)
    Q_PROPERTY(int behind READ behind NOTIFY statusChanged)
    Q_PROPERTY(QVariantList recentCommits READ recentCommits NOTIFY commitsChanged)
    Q_PROPERTY(QStringList modifiedFiles READ modifiedFiles NOTIFY statusChanged)

public:
    explicit GitService(QObject *parent = nullptr);
    ~GitService() override;

    // Repository management
    Q_INVOKABLE bool openRepository(const QString& path);
    Q_INVOKABLE bool initRepository(const QString& path);
    Q_INVOKABLE bool cloneRepository(const QString& url, const QString& path, const QString& token = "");
    Q_INVOKABLE void closeRepository();
    
    // Git operations  
    Q_INVOKABLE QVariantMap getStatus();
    Q_INVOKABLE QVariantList getCommitHistory(int limit = 50);
    Q_INVOKABLE bool stageFile(const QString& filePath);
    Q_INVOKABLE bool unstageFile(const QString& filePath);
    Q_INVOKABLE bool commitChanges(const QString& message, const QString& author = "");
    Q_INVOKABLE bool push(const QString& remote = "origin", const QString& branch = "");
    Q_INVOKABLE bool pull(const QString& remote = "origin", const QString& branch = "");
    
    // Branch operations
    Q_INVOKABLE QVariantList getBranches();
    Q_INVOKABLE bool createBranch(const QString& name, const QString& startPoint = "");
    Q_INVOKABLE bool checkoutBranch(const QString& name);
    Q_INVOKABLE bool mergeBranch(const QString& branch);
    Q_INVOKABLE bool deleteBranch(const QString& branch);
    
    // Analytics and intelligence
    Q_INVOKABLE QVariantMap getCodeMetrics();
    Q_INVOKABLE QVariantMap getChangeImpact(const QString& filePath);
    Q_INVOKABLE double predictQualityScore(const QString& filePath);
    Q_INVOKABLE QVariantList getOwnershipData();
    Q_INVOKABLE QVariantMap getCouplingMatrix();
    Q_INVOKABLE QVariantList identifyRiskyFiles();
    
    // GitHub integration (optional)
    Q_INVOKABLE void configureGitHub(const QString& token, const QString& username);
    Q_INVOKABLE QVariantList getPullRequests();
    Q_INVOKABLE QVariantMap createPullRequest(const QString& title, const QString& body, const QString& branch);
    
    // Properties
    QString currentRepo() const { return m_currentRepo; }
    QString currentBranch() const { return m_currentBranch; }
    bool hasChanges() const { return m_hasChanges; }
    int ahead() const { return m_ahead; }
    int behind() const { return m_behind; }
    QVariantList recentCommits() const { return m_recentCommits; }
    QStringList modifiedFiles() const { return m_modifiedFiles; }

public slots:
    void refresh();
    void startMonitoring();
    void stopMonitoring();

signals:
    void repositoryChanged(const QString& path);
    void currentRepoChanged();
    void currentBranchChanged();
    void statusChanged();
    void commitsChanged();
    void operationCompleted(const QString& operation, bool success, const QString& message);
    void analyticsReady(const QVariantMap& analytics);

private slots:
    void checkForChanges();

private:
    git_repository* m_repo = nullptr;
    QString m_currentRepo;
    QString m_currentBranch;
    bool m_hasChanges = false;
    int m_ahead = 0;
    int m_behind = 0; 
    QVariantList m_recentCommits;
    QStringList m_modifiedFiles;
    QTimer* m_monitorTimer;
    
    // GitHub integration
    QString m_githubToken;
    QString m_githubUsername;
    bool m_githubEnabled = false;
    
    // Analytics cache
    struct AnalyticsCache {
        QVariantMap metrics;
        QVariantMap ownershipData;
        QVariantMap couplingMatrix;
        QDateTime lastUpdated;
    } m_cache;
    
    // Private methods
    void initLibGit2();
    void cleanupLibGit2();
    bool authenticateRemote(git_remote* remote);
    QVariantMap convertCommit(const git_commit* commit);
    void updateBranchInfo();
    void updateRecentCommits();
    void computeAnalytics();
    
    // Secret management
    QString getSecureToken(const QString& service, const QString& key);
    bool setSecureToken(const QString& service, const QString& key, const QString& value);
    
    // Security checks
    bool validateCommitSignature(const git_commit* commit);
    bool scanForSecrets(const QString& content);
    void installPreCommitHooks();
};

} // namespace haasp