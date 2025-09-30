#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QDir>
#include <QDebug>

#include "nucleus/associative_nexus.hpp"
#include "nucleus/git_service.hpp"
#include "nucleus/quantum_conduit.hpp"
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
    haasp::ui::Controller controller;
    
    // Setup QML engine
    QQmlApplicationEngine engine;
    
    // Expose components to QML context
    engine.rootContext()->setContextProperty("gitService", &gitService);
    engine.rootContext()->setContextProperty("nexus", &nexus);
    engine.rootContext()->setContextProperty("controller", &controller);
    
    // Load simplified QML - VS Code development approach
    QString projectRoot = QDir::currentPath();
    while (!QDir(projectRoot).exists("src") && projectRoot != "/") {
        projectRoot = QDir(projectRoot).absoluteFilePath("..");
    }
    
    QString qmlPath = projectRoot + "/src/ui/qml/SimpleMain.qml";
    qDebug() << "🔍 Project root:" << projectRoot;
    qDebug() << "🔍 QML path:" << qmlPath;
    qDebug() << "🔍 QML exists:" << QFile::exists(qmlPath);
    
    QUrl qmlUrl = QUrl::fromLocalFile(qmlPath);
    engine.load(qmlUrl);
    
    if (engine.rootObjects().isEmpty()) {
        qDebug() << "❌ Failed to load QML from:" << qmlPath;
        return -1;
    }
    
    qDebug() << "✅ HAASP QML Interface Loaded Successfully!";
    return app.exec();
}
