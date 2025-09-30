import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/*
 * Infinite Canvas for Pilot Orchestration
 * Features:
 * - Infinite pan/zoom with double precision
 * - Drag & drop pilot creation
 * - Connection system with typed ports
 * - Performance optimized rendering
 */

Item {
    id: infiniteCanvas
    
    // Canvas state
    property real zoomLevel: 1.0
    property point panOffset: Qt.point(0, 0)
    property bool isDragging: false
    property bool isConnecting: false
    
    // Pilot management
    property alias pilots: pilotsModel
    property alias connections: connectionsModel
    
    // Performance properties
    property bool asyncRendering: true
    property int maxVisibleNodes: 1000
    property real cullingMargin: 500
    
    signal pilotCreated(string pilotType, real x, real y)
    signal pilotDeleted(string pilotId)
    signal connectionCreated(string fromPilot, string fromPort, string toPilot, string toPort)
    signal selectionChanged(var selectedPilots)
    
    // Canvas container with transform
    Item {
        id: canvasContent
        
        transform: [
            Scale {
                xScale: infiniteCanvas.zoomLevel
                yScale: infiniteCanvas.zoomLevel
                origin.x: infiniteCanvas.width / 2
                origin.y: infiniteCanvas.height / 2
            },
            Translate {
                x: infiniteCanvas.panOffset.x
                y: infiniteCanvas.panOffset.y
            }
        ]
        
        // Grid background (performance optimized)
        GridBackground {
            id: gridBackground
            visible: zoomLevel > 0.3
            opacity: Math.min(1.0, zoomLevel)
            gridSize: 50
            gridColor: "#333333"
        }
        
        // Pilot nodes
        Repeater {
            id: pilotRepeater
            model: ListModel {
                id: pilotsModel
                
                // Example pilots
                Component.onCompleted: {
                    append({
                        "pilotId": "pilot_0_sentinel",
                        "pilotType": "sentinel",
                        "displayName": "Sentinel",
                        "x": 100,
                        "y": 100,
                        "selected": false,
                        "inputs": [
                            {"name": "context", "type": "text", "connected": false}
                        ],
                        "outputs": [
                            {"name": "validation", "type": "diagnostic", "connected": false}
                        ]
                    })
                    
                    append({
                        "pilotId": "pilot_1_doc_architect", 
                        "pilotType": "doc_architect",
                        "displayName": "Doc Architect",
                        "x": 400,
                        "y": 100,
                        "selected": false,
                        "inputs": [
                            {"name": "requirements", "type": "text", "connected": false},
                            {"name": "validation", "type": "diagnostic", "connected": false}
                        ],
                        "outputs": [
                            {"name": "documentation", "type": "doc", "connected": false}
                        ]
                    })
                }
            }
            
            delegate: PilotCard {
                pilotData: model
                
                // Position and scaling
                x: model.x
                y: model.y
                scale: Math.max(0.3, Math.min(2.0, infiniteCanvas.zoomLevel))
                visible: isInViewport()
                
                // Selection handling
                selected: model.selected
                onClicked: selectPilot(model.pilotId)
                onDoubleClicked: editPilot(model.pilotId)
                
                // Connection handling
                onPortClicked: (portName, portType, isOutput) => {
                    handlePortInteraction(model.pilotId, portName, portType, isOutput)
                }
                
                // Drag handling
                onPositionChanged: (newX, newY) => {
                    pilotsModel.setProperty(index, "x", newX)
                    pilotsModel.setProperty(index, "y", newY)
                    updateConnections()
                }
                
                function isInViewport() {
                    // Viewport culling for performance
                    var screenX = (model.x + infiniteCanvas.panOffset.x) * infiniteCanvas.zoomLevel
                    var screenY = (model.y + infiniteCanvas.panOffset.y) * infiniteCanvas.zoomLevel
                    
                    return screenX >= -cullingMargin && 
                           screenX <= infiniteCanvas.width + cullingMargin &&
                           screenY >= -cullingMargin && 
                           screenY <= infiniteCanvas.height + cullingMargin
                }
            }
        }
        
        // Connection lines
        Repeater {
            model: ListModel {
                id: connectionsModel
            }
            
            delegate: ConnectionLine {
                connectionData: model
                sourceNode: findPilotById(model.fromPilot)
                targetNode: findPilotById(model.toPilot)
                
                visible: sourceNode && targetNode && 
                        sourceNode.visible && targetNode.visible
            }
        }
        
        // Connection preview (while dragging)
        ConnectionPreview {
            id: connectionPreview
            visible: infiniteCanvas.isConnecting
        }
    }
    
    // Pan and zoom controls
    MouseArea {
        id: canvasMouseArea
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
        
        property point lastPanPoint
        
        onPressed: (mouse) => {
            if (mouse.button === Qt.MiddleButton || 
                (mouse.button === Qt.LeftButton && mouse.modifiers & Qt.AltModifier)) {
                // Start panning
                lastPanPoint = Qt.point(mouse.x, mouse.y)
                isDragging = true
            } else if (mouse.button === Qt.RightButton) {
                // Context menu
                showContextMenu(mouse.x, mouse.y)
            }
        }
        
        onPositionChanged: (mouse) => {
            if (isDragging) {
                // Update pan offset
                var deltaX = mouse.x - lastPanPoint.x
                var deltaY = mouse.y - lastPanPoint.y
                
                panOffset = Qt.point(
                    panOffset.x + deltaX,
                    panOffset.y + deltaY
                )
                
                lastPanPoint = Qt.point(mouse.x, mouse.y)
            }
        }
        
        onReleased: {
            isDragging = false
        }
        
        onWheel: (wheel) => {
            // Zoom centered on cursor
            var zoomFactor = wheel.angleDelta.y > 0 ? 1.2 : 0.8
            var newZoom = Math.max(0.1, Math.min(10.0, zoomLevel * zoomFactor))
            
            // Calculate zoom offset to center on cursor
            var cursorX = wheel.x
            var cursorY = wheel.y
            
            var oldPanX = panOffset.x
            var oldPanY = panOffset.y
            
            // Apply zoom
            zoomLevel = newZoom
            
            // Adjust pan to keep cursor position stable
            var zoomDelta = newZoom / (newZoom / zoomFactor)
            panOffset = Qt.point(
                oldPanX + (cursorX - infiniteCanvas.width / 2) * (1 - zoomDelta),
                oldPanY + (cursorY - infiniteCanvas.height / 2) * (1 - zoomDelta)
            )
        }
    }
    
    // Multi-touch gestures for mobile/touch support
    PinchHandler {
        target: canvasContent
        minimumScale: 0.1
        maximumScale: 10.0
        
        onActiveScaleChanged: {
            zoomLevel = activeScale
        }
    }
    
    // Context menu for pilot creation
    Menu {
        id: contextMenu
        
        MenuItem {
            text: "Create Sentinel Pilot"
            onTriggered: createPilot("sentinel", contextMenu.x, contextMenu.y)
        }
        MenuItem {
            text: "Create Doc Architect" 
            onTriggered: createPilot("doc_architect", contextMenu.x, contextMenu.y)
        }
        MenuItem {
            text: "Create Remediator"
            onTriggered: createPilot("remediator", contextMenu.x, contextMenu.y)
        }
        MenuItem {
            text: "Create Codewright"
            onTriggered: createPilot("codewright", contextMenu.x, contextMenu.y)
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Fit to View"
            onTriggered: fitToView()
        }
        MenuItem {
            text: "Reset Zoom"
            onTriggered: {
                zoomLevel = 1.0
                panOffset = Qt.point(0, 0)
            }
        }
    }
    
    // Functions
    function showContextMenu(x, y) {
        // Transform screen coordinates to canvas coordinates
        var canvasX = (x - panOffset.x) / zoomLevel
        var canvasY = (y - panOffset.y) / zoomLevel
        
        contextMenu.x = canvasX
        contextMenu.y = canvasY
        contextMenu.open()
    }
    
    function createPilot(pilotType, x, y) {
        var pilotId = "pilot_" + pilotType + "_" + Date.now()
        
        var pilotConfig = getPilotConfig(pilotType)
        
        pilotsModel.append({
            "pilotId": pilotId,
            "pilotType": pilotType,
            "displayName": pilotConfig.displayName,
            "x": x,
            "y": y,
            "selected": false,
            "inputs": pilotConfig.inputs,
            "outputs": pilotConfig.outputs
        })
        
        pilotCreated(pilotType, x, y)
        
        console.log("Created pilot:", pilotId)
    }
    
    function getPilotConfig(pilotType) {
        var configs = {
            "sentinel": {
                "displayName": "Sentinel",
                "inputs": [{"name": "context", "type": "text", "connected": false}],
                "outputs": [{"name": "validation", "type": "diagnostic", "connected": false}]
            },
            "doc_architect": {
                "displayName": "Doc Architect", 
                "inputs": [
                    {"name": "requirements", "type": "text", "connected": false},
                    {"name": "validation", "type": "diagnostic", "connected": false}
                ],
                "outputs": [{"name": "documentation", "type": "doc", "connected": false}]
            },
            "remediator": {
                "displayName": "Remediator",
                "inputs": [
                    {"name": "diagnostics", "type": "diagnostic", "connected": false},
                    {"name": "code", "type": "code", "connected": false}
                ],
                "outputs": [
                    {"name": "patches", "type": "patch", "connected": false},
                    {"name": "analysis", "type": "text", "connected": false}
                ]
            },
            "codewright": {
                "displayName": "Codewright",
                "inputs": [
                    {"name": "requirements", "type": "text", "connected": false},
                    {"name": "patches", "type": "patch", "connected": false}
                ],
                "outputs": [
                    {"name": "code", "type": "code", "connected": false},
                    {"name": "tests", "type": "code", "connected": false}
                ]
            }
        }
        
        return configs[pilotType] || {
            "displayName": "Unknown Pilot",
            "inputs": [],
            "outputs": []
        }
    }
    
    function selectPilot(pilotId) {
        // Clear other selections
        for (var i = 0; i < pilotsModel.count; i++) {
            pilotsModel.setProperty(i, "selected", pilotsModel.get(i).pilotId === pilotId)
        }
        
        selectionChanged([pilotId])
    }
    
    function handlePortInteraction(pilotId, portName, portType, isOutput) {
        if (!isConnecting) {
            // Start connection
            isConnecting = true
            connectionPreview.startConnection(pilotId, portName, portType, isOutput)
        } else {
            // Complete connection
            var result = connectionPreview.completeConnection(pilotId, portName, portType, isOutput)
            if (result.success) {
                createConnection(result.from, result.to)
            }
            isConnecting = false
        }
    }
    
    function createConnection(fromInfo, toInfo) {
        // Validate connection types
        if (!isValidConnectionType(fromInfo.portType, toInfo.portType)) {
            console.warn("Invalid connection type:", fromInfo.portType, "->", toInfo.portType)
            return false
        }
        
        var connectionId = "conn_" + Date.now()
        
        connectionsModel.append({
            "connectionId": connectionId,
            "fromPilot": fromInfo.pilotId,
            "fromPort": fromInfo.portName,
            "toPilot": toInfo.pilotId,
            "toPort": toInfo.portName,
            "connectionType": fromInfo.portType
        })
        
        // Mark ports as connected
        updatePortConnectionStatus(fromInfo.pilotId, fromInfo.portName, true)
        updatePortConnectionStatus(toInfo.pilotId, toInfo.portName, true)
        
        connectionCreated(fromInfo.pilotId, fromInfo.portName, toInfo.pilotId, toInfo.portName)
        
        console.log("Created connection:", connectionId)
        return true
    }
    
    function isValidConnectionType(outputType, inputType) {
        // Define compatible connection types
        var compatibilityMatrix = {
            "text": ["text", "doc"],
            "code": ["code", "text"],
            "doc": ["doc", "text"],
            "diagnostic": ["diagnostic", "text"],
            "patch": ["patch", "code"]
        }
        
        var compatibleTypes = compatibilityMatrix[outputType] || []
        return compatibleTypes.includes(inputType)
    }
    
    function updatePortConnectionStatus(pilotId, portName, connected) {
        for (var i = 0; i < pilotsModel.count; i++) {
            var pilot = pilotsModel.get(i)
            if (pilot.pilotId === pilotId) {
                // Update input ports
                var inputs = pilot.inputs
                for (var j = 0; j < inputs.length; j++) {
                    if (inputs[j].name === portName) {
                        inputs[j].connected = connected
                        break
                    }
                }
                
                // Update output ports
                var outputs = pilot.outputs
                for (var k = 0; k < outputs.length; k++) {
                    if (outputs[k].name === portName) {
                        outputs[k].connected = connected
                        break
                    }
                }
                
                pilotsModel.setProperty(i, "inputs", inputs)
                pilotsModel.setProperty(i, "outputs", outputs)
                break
            }
        }
    }
    
    function findPilotById(pilotId) {
        for (var i = 0; i < pilotsModel.count; i++) {
            if (pilotsModel.get(i).pilotId === pilotId) {
                return pilotsModel.get(i)
            }
        }
        return null
    }
    
    function fitToView() {
        if (pilotsModel.count === 0) return
        
        // Calculate bounding box of all pilots
        var minX = Number.MAX_VALUE
        var minY = Number.MAX_VALUE
        var maxX = Number.MIN_VALUE
        var maxY = Number.MIN_VALUE
        
        for (var i = 0; i < pilotsModel.count; i++) {
            var pilot = pilotsModel.get(i)
            minX = Math.min(minX, pilot.x)
            minY = Math.min(minY, pilot.y)
            maxX = Math.max(maxX, pilot.x + 200)  // Approximate pilot width
            maxY = Math.max(maxY, pilot.y + 150)  // Approximate pilot height
        }
        
        // Calculate zoom and pan to fit
        var contentWidth = maxX - minX
        var contentHeight = maxY - minY
        var scaleX = infiniteCanvas.width / contentWidth
        var scaleY = infiniteCanvas.height / contentHeight
        var newZoom = Math.min(scaleX, scaleY) * 0.8  // 80% for padding
        
        var centerX = (minX + maxX) / 2
        var centerY = (minY + maxY) / 2
        
        // Animate to new position
        zoomAnimation.to = newZoom
        panXAnimation.to = infiniteCanvas.width / 2 - centerX * newZoom
        panYAnimation.to = infiniteCanvas.height / 2 - centerY * newZoom
        
        fitAnimation.start()
    }
    
    function updateConnections() {
        // Trigger connection line updates
        for (var i = 0; i < connectionsModel.count; i++) {
            connectionsModel.setProperty(i, "updated", Date.now())
        }
    }
    
    function exportGraph() {
        // Export current graph configuration
        var graph = {
            "pilots": [],
            "connections": [],
            "canvas": {
                "zoom": zoomLevel,
                "pan": {"x": panOffset.x, "y": panOffset.y}
            },
            "exported_at": new Date().toISOString()
        }
        
        // Export pilots
        for (var i = 0; i < pilotsModel.count; i++) {
            var pilot = pilotsModel.get(i)
            graph.pilots.push({
                "id": pilot.pilotId,
                "type": pilot.pilotType,
                "position": {"x": pilot.x, "y": pilot.y},
                "inputs": pilot.inputs,
                "outputs": pilot.outputs
            })
        }
        
        // Export connections
        for (var j = 0; j < connectionsModel.count; j++) {
            var conn = connectionsModel.get(j)
            graph.connections.push({
                "id": conn.connectionId,
                "from": {"pilot": conn.fromPilot, "port": conn.fromPort},
                "to": {"pilot": conn.toPilot, "port": conn.toPort},
                "type": conn.connectionType
            })
        }
        
        return JSON.stringify(graph, null, 2)
    }
    
    function importGraph(graphJson) {
        try {
            var graph = JSON.parse(graphJson)
            
            // Clear existing
            pilotsModel.clear()
            connectionsModel.clear()
            
            // Import pilots
            for (var i = 0; i < graph.pilots.length; i++) {
                var pilot = graph.pilots[i]
                pilotsModel.append({
                    "pilotId": pilot.id,
                    "pilotType": pilot.type,
                    "displayName": getPilotConfig(pilot.type).displayName,
                    "x": pilot.position.x,
                    "y": pilot.position.y,
                    "selected": false,
                    "inputs": pilot.inputs,
                    "outputs": pilot.outputs
                })
            }
            
            // Import connections
            for (var j = 0; j < graph.connections.length; j++) {
                var conn = graph.connections[j]
                connectionsModel.append({
                    "connectionId": conn.id,
                    "fromPilot": conn.from.pilot,
                    "fromPort": conn.from.port,
                    "toPilot": conn.to.pilot,
                    "toPort": conn.to.port,
                    "connectionType": conn.type
                })
            }
            
            // Restore canvas state
            if (graph.canvas) {
                zoomLevel = graph.canvas.zoom || 1.0
                panOffset = Qt.point(
                    graph.canvas.pan.x || 0,
                    graph.canvas.pan.y || 0
                )
            }
            
            console.log("Graph imported successfully")
            return true
            
        } catch (error) {
            console.error("Graph import failed:", error)
            return false
        }
    }
    
    // Animations for smooth interactions
    ParallelAnimation {
        id: fitAnimation
        
        NumberAnimation {
            id: zoomAnimation
            target: infiniteCanvas
            property: "zoomLevel"
            duration: 500
            easing.type: Easing.OutCubic
        }
        
        NumberAnimation {
            id: panXAnimation
            target: infiniteCanvas
            property: "panOffset.x"
            duration: 500
            easing.type: Easing.OutCubic
        }
        
        NumberAnimation {
            id: panYAnimation
            target: infiniteCanvas
            property: "panOffset.y"
            duration: 500
            easing.type: Easing.OutCubic
        }
    }
}

// Grid background component
Component {
    id: gridBackgroundComponent
    
    Item {
        id: gridBackground
        anchors.fill: parent
    
    property int gridSize: 50
    property color gridColor: "#333333"
    
    Canvas {
        anchors.fill: parent
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            // Draw grid lines
            ctx.strokeStyle = gridColor
            ctx.lineWidth = 1
            ctx.globalAlpha = 0.3
            
            // Vertical lines
            for (var x = 0; x < width; x += gridSize) {
                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            }
            
            // Horizontal lines
            for (var y = 0; y < height; y += gridSize) {
                ctx.beginPath()
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
                ctx.stroke()
            }
            
            ctx.globalAlpha = 1.0
        }
    }
    }
}