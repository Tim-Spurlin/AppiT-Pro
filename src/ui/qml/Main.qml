import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import org.kde.kirigami 2.19 as Kirigami

Kirigami.ApplicationWindow {

    id: root

    title: "HAASP - Hyper-Advanced Associative Application Synthesis Platform"
    visible: true
    width: 1600
    height: 1000
    minimumWidth: 1200
    minimumHeight: 800

    // Global theme
    Kirigami.Theme.colorSet: Kirigami.Theme.Window
    Kirigami.Theme.inherit: false
    
    // Performance optimizations
    property bool __asyncRendering: true
    
    // Modern dark theme
    color: "#1e1e1e"
    
    pageStack.initialPage: mainPage
    
    Kirigami.Page {
        id: mainPage
        title: "HAASP Development Environment"

        Component.onCompleted: {
            console.log("HAASP Application Started")
        }

        actions: [
            Kirigami.Action {
                icon.name: "document-new"
                text: "New Project"
                onTriggered: newProjectDialog.open()
            },
            Kirigami.Action {
                icon.name: "document-open"
                text: "Open Project"
                onTriggered: openProjectDialog.open()
            }
        ]

        ColumnLayout {
            anchors.fill: parent        

                icon.name: "folder-open"        // Header

                text: "Open Repository"        Rectangle {

                onTriggered: openRepoDialog.open()            Layout.fillWidth: true

            }            Layout.preferredHeight: 60

            right: Kirigami.Action {            color: "#2d2d2d"

                icon.name: "settings-configure"            

                text: "Settings"            Text {

                onTriggered: settingsPage.open()                anchors.centerIn: parent

            }                text: "HAASP - Development Platform"

        }                color: "white"

                font.pixelSize: 18

        RowLayout {                font.bold: true

            anchors.fill: parent            }

            spacing: 0        }

        

            // Git Portal (Left Sidebar)        // Main content area

            GitPortal {        Rectangle {

                id: gitPortal            Layout.fillWidth: true

                Layout.preferredWidth: 300            Layout.fillHeight: true

                Layout.fillHeight: true            color: "#1e1e1e"

                Layout.minimumWidth: 250            

            Text {

                onRepositoryOpened: {                anchors.centerIn: parent

                    previewSurface.loadProject(repoPath)                text: "🎉 HAASP Application Started Successfully!\n\nThis is the QML interface.\nIt's working!"

                    controller.onRepositoryOpened()                color: "white"

                }                font.pixelSize: 16

            }                horizontalAlignment: Text.AlignHCenter

            }

            // Preview Surface (Center)        }

            PreviewSurface {        

                id: previewSurface        // Status bar

                Layout.fillWidth: true        Rectangle {

                Layout.fillHeight: true            Layout.fillWidth: true

            Layout.preferredHeight: 30

                onElementSelected: {            color: "#2d2d2d"

                    inspector.loadElement(elementId)            

                    hierarchy.selectElement(elementId)            Text {

                }                anchors.left: parent.left

                anchors.leftMargin: 10

                onCodeGenerated: {                anchors.verticalCenter: parent.verticalCenter

                    codeEditor.text = code                text: "Status: Ready"

                }                color: "#00ff00"

            }                font.pixelSize: 12

            }

            // Inspector & AI Panel (Right Sidebar)        }

            ColumnLayout {    }

                Layout.preferredWidth: 350        

                Layout.fillHeight: true        RowLayout {

                Layout.minimumWidth: 300            anchors.fill: parent

                spacing: 0            spacing: 1

            

                // Component Hierarchy            // Left sidebar - Git Portal & Hierarchy

                Hierarchy {            Kirigami.Card {

                    id: hierarchy                Layout.fillHeight: true

                    Layout.fillWidth: true                Layout.preferredWidth: 320

                    Layout.preferredHeight: 200                Layout.minimumWidth: 250

                

                    onElementSelected: {                ColumnLayout {

                        previewSurface.selectElement(elementId)                    anchors.fill: parent

                        inspector.loadElement(elementId)                    anchors.margins: Kirigami.Units.smallSpacing

                    }                    spacing: Kirigami.Units.smallSpacing

                }                    

                    // Git status header

                Kirigami.Separator { Layout.fillWidth: true }                    Kirigami.Heading {

                        text: "Repository"

                // Properties Inspector                        level: 3

                Inspector {                    }

                    id: inspector                    

                    Layout.fillWidth: true                    GitPortal {

                    Layout.preferredHeight: 300                        id: gitPortal

                        Layout.fillWidth: true

                    onPropertyChanged: {                        Layout.preferredHeight: 200

                        previewSurface.updateProperty(elementId, property, value)                    }

                    }                    

                }                    Kirigami.Separator {

                        Layout.fillWidth: true

                Kirigami.Separator { Layout.fillWidth: true }                    }

                    

                // AI Code Generation Panel                    // Component hierarchy

                AiCodePanel {                    Kirigami.Heading {

                    id: aiCodePanel                        text: "Components"

                    Layout.fillWidth: true                        level: 3

                    Layout.fillHeight: true                    }

                    

                    onGenerateCode: {                    Hierarchy {

                        controller.generateCode(prompt, language)                        id: hierarchy

                    }                        Layout.fillWidth: true

                        Layout.fillHeight: true

                    onAnalyzeCode: {                        

                        controller.analyzeCurrentCode()                        onElementSelected: {

                    }                            previewSurface.selectElement(elementId)

                }                            inspector.loadElement(elementId)

            }                        }

        }                    }

    }                }

            }

    // Code Editor Dialog            

    Kirigami.OverlaySheet {            // Center - Live Preview Surface

        id: codeEditorDialog            Kirigami.Card {

        title: "Generated Code"                Layout.fillWidth: true

                Layout.fillHeight: true

        QQC2.TextArea {                

            id: codeEditor                PreviewSurface {

            Layout.fillWidth: true                    id: previewSurface

            Layout.preferredHeight: 400                    anchors.fill: parent

            text: "// Generated code will appear here"                    anchors.margins: Kirigami.Units.smallSpacing

            font.family: "Monospace"                    

            wrapMode: TextEdit.Wrap                    // Async loading optimization

        }                    asynchronous: true

                    

        footer: RowLayout {                    onElementClicked: {

            QQC2.Button {                        hierarchy.selectElement(elementId)

                text: "Apply to Project"                        inspector.loadElement(elementId) 

                onClicked: {                    }

                    previewSurface.applyGeneratedCode(codeEditor.text)                    

                    codeEditorDialog.close()                    onSynthesisRequested: {

                }                        AssociativeNexus.synthesizeComponent(componentType, constraints)

            }                    }

            QQC2.Button {                }

                text: "Copy"            }

                onClicked: codeEditor.selectAll()            

            }            // Right sidebar - Inspector & Timeline  

            QQC2.Button {            Kirigami.Card {

                text: "Close"                Layout.fillHeight: true

                onClicked: codeEditorDialog.close()                Layout.preferredWidth: 320

            }                Layout.minimumWidth: 250

        }                

    }                ColumnLayout {

                    anchors.fill: parent

    // Dialogs                    anchors.margins: Kirigami.Units.smallSpacing

    NewProjectDialog {                    spacing: Kirigami.Units.smallSpacing

        id: newProjectDialog                    

    }                    // Properties inspector

                    Kirigami.Heading {

    OpenRepoDialog {                        text: "Inspector"

        id: openRepoDialog                        level: 3

    }                    }

                    

    SettingsPage {                    Inspector {

        id: settingsPage                        id: inspector

    }                        Layout.fillWidth: true

                        Layout.fillHeight: true

    // Connections                        

    Connections {                        onPropertyChanged: {

        target: controller                            previewSurface.updateProperty(elementId, property, value)

        onCodeGenerated: {                            AssociativeNexus.recordFeedback(elementId, 0.8) // Positive feedback

            codeEditor.text = code                        }

            codeEditorDialog.open()                    }

        }                    

        onAiError: {                    Kirigami.Separator {

            showPassiveNotification("AI Error: " + error)                        Layout.fillWidth: true

        }                    }

    }                    

                    // Timeline for undo/redo

    Connections {                    Kirigami.Heading {

        target: gitService                        text: "Timeline"

        onRepositoryOpened: controller.onRepositoryOpened()                        level: 3

        onRepositoryClosed: controller.onRepositoryClosed()                    }

    }                    

}                    Timeline {
                        id: timeline
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        
                        onUndoRequested: previewSurface.undo()
                        onRedoRequested: previewSurface.redo()
                        onReplayRequested: previewSurface.replayTo(timestamp)
                    }
                }
            }
        }
    }
    
    // Status bar with Git info and learning state
    footer: QQC2.ToolBar {
        height: 32
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 4
            
            // Git status indicator
            Rectangle {
                width: 12
                height: 12
                radius: 6
                color: GitService.hasChanges ? "#ff6b6b" : "#4ecdc4"
            }
            
            QQC2.Label {
                text: GitService.currentRepo ? 
                      `${GitService.currentBranch} • ${GitService.ahead}↑ ${GitService.behind}↓` :
                      "No repository"
                font.pointSize: 9
            }
            
            Item { Layout.fillWidth: true }
            
            // ML learning indicator  
            QQC2.Label {
                text: AssociativeNexus.learning ? 
                      `Learning • Epoch ${AssociativeNexus.epoch} • Confidence ${(AssociativeNexus.confidence * 100).toFixed(1)}%` :
                      "Ready"
                font.pointSize: 9
                color: AssociativeNexus.learning ? "#ffd93d" : "#95e1d3"
            }
            
            QQC2.ProgressBar {
                visible: AssociativeNexus.learning
                value: AssociativeNexus.confidence
                Layout.preferredWidth: 100
                Layout.preferredHeight: 8
            }
        }
    }
    
    // Dialogs
    NewProjectDialog {
        id: newProjectDialog
        onProjectCreated: {
            GitService.initRepository(projectPath)
            previewSurface.loadProject(projectPath)
        }
    }
    
    OpenRepoDialog {
        id: openRepoDialog
        onRepositorySelected: {
            GitService.openRepository(repoPath)
            previewSurface.loadProject(repoPath)
        }
    }
    
    SettingsPage {
        id: settingsPage
    }
    
    // Global keyboard shortcuts
    QQC2.Shortcut {
        sequence: "Ctrl+S"
        onActivated: GitService.commitChanges("Auto-save via HAASP", "HAASP <haasp@local>")
    }
    
    QQC2.Shortcut {
        sequence: "Ctrl+Z"
        onActivated: timeline.undo()
    }
    
    QQC2.Shortcut {
        sequence: "Ctrl+Y"
        onActivated: timeline.redo()
    }
}