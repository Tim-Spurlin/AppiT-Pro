import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import org.kde.kirigami 2.19 as Kirigami

ApplicationWindow {
    id: haaspWindow
    
    title: "HAASP - Hyper-Advanced Associative Application Synthesis Platform"
    import QtQuick 2.15
    import QtQuick.Controls 2.15
    import QtQuick.Layouts 1.15
    import QtQuick.Window 2.15

    // CLEAN REBUILD OF ADVANCED INTERFACE (syntax-fixed minimal version)
    ApplicationWindow {
        id: root
        title: "HAASP - Advanced Interface"
        visible: true
        width: 1600; height: 1000
        minimumWidth: 1200; minimumHeight: 800
        color: "#1B1C20"

        property bool voiceActivationEnabled: false
        property var selectedPilots: []
        property var currentProject: null

        Component.onCompleted: console.log("🚀 FullAdvancedMain.qml loaded")

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // Top bar
            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 42; color: "#2d2d2d"
                RowLayout { anchors.fill: parent; anchors.margins: 8
                    Text { text: "HAASP v1.0.0"; color: "#ffffff"; font.bold: true }
                    Item { Layout.fillWidth: true }
                    Button { text: voiceActivationEnabled ? "🎤 On" : "🎤 Off"; onClicked: voiceActivationEnabled = !voiceActivationEnabled }
                    Button { text: "Analytics"; onClicked: console.log("analytics") }
                    Button { text: "Settings"; onClicked: console.log("settings") }
                }
            }

            RowLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 0
                // Left
                Rectangle { Layout.preferredWidth: 260; Layout.fillHeight: true; color: "#252526"
                    ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 8
                        Text { text: "🤖 AI Pilots"; color: "#fff"; font.bold: true }
                        ListView { id: pilotList; Layout.fillWidth: true; Layout.fillHeight: true; model: pilotModel; spacing: 4; clip: true
                            delegate: Rectangle { width: pilotList.width; height: 54; radius: 4; color: active ? "#404040" : "#333"; border.width: selected ? 2 : 0; border.color: "#00aaff"
                                RowLayout { anchors.fill: parent; anchors.margins: 6
                                    Rectangle { width:10; height:10; radius:5; color: active?"#4CAF50":"#757575" }
                                    ColumnLayout { Layout.fillWidth: true; spacing:2
                                        Text { text: name; color: "#fff"; font.pixelSize:11; font.bold: true }
                                        Text { text: type + " | " + status; color: "#bbb"; font.pixelSize:9 }
                                    }
                                    Button { text: active?"⏸":"▶"; width:32; onClicked: console.log("toggle pilot", pilotId) }
                                }
                                MouseArea { anchors.fill: parent; onClicked: selectedPilots=[pilotId] }
                            }
                        }
                    }
                }
                // Center
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: "#1e1e1e"
                    ColumnLayout { anchors.fill: parent
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight:40; color: "#2d2d2d"
                            RowLayout { anchors.fill: parent; anchors.margins:8
                                Text { text: "🎨 Infinite Canvas"; color: "#fff"; font.bold: true }
                                Item { Layout.fillWidth: true }
                                Row { spacing:4
                                    Button { text:"+"; onClicked: console.log("zoom+") }
                                    Button { text:"-"; onClicked: console.log("zoom-") }
                                    Button { text:"🎯"; onClicked: console.log("reset") }
                                    Button { text:"💾"; onClicked: console.log("save graph") }
                                }
                            }
                        }
                        Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: "#1a1a1a"
                            Text { anchors.centerIn: parent; text: "Advanced Canvas Placeholder"; color: "#666" }
                        }
                    }
                }
                // Right
                Rectangle { Layout.preferredWidth: 340; Layout.fillHeight: true; color: "#252526"
                    ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 10
                        GroupBox { title: "🔍 Search"; Layout.fillWidth: true
                            ColumnLayout { width:parent.width
                                TextField { id: searchField; Layout.fillWidth: true; placeholderText: "Search..."; onAccepted: performSearch(text) }
                                Row { spacing:4
                                    Button { text:"Search"; onClicked: performSearch(searchField.text) }
                                    Button { text:"Clear"; onClicked: clearSearch() }
                                }
                            }
                        }
                        ListView { id: searchResults; Layout.fillWidth: true; Layout.preferredHeight:180; model: searchResultsModel; spacing:4; clip:true
                            delegate: Rectangle { width: searchResults.width; height: implicitHeight; color: "#333"; radius:4; border.width:1; border.color: "#555"
                                ColumnLayout { anchors.fill: parent; anchors.margins:8; spacing:4
                                    Text { text: title; color: "#fff"; font.pixelSize:11; font.bold:true }
                                    Text { text: content; color: "#ccc"; font.pixelSize:9; wrapMode: Text.WordWrap; maximumLineCount:3; elide: Text.ElideRight }
                                    Text { text: "Source: " + (source||"unknown"); color: "#888"; font.pixelSize:8 }
                                }
                            }
                        }
                        GroupBox { title: "📊 System"; Layout.fillWidth: true
                            ColumnLayout { width:parent.width; spacing:4
                                Text { text: "Memory: 128MB"; color: "#ccc"; font.pixelSize:10 }
                                Text { text: "Active Pilots: " + selectedPilots.length; color: "#ccc"; font.pixelSize:10 }
                                Text { text: "Vector Count: 42"; color: "#ccc"; font.pixelSize:10 }
                                ProgressBar { Layout.fillWidth: true; value:0.55 }
                            }
                        }
                        GroupBox { title: "📋 Activity"; Layout.fillWidth: true; Layout.fillHeight: true
                            ListView { anchors.fill: parent; model: activityModel; spacing:2; clip:true
                                delegate: Text { text: "• " + activity; color: "#ccc"; font.pixelSize:9; wrapMode: Text.WordWrap }
                            }
                        }
                    }
                }
            }

            // Status bar
            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 24; color: "#007ACC"
                RowLayout { anchors.fill: parent; anchors.margins:4
                    Text { text: "🟢 Ready"; color: "#fff"; font.pixelSize:9 }
                    Item { Layout.fillWidth: true }
                    Text { text: currentProject ? "Project: " + currentProject : "No project loaded"; color: "#fff"; font.pixelSize:9 }
                }
            }
        }

        // Models
        ListModel { id: pilotModel
            ListElement { pilotId: "codewright_001"; name: "CodeWright Alpha"; type: "CodeGen"; status: "Ready"; active: true; selected: false }
            ListElement { pilotId: "doc_architect_001"; name: "Doc Architect"; type: "Docs"; status: "Idle"; active: false; selected: false }
            ListElement { pilotId: "sentinel_001"; name: "Code Sentinel"; type: "QA"; status: "Monitoring"; active: true; selected: false }
            ListElement { pilotId: "remediator_001"; name: "Bug Remediator"; type: "Fix"; status: "Ready"; active: false; selected: false }
        }
        ListModel { id: searchResultsModel }
        ListModel { id: activityModel
            ListElement { activity: "Generated 3 new components" }
            ListElement { activity: "Fixed 2 linting errors" }
            ListElement { activity: "Updated documentation" }
            ListElement { activity: "Optimized code structure" }
            ListElement { activity: "Processed user query" }
        }

        // Functions
        function performSearch(q) {
            searchResultsModel.clear();
            if (!q) return;
            searchResultsModel.append({ title: "Result", content: "Result for '" + q + "'", source: "src/main.cpp" });
        }
        function clearSearch() { searchField.text = ""; searchResultsModel.clear(); }
    }
                    anchors.fill: parent
                    spacing: 0
                    
                    // Canvas toolbar
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "#2d2d2d"
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            
                            Text {
                                text: "🎨 Infinite Canvas"
                                color: "#ffffff"
                                font.bold: true
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            Row {
                                spacing: 4
                                
                                Button {
                                    text: "🔍+"
                                    onClicked: canvasZoomIn()
                                    ToolTip.text: "Zoom in"
                                }
                                
                                Button {
                                    text: "🔍-"
                                    onClicked: canvasZoomOut()
                                    ToolTip.text: "Zoom out"
                                }
                                
                                Button {
                                    text: "🎯"
                                    onClicked: canvasResetView()
                                    ToolTip.text: "Reset view"
                                }
                                
                                Button {
                                    text: "💾"
                                    onClicked: saveCurrentGraph()
                                    ToolTip.text: "Save current graph"
                                }
                            }
                        }
                    }
                    
                    // Canvas area
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#1a1a1a"
                        
                        // Grid background
                        Canvas {
                            id: gridCanvas
                            anchors.fill: parent
                            
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.clearRect(0, 0, width, height)
                                ctx.strokeStyle = "#333333"
                                ctx.lineWidth = 1
                                ctx.globalAlpha = 0.3
                                
                                var gridSize = 50
                                
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
                        
                        // Canvas content would go here
                        Text {
                            anchors.centerIn: parent
                            text: "🎨 Infinite Canvas\\n\\nDrag and drop pilots here\\nConnect pilots with visual links\\nBuild your AI workflow"
                            color: "#666666"
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            
                            onClicked: {
                                if (mouse.button === Qt.RightButton) {
                                    canvasContextMenu.popup()
                                }
                            }
                            
                            onDoubleClicked: {
                                createPilotAtPosition(mouse.x, mouse.y)
                            }
                        }
                    }
                }
            }
            
            // Right sidebar - Tools and Search
            Rectangle {
                Layout.preferredWidth: 350
                Layout.fillHeight: true
                color: "#252526"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    // Search section
                    GroupBox {
                        title: "🔍 Semantic Search"
                        Layout.fillWidth: true
                        
                        ColumnLayout {
                            width: parent.width
                            
                            TextField {
                                id: searchField
                                Layout.fillWidth: true
                                placeholderText: "Search codebase, docs, or ask questions..."
                                onAccepted: performSearch(text)
                            }
                            
                            Row {
                                spacing: 4
                                
                                Button {
                                    text: "Search"
                                    onClicked: performSearch(searchField.text)
                                }
                                
                                Button {
                                    text: "Clear"
                                    onClicked: clearSearch()
                                }
                            }
                        }
                    }
                    
                    // Search results
                    ListView {
                        id: searchResults
                        model: searchResultsModel
                        spacing: 4
                        clip: true
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                            
                            delegate: Rectangle {
                                width: searchResults.width
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
                                    
                                    Text {
                                        text: model.title || "Untitled"
                                        color: "#ffffff"
                                        font.bold: true
                                        font.pixelSize: 12
                                    }
                                    
                                    Text {
                                        text: model.content || ""
                                        color: "#cccccc"
                                        font.pixelSize: 10
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                        maximumLineCount: 3
                                        elide: Text.ElideRight
                                    }
                                    
                                    Text {
                                        text: "Source: " + (model.source || "unknown")
                                        color: "#888888"
                                        font.pixelSize: 9
                                    }
                                }
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: openSearchResult(model)
                                    cursorShape: Qt.PointingHandCursor
                                }
                            }
                        }
                    }
                    
                    // System monitoring
                    GroupBox {
                        title: "📊 System Monitor"
                        Layout.fillWidth: true
                        
                        ColumnLayout {
                            width: parent.width
                            spacing: 8
                            
                            Text {
                                text: "Memory: 128MB"
                                color: "#cccccc"
                                font.pixelSize: 10
                            }
                            
                            Text {
                                text: "Active Pilots: " + selectedPilots.length
                                color: "#cccccc"
                                font.pixelSize: 10
                            }
                            
                            Text {
                                text: "Vector Count: 42"
                                color: "#cccccc"
                                font.pixelSize: 10
                            }
                            
                            ProgressBar {
                                Layout.fillWidth: true
                                value: 0.65
                                ToolTip.text: "System load: 65%"
                            }
                        }
                    }
                    
                    // Recent activity
                    GroupBox {
                        title: "📋 Recent Activity"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        ListView {
                            anchors.fill: parent
                            model: activityModel
                            spacing: 2
                            clip: true
                            
                            delegate: Text {
                                text: "• " + model.activity
                                color: "#cccccc"
                                font.pixelSize: 9
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 24
            color: "#007ACC"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 4
                
                Text {
                    text: "🟢 Ready"
                    color: "#ffffff"
                    font.pixelSize: 9
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: currentProject ? "Project: " + currentProject : "No project loaded"
                    color: "#ffffff"
                    font.pixelSize: 9
                }
            }
        }
    } // end ColumnLayout (anchors.fill: parent)
    
    // Context menus
    Menu {
        id: canvasContextMenu
        
        MenuItem {
            text: "Create Pilot Here"
            onTriggered: createPilotAtCursor()
        }
        
        MenuItem {
            text: "Paste Pilot"
            enabled: false // TODO: implement clipboard
        }
        
        MenuSeparator {}
        
        MenuItem {
            text: "Reset View"
            onTriggered: canvasResetView()
        }
    }
} // end ApplicationWindow
    // Data models
    ListModel {
        id: pilotModel
        
        ListElement {
            pilotId: "codewright_001"
            name: "CodeWright Alpha"
            type: "Code Generator"
            status: "Ready"
            active: true
            selected: false
        }
        
        ListElement {
            pilotId: "doc_architect_001"
            name: "Doc Architect"
            type: "Documentation"
            status: "Idle"
            active: false
            selected: false
        }
        
        ListElement {
            pilotId: "sentinel_001"
            name: "Code Sentinel"
            type: "Quality Assurance"
            status: "Monitoring"
            active: true
            selected: false
        }
        
        ListElement {
            pilotId: "remediator_001"
            name: "Bug Remediator"
            type: "Bug Fixing"
            status: "Ready"
            active: false
            selected: false
        }
    }
    
    ListModel {
        id: searchResultsModel
        // Will be populated by search operations
    }
    
    ListModel {
        id: activityModel
        
        ListElement { activity: "Generated 3 new components" }
        ListElement { activity: "Fixed 2 linting errors" }
        ListElement { activity: "Updated documentation" }
        ListElement { activity: "Optimized code structure" }
        ListElement { activity: "Processed user query" }
    }
    
    // Functions
    function initializeServices() {
        console.log("🔧 Initializing HAASP services...")
        // Connect to C++ backend services
    }
    
    function toggleVoiceActivation() {
        voiceActivationEnabled = !voiceActivationEnabled
        console.log("🎤 Voice activation:", voiceActivationEnabled ? "ON" : "OFF")
    }
    
    function showAnalytics() {
        console.log("📊 Opening analytics...")
        controller.navigateTo("analytics")
    }
    
    function showSettings() {
        console.log("⚙️ Opening settings...")
        controller.navigateTo("settings")
    }
    
    function createNewPilot() {
        console.log("🤖 Creating new pilot...")
        // TODO: Show pilot creation dialog
    }
    
    function startPilot(pilotId) {
        console.log("▶ Starting pilot:", pilotId)
        pilotOrchestrator.startPilot(pilotId)
    }
    
    function stopPilot(pilotId) {
        console.log("⏸ Stopping pilot:", pilotId)
        pilotOrchestrator.stopPilot(pilotId)
    }
    
    function selectPilot(pilotId) {
        console.log("👆 Selected pilot:", pilotId)
        selectedPilots = [pilotId]
        // TODO: Update model selection
    }
    
    function configePilot(pilotId) {
        console.log("⚙️ Configuring pilot:", pilotId)
        // TODO: Open pilot configuration
    }
    
    function resetAllPilots() {
        console.log("🔄 Resetting all pilots...")
        // TODO: Reset all pilot states
    }
    
    function showSystemStatus() {
        console.log("📊 Opening system status...")
        // TODO: Show system status dialog
    }
    
    function rebuildIndexes() {
        console.log("🔧 Rebuilding indexes...")
        // TODO: Trigger index rebuild
    }
    
    function canvasZoomIn() {
        console.log("🔍+ Canvas zoom in")
        // TODO: Implement canvas zoom
    }
    
    function canvasZoomOut() {
        console.log("🔍- Canvas zoom out")
        // TODO: Implement canvas zoom
    }
    
    function canvasResetView() {
        console.log("🎯 Canvas reset view")
        // TODO: Reset canvas view
    }
    
    function saveCurrentGraph() {
        console.log("💾 Saving current graph...")
        // TODO: Save graph to file
    }
    
    function createPilotAtPosition(x, y) {
        console.log("🤖 Creating pilot at:", x, y)
        // TODO: Create pilot at canvas position
    }
    
    function createPilotAtCursor() {
        console.log("🤖 Creating pilot at cursor...")
        // TODO: Create pilot at cursor position
    }
    
    function performSearch(query) {
        console.log("🔍 Searching for:", query)
        // TODO: Perform semantic search
        searchResultsModel.clear()
        // Add sample results
        searchResultsModel.append({
            title: "Sample Result 1",
            content: "This is a sample search result for demonstration...",
            source: "src/main.cpp"
        })
    }
    
    function clearSearch() {
        searchField.text = ""
        searchResultsModel.clear()
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