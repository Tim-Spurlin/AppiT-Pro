import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami

/**
 * Inspector - Property editor for selected QML elements
 * 
 * Features:
 * - Real-time property editing with live preview
 * - Type-specific editors (color picker, number input, etc.)
 * - Binding inspector with expression evaluation
 * - Undo/redo integration
 * - Performance optimized with caching
 */
QQC2.ScrollView {
    id: root
    
    // Signals
    signal propertyChanged(string elementId, string property, var value)
    signal bindingChanged(string elementId, string property, string binding)
    
    // Properties
    property string currentElementId: ""
    property var currentElement: null
    property var elementProperties: ({})
    property var elementBindings: ({})
    
    // Performance optimization
    readonly property bool __cachingEnabled: true
    
    Column {
        width: root.width
        spacing: Kirigami.Units.smallSpacing
        
        // Element info header
        Rectangle {
            width: parent.width
            height: 60
            color: Kirigami.Theme.backgroundColor
            border.color: Kirigami.Theme.separatorColor
            border.width: 1
            radius: 4
            visible: root.currentElementId !== ""
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.smallSpacing
                spacing: Kirigami.Units.smallSpacing
                
                Kirigami.Icon {
                    source: "zoom-select-fit"
                    width: 24
                    height: 24
                }
                
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    
                    QQC2.Label {
                        text: root.currentElementId || "No selection"
                        font.weight: Font.Bold
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                    
                    QQC2.Label {
                        text: root.currentElement ? root.currentElement.toString().split('_')[0] : ""
                        font.pointSize: 9
                        color: Kirigami.Theme.disabledTextColor
                        Layout.fillWidth: true
                    }
                }
                
                QQC2.ToolButton {
                    icon.name: "view-refresh"
                    onClicked: refreshProperties()
                }
            }
        }
        
        // No selection state
        Rectangle {
            width: parent.width
            height: 120
            color: "#f5f5f5"
            border.color: "#cccccc"
            border.width: 1
            radius: 4
            visible: root.currentElementId === ""
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: Kirigami.Units.largeSpacing
                
                Kirigami.Icon {
                    source: "select-rectangular"
                    width: 48
                    height: 48
                    Layout.alignment: Qt.AlignHCenter
                    opacity: 0.6
                }
                
                QQC2.Label {
                    text: "Select an element to inspect its properties"
                    color: "#666666"
                    font.pointSize: 10
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Properties section
        Kirigami.Card {
            width: parent.width
            visible: root.currentElementId !== ""
            
            ColumnLayout {
                width: parent.width
                spacing: Kirigami.Units.smallSpacing
                
                Kirigami.Heading {
                    text: "Properties"
                    level: 4
                }
                
                Kirigami.Separator {
                    Layout.fillWidth: true
                }
                
                // Common properties
                PropertyEditor {
                    id: positionGroup
                    Layout.fillWidth: true
                    title: "Position & Size"
                    expanded: true
                    
                    properties: [
                        {"name": "x", "type": "number", "value": root.elementProperties.x || 0, "suffix": "px"},
                        {"name": "y", "type": "number", "value": root.elementProperties.y || 0, "suffix": "px"},
                        {"name": "width", "type": "number", "value": root.elementProperties.width || 100, "suffix": "px"},
                        {"name": "height", "type": "number", "value": root.elementProperties.height || 100, "suffix": "px"}
                    ]
                    
                    onPropertyChanged: root.propertyChanged(root.currentElementId, property, value)
                }
                
                PropertyEditor {
                    id: appearanceGroup
                    Layout.fillWidth: true
                    title: "Appearance"
                    expanded: false
                    
                    properties: [
                        {"name": "opacity", "type": "slider", "value": root.elementProperties.opacity || 1.0, "min": 0, "max": 1, "step": 0.1},
                        {"name": "rotation", "type": "slider", "value": root.elementProperties.rotation || 0, "min": -180, "max": 180, "suffix": "°"},
                        {"name": "scale", "type": "slider", "value": root.elementProperties.scale || 1.0, "min": 0.1, "max": 3.0, "step": 0.1},
                        {"name": "visible", "type": "boolean", "value": root.elementProperties.visible !== false}
                    ]
                    
                    onPropertyChanged: root.propertyChanged(root.currentElementId, property, value)
                }
                
                // Type-specific properties
                PropertyEditor {
                    id: typeSpecificGroup
                    Layout.fillWidth: true
                    title: getElementTypeName()
                    expanded: false
                    visible: getTypeSpecificProperties().length > 0
                    
                    properties: getTypeSpecificProperties()
                    
                    onPropertyChanged: root.propertyChanged(root.currentElementId, property, value)
                }
            }
        }
        
        // Bindings section
        Kirigami.Card {
            width: parent.width
            visible: root.currentElementId !== "" && Object.keys(root.elementBindings).length > 0
            
            ColumnLayout {
                width: parent.width
                spacing: Kirigami.Units.smallSpacing
                
                Kirigami.Heading {
                    text: "Bindings"
                    level: 4
                }
                
                Kirigami.Separator {
                    Layout.fillWidth: true
                }
                
                Repeater {
                    model: Object.keys(root.elementBindings)
                    
                    delegate: BindingEditor {
                        Layout.fillWidth: true
                        propertyName: modelData
                        bindingExpression: root.elementBindings[modelData]
                        
                        onBindingChanged: {
                            root.bindingChanged(root.currentElementId, propertyName, expression)
                        }
                    }
                }
            }
        }
        
        // AI Suggestions section
        Kirigami.Card {
            width: parent.width
            visible: root.currentElementId !== ""
            
            ColumnLayout {
                width: parent.width
                spacing: Kirigami.Units.smallSpacing
                
                RowLayout {
                    Layout.fillWidth: true
                    
                    Kirigami.Heading {
                        text: "AI Suggestions"
                        level: 4
                        Layout.fillWidth: true
                    }
                    
                    QQC2.BusyIndicator {
                        visible: suggestionsLoader.active
                        running: visible
                        implicitWidth: 16
                        implicitHeight: 16
                    }
                }
                
                Kirigami.Separator {
                    Layout.fillWidth: true
                }
                
                // ML-generated suggestions
                Loader {
                    id: suggestionsLoader
                    Layout.fillWidth: true
                    active: false
                    
                    sourceComponent: Column {
                        spacing: 4
                        
                        Repeater {
                            model: getSuggestions()
                            
                            delegate: Rectangle {
                                width: parent.width
                                height: suggestionText.height + 8
                                color: "#e3f2fd"
                                border.color: "#2196f3"
                                border.width: 1
                                radius: 3
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    spacing: 6
                                    
                                    Kirigami.Icon {
                                        source: "lightbulb"
                                        width: 16
                                        height: 16
                                        color: "#2196f3"
                                    }
                                    
                                    QQC2.Label {
                                        id: suggestionText
                                        text: modelData.text
                                        font.pointSize: 9
                                        Layout.fillWidth: true
                                        wrapMode: Text.Wrap
                                    }
                                    
                                    QQC2.Button {
                                        text: "Apply"
                                        font.pointSize: 8
                                        onClicked: applySuggestion(modelData)
                                    }
                                }
                            }
                        }
                    }
                }
                
                QQC2.Button {
                    text: "Get Suggestions"
                    icon.name: "view-refresh"
                    Layout.fillWidth: true
                    enabled: !suggestionsLoader.active
                    
                    onClicked: {
                        suggestionsLoader.active = true
                        // Request AI suggestions from AssociativeNexus
                        // This would call the C++ backend
                    }
                }
            }
        }
    }
    
    // Functions
    function loadElement(elementId) {
        console.log("Loading element for inspection:", elementId)
        root.currentElementId = elementId
        
        // This would normally query the C++ backend for element data
        // For now, using mock data
        root.elementProperties = {
            x: 50,
            y: 30,
            width: 200,
            height: 100,
            opacity: 1.0,
            rotation: 0,
            scale: 1.0,
            visible: true,
            text: "Sample Text",
            color: "#000000"
        }
        
        root.elementBindings = {
            width: "parent.width * 0.5",
            opacity: "mouseArea.containsMouse ? 1.0 : 0.7"
        }
    }
    
    function refreshProperties() {
        if (root.currentElementId) {
            loadElement(root.currentElementId)
        }
    }
    
    function getElementTypeName() {
        if (!root.currentElement) return "Element"
        
        var typeName = root.currentElement.toString()
        if (typeName.includes("Rectangle")) return "Rectangle"
        if (typeName.includes("Text")) return "Text"
        if (typeName.includes("Button")) return "Button"
        if (typeName.includes("Image")) return "Image"
        return "Element"
    }
    
    function getTypeSpecificProperties() {
        var typeName = getElementTypeName()
        
        switch (typeName) {
            case "Rectangle":
                return [
                    {"name": "color", "type": "color", "value": root.elementProperties.color || "#ffffff"},
                    {"name": "border.width", "type": "number", "value": root.elementProperties["border.width"] || 0, "suffix": "px"},
                    {"name": "border.color", "type": "color", "value": root.elementProperties["border.color"] || "#000000"},
                    {"name": "radius", "type": "number", "value": root.elementProperties.radius || 0, "suffix": "px"}
                ]
            case "Text":
                return [
                    {"name": "text", "type": "string", "value": root.elementProperties.text || ""},
                    {"name": "color", "type": "color", "value": root.elementProperties.color || "#000000"},
                    {"name": "font.pointSize", "type": "number", "value": root.elementProperties["font.pointSize"] || 12, "suffix": "pt"},
                    {"name": "font.weight", "type": "choice", "value": root.elementProperties["font.weight"] || "Normal", "options": ["Light", "Normal", "DemiBold", "Bold"]}
                ]
            case "Button":
                return [
                    {"name": "text", "type": "string", "value": root.elementProperties.text || ""},
                    {"name": "enabled", "type": "boolean", "value": root.elementProperties.enabled !== false},
                    {"name": "flat", "type": "boolean", "value": root.elementProperties.flat === true}
                ]
            case "Image":
                return [
                    {"name": "source", "type": "url", "value": root.elementProperties.source || ""},
                    {"name": "fillMode", "type": "choice", "value": root.elementProperties.fillMode || "Stretch", "options": ["Stretch", "PreserveAspectFit", "PreserveAspectCrop", "Tile"]},
                    {"name": "asynchronous", "type": "boolean", "value": root.elementProperties.asynchronous === true}
                ]
            default:
                return []
        }
    }
    
    function getSuggestions() {
        // Mock AI suggestions - in production this would come from ML models
        return [
            {"text": "Consider using anchors instead of fixed positioning for responsive design", "type": "layout"},
            {"text": "Add hover effects to improve user interaction", "type": "ux"},
            {"text": "This element could benefit from animation transitions", "type": "animation"}
        ]
    }
    
    function applySuggestion(suggestion) {
        console.log("Applying suggestion:", suggestion.text)
        // Implementation would depend on suggestion type
    }
}