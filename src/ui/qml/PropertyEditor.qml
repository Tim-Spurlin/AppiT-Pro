import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3 as Dialogs
import org.kde.kirigami 2.20 as Kirigami

/**
 * PropertyEditor - Collapsible group of property editors
 * 
 * Supports multiple input types:
 * - number: Numeric input with optional suffix
 * - slider: Slider with min/max/step
 * - boolean: Checkbox
 * - color: Color picker
 * - string: Text input
 * - choice: ComboBox with options
 * - url: File picker
 */
Rectangle {
    id: root
    
    // Properties
    property string title: "Properties"
    property bool expanded: false
    property var properties: []
    
    // Signals
    signal propertyChanged(string property, var value)
    
    // Styling
    color: "transparent"
    border.color: Kirigami.Theme.separatorColor
    border.width: 1
    radius: 4
    
    height: expanded ? header.height + content.height + 8 : header.height
    
    Behavior on height {
        NumberAnimation {
            duration: 200
            easing.type: Easing.OutCubic
        }
    }
    
    // Header
    Rectangle {
        id: header
        width: parent.width
        height: 32
        color: Kirigami.Theme.alternateBackgroundColor
        radius: parent.radius
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 6
            
            Kirigami.Icon {
                source: root.expanded ? "arrow-down" : "arrow-right"
                width: 12
                height: 12
                
                Behavior on rotation {
                    NumberAnimation {
                        duration: 150
                    }
                }
            }
            
            QQC2.Label {
                text: root.title
                font.weight: Font.DemiBold
                font.pointSize: 10
                Layout.fillWidth: true
            }
            
            QQC2.Label {
                text: root.properties.length
                font.pointSize: 9
                color: Kirigami.Theme.disabledTextColor
                visible: !root.expanded
            }
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: root.expanded = !root.expanded
            cursorShape: Qt.PointingHandCursor
        }
    }
    
    // Content
    Column {
        id: content
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 4
        spacing: 6
        visible: root.expanded
        opacity: root.expanded ? 1.0 : 0.0
        
        Behavior on opacity {
            NumberAnimation {
                duration: 200
            }
        }
        
        Repeater {
            model: root.properties
            
            delegate: Loader {
                width: content.width
                
                property var propData: modelData
                
                sourceComponent: {
                    switch (propData.type) {
                        case "number": return numberEditor
                        case "slider": return sliderEditor
                        case "boolean": return booleanEditor
                        case "color": return colorEditor
                        case "string": return stringEditor
                        case "choice": return choiceEditor
                        case "url": return urlEditor
                        default: return stringEditor
                    }
                }
            }
        }
    }
    
    // Editor Components
    Component {
        id: numberEditor
        
        RowLayout {
            spacing: 8
            
            QQC2.Label {
                text: propData.name
                Layout.preferredWidth: 80
                Layout.alignment: Qt.AlignTop
                font.pointSize: 9
                elide: Text.ElideRight
            }
            
            QQC2.SpinBox {
                Layout.fillWidth: true
                value: propData.value || 0
                from: propData.min !== undefined ? propData.min : -999999
                to: propData.max !== undefined ? propData.max : 999999
                stepSize: propData.step || 1
                
                // Handle decimal values
                property real factor: propData.step === 0.1 ? 10 : 1
                
                validator: DoubleValidator {
                    bottom: Math.min(from, to)
                    top: Math.max(from, to)
                }
                
                textFromValue: function(value, locale) {
                    return Number(value / factor).toLocaleString(locale, 'f', factor === 10 ? 1 : 0)
                }
                
                valueFromText: function(text, locale) {
                    return Number.fromLocaleString(locale, text) * factor
                }
                
                onValueModified: {
                    root.propertyChanged(propData.name, value / factor)
                }
            }
            
            QQC2.Label {
                text: propData.suffix || ""
                font.pointSize: 8
                color: Kirigami.Theme.disabledTextColor
                visible: propData.suffix
            }
        }
    }
    
    Component {
        id: sliderEditor
        
        ColumnLayout {
            spacing: 4
            
            RowLayout {
                Layout.fillWidth: true
                
                QQC2.Label {
                    text: propData.name
                    font.pointSize: 9
                    Layout.fillWidth: true
                }
                
                QQC2.Label {
                    text: slider.value.toFixed(slider.stepSize < 1 ? 1 : 0) + (propData.suffix || "")
                    font.pointSize: 8
                    color: Kirigami.Theme.disabledTextColor
                }
            }
            
            QQC2.Slider {
                id: slider
                Layout.fillWidth: true
                from: propData.min || 0
                to: propData.max || 1
                stepSize: propData.step || 0.1
                value: propData.value || 0
                
                onMoved: {
                    root.propertyChanged(propData.name, value)
                }
            }
        }
    }
    
    Component {
        id: booleanEditor
        
        RowLayout {
            spacing: 8
            
            QQC2.CheckBox {
                id: checkbox
                text: propData.name
                checked: propData.value === true
                font.pointSize: 9
                
                onToggled: {
                    root.propertyChanged(propData.name, checked)
                }
            }
            
            Item { Layout.fillWidth: true }
        }
    }
    
    Component {
        id: colorEditor
        
        RowLayout {
            spacing: 8
            
            QQC2.Label {
                text: propData.name
                Layout.preferredWidth: 80
                font.pointSize: 9
                elide: Text.ElideRight
            }
            
            Rectangle {
                width: 24
                height: 24
                color: propData.value || "#ffffff"
                border.color: "#cccccc"
                border.width: 1
                radius: 2
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: colorDialog.open()
                    cursorShape: Qt.PointingHandCursor
                }
                
                Dialogs.ColorDialog {
                    id: colorDialog
                    title: "Choose " + propData.name
                    color: propData.value || "#ffffff"
                    
                    onAccepted: {
                        root.propertyChanged(propData.name, color)
                    }
                }
            }
            
            QQC2.TextField {
                Layout.fillWidth: true
                text: propData.value || "#ffffff"
                font.pointSize: 9
                font.family: "monospace"
                
                onEditingFinished: {
                    if (text.match(/^#[0-9A-Fa-f]{6}$/)) {
                        root.propertyChanged(propData.name, text)
                    }
                }
            }
        }
    }
    
    Component {
        id: stringEditor
        
        RowLayout {
            spacing: 8
            
            QQC2.Label {
                text: propData.name
                Layout.preferredWidth: 80
                Layout.alignment: Qt.AlignTop
                font.pointSize: 9
                elide: Text.ElideRight
            }
            
            QQC2.TextField {
                Layout.fillWidth: true
                text: propData.value || ""
                font.pointSize: 9
                
                onEditingFinished: {
                    root.propertyChanged(propData.name, text)
                }
            }
        }
    }
    
    Component {
        id: choiceEditor
        
        RowLayout {
            spacing: 8
            
            QQC2.Label {
                text: propData.name
                Layout.preferredWidth: 80
                font.pointSize: 9
                elide: Text.ElideRight
            }
            
            QQC2.ComboBox {
                Layout.fillWidth: true
                model: propData.options || []
                currentIndex: {
                    var idx = model.indexOf(propData.value)
                    return idx >= 0 ? idx : 0
                }
                font.pointSize: 9
                
                onActivated: {
                    root.propertyChanged(propData.name, currentText)
                }
            }
        }
    }
    
    Component {
        id: urlEditor
        
        RowLayout {
            spacing: 8
            
            QQC2.Label {
                text: propData.name
                Layout.preferredWidth: 80
                Layout.alignment: Qt.AlignTop
                font.pointSize: 9
                elide: Text.ElideRight
            }
            
            QQC2.TextField {
                id: urlField
                Layout.fillWidth: true
                text: propData.value || ""
                font.pointSize: 9
                placeholderText: "file:// or https://"
                
                onEditingFinished: {
                    root.propertyChanged(propData.name, text)
                }
            }
            
            QQC2.Button {
                text: "..."
                implicitWidth: 24
                font.pointSize: 8
                
                onClicked: fileDialog.open()
                
                Dialogs.FileDialog {
                    id: fileDialog
                    title: "Choose file for " + propData.name
                    folder: shortcuts.pictures
                    nameFilters: ["Image files (*.jpg *.png *.gif *.svg)", "All files (*)"]
                    
                    onAccepted: {
                        urlField.text = fileUrl
                        root.propertyChanged(propData.name, fileUrl)
                    }
                }
            }
        }
    }
}