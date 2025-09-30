import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: haaspWindow
    
    title: "HAASP - Advanced Interface"
    visible: true
    width: 1600
    height: 1000
    minimumWidth: 1200
    minimumHeight: 800
    
    color: "#1B1C20"
    
    // Global state
    property bool servicesConnected: false
    property bool voiceEnabled: false
    property var currentProject: null
    
    Component.onCompleted: {
        console.log("🚀 HAASP Advanced Interface Started")
        initializeAdvancedFeatures()
    }
    
    // Main interface layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Top toolbar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: "#2d2d2d"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                
                // Branding
                Row {
                    spacing: 10
                    
                    Text {
                        text: "🚀"
                        color: "#00ff88"
                        font.pixelSize: 20
                    }
                    
                    Text {
                        text: "HAASP Advanced"
                        color: "#ffffff"
                        font.bold: true
                        font.pixelSize: 16
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                // Quick actions
                Row {
                    spacing: 8
                    
                    Button {
                        text: "📁 Repository"
                        onClicked: loadRepository()
                    }
                    
                    Button {
                        text: voiceEnabled ? "🎤 ON" : "🎤 OFF"
                        checkable: true
                        checked: voiceEnabled
                        onToggled: voiceEnabled = checked
                    }
                    
                    Button {
                        text: "⚙️ Settings"
                        onClicked: showSettings()
                    }
                }
            }
        }
        
        // Main workspace
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal
            
            // Left sidebar - Pilots & Project
            Rectangle {
                SplitView.minimumWidth: 300
                SplitView.preferredWidth: 350
                color: "#252525"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    // Project info
                    GroupBox {
                        title: "Project"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 150
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            Text {
                                text: currentProject ? 
                                      `📁 ${currentProject.name}\n📍 ${currentProject.path}` :
                                      "No project loaded"
                                color: "#ffffff"
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                            
                            Button {
                                text: "📊 View Analytics"
                                Layout.fillWidth: true
                                enabled: currentProject !== null
                                onClicked: Qt.openUrlExternally("https://127.0.0.1:7420")
                            }
                        }
                    }
                    
                    // AI Pilots
                    GroupBox {
                        title: "AI Pilots"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            // Control buttons
                            RowLayout {
                                Layout.fillWidth: true
                                
                                Button {
                                    text: "▶️ Run"
                                    Layout.fillWidth: true
                                    onClicked: runPilots()
                                }
                                
                                Button {
                                    text: "⏹️ Stop"
                                    Layout.fillWidth: true
                                    onClicked: stopPilots()
                                }
                            }
                            
                            // Pilot list
                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                model: pilotsModel
                                spacing: 5
                                
                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 60
                                    color: "#333333"
                                    radius: 4
                                    
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        
                                        Rectangle {
                                            width: 12
                                            height: 12
                                            radius: 6
                                            color: model.active ? "#4CAF50" : "#666666"
                                        }
                                        
                                        Column {
                                            Layout.fillWidth: true
                                            
                                            Text {
                                                text: model.name
                                                color: "#ffffff"
                                                font.bold: true
                                            }
                                            
                                            Text {
                                                text: `Status: ${model.status}`
                                                color: "#cccccc"
                                                font.pixelSize: 10
                                            }
                                        }
                                        
                                        Switch {
                                            checked: model.active
                                            onToggled: togglePilot(model.id, checked)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Center - Canvas or Main View
            Rectangle {
                SplitView.fillWidth: true
                color: "#1e1e1e"
                
                StackLayout {
                    anchors.fill: parent
                    currentIndex: tabBar.currentIndex
                    
                    // Canvas View
                    Item {
                        Rectangle {
                            anchors.fill: parent
                            color: "#1a1a1a"
                            
                            Text {
                                anchors.centerIn: parent
                                text: "🎨 Infinite Canvas\n\n(Advanced canvas will be implemented here)\n\nFor now: Drag & drop pilot orchestration"
                                color: "#ffffff"
                                font.pixelSize: 14
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                    
                    // Chat View
                    Rectangle {
                        color: "#1a1a1a"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            // Chat messages
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                ListView {
                                    id: chatView
                                    model: chatModel
                                    spacing: 8
                                    
                                    delegate: Rectangle {
                                        width: chatView.width
                                        height: messageText.implicitHeight + 20
                                        color: model.sender === "user" ? "#2d4a2d" : "#2d2a4a"
                                        radius: 6
                                        
                                        Text {
                                            id: messageText
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            text: `${model.sender}: ${model.message}`
                                            color: "#ffffff"
                                            wrapMode: Text.WordWrap
                                        }
                                    }
                                }
                            }
                            
                            // Chat input
                            RowLayout {
                                Layout.fillWidth: true
                                
                                TextField {
                                    id: chatInput
                                    Layout.fillWidth: true
                                    placeholderText: "Ask HAASP anything..."
                                    onAccepted: sendChatMessage()
                                }
                                
                                Button {
                                    text: "Send"
                                    onClicked: sendChatMessage()
                                }
                                
                                Button {
                                    text: "🎤"
                                    enabled: voiceEnabled
                                    onClicked: startVoiceInput()
                                }
                            }
                        }
                    }
                    
                    // Analytics View
                    Rectangle {
                        color: "#1a1a1a"
                        
                        Text {
                            anchors.centerIn: parent
                            text: "📊 Advanced Analytics\n\n(Real-time analytics dashboard)\n\nVisit: https://127.0.0.1:7420"
                            color: "#ffffff"
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
            
            // Right sidebar - Search & Inspector
            Rectangle {
                SplitView.minimumWidth: 300
                SplitView.preferredWidth: 400
                color: "#252525"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    // Search interface
                    GroupBox {
                        title: "🔍 Intelligent Search"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 400
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            // Search input
                            RowLayout {
                                Layout.fillWidth: true
                                
                                TextField {
                                    id: searchField
                                    Layout.fillWidth: true
                                    placeholderText: "Search anything..."
                                    onAccepted: performSearch()
                                }
                                
                                Button {
                                    text: "🔍"
                                    onClicked: performSearch()
                                }
                                
                                Button {
                                    text: "🎯"
                                    onClicked: performRAGSearch()
                                }
                            }
                            
                            // Search modes
                            Row {
                                spacing: 8
                                
                                ButtonGroup {
                                    id: searchModeGroup
                                }
                                
                                RadioButton {
                                    text: "All"
                                    checked: true
                                    ButtonGroup.group: searchModeGroup
                                }
                                RadioButton {
                                    text: "Code"
                                    ButtonGroup.group: searchModeGroup
                                }
                                RadioButton {
                                    text: "Docs"
                                    ButtonGroup.group: searchModeGroup
                                }
                            }
                            
                            // Results
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                ListView {
                                    model: searchResultsModel
                                    spacing: 4
                                    
                                    delegate: Rectangle {
                                        width: ListView.view.width
                                        height: 80
                                        color: "#333333"
                                        radius: 4
                                        
                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 8
                                            
                                            Text {
                                                text: model.title || "Result"
                                                color: "#ffffff"
                                                font.bold: true
                                            }
                                            
                                            Text {
                                                text: model.content || ""
                                                color: "#cccccc"
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                                maximumLineCount: 2
                                                elide: Text.ElideRight
                                            }
                                            
                                            Text {
                                                text: `Score: ${(model.score || 0).toFixed(3)} | Source: ${model.source || "unknown"}`
                                                color: "#888888"
                                                font.pixelSize: 9
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Inspector
                    GroupBox {
                        title: "🔧 Inspector"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        ScrollView {
                            anchors.fill: parent
                            
                            ColumnLayout {
                                width: parent.width - 20
                                spacing: 10
                                
                                Text {
                                    text: "System Status"
                                    color: "#ffffff"
                                    font.bold: true
                                }
                                
                                Text {
                                    text: servicesConnected ? "✅ All services connected" : "⚠️ Some services offline"
                                    color: servicesConnected ? "#4CAF50" : "#FF9800"
                                }
                                
                                Text {
                                    text: "Advanced Features"
                                    color: "#ffffff"
                                    font.bold: true
                                }
                                
                                Text {
                                    text: "• Hybrid Vector Search\n• Fuzzy Text Matching\n• Neural Graph Memory\n• Voice Activation\n• RAG Generation\n• AI Pilot Orchestration"
                                    color: "#cccccc"
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Tab bar for different views
        TabBar {
            id: tabBar
            width: parent.width
            
            TabButton {
                text: "🎨 Canvas"
            }
            TabButton {
                text: "💬 Chat"
            }
            TabButton {
                text: "📊 Analytics"
            }
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 25
            color: "#2d2d2d"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                
                Text {
                    text: "🟢 Ready"
                    color: "#4CAF50"
                    font.pixelSize: 10
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: "HAASP v2.0.0 Advanced"
                    color: "#666666"
                    font.pixelSize: 9
                }
            }
        }
    }
    
    // Data models
    ListModel {
        id: pilotsModel
        
        Component.onCompleted: {
            append({"id": "sentinel", "name": "Sentinel", "status": "ready", "active": true})
            append({"id": "doc_architect", "name": "Doc Architect", "status": "ready", "active": true})
            append({"id": "remediator", "name": "Remediator", "status": "ready", "active": true})
            append({"id": "codewright", "name": "Codewright", "status": "ready", "active": true})
        }
    }
    
    ListModel {
        id: searchResultsModel
    }
    
    ListModel {
        id: chatModel
        
        Component.onCompleted: {
            append({
                "sender": "assistant",
                "message": "Hello! I'm HAASP, your advanced AI development assistant. I have access to:\n\n🧠 Hybrid retrieval (vector + fuzzy + graph search)\n🤖 AI pilots for specialized tasks\n🎤 Voice activation\n📊 Advanced analytics\n\nHow can I help you today?",
                "timestamp": new Date().toISOString()
            })
        }
    }
    
    // Functions
    function initializeAdvancedFeatures() {
        console.log("🔧 Initializing advanced features...")
        
        // Test service connections
        testServiceConnections()
        
        // Initialize voice if enabled
        if (voiceEnabled) {
            initializeVoice()
        }
    }
    
    function testServiceConnections() {
        console.log("🔗 Testing service connections...")
        
        // Test retrieval service
        var xhr = new XMLHttpRequest()
        xhr.open("GET", "http://127.0.0.1:8000/")
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    servicesConnected = true
                    console.log("✅ Retrieval service connected")
                } else {
                    console.log("❌ Retrieval service not available")
                }
            }
        }
        xhr.send()
    }
    
    function loadRepository() {
        console.log("📁 Loading repository...")
        // Simulate repository loading
        currentProject = {
            "name": "AppiT-Pro",
            "path": "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"
        }
        console.log("✅ Repository loaded:", currentProject.name)
    }
    
    function performSearch() {
        var query = searchField.text.trim()
        if (!query) return
        
        console.log("🔍 Performing search:", query)
        
        // Add mock results for demonstration
        searchResultsModel.clear()
        
        searchResultsModel.append({
            "title": `Search result for: ${query}`,
            "content": "This is a mock search result. The real hybrid search will return semantic, fuzzy, and graph-based results.",
            "source": "search_system",
            "score": 0.95
        })
        
        searchResultsModel.append({
            "title": "Related Documentation",
            "content": "Found related documentation and code examples through vector similarity search.",
            "source": "documentation.md",
            "score": 0.87
        })
        
        searchResultsModel.append({
            "title": "Graph Memory Match",
            "content": "Neural graph memory found related concepts and dependencies.",
            "source": "graph_memory",
            "score": 0.82
        })
    }
    
    function performRAGSearch() {
        var query = searchField.text.trim()
        if (!query) return
        
        console.log("🎯 Performing RAG query:", query)
        
        // Add to chat
        chatModel.append({
            "sender": "user", 
            "message": query,
            "timestamp": new Date().toISOString()
        })
        
        // Simulate AI response
        setTimeout(function() {
            chatModel.append({
                "sender": "assistant",
                "message": `I understand you're asking about: "${query}"\n\nBased on my hybrid retrieval system, I found relevant information from multiple sources. The RAG system will provide a comprehensive response combining:\n\n🔍 Vector search results\n📝 Fuzzy text matches\n🧠 Graph memory connections\n🎯 Generated insights\n\nThis is a demonstration of the full RAG capabilities.`,
                "timestamp": new Date().toISOString()
            })
        }, 1500)
    }
    
    function sendChatMessage() {
        var message = chatInput.text.trim()
        if (!message) return
        
        chatModel.append({
            "sender": "user",
            "message": message, 
            "timestamp": new Date().toISOString()
        })
        
        chatInput.clear()
        
        // Process through RAG system
        setTimeout(function() {
            chatModel.append({
                "sender": "assistant",
                "message": `Processing your request: "${message}"\n\nI'm analyzing this through my AI pilots and retrieval systems...`,
                "timestamp": new Date().toISOString()
            })
        }, 500)
    }
    
    function runPilots() {
        console.log("▶️ Running AI pilot chain...")
        
        // Update pilot statuses
        for (var i = 0; i < pilotsModel.count; i++) {
            if (pilotsModel.get(i).active) {
                pilotsModel.setProperty(i, "status", "processing")
            }
        }
        
        // Simulate pilot execution
        setTimeout(function() {
            for (var i = 0; i < pilotsModel.count; i++) {
                if (pilotsModel.get(i).active) {
                    pilotsModel.setProperty(i, "status", "completed")
                }
            }
            console.log("✅ Pilot chain execution completed")
        }, 3000)
    }
    
    function stopPilots() {
        console.log("⏹️ Stopping pilots...")
        
        for (var i = 0; i < pilotsModel.count; i++) {
            pilotsModel.setProperty(i, "status", "idle")
        }
    }
    
    function togglePilot(pilotId, active) {
        console.log(`🔄 Toggle pilot ${pilotId}: ${active}`)
        
        for (var i = 0; i < pilotsModel.count; i++) {
            if (pilotsModel.get(i).id === pilotId) {
                pilotsModel.setProperty(i, "active", active)
                break
            }
        }
    }
    
    function showSettings() {
        console.log("⚙️ Opening settings...")
        // TODO: Implement settings dialog
    }
    
    function initializeVoice() {
        console.log("🎤 Initializing voice activation...")
        // TODO: Connect to voice service
    }
    
    function startVoiceInput() {
        console.log("🎤 Starting voice input...")
        // TODO: Trigger voice capture
    }

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

    ColumnLayout {
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