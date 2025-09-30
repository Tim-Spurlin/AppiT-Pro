import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami

/**
 * TreeItem - Individual item in the hierarchy tree
 * 
 * Features:
 * - Indentation based on depth
 * - Expand/collapse for parent items
 * - Selection highlighting
 * - Visibility toggle
 * - Drag & drop support
 * - Search result highlighting
 */
Rectangle {
    id: root
    
    // Properties
    property var elementData: ({})
    property string searchText: ""
    property bool isSelected: false
    
    // Signals
    signal elementClicked(string elementId)
    signal expandToggled(string elementId)
    signal visibilityToggled(string elementId, bool visible)
    signal contextMenuRequested(real x, real y)
    
    // Styling
    height: 28
    width: parent.width
    color: root.isSelected ? Kirigami.Theme.highlightColor : 
           mouseArea.containsMouse ? Kirigami.Theme.hoverColor : "transparent"
    
    // Hover and selection effects
    Behavior on color {
        ColorAnimation { duration: 100 }
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: (elementData.depth || 0) * 16 + 8
        anchors.rightMargin: 8
        spacing: 4
        
        // Expand/collapse button
        QQC2.Button {
            Layout.preferredWidth: 16
            Layout.preferredHeight: 16
            flat: true
            
            visible: elementData.children && elementData.children.length > 0
            
            background: Rectangle {
                color: "transparent"
                radius: 2
                border.color: parent.hovered ? Kirigami.Theme.highlightColor : "transparent"
                border.width: 1
            }
            
            contentItem: Kirigami.Icon {
                source: elementData.expanded ? "arrow-down" : "arrow-right"
                width: 10
                height: 10
                color: Kirigami.Theme.textColor
            }
            
            onClicked: {
                root.expandToggled(elementData.id)
            }
        }
        
        // Spacer for non-expandable items
        Item {
            Layout.preferredWidth: 16
            Layout.preferredHeight: 16
            visible: !(elementData.children && elementData.children.length > 0)
        }
        
        // Element type icon
        Kirigami.Icon {
            Layout.preferredWidth: 16
            Layout.preferredHeight: 16
            source: getElementIcon()
            color: elementData.visible ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor
            opacity: elementData.visible ? 1.0 : 0.5
        }
        
        // Element name with search highlighting
        QQC2.Label {
            id: nameLabel
            Layout.fillWidth: true
            text: getHighlightedName()
            font.pointSize: 9
            color: elementData.visible ? 
                   (root.isSelected ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor) :
                   Kirigami.Theme.disabledTextColor
            elide: Text.ElideRight
            
            textFormat: root.searchText ? Text.RichText : Text.PlainText
        }
        
        // Element type badge
        Rectangle {
            Layout.preferredWidth: typeLabel.implicitWidth + 8
            Layout.preferredHeight: 16
            color: getTypeBadgeColor()
            radius: 8
            visible: elementData.type
            
            QQC2.Label {
                id: typeLabel
                anchors.centerIn: parent
                text: elementData.type || ""
                font.pointSize: 7
                font.weight: Font.DemiBold
                color: "#ffffff"
            }
        }
        
        // Visibility toggle
        QQC2.Button {
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            flat: true
            
            background: Rectangle {
                color: "transparent"
                radius: 2
            }
            
            contentItem: Kirigami.Icon {
                source: elementData.visible ? "view-visible" : "view-hidden"
                width: 12
                height: 12
                color: elementData.visible ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor
            }
            
            onClicked: {
                root.visibilityToggled(elementData.id, !elementData.visible)
            }
            
            QQC2.ToolTip.text: elementData.visible ? "Hide element" : "Show element"
            QQC2.ToolTip.visible: hovered
        }
    }
    
    // Mouse interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        
        onClicked: {
            if (mouse.button === Qt.LeftButton) {
                root.elementClicked(elementData.id)
            } else if (mouse.button === Qt.RightButton) {
                root.contextMenuRequested(mouse.x, mouse.y)
            }
        }
        
        onDoubleClicked: {
            if (elementData.children && elementData.children.length > 0) {
                root.expandToggled(elementData.id)
            }
        }
    }
    
    // Drag & drop support
    Drag.active: dragArea.drag.active
    Drag.hotSpot.x: width / 2
    Drag.hotSpot.y: height / 2
    Drag.mimeData: { "text/plain": elementData.id }
    
    MouseArea {
        id: dragArea
        anchors.fill: parent
        drag.target: root
        
        onPressed: {
            root.z = 1000  // Bring to front
        }
        
        onReleased: {
            root.z = 0
            // Handle drop logic here
        }
    }
    
    // Drop area for reordering
    DropArea {
        anchors.fill: parent
        
        onEntered: {
            // Visual feedback for drop target
            dropIndicator.visible = true
        }
        
        onExited: {
            dropIndicator.visible = false
        }
        
        onDropped: {
            dropIndicator.visible = false
            
            if (drop.hasText) {
                var draggedId = drop.text
                // Handle reordering logic
                console.log("Drop", draggedId, "onto", elementData.id)
            }
        }
    }
    
    // Drop indicator
    Rectangle {
        id: dropIndicator
        anchors.fill: parent
        color: Kirigami.Theme.highlightColor
        opacity: 0.2
        visible: false
        radius: 2
        
        border.color: Kirigami.Theme.highlightColor
        border.width: 2
    }
    
    // Functions
    function getElementIcon() {
        switch (elementData.type) {
            case "ApplicationWindow":
            case "Window": return "window"
            case "Page": return "view-pages"
            case "Rectangle": return "draw-rectangle"
            case "Text": return "draw-text"
            case "Button": return "games-config-board"
            case "TextField": return "edit-entry"
            case "ListView": return "view-list-details"
            case "ColumnLayout":
            case "RowLayout": return "view-split-top-bottom"
            case "GridLayout": return "view-grid"
            case "Image": return "image-x-generic"
            case "ScrollView": return "view-fullscreen"
            case "TabView": return "view-file-columns"
            default: return "code-context"
        }
    }
    
    function getTypeBadgeColor() {
        switch (elementData.type) {
            case "ApplicationWindow":
            case "Window":
            case "Page": return "#9c27b0"  // Purple for containers
            case "Rectangle": return "#2196f3"  // Blue for shapes
            case "Text": return "#4caf50"  // Green for text
            case "Button": return "#ff9800"  // Orange for controls
            case "TextField": return "#ff5722"  // Red for inputs
            case "ListView": return "#795548"  // Brown for lists
            case "ColumnLayout":
            case "RowLayout": 
            case "GridLayout": return "#607d8b"  // Blue-grey for layouts
            case "Image": return "#e91e63"  // Pink for media
            default: return "#757575"  // Grey for others
        }
    }
    
    function getHighlightedName() {
        if (!root.searchText) {
            return elementData.name || "Unnamed"
        }
        
        var name = elementData.name || "Unnamed"
        var search = root.searchText.toLowerCase()
        var lowerName = name.toLowerCase()
        
        if (!lowerName.includes(search)) {
            return name
        }
        
        // Simple highlighting - replace with proper HTML escaping in production
        var regex = new RegExp("(" + search + ")", "gi")
        return name.replace(regex, '<span style="background-color: #ffeb3b; color: #000000;">$1</span>')
    }
}