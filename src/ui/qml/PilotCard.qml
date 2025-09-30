import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/*
 * Pilot Card Component
 * Visual representation of AI pilots in the infinite canvas
 */

Rectangle {
    id: pilotCard
    
    // Properties
    property var pilotData
    property bool selected: false
    property bool dragging: false
    property bool connecting: false
    
    // Visual configuration
    width: 240
    height: Math.max(180, contentLayout.implicitHeight + 20)
    radius: 8
    border.width: selected ? 3 : 1
    border.color: selected ? "#00aaff" : "#555555"
    
    // Dynamic colors based on pilot type
    color: {
        switch(pilotData.pilotType) {
            case "sentinel": return "#2d4a2b"      // Dark green
            case "doc_architect": return "#2b3a4a" // Dark blue
            case "remediator": return "#4a2d2b"    // Dark red
            case "codewright": return "#4a3f2b"    // Dark orange
            default: return "#2d2d2d"              // Default dark
        }
    }
    
    // Signals
    signal clicked()
    signal doubleClicked()
    signal positionChanged(real newX, real newY)
    signal portClicked(string portName, string portType, bool isOutput)
    
    // Drop shadow effect
    Rectangle {
        anchors.fill: parent
        anchors.margins: -2
        radius: parent.radius + 2
        color: "#000000"
        opacity: 0.3
        z: -1
    }
    
    // Main content layout
    ColumnLayout {
        id: contentLayout
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8
        
        // Header with pilot info
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#1a1a1a"
            radius: 4
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                
                // Pilot icon
                Rectangle {
                    width: 24
                    height: 24
                    radius: 12
                    color: getPilotIconColor()
                    
                    Text {
                        anchors.centerIn: parent
                        text: getPilotIcon()
                        color: "white"
                        font.bold: true
                        font.pixelSize: 12
                    }
                }
                
                // Pilot name and type
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    
                    Text {
                        text: pilotData.displayName || "Unknown Pilot"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 14
                    }
                    
                    Text {
                        text: pilotData.pilotType || "unknown"
                        color: "#cccccc"
                        font.pixelSize: 10
                    }
                }
                
                // Status indicator
                Rectangle {
                    width: 12
                    height: 12
                    radius: 6
                    color: getPilotStatusColor()
                    
                    SequentialAnimation on opacity {
                        running: pilotData.status === "processing"
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.3; duration: 1000 }
                        NumberAnimation { to: 1.0; duration: 1000 }
                    }
                }
            }
        }
        
        // Input ports
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(30, inputPortsLayout.implicitHeight + 10)
            color: "#252525"
            radius: 4
            visible: pilotData.inputs && pilotData.inputs.length > 0
            
            ColumnLayout {
                id: inputPortsLayout
                anchors.fill: parent
                anchors.margins: 5
                spacing: 3
                
                Text {
                    text: "Inputs"
                    color: "#aaaaaa"
                    font.pixelSize: 10
                    font.bold: true
                }
                
                Flow {
                    Layout.fillWidth: true
                    spacing: 4
                    
                    Repeater {
                        model: pilotData.inputs || []
                        
                        delegate: PortIndicator {
                            portName: modelData.name
                            portType: modelData.type
                            connected: modelData.connected
                            isOutput: false
                            
                            onClicked: {
                                pilotCard.portClicked(portName, portType, false)
                            }
                        }
                    }
                }
            }
        }
        
        // Processing indicator (when active)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 30
            color: "#1a3a1a"
            radius: 4
            visible: pilotData.status === "processing"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                
                // Animated processing indicator
                Rectangle {
                    width: 16
                    height: 4
                    color: "#4CAF50"
                    radius: 2
                    
                    SequentialAnimation on x {
                        running: parent.parent.visible
                        loops: Animation.Infinite
                        NumberAnimation { to: parent.width - 20; duration: 1500 }
                        NumberAnimation { to: 0; duration: 1500 }
                    }
                }
                
                Text {
                    text: "Processing..."
                    color: "#4CAF50"
                    font.pixelSize: 10
                    Layout.fillWidth: true
                }
            }
        }
        
        // Output ports
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(30, outputPortsLayout.implicitHeight + 10)
            color: "#252525"
            radius: 4
            visible: pilotData.outputs && pilotData.outputs.length > 0
            
            ColumnLayout {
                id: outputPortsLayout
                anchors.fill: parent
                anchors.margins: 5
                spacing: 3
                
                Text {
                    text: "Outputs"
                    color: "#aaaaaa"
                    font.pixelSize: 10
                    font.bold: true
                }
                
                Flow {
                    Layout.fillWidth: true
                    spacing: 4
                    
                    Repeater {
                        model: pilotData.outputs || []
                        
                        delegate: PortIndicator {
                            portName: modelData.name
                            portType: modelData.type
                            connected: modelData.connected
                            isOutput: true
                            
                            onClicked: {
                                pilotCard.portClicked(portName, portType, true)
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Mouse area for selection and dragging
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        
        property point lastMousePos
        
        onPressed: (mouse) => {
            if (mouse.button === Qt.LeftButton) {
                lastMousePos = Qt.point(mouse.x, mouse.y)
                pilotCard.clicked()
            }
        }
        
        onDoubleClicked: {
            pilotCard.doubleClicked()
        }
        
        onPositionChanged: (mouse) => {
            if (pressed && mouse.button === Qt.LeftButton) {
                if (!dragging) {
                    dragging = true
                }
                
                // Calculate new position
                var deltaX = mouse.x - lastMousePos.x
                var deltaY = mouse.y - lastMousePos.y
                
                var newX = pilotCard.x + deltaX
                var newY = pilotCard.y + deltaY
                
                pilotCard.x = newX
                pilotCard.y = newY
                
                positionChanged(newX, newY)
            }
        }
        
        onReleased: {
            dragging = false
        }
    }
    
    // Context menu
    Menu {
        id: contextMenu
        
        MenuItem {
            text: "Edit Pilot"
            onTriggered: pilotCard.doubleClicked()
        }
        
        MenuItem {
            text: "View Memory"
            onTriggered: showPilotMemory()
        }
        
        MenuItem {
            text: "Run Pilot"
            onTriggered: runPilot()
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Delete"
            onTriggered: deletePilot()
        }
    }
    
    // Helper functions
    function getPilotIcon() {
        switch(pilotData.pilotType) {
            case "sentinel": return "👁"
            case "doc_architect": return "📋"
            case "remediator": return "🔧"
            case "codewright": return "⚡"
            default: return "🤖"
        }
    }
    
    function getPilotIconColor() {
        switch(pilotData.pilotType) {
            case "sentinel": return "#4CAF50"
            case "doc_architect": return "#2196F3"
            case "remediator": return "#FF5722"
            case "codewright": return "#FF9800"
            default: return "#666666"
        }
    }
    
    function getPilotStatusColor() {
        switch(pilotData.status) {
            case "active": return "#4CAF50"      // Green
            case "processing": return "#FF9800"  // Orange
            case "error": return "#F44336"       // Red
            case "idle": return "#9E9E9E"        // Gray
            default: return "#9E9E9E"
        }
    }
    
    function showPilotMemory() {
        // TODO: Implement pilot memory viewer
        console.log("Show memory for pilot:", pilotData.pilotId)
    }
    
    function runPilot() {
        // TODO: Implement pilot execution
        console.log("Run pilot:", pilotData.pilotId)
    }
    
    function deletePilot() {
        // TODO: Implement pilot deletion with confirmation
        console.log("Delete pilot:", pilotData.pilotId)
    }
}

// Port indicator component
Component {
    id: portIndicatorComponent
    
    Rectangle {
        id: portIndicator
        
        property string portName
        property string portType
        property bool connected: false
        property bool isOutput: false
    
    signal clicked()
    
    width: portText.implicitWidth + 16
    height: 20
    radius: 10
    
    color: connected ? getPortTypeColor() : "#444444"
    border.width: 1
    border.color: connected ? "#ffffff" : "#666666"
    
    Text {
        id: portText
        anchors.centerIn: parent
        text: portName
        color: "white"
        font.pixelSize: 9
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: parent.clicked()
        
        cursorShape: Qt.PointingHandCursor
    }
    
    function getPortTypeColor() {
        switch(portType) {
            case "text": return "#4CAF50"
            case "code": return "#2196F3"
            case "doc": return "#9C27B0"
            case "diagnostic": return "#FF9800"
            case "patch": return "#F44336"
            default: return "#666666"
        }
    }
    }
}

// Connection line component
Component {
    id: connectionLineComponent
    
    Item {
        id: connectionLine
        
        property var connectionData
        property var sourceNode
        property var targetNode
    
    Canvas {
        anchors.fill: parent
        
        onPaint: {
            if (!sourceNode || !targetNode) return
            
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            // Calculate connection points
            var startX = sourceNode.x + sourceNode.width
            var startY = sourceNode.y + sourceNode.height / 2
            var endX = targetNode.x
            var endY = targetNode.y + targetNode.height / 2
            
            // Draw curved connection
            ctx.strokeStyle = "#00aaff"
            ctx.lineWidth = 2
            ctx.globalAlpha = 0.8
            
            ctx.beginPath()
            ctx.moveTo(startX, startY)
            
            // Control points for smooth curve
            var controlX1 = startX + (endX - startX) * 0.5
            var controlY1 = startY
            var controlX2 = startX + (endX - startX) * 0.5  
            var controlY2 = endY
            
            ctx.bezierCurveTo(controlX1, controlY1, controlX2, controlY2, endX, endY)
            ctx.stroke()
            
            // Draw arrowhead
            var arrowSize = 8
            var angle = Math.atan2(endY - controlY2, endX - controlX2)
            
            ctx.fillStyle = "#00aaff"
            ctx.beginPath()
            ctx.moveTo(endX, endY)
            ctx.lineTo(
                endX - arrowSize * Math.cos(angle - Math.PI / 6),
                endY - arrowSize * Math.sin(angle - Math.PI / 6)
            )
            ctx.lineTo(
                endX - arrowSize * Math.cos(angle + Math.PI / 6),
                endY - arrowSize * Math.sin(angle + Math.PI / 6)
            )
            ctx.closePath()
            ctx.fill()
        }
    }
}

// Connection preview component (while dragging)
Item {
    id: connectionPreview
    
    property var startInfo: null
    property point mousePos: Qt.point(0, 0)
    
    function startConnection(pilotId, portName, portType, isOutput) {
        startInfo = {
            "pilotId": pilotId,
            "portName": portName,
            "portType": portType,
            "isOutput": isOutput
        }
        visible = true
    }
    
    function completeConnection(pilotId, portName, portType, isOutput) {
        if (!startInfo) return {"success": false}
        
        // Validate connection
        if (startInfo.pilotId === pilotId) {
            // Can't connect to self
            reset()
            return {"success": false, "error": "Cannot connect pilot to itself"}
        }
        
        if (startInfo.isOutput === isOutput) {
            // Can't connect output to output or input to input
            reset()
            return {"success": false, "error": "Invalid connection direction"}
        }
        
        var result = {
            "success": true,
            "from": startInfo.isOutput ? startInfo : {"pilotId": pilotId, "portName": portName, "portType": portType},
            "to": startInfo.isOutput ? {"pilotId": pilotId, "portName": portName, "portType": portType} : startInfo
        }
        
        reset()
        return result
    }
    
    function reset() {
        startInfo = null
        visible = false
    }
    
    Canvas {
        anchors.fill: parent
        visible: startInfo !== null
        
        onPaint: {
            if (!startInfo) return
            
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            // Draw preview line from start port to mouse
            ctx.strokeStyle = "#00aaff"
            ctx.lineWidth = 2
            ctx.globalAlpha = 0.6
            ctx.setLineDash([5, 5])
            
            ctx.beginPath()
            // TODO: Calculate actual port position
            ctx.moveTo(100, 100)  // Placeholder start position
            ctx.lineTo(mousePos.x, mousePos.y)
            ctx.stroke()
        }
    }
    
    MouseArea {
        anchors.fill: parent
        
        onPositionChanged: (mouse) => {
            mousePos = Qt.point(mouse.x, mouse.y)
        }
        
        onClicked: {
            // Cancel connection on empty click
            connectionPreview.reset()
        }
    }
    }
}