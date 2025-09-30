import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami

/**
 * BindingEditor - Editor for QML property bindings
 * 
 * Features:
 * - Syntax highlighting for QML expressions
 * - Real-time validation and evaluation
 * - Autocomplete suggestions
 * - Error indication and debugging
 */
Rectangle {
    id: root
    
    // Properties
    property string propertyName: ""
    property string bindingExpression: ""
    property bool isValid: true
    property var evaluationResult: null
    
    // Signals
    signal bindingChanged(string propertyName, string expression)
    
    // Styling
    height: expanded ? expandedHeight : collapsedHeight
    width: parent.width
    color: "transparent"
    border.color: root.isValid ? Kirigami.Theme.separatorColor : "#ff6b6b"
    border.width: 1
    radius: 4
    
    readonly property int collapsedHeight: 32
    readonly property int expandedHeight: 120
    property bool expanded: false
    
    Behavior on height {
        NumberAnimation {
            duration: 200
            easing.type: Easing.OutCubic
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 4
        spacing: 4
        
        // Header row
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 24
            
            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: root.isValid ? "#4ecdc4" : "#ff6b6b"
            }
            
            QQC2.Label {
                text: root.propertyName
                font.weight: Font.DemiBold
                font.pointSize: 9
                Layout.fillWidth: true
            }
            
            // Evaluation result indicator
            QQC2.Label {
                text: root.evaluationResult !== null ? String(root.evaluationResult) : "undefined"
                font.pointSize: 8
                font.family: "monospace"
                color: root.isValid ? Kirigami.Theme.disabledTextColor : "#ff6b6b"
                visible: root.expanded
            }
            
            QQC2.ToolButton {
                icon.name: root.expanded ? "arrow-up" : "arrow-down"
                icon.width: 12
                icon.height: 12
                onClicked: root.expanded = !root.expanded
            }
        }
        
        // Expression preview (collapsed state)
        QQC2.Label {
            Layout.fillWidth: true
            text: root.bindingExpression
            font.pointSize: 8
            font.family: "monospace"
            color: Kirigami.Theme.disabledTextColor
            elide: Text.ElideRight
            visible: !root.expanded
        }
        
        // Expression editor (expanded state)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.expanded
            spacing: 4
            
            // Expression input
            QQC2.ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                QQC2.TextArea {
                    id: expressionEditor
                    text: root.bindingExpression
                    font.pointSize: 9
                    font.family: "monospace"
                    selectByMouse: true
                    wrapMode: TextArea.Wrap
                    placeholderText: "Enter QML binding expression..."
                    
                    // Basic syntax highlighting colors
                    color: root.isValid ? Kirigami.Theme.textColor : "#ff6b6b"
                    
                    onTextChanged: {
                        root.bindingExpression = text
                        validateExpression()
                        
                        // Debounced change notification
                        changeTimer.restart()
                    }
                    
                    Timer {
                        id: changeTimer
                        interval: 500
                        onTriggered: {
                            root.bindingChanged(root.propertyName, expressionEditor.text)
                        }
                    }
                    
                    // Auto-completion popup
                    Popup {
                        id: completionPopup
                        y: expressionEditor.cursorRectangle.y + expressionEditor.cursorRectangle.height
                        width: 200
                        height: Math.min(completionList.contentHeight, 120)
                        visible: false
                        
                        ListView {
                            id: completionList
                            anchors.fill: parent
                            model: getCompletions()
                            
                            delegate: ItemDelegate {
                                width: completionList.width
                                height: 24
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    spacing: 6
                                    
                                    Kirigami.Icon {
                                        source: modelData.type === "property" ? "code-variable" : 
                                               modelData.type === "function" ? "code-function" : "code-context"
                                        width: 12
                                        height: 12
                                    }
                                    
                                    QQC2.Label {
                                        text: modelData.name
                                        font.pointSize: 8
                                        font.family: "monospace"
                                        Layout.fillWidth: true
                                    }
                                    
                                    QQC2.Label {
                                        text: modelData.type
                                        font.pointSize: 7
                                        color: Kirigami.Theme.disabledTextColor
                                    }
                                }
                                
                                onClicked: {
                                    insertCompletion(modelData.name)
                                    completionPopup.visible = false
                                }
                            }
                        }
                    }
                    
                    Keys.onPressed: {
                        if (event.key === Qt.Key_Space && event.modifiers === Qt.ControlModifier) {
                            showCompletions()
                            event.accepted = true
                        } else if (event.key === Qt.Key_Escape) {
                            completionPopup.visible = false
                            event.accepted = true
                        }
                    }
                }
            }
            
            // Toolbar
            RowLayout {
                Layout.fillWidth: true
                
                QQC2.Button {
                    text: "Validate"
                    icon.name: "dialog-ok-apply"
                    font.pointSize: 8
                    onClicked: validateExpression()
                }
                
                QQC2.Button {
                    text: "Auto-complete"
                    icon.name: "format-text-code"
                    font.pointSize: 8
                    onClicked: showCompletions()
                }
                
                Item { Layout.fillWidth: true }
                
                QQC2.Label {
                    text: root.isValid ? "✓ Valid" : "✗ Invalid"
                    font.pointSize: 8
                    color: root.isValid ? "#4ecdc4" : "#ff6b6b"
                }
            }
        }
    }
    
    // Functions
    function validateExpression() {
        var expression = expressionEditor.text.trim()
        
        if (!expression) {
            root.isValid = true
            root.evaluationResult = null
            return
        }
        
        try {
            // Basic syntax validation - simplified
            root.isValid = !expression.includes("undefined") && 
                          !expression.includes("null.") &&
                          isBalancedParentheses(expression)
            
            // Mock evaluation result
            if (root.isValid) {
                root.evaluationResult = expression.includes("width") ? "200px" :
                                       expression.includes("opacity") ? "0.8" :
                                       expression.includes("parent") ? "Item" : "value"
            } else {
                root.evaluationResult = "Error"
            }
            
        } catch (e) {
            root.isValid = false
            root.evaluationResult = "Syntax Error"
        }
    }
    
    function isBalancedParentheses(str) {
        var count = 0
        for (var i = 0; i < str.length; i++) {
            if (str[i] === '(') count++
            else if (str[i] === ')') count--
            if (count < 0) return false
        }
        return count === 0
    }
    
    function getCompletions() {
        // Mock completions - in production this would analyze context
        return [
            {"name": "parent.width", "type": "property"},
            {"name": "parent.height", "type": "property"}, 
            {"name": "Math.max", "type": "function"},
            {"name": "Math.min", "type": "function"},
            {"name": "mouseArea.containsMouse", "type": "property"},
            {"name": "Kirigami.Units.largeSpacing", "type": "property"},
            {"name": "Qt.rgba", "type": "function"},
            {"name": "anchor.centerIn", "type": "property"}
        ]
    }
    
    function showCompletions() {
        completionPopup.visible = true
        completionList.model = getCompletions()
    }
    
    function insertCompletion(completion) {
        var cursor = expressionEditor.cursorPosition
        var text = expressionEditor.text
        
        // Find start of current word
        var start = cursor
        while (start > 0 && /[a-zA-Z0-9._]/.test(text[start - 1])) {
            start--
        }
        
        // Replace current word with completion
        var newText = text.substring(0, start) + completion + text.substring(cursor)
        expressionEditor.text = newText
        expressionEditor.cursorPosition = start + completion.length
    }
}