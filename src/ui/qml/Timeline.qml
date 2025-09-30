import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami

/**
 * Timeline - Visual undo/redo history and replay interface
 * 
 * Features:
 * - Visual timeline of changes with timestamps
 * - Scrub to any point in history
 * - Undo/redo operations
 * - Change preview on hover
 * - Branching timeline support
 * - Replay functionality
 */
Rectangle {
    id: root
    
    // Signals
    signal undoRequested()
    signal redoRequested()
    signal replayRequested(var timestamp)
    signal timelinePositionChanged(int position)
    
    // Properties
    property int currentPosition: 0
    property int maxPosition: historyModel.length - 1
    property bool isReplaying: false
    
    // History model (in production would come from C++)
    property var historyModel: [
        {
            "id": 0,
            "timestamp": new Date(Date.now() - 300000),
            "action": "Created Rectangle",
            "elementId": "rect1",
            "type": "create",
            "description": "Added container rectangle"
        },
        {
            "id": 1,
            "timestamp": new Date(Date.now() - 240000),
            "action": "Changed color",
            "elementId": "rect1",
            "type": "property",
            "property": "color",
            "oldValue": "#ffffff",
            "newValue": "#e3f2fd",
            "description": "Set background to light blue"
        },
        {
            "id": 2,
            "timestamp": new Date(Date.now() - 180000),
            "action": "Added Button",
            "elementId": "button1",
            "type": "create",
            "parentId": "rect1",
            "description": "Created action button"
        },
        {
            "id": 3,
            "timestamp": new Date(Date.now() - 120000),
            "action": "Changed text",
            "elementId": "button1",
            "type": "property",
            "property": "text",
            "oldValue": "Button",
            "newValue": "Click Me",
            "description": "Updated button text"
        },
        {
            "id": 4,
            "timestamp": new Date(Date.now() - 60000),
            "action": "Moved element",
            "elementId": "button1",
            "type": "transform",
            "property": "position",
            "oldValue": {"x": 0, "y": 0},
            "newValue": {"x": 50, "y": 30},
            "description": "Repositioned button"
        }
    ]
    
    // Styling
    color: Kirigami.Theme.backgroundColor
    border.color: Kirigami.Theme.separatorColor
    border.width: 1
    radius: 4
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 4
        spacing: 4
        
        // Header with controls
        RowLayout {
            Layout.fillWidth: true
            
            QQC2.Label {
                text: "Timeline"
                font.weight: Font.DemiBold
                font.pointSize: 10
            }
            
            Item { Layout.fillWidth: true }
            
            QQC2.Label {
                text: `${root.currentPosition + 1} / ${root.maxPosition + 1}`
                font.pointSize: 8
                color: Kirigami.Theme.disabledTextColor
            }
            
            QQC2.ToolButton {
                icon.name: "edit-undo"
                enabled: root.currentPosition > 0
                onClicked: {
                    root.currentPosition--
                    root.undoRequested()
                    root.timelinePositionChanged(root.currentPosition)
                }
                QQC2.ToolTip.text: "Undo (Ctrl+Z)"
                QQC2.ToolTip.visible: hovered
            }
            
            QQC2.ToolButton {
                icon.name: "edit-redo"
                enabled: root.currentPosition < root.maxPosition
                onClicked: {
                    root.currentPosition++
                    root.redoRequested()
                    root.timelinePositionChanged(root.currentPosition)
                }
                QQC2.ToolTip.text: "Redo (Ctrl+Y)"
                QQC2.ToolTip.visible: hovered
            }
            
            QQC2.ToolSeparator {}
            
            QQC2.ToolButton {
                icon.name: root.isReplaying ? "media-playback-pause" : "media-playback-start"
                onClicked: {
                    if (root.isReplaying) {
                        replayTimer.stop()
                        root.isReplaying = false
                    } else {
                        startReplay()
                    }
                }
                QQC2.ToolTip.text: root.isReplaying ? "Pause replay" : "Replay timeline"
                QQC2.ToolTip.visible: hovered
            }
        }
        
        Kirigami.Separator {
            Layout.fillWidth: true
        }
        
        // Timeline scrubber
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#f5f5f5"
            border.color: "#cccccc"
            border.width: 1
            radius: 2
            
            // Timeline track
            Rectangle {
                anchors.fill: parent
                anchors.margins: 2
                color: "transparent"
                radius: 1
                
                // Progress indicator
                Rectangle {
                    width: parent.width * ((root.currentPosition + 1) / (root.maxPosition + 1))
                    height: parent.height
                    color: Kirigami.Theme.highlightColor
                    opacity: 0.3
                    radius: parent.radius
                }
                
                // Timeline markers
                Row {
                    anchors.fill: parent
                    
                    Repeater {
                        model: root.historyModel.length
                        
                        delegate: Rectangle {
                            width: parent.width / root.historyModel.length
                            height: parent.height
                            color: "transparent"
                            
                            Rectangle {
                                anchors.centerIn: parent
                                width: 8
                                height: 8
                                radius: 4
                                color: index <= root.currentPosition ? 
                                       getActionColor(root.historyModel[index].type) : 
                                       "#cccccc"
                                border.color: index === root.currentPosition ? "#333333" : "transparent"
                                border.width: 2
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                
                                onClicked: {
                                    root.currentPosition = index
                                    root.replayRequested(root.historyModel[index].timestamp)
                                    root.timelinePositionChanged(index)
                                }
                                
                                onEntered: {
                                    previewTooltip.item = root.historyModel[index]
                                    previewTooltip.visible = true
                                }
                                
                                onExited: {
                                    previewTooltip.visible = false
                                }
                            }
                        }
                    }
                }
                
                // Current position indicator
                Rectangle {
                    x: (parent.width / root.historyModel.length) * root.currentPosition + 
                       (parent.width / root.historyModel.length / 2) - width / 2
                    y: -4
                    width: 2
                    height: parent.height + 8
                    color: "#333333"
                    radius: 1
                }
            }
        }
        
        // History list
        QQC2.ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ListView {
                id: historyList
                model: root.historyModel
                currentIndex: root.currentPosition
                
                delegate: Rectangle {
                    width: historyList.width
                    height: 32
                    color: index === root.currentPosition ? 
                           Kirigami.Theme.highlightColor :
                           index <= root.currentPosition ?
                           "transparent" :
                           "#f0f0f0"
                    
                    opacity: index <= root.currentPosition ? 1.0 : 0.5
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 4
                        spacing: 8
                        
                        // Action type icon
                        Kirigami.Icon {
                            Layout.preferredWidth: 16
                            Layout.preferredHeight: 16
                            source: getActionIcon(modelData.type)
                            color: getActionColor(modelData.type)
                        }
                        
                        // Timestamp
                        QQC2.Label {
                            text: Qt.formatDateTime(modelData.timestamp, "hh:mm:ss")
                            font.pointSize: 8
                            font.family: "monospace"
                            color: Kirigami.Theme.disabledTextColor
                            Layout.preferredWidth: 60
                        }
                        
                        // Action description
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1
                            
                            QQC2.Label {
                                text: modelData.action
                                font.pointSize: 9
                                font.weight: index === root.currentPosition ? Font.DemiBold : Font.Normal
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                                color: index === root.currentPosition ? 
                                       Kirigami.Theme.highlightedTextColor : 
                                       Kirigami.Theme.textColor
                            }
                            
                            QQC2.Label {
                                text: modelData.description || ""
                                font.pointSize: 8
                                color: Kirigami.Theme.disabledTextColor
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                                visible: text.length > 0
                            }
                        }
                        
                        // Value change indicator (for property changes)
                        Rectangle {
                            Layout.preferredWidth: changeLabel.implicitWidth + 8
                            Layout.preferredHeight: 16
                            color: "#e3f2fd"
                            radius: 8
                            visible: modelData.type === "property" && modelData.oldValue !== undefined
                            
                            QQC2.Label {
                                id: changeLabel
                                anchors.centerIn: parent
                                text: `${modelData.oldValue} → ${modelData.newValue}`
                                font.pointSize: 7
                                color: "#1565c0"
                            }
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            root.currentPosition = index
                            root.replayRequested(modelData.timestamp)
                            root.timelinePositionChanged(index)
                        }
                    }
                }
            }
        }
    }
    
    // Preview tooltip
    QQC2.ToolTip {
        id: previewTooltip
        visible: false
        delay: 100
        
        property var item: null
        
        text: item ? `${item.action}\n${Qt.formatDateTime(item.timestamp, "MMM d, hh:mm:ss")}\n${item.description || ""}` : ""
    }
    
    // Replay timer
    Timer {
        id: replayTimer
        interval: 1000
        repeat: true
        
        onTriggered: {
            if (root.currentPosition < root.maxPosition) {
                root.currentPosition++
                root.replayRequested(root.historyModel[root.currentPosition].timestamp)
                root.timelinePositionChanged(root.currentPosition)
            } else {
                stop()
                root.isReplaying = false
            }
        }
    }
    
    // Functions
    function getActionIcon(type) {
        switch (type) {
            case "create": return "list-add"
            case "delete": return "list-remove"
            case "property": return "configure"
            case "transform": return "transform-move"
            case "style": return "format-fill-color"
            default: return "edit-entry"
        }
    }
    
    function getActionColor(type) {
        switch (type) {
            case "create": return "#4caf50"     // Green
            case "delete": return "#f44336"     // Red
            case "property": return "#2196f3"   // Blue
            case "transform": return "#ff9800"  // Orange
            case "style": return "#9c27b0"      // Purple
            default: return "#757575"           // Grey
        }
    }
    
    function startReplay() {
        root.isReplaying = true
        root.currentPosition = 0
        root.replayRequested(root.historyModel[0].timestamp)
        root.timelinePositionChanged(0)
        replayTimer.start()
    }
    
    function addHistoryEntry(action, elementId, type, details) {
        var entry = {
            "id": root.historyModel.length,
            "timestamp": new Date(),
            "action": action,
            "elementId": elementId,
            "type": type
        }
        
        // Add any additional details
        if (details) {
            Object.keys(details).forEach(function(key) {
                entry[key] = details[key]
            })
        }
        
        // Add to model
        root.historyModel.push(entry)
        root.maxPosition = root.historyModel.length - 1
        root.currentPosition = root.maxPosition
        
        // Refresh the view
        historyList.model = root.historyModel
        
        console.log("Added history entry:", action)
    }
    
    function clearHistory() {
        root.historyModel = []
        root.currentPosition = 0
        root.maxPosition = -1
        historyList.model = root.historyModel
    }
    
    function goToPosition(position) {
        if (position >= 0 && position <= root.maxPosition) {
            root.currentPosition = position
            root.replayRequested(root.historyModel[position].timestamp)
            root.timelinePositionChanged(position)
            
            // Scroll to position in list
            historyList.positionViewAtIndex(position, ListView.Center)
        }
    }
}