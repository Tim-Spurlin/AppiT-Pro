#!/bin/bash
set -e

echo "🚨 IMMEDIATE FIX - Terminal Stuck Issue"
echo "===================================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🛑 Step 1: Kill any running processes"
pkill -f haasp 2>/dev/null || true
pkill -f git_intelligence 2>/dev/null || true
pkill -f haasp-insights 2>/dev/null || true

echo "🔧 Step 2: Fix QML resource path issue"
# Update main.cpp to use absolute file path for testing
cat > src/main.cpp << 'EOF'
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickStyle>
#include <QDir>

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
    
    // Set Kirigami style
    QQuickStyle::setStyle("org.kde.kirigami2");
    
    // Initialize components
    haasp::AssociativeNexus nexus;
    haasp::GitService gitService; 
    haasp::QuantumConduit conduit;
    haasp::ui::Controller controller;
    
    // Wire connections
    QObject::connect(&nexus, &haasp::AssociativeNexus::synthesisRequested,
                     [&conduit](const QVariantMap& request) {
                         QString message = request.value("action").toString() + ": " + 
                                         request.value("path", request.value("message")).toString();
                         conduit.routeMessage(message);
                     });
    
    // Setup QML engine
    QQmlApplicationEngine engine;
    
    // Expose components to QML context
    engine.rootContext()->setContextProperty("gitService", &gitService);
    engine.rootContext()->setContextProperty("nexus", &nexus);
    engine.rootContext()->setContextProperty("controller", &controller);
    
    // Try to load QML file - first try resource, then file path
    QUrl qmlUrl("qrc:/qml/Main.qml");
    engine.load(qmlUrl);
    
    // If resource failed, try direct file path
    if (engine.rootObjects().isEmpty()) {
        qDebug() << "Resource failed, trying direct file path...";
        QString qmlPath = QDir::currentPath() + "/src/ui/qml/Main.qml";
        qmlUrl = QUrl::fromLocalFile(qmlPath);
        engine.load(qmlUrl);
        
        if (engine.rootObjects().isEmpty()) {
            qDebug() << "Direct file path also failed, trying working directory...";
            qmlPath = "src/ui/qml/Main.qml";
            qmlUrl = QUrl::fromLocalFile(qmlPath);
            engine.load(qmlUrl);
        }
    }
    
    if (engine.rootObjects().isEmpty()) {
        qDebug() << "❌ Failed to load QML interface";
        return -1;
    }
    
    qDebug() << "✅ QML interface loaded successfully";
    return app.exec();
}
EOF

echo "🔨 Step 3: Reconfigure and rebuild"
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)

echo "🚀 Step 4: Test QML application only (no Kafka)"
echo "   Starting QML application..."
./haasp

echo "✅ Fix applied - QML should now load!"