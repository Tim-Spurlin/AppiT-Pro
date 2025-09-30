import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: haaspWindow
    
    title: "HAASP - Hyper-Advanced Associative Application Synthesis Platform"
    visible: true
    width: 1600
    height: 1000
    minimumWidth: 1200
    minimumHeight: 800
    
    color: "#1B1C20"
    
    // Global state
    property bool voiceActivationEnabled: false
    property var selectedPilots: []
    property var currentProject: null
    property bool advancedMode: true
    
    // Connections to C++ backend
    property var retrievalService: null  // Will be set from C++
    property var pilotOrchestrator: null
    
    Component.onCompleted: {
        console.log("🚀 HAASP Advanced Interface Loaded")
        initializeServices()
    }
    
    // Main layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Top menu bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#2d2d2d"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                
                // HAASP logo and title
                Row {
                    spacing: 10
                    
                    Text {
                        text: "🚀"
                        color: "#00ff00" 
                        font.pixelSize: 20
                            // Avoid ES6 template literals for broader Qt compatibility
                            text: "Score: " + (resultData.score || 0).toFixed(3)
                    
                    Text {
                        text: "HAASP"
                        color: "#ffffff"
                        font.bold: true
                        font.pixelSize: 16
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                // Voice activation toggle
                Button {
                    text: voiceActivationEnabled ? "🎤 Voice: ON" : "🎤 Voice: OFF"
                    checkable: true
                    checked: voiceActivationEnabled
                        text: "Source: " + (resultData.source || "unknown")
                }
                
                // View mode toggle
                Button {
                    text: advancedMode ? "Advanced" : "Simple"
                    onClicked: advancedMode = !advancedMode
                }
                
                // Settings
                Button {
                    text: "⚙️"
                    onClicked: settingsDialog.open()
                }
            }
        }
        
        // Main content area
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal
            
            // Left sidebar - Project explorer and pilot management
            Rectangle {
                SplitView.minimumWidth: 300
                SplitView.preferredWidth: 350
                color: "#252525"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    // Project section
                    GroupBox {
                        title: "Project"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            Button {
                                text: "📁 Open Repository"
                                Layout.fillWidth: true
                                onClicked: openRepositoryDialog.open()
                            }
                            
                            Button {
                                text: "📊 View Analytics"
                                Layout.fillWidth: true
                                enabled: currentProject !== null
                                onClicked: showAnalytics()
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                Text {
                                    text: currentProject ? 
                                          `Current: ${currentProject.name}\nPath: ${currentProject.path}` :
                                          "No project loaded"
                                    color: "#cccccc"
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                    
                    // Pilots section
                    GroupBox {
                        title: "AI Pilots"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            // Pilot quick actions
                            RowLayout {
                                Layout.fillWidth: true
                                
                                Button {
                                    text: "▶️ Run Chain"
                                    onClicked: runPilotChain()
                                }
                                
                                Button {
                                    text: "🔄 Reset"
                                    onClicked: resetPilots()
                                }
                            }
                            
                            // Pilot list
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                ListView {
                                    id: pilotListView
                                    model: pilotListModel
                                    spacing: 5
                                    
                                    delegate: PilotListItem {
                                        width: pilotListView.width
                                        pilotInfo: model
                                        
                                        onPilotClicked: selectPilotInCanvas(pilotId)
                                        onPilotToggled: togglePilotActive(pilotId, active)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Center - Infinite canvas
            Rectangle {
                SplitView.fillWidth: true
                color: "#1e1e1e"
                
                InfiniteCanvas {
                    id: infiniteCanvas
                    anchors.fill: parent
                    
                    onPilotCreated: (pilotType, x, y) => {
                        addPilotToList(pilotType, x, y)
                    }
                    
                    onSelectionChanged: (selectedPilots) => {
                        haaspWindow.selectedPilots = selectedPilots
                        updateInspector()
                    }
                    
                    onConnectionCreated: (fromPilot, fromPort, toPilot, toPort) => {
                        console.log("Connection created:", fromPilot, "->", toPilot)
                    }
                }
                
                // Canvas overlay - tools and info
                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 10
                    width: 200
                    height: canvasToolsLayout.implicitHeight + 20
                    color: "#2d2d2d"
                    radius: 8
                    opacity: 0.9
                    
                    ColumnLayout {
                        id: canvasToolsLayout
                        anchors.fill: parent
                        anchors.margins: 10
                        
                        Text {
                            text: "Canvas Tools"
                            color: "#ffffff"
                            font.bold: true
                        }
                        
                        Button {
                            text: "🔍 Fit to View"
                            Layout.fillWidth: true
                            onClicked: infiniteCanvas.fitToView()
                        }
                        
                        Button {
                            text: "💾 Save Graph"
                            Layout.fillWidth: true
                            onClicked: saveCurrentGraph()
                        }
                        
                        Button {
                            text: "📁 Load Graph"
                            Layout.fillWidth: true
                            onClicked: loadGraphDialog.open()
                        }
                        
                        Text {
                            text: `Zoom: ${infiniteCanvas.zoomLevel.toFixed(2)}x`
                            color: "#cccccc"
                            font.pixelSize: 10
                        }
                    }
                }
            }
            
            // Right sidebar - Inspector and results
            Rectangle {
                SplitView.minimumWidth: 300
                SplitView.preferredWidth: 400
                color: "#252525"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    // Inspector
                    GroupBox {
                        title: "Inspector"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 300
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            Text {
                                text: selectedPilots.length > 0 ? 
                                      `Selected: ${selectedPilots[0]}` :
                                      "No selection"
                                color: "#cccccc"
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                // Inspector content will be loaded dynamically
                                PilotInspector {
                                    id: pilotInspector
                                    pilotId: selectedPilots.length > 0 ? selectedPilots[0] : ""
                                }
                            }
                        }
                    }
                    
                    // Search and retrieval
                    GroupBox {
                        title: "Intelligent Search"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            // Search input
                            RowLayout {
                                Layout.fillWidth: true
                                
                                TextField {
                                    id: searchField
                                    Layout.fillWidth: true
                                    placeholderText: "Ask HAASP anything..."
                                    
                                    onAccepted: performSearch()
                                }
                                
                                Button {
                                    text: "🔍"
                                    onClicked: performSearch()
                                }
                                
                                Button {
                                    text: "🎯"
                                    onClicked: performRAGQuery()
                                }
                            }
                            
                            // Search mode selection
                            RowLayout {
                                Layout.fillWidth: true
                                
                                ButtonGroup {
                                    id: searchModeGroup
                                }
                                
                                RadioButton {
                                    text: "Hybrid"
                                    checked: true
                                    ButtonGroup.group: searchModeGroup
                                }
                                
                                RadioButton {
                                    text: "Semantic"
                                    ButtonGroup.group: searchModeGroup
                                }
                                
                                RadioButton {
                                    text: "Fuzzy"
                                    ButtonGroup.group: searchModeGroup
                                }
                                
                                RadioButton {
                                    text: "Graph"
                                    ButtonGroup.group: searchModeGroup
                                }
                            }
                            
                            // Results
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                ListView {
                                    id: searchResults
                                    model: searchResultsModel
                                    spacing: 5
                                    
                                    delegate: SearchResultItem {
                                        width: searchResults.width
                                        resultData: model
                                        
                                        onClicked: openSearchResult(model)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Bottom status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 30
            color: "#2d2d2d"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                
                // System status
                Row {
                    spacing: 10
                    
                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: "#00ff00"  // Green = healthy
                    }
                    
                    Text {
                        text: "System: Ready"
                        color: "#ffffff"
                        font.pixelSize: 10
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                // Performance indicators
                Text {
                    text: `Memory: ${getMemoryUsage()} | Vectors: ${getVectorCount()}`
                    color: "#cccccc"
                    font.pixelSize: 10
                }
                
                Text {
                    text: "HAASP v2.0.0"
                    color: "#aaaaaa"
                    font.pixelSize: 9
                }
            }
        }
    }
    
    // Models
    ListModel {
        id: pilotListModel
        
        Component.onCompleted: {
            // Initialize with default pilots
            append({
                "pilotId": "pilot_0_sentinel",
                "name": "Sentinel",
                "type": "sentinel", 
                "active": true,
                "status": "idle"
            })
            
            append({
                "pilotId": "pilot_1_doc_architect",
                "name": "Doc Architect",
                "type": "doc_architect",
                "active": true,
                "status": "idle"
            })
            
            append({
                "pilotId": "pilot_2_remediator", 
                "name": "Remediator",
                "type": "remediator",
                "active": true,
                "status": "idle"
            })
            
            append({
                "pilotId": "pilot_3_codewright",
                "name": "Codewright", 
                "type": "codewright",
                "active": true,
                "status": "idle"
            })
        }
    }
    
    ListModel {
        id: searchResultsModel
    }
    
    // Dialogs
    FileDialog {
        id: openRepositoryDialog
        title: "Open Repository"
        // TODO: Implement file dialog for repository selection
    }
    
    Dialog {
        id: settingsDialog
        title: "HAASP Settings"
        width: 500
        height: 400
        
        ColumnLayout {
            anchors.fill: parent
            
            GroupBox {
                title: "Voice Activation"
                Layout.fillWidth: true
                
                ColumnLayout {
                    CheckBox {
                        text: "Enable voice commands"
                        checked: voiceActivationEnabled
                        onToggled: voiceActivationEnabled = checked
                    }
                    
                    Button {
                        text: "Calibrate Microphone"
                        onClicked: calibrateMicrophone()
                    }
                }
            }
            
            GroupBox {
                title: "Retrieval System"
                Layout.fillWidth: true
                
                ColumnLayout {
                    CheckBox {
                        text: "Enable GPU acceleration"
                        // TODO: Connect to backend setting
                    }
                    
                    CheckBox {
                        text: "Advanced graph reasoning"
                        checked: true
                    }
                    
                    Button {
                        text: "Rebuild Indexes"
                        onClicked: rebuildIndexes()
                    }
                }
            }
        }
    }
    
    Dialog {
        id: loadGraphDialog
        title: "Load Pilot Graph"
        width: 400
        height: 300
        
        // TODO: Implement graph loading interface
    }
    
    // Functions
    function initializeServices() {
        // Initialize connections to C++ backend services
        console.log("Initializing HAASP services...")
        
        // TODO: Connect to retrieval service
        // TODO: Connect to pilot orchestrator
        // TODO: Connect to voice service
    }
    
    function toggleVoiceActivation() {
        voiceActivationEnabled = !voiceActivationEnabled
        
        if (voiceActivationEnabled) {
            console.log("🎤 Voice activation enabled")
            // TODO: Start voice service
        } else {
            console.log("🔇 Voice activation disabled")
            // TODO: Stop voice service
        }
    }
    
    function performSearch() {
        if (!searchField.text.trim()) return
        
        console.log("🔍 Performing search:", searchField.text)
        
        // Clear previous results
        searchResultsModel.clear()
        
        // TODO: Call retrieval service
        // Placeholder results for now
        searchResultsModel.append({
            "title": "Search result 1",
            "content": "This is a placeholder search result",
            "source": "example.py",
            "score": 0.95
        })
    }
    
    function performRAGQuery() {
        if (!searchField.text.trim()) return
        
        console.log("🎯 Performing RAG query:", searchField.text)
        
        // TODO: Call RAG service with full context
        // For now, show that RAG is more sophisticated
        searchResultsModel.clear()
        searchResultsModel.append({
            "title": "RAG Generated Response",
            "content": "This would be an AI-generated response based on retrieved context",
            "source": "Generated by HAASP",
            "score": 1.0,
            "type": "generated"
        })
    }
    
    function addPilotToList(pilotType, x, y) {
        var pilotId = "pilot_" + pilotType + "_" + Date.now()
        
        pilotListModel.append({
            "pilotId": pilotId,
            "name": getPilotDisplayName(pilotType),
            "type": pilotType,
            "active": true,
            "status": "idle",
            "position": {"x": x, "y": y}
        })
        
        console.log("Added pilot to list:", pilotId)
    }
    
    function getPilotDisplayName(pilotType) {
        var names = {
            "sentinel": "Sentinel",
            "doc_architect": "Doc Architect", 
            "remediator": "Remediator",
            "codewright": "Codewright"
        }
        return names[pilotType] || "Custom Pilot"
    }
    
    function selectPilotInCanvas(pilotId) {
        infiniteCanvas.selectPilot(pilotId)
    }
    
    function togglePilotActive(pilotId, active) {
        console.log("Toggle pilot:", pilotId, active)
        // TODO: Implement pilot activation/deactivation
    }
    
    function updateInspector() {
        // Update inspector with selected pilot info
        // TODO: Load pilot details into inspector
    }
    
    function runPilotChain() {
        console.log("🔄 Running pilot chain...")
        // TODO: Execute pilot chain through orchestrator
    }
    
    function resetPilots() {
        console.log("🔄 Resetting pilots...")
        // TODO: Reset all pilot states
    }
    
    function showAnalytics() {
        console.log("📊 Opening analytics...")
        // TODO: Open analytics view/dialog
    }
    
    function calibrateMicrophone() {
        console.log("🎤 Calibrating microphone...")
        // TODO: Start microphone calibration
    }
    
    function rebuildIndexes() {
        console.log("🔄 Rebuilding indexes...")
        // TODO: Trigger index rebuild
    }
    
    function saveCurrentGraph() {
        var graphData = infiniteCanvas.exportGraph()
        console.log("💾 Saving graph:", graphData.length, "characters")
        // TODO: Save to file system
    }
    
    function openSearchResult(resultData) {
        console.log("📂 Opening result:", resultData.title)
        // TODO: Open file or show result details
    }
    
    function getMemoryUsage() {
        // TODO: Get actual memory usage from backend
        return "156MB"
    }
    
    function getVectorCount() {
        // TODO: Get actual vector count from backend
        return "1,247"
    }
}

// Pilot list item component - moved to external file for modularity
// This will be instantiated dynamically when needed

// Pilot list item factory - creates items dynamically
function createPilotListItem(pilotInfo, parent) {
    var componentString = "import QtQuick 2.15; import QtQuick.Controls 2.15; import QtQuick.Layouts 1.15; " +
        "Rectangle { " +
        "property var pilotInfo; " +
        "signal pilotClicked(string pilotId); " +
        "signal pilotToggled(string pilotId, bool active); " +
        "height: 50; " +
        "color: '#333333'; " +
        "radius: 4; " +
        "RowLayout { " +
        "anchors.fill: parent; " +
        "anchors.margins: 8; " +
        "Rectangle { " +
        "width: 12; " +
        "height: 12; " +
        "radius: 6; " +
        "color: parent.parent.pilotInfo.active ? '#4CAF50' : '#666666' " +
        "} " +
        "Text { " +
        "text: parent.parent.pilotInfo.name || 'Unknown'; " +
        "color: '#ffffff'; " +
        "Layout.fillWidth: true " +
        "} " +
        "Switch { " +
        "checked: parent.parent.pilotInfo.active; " +
        "onToggled: parent.parent.pilotToggled(parent.parent.pilotInfo.pilotId, checked) " +
        "} " +
        "} " +
        "MouseArea { " +
        "anchors.fill: parent; " +
        "onClicked: parent.pilotClicked(parent.pilotInfo.pilotId) " +
        "} " +
        "}"

    var component = Qt.createComponent("data:text/plain," + componentString)
    if (component.status === Component.Ready) {
        var item = component.createObject(parent)
        item.pilotInfo = pilotInfo
        return item
    }
    return null
}

// Search result item component
Component {
    id: searchResultItemComponent
    
    Rectangle {
        id: searchResultItem
        
        property var resultData
        signal clicked()
        
        height: resultContent.implicitHeight + 20
        color: "#333333"
        radius: 4
            border.width: 1
            border.color: "#555555"
        
        ColumnLayout {
            id: resultContent
            anchors.fill: parent
            anchors.margins: 10
            spacing: 5
            
            RowLayout {
                Layout.fillWidth: true
                
                Text {
                    text: resultData.title || "Untitled"
                    color: "#ffffff"
                    font.bold: true
                    font.pixelSize: 12
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: "Score: " + (resultData.score || 0).toFixed(3)
                    color: "#4CAF50"
                    font.pixelSize: 10
                }
            }
            
            Text {
                text: resultData.content || ""
                color: "#cccccc"
                font.pixelSize: 10
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                maximumLineCount: 3
                elide: Text.ElideRight
            }
            
            Text {
                text: "Source: " + (resultData.source || "unknown")
                color: "#888888"
                font.pixelSize: 9
            }
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: searchResultItem.clicked()
            cursorShape: Qt.PointingHandCursor
        }
    }
    // End of searchResultItem Rectangle
}

// Pilot inspector component
Component {
    id: pilotInspectorComponent
    
    Rectangle {
        id: pilotInspector
        
        property string pilotId
        
        color: "transparent"
    
        ColumnLayout {
            anchors.fill: parent
            spacing: 10
            
            Text {
                text: pilotId ? ("Inspecting: " + pilotId) : "No pilot selected"
                color: "#ffffff"
                font.bold: true
            }
            
            // Pilot-specific configuration
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ColumnLayout {
                    width: pilotInspector.width - 20
                    spacing: 8
                    
                    GroupBox {
                        title: "Memory Configuration"
                        Layout.fillWidth: true
                        
                        ColumnLayout {
                            Text { text: "Vector Dimensions: 384"; color: "#cccccc"; font.pixelSize: 10 }
                            Text { text: "FAISS Index: HNSW"; color: "#cccccc"; font.pixelSize: 10 }
                            Text { text: "Conversation History: 47 messages"; color: "#cccccc"; font.pixelSize: 10 }
                        }
                    }
                    
                    GroupBox {
                        title: "Performance Metrics"
                        Layout.fillWidth: true
                        
                        ColumnLayout {
                            Text { text: "Query Latency: 45ms"; color: "#4CAF50"; font.pixelSize: 10 }
                            Text { text: "Success Rate: 94.2%"; color: "#4CAF50"; font.pixelSize: 10 }
                            Text { text: "Last Active: 2 minutes ago"; color: "#cccccc"; font.pixelSize: 10 }
                        }
                    }
                    
                    GroupBox {
                        title: "Recent Activity"
                        Layout.fillWidth: true
                        
                        ColumnLayout {
                            Text { 
                                text: "• Generated documentation\n• Fixed 3 code issues\n• Processed 12 queries"
                                color: "#cccccc"
                                font.pixelSize: 10
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
        }
    }
}

// End pilotInspectorComponent

// Close root ApplicationWindow
}