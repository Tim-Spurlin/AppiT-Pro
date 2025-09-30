import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami
import org.haasp.core 1.0

/**
 * GitPortal - VS Code integration bridge for Git operations
 * 
 * Provides real-time Git status, branch management, and commit history.
 * Integrates with GitService for repository operations and analytics.
 */
Rectangle {
    id: root
    
    color: Kirigami.Theme.backgroundColor
    border.color: Kirigami.Theme.separatorColor
    border.width: 1
    radius: 4
    
    // Properties
    property alias currentBranch: GitService.currentBranch
    property alias hasChanges: GitService.hasChanges
    property bool expanded: true
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Kirigami.Units.smallSpacing
        spacing: Kirigami.Units.smallSpacing
        
        // Header with repo name and status
        RowLayout {
            Layout.fillWidth: true
            
            Kirigami.Icon {
                source: "vcs-normal"
                width: 16
                height: 16
            }
            
            QQC2.Label {
                text: GitService.currentRepo ? 
                      GitService.currentRepo.split('/').pop() : 
                      "No repository"
                font.weight: Font.DemiBold
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            
            // Expand/collapse button
            QQC2.ToolButton {
                icon.name: root.expanded ? "arrow-up" : "arrow-down"
                icon.width: 12
                icon.height: 12
                onClicked: root.expanded = !root.expanded
            }
        }
        
        // Repository details (collapsible)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.expanded
            spacing: Kirigami.Units.smallSpacing
            
            // Branch and sync status
            RowLayout {
                Layout.fillWidth: true
                
                Kirigami.Icon {
                    source: "vcs-branch"
                    width: 14
                    height: 14
                }
                
                QQC2.Label {
                    text: GitService.currentBranch || "main"
                    font.pointSize: 9
                    Layout.fillWidth: true
                }
                
                // Ahead/behind indicators
                Row {
                    spacing: 4
                    visible: GitService.ahead > 0 || GitService.behind > 0
                    
                    QQC2.Label {
                        text: GitService.ahead
                        font.pointSize: 8
                        color: "#4ecdc4"
                        visible: GitService.ahead > 0
                    }
                    
                    Kirigami.Icon {
                        source: "arrow-up"
                        width: 10
                        height: 10
                        color: "#4ecdc4"
                        visible: GitService.ahead > 0
                    }
                    
                    QQC2.Label {
                        text: GitService.behind
                        font.pointSize: 8 
                        color: "#ff6b6b"
                        visible: GitService.behind > 0
                    }
                    
                    Kirigami.Icon {
                        source: "arrow-down" 
                        width: 10
                        height: 10
                        color: "#ff6b6b"
                        visible: GitService.behind > 0
                    }
                }
            }
            
            // Changes summary
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: changesColumn.height + 8
                color: GitService.hasChanges ? "#ff6b6b22" : "#4ecdc422"
                border.color: GitService.hasChanges ? "#ff6b6b" : "#4ecdc4"
                border.width: 1
                radius: 3
                visible: GitService.currentRepo
                
                ColumnLayout {
                    id: changesColumn
                    anchors.fill: parent
                    anchors.margins: 4
                    spacing: 2
                    
                    QQC2.Label {
                        text: GitService.hasChanges ? "Uncommitted changes" : "Working tree clean"
                        font.pointSize: 8
                        font.weight: Font.DemiBold
                        color: GitService.hasChanges ? "#ff6b6b" : "#4ecdc4"
                    }
                    
                    // File changes (simplified view)
                    Repeater {
                        model: GitService.hasChanges ? ["src/main.qml", "components/Button.qml"] : []
                        delegate: RowLayout {
                            Layout.fillWidth: true
                            
                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: "#ffd93d"
                            }
                            
                            QQC2.Label {
                                text: modelData
                                font.pointSize: 7
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                    }
                }
            }
            
            // Action buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 4
                
                QQC2.Button {
                    text: "Commit"
                    enabled: GitService.hasChanges
                    font.pointSize: 9
                    Layout.fillWidth: true
                    
                    onClicked: {
                        commitDialog.open()
                    }
                }
                
                QQC2.Button {
                    text: "Push"
                    enabled: GitService.ahead > 0
                    font.pointSize: 9
                    Layout.fillWidth: true
                    
                    onClicked: {
                        GitService.push()
                    }
                }
                
                QQC2.Button {
                    text: "Pull"
                    enabled: GitService.behind > 0
                    font.pointSize: 9
                    Layout.fillWidth: true
                    
                    onClicked: {
                        GitService.pull()
                    }
                }
            }
            
            // Recent commits
            QQC2.Label {
                text: "Recent Commits"
                font.weight: Font.DemiBold
                font.pointSize: 9
            }
            
            QQC2.ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 80
                
                ListView {
                    model: GitService.recentCommits
                    
                    delegate: ItemDelegate {
                        width: parent.width
                        height: 32
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 4
                            spacing: 6
                            
                            Rectangle {
                                width: 6
                                height: 6
                                radius: 3
                                color: "#95e1d3"
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 1
                                
                                QQC2.Label {
                                    text: modelData.message || "No message"
                                    font.pointSize: 8
                                    font.weight: Font.DemiBold
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                                
                                QQC2.Label {
                                    text: `${modelData.author} • ${modelData.time}`
                                    font.pointSize: 7
                                    color: Kirigami.Theme.disabledTextColor
                                    Layout.fillWidth: true
                                }
                            }
                        }
                        
                        onClicked: {
                            // Show commit details
                            commitDetailsDialog.commitId = modelData.id
                            commitDetailsDialog.open()
                        }
                    }
                }
            }
            
            // Insights++ launcher button
            QQC2.Button {
                text: "Open Git Insights"
                icon.name: "view-statistics"
                Layout.fillWidth: true
                
                onClicked: {
                    // Launch local Rust WebApp at https://127.0.0.1:7420
                    Qt.openUrlExternally("https://127.0.0.1:7420/repo/overview")
                }
            }
        }
    }
    
    // Commit dialog
    Kirigami.PromptDialog {
        id: commitDialog
        title: "Commit Changes"
        
        standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
        
        ColumnLayout {
            Kirigami.FormLayout {
                QQC2.TextField {
                    id: commitMessageField
                    Kirigami.FormData.label: "Message:"
                    placeholderText: "Enter commit message"
                }
                
                QQC2.TextField {
                    id: authorField  
                    Kirigami.FormData.label: "Author:"
                    text: "HAASP <haasp@local>"
                }
            }
        }
        
        onAccepted: {
            if (commitMessageField.text.length > 0) {
                GitService.commitChanges(
                    commitMessageField.text + "\n\nGenerated with Memex (https://memex.tech)\nCo-Authored-By: Memex <noreply@memex.tech>",
                    authorField.text
                )
                commitMessageField.clear()
            }
        }
    }
    
    // Commit details dialog
    Kirigami.Dialog {
        id: commitDetailsDialog
        title: "Commit Details"
        
        property string commitId: ""
        
        standardButtons: Kirigami.Dialog.Close
        
        QQC2.ScrollView {
            implicitWidth: 400
            implicitHeight: 300
            
            QQC2.Label {
                text: `Commit: ${commitDetailsDialog.commitId}\n\nDetails loading...`
                wrapMode: Text.Wrap
            }
        }
    }
    
    // Auto-refresh timer
    Timer {
        interval: 2000 // 2 seconds
        running: GitService.currentRepo
        repeat: true
        onTriggered: GitService.refresh()
    }
}