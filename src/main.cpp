#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QDir>
#include <QDebug>
#include <QFile>
#include <QUrl>

#include "nucleus/associative_nexus.hpp"
#include "nucleus/git_service.hpp"
#include "nucleus/quantum_conduit.hpp"
#include "nucleus/ai_oracle.hpp"
#include "nucleus/pilot_orchestrator.hpp"
#include "ui/controller.hpp"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setApplicationName("HAASP");
    app.setOrganizationName("Saphyre Solutions");
    app.setApplicationVersion("1.0.0");
    
    // Initialize components
    haasp::AssociativeNexus nexus;
    haasp::GitService gitService; 
    haasp::QuantumConduit conduit;
    haasp::AiOracle aiOracle;
    haasp::PilotOrchestrator pilotOrchestrator;
    haasp::ui::Controller controller;
    
    // Setup QML engine
    QQmlApplicationEngine engine;
    
    // Expose components to QML context
    engine.rootContext()->setContextProperty("gitService", &gitService);
    engine.rootContext()->setContextProperty("nexus", &nexus);
    engine.rootContext()->setContextProperty("controller", &controller);
    engine.rootContext()->setContextProperty("aiOracle", &aiOracle);
    engine.rootContext()->setContextProperty("pilotOrchestrator", &pilotOrchestrator);
    
    // Load QML interface with advanced/simple fallback
    QString projectRoot = QDir::currentPath();
    while (!QDir(projectRoot).exists("src") && projectRoot != "/") {
        projectRoot = QDir(projectRoot).absoluteFilePath("..");
    }
    
    // Try advanced interface first, fallback to simple
    QStringList qmlCandidates = {
        projectRoot + "/src/ui/qml/FullAdvancedMain.qml",
        projectRoot + "/src/ui/qml/AdvancedMain.qml", 
        projectRoot + "/src/ui/qml/SimpleMain.qml",
        projectRoot + "/src/ui/qml/Main.qml"
    };
    
    bool loaded = false;
    for (const QString& qmlPath : qmlCandidates) {
        qDebug() << "🔍 Trying QML:" << qmlPath;
        
        if (QFile::exists(qmlPath)) {
            QUrl qmlUrl = QUrl::fromLocalFile(qmlPath);
            engine.load(qmlUrl);
            
            if (!engine.rootObjects().isEmpty()) {
                qDebug() << "✅ Loaded QML interface:" << qmlPath;
                loaded = true;
                break;
            } else {
                qDebug() << "⚠️ Failed to load:" << qmlPath;
                engine.clearComponentCache();
            }
        }
    }
    
    if (!loaded) {
        qDebug() << "❌ Failed to load any QML interface";
        qDebug() << "   Project root:" << projectRoot;
        qDebug() << "   Candidates tried:" << qmlCandidates.join(", ");
        return -1;
    }
    
    qDebug() << "✅ HAASP QML Interface Loaded Successfully!";
    return app.exec();
}
