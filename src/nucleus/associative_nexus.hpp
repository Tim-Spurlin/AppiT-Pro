#pragma once

#include <QObject>
#include <QVariantMap>
#include <QJsonObject>
#include <QTimer>
#include <memory>
#include <unordered_map>
#include <vector>

namespace haasp {

/**
 * @brief The AssociativeNexus is the core intelligence of HAASP
 * 
 * Manages hypergraph relationships between QML components, performs
 * reinforcement learning optimization, and coordinates synthesis operations.
 * 
 * Performance optimizations:
 * - AVX-512 vectorization for Bayesian inference
 * - Memory-mapped hypergraph storage 
 * - QtConcurrent for parallel graph operations
 */
class AssociativeNexus : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool learning READ isLearning NOTIFY learningChanged)
    Q_PROPERTY(double confidence READ confidence NOTIFY confidenceChanged)
    Q_PROPERTY(int epoch READ epoch NOTIFY epochChanged)

public:
    explicit AssociativeNexus(QObject *parent = nullptr);
    ~AssociativeNexus() override;

    // Core synthesis operations
    Q_INVOKABLE QVariantMap synthesizeComponent(const QString& type, const QJsonObject& constraints);
    Q_INVOKABLE bool validateConstraints(const QJsonObject& component, const QJsonObject& schema);
    Q_INVOKABLE QVariantList suggestImprovements(const QString& componentId);
    
    // Learning interface
    Q_INVOKABLE void startLearning();
    Q_INVOKABLE void stopLearning();
    Q_INVOKABLE void recordFeedback(const QString& componentId, double reward);
    
    // State queries
    bool isLearning() const { return m_learning; }
    double confidence() const { return m_confidence; }
    int epoch() const { return m_epoch; }

public slots:
    void onRepositoryChanged(const QString& repoPath);
    void onComponentEdited(const QString& componentId, const QVariantMap& changes);
    void performOptimization();

signals:
    void synthesisRequested(const QVariantMap& request);
    void componentSynthesized(const QString& componentId, const QVariantMap& data);
    void learningChanged();
    void confidenceChanged();
    void epochChanged();
    void optimizationComplete(double improvement);

private slots:
    void onLearningTimer();

private:
    // Hypergraph structure
    struct Node {
        QString id;
        QString type;
        QVariantMap properties;
        std::vector<QString> edges;
        double activation = 0.0;
    };
    
    struct Edge {
        QString source;
        QString target;
        double weight = 1.0;
        QString relationship;
    };
    
    // Core data structures
    std::unordered_map<QString, Node> m_nodes;
    std::vector<Edge> m_edges;
    
    // Learning state
    bool m_learning = false;
    double m_confidence = 0.0;
    int m_epoch = 0;
    QTimer* m_learningTimer;
    
    // Performance optimization structures
    struct OptimizationCache {
        QVariantMap lastSynthesis;
        double lastReward = 0.0;
        std::vector<double> rewardHistory;
    };
    std::unordered_map<QString, OptimizationCache> m_cache;
    
    // Private methods
    void initializeHypergraph();
    void updateNodeActivation(const QString& nodeId);
    double calculateBayesianInference(const Node& node);
    void optimizeWeightsWithRL();
    QVariantMap generateQMLCode(const QString& type, const QJsonObject& constraints);
    
    // AVX-512 optimized functions
    void vectorizedGraphTraversal();
    void parallelConstraintSolving(const QJsonObject& constraints);
};

} // namespace haasp