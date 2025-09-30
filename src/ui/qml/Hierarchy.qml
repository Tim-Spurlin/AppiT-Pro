import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.20 as Kirigami

/**
 * Hierarchy - Tree view of QML component hierarchy
 * 
 * Features:
 * - Collapsible tree structure
 * - Drag & drop reordering  
 * - Search and filtering
 * - Element visibility toggle
 * - Context menu actions
 */
QQC2.ScrollView {
    id: root
    
    // Signals
    signal elementSelected(string elementId)
    signal elementRenamed(string elementId, string newName)
    signal elementDeleted(string elementId)
    signal elementMoved(string elementId, string newParentId, int index)
    signal visibilityToggled(string elementId, bool visible)
    
    // Properties
    property string selectedElementId: ""
    property bool searchMode: false
    property string searchText: ""
    
    // Tree model (simplified - in production would come from C++)
    property var treeModel: [
        {
            "id": "root",
            "name": "Main",
            "type": "ApplicationWindow",
            "visible": true,
            "expanded": true,
            "children": [
                {
                    "id": "page1", 
                    "name": "Page",
                    "type": "Page",
                    "visible": true,
                    "expanded": true,
                    "children": [
                        {
                            "id": "rect1",
                            "name": "Container",
                            "type": "Rectangle", 
                            "visible": true,
                            "expanded": false,
                            "children": [
                                {"id": "text1", "name": "Title", "type": "Text", "visible": true, "children": []},
                                {"id": "button1", "name": "Action Button", "type": "Button", "visible": true, "children": []}
                            ]
                        },
                        {
                            "id": "column1",
                            "name": "Layout",
                            "type": "ColumnLayout",
                            "visible": true,
                            "expanded": false,
                            "children": [
                                {"id": "input1", "name": "Input Field", "type": "TextField", "visible": true, "children": []},
                                {"id": "list1", "name": "Data List", "type": "ListView", "visible": true, "children": []}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    
    ColumnLayout {
        width: root.width
        spacing: 0
        
        // Search bar
        Rectangle {
            Layout.fillWidth: true
            height: searchMode ? 36 : 0
            color: Kirigami.Theme.backgroundColor
            border.color: Kirigami.Theme.separatorColor  
            border.width: searchMode ? 1 : 0
            visible: searchMode
            
            Behavior on height {
                NumberAnimation { duration: 200 }
            }
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4
                
                Kirigami.SearchField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Search elements..."
                    text: root.searchText
                    
                    onTextChanged: {
                        root.searchText = text
                        filterTree()
                    }
                    
                    onAccepted: {
                        if (text.length > 0) {
                            selectFirstMatch()
                        }
                    }
                }
                
                QQC2.ToolButton {
                    icon.name: "window-close"
                    onClicked: {
                        root.searchMode = false
                        root.searchText = ""
                        filterTree()
                    }
                }
            }
        }
        
        // Tree view
        ListView {
            id: treeView
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            model: flattenTree(root.treeModel)
            
            // Custom delegate for tree items
            delegate: TreeItem {
                width: treeView.width
                elementData: modelData
                searchText: root.searchText
                isSelected: modelData.id === root.selectedElementId
                
                onElementClicked: {
                    root.selectedElementId = elementId
                    root.elementSelected(elementId)
                }
                
                onExpandToggled: {
                    toggleExpanded(elementId)
                }
                
                onVisibilityToggled: {
                    root.visibilityToggled(elementId, visible)
                    updateElementVisibility(elementId, visible)
                }
                
                onContextMenuRequested: {
                    contextMenu.elementId = elementId
                    contextMenu.x = x
                    contextMenu.y = y + height
                    contextMenu.open()
                }
            }
        }
        
        // Empty state
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#f5f5f5"
            visible: treeView.count === 0
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: Kirigami.Units.largeSpacing
                
                Kirigami.Icon {
                    source: "view-list-tree"
                    width: 48
                    height: 48
                    Layout.alignment: Qt.AlignHCenter
                    opacity: 0.6
                }
                
                QQC2.Label {
                    text: "No elements found"
                    color: "#666666"
                    font.pointSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
                
                QQC2.Label {
                    text: root.searchMode ? "Try a different search term" : "Add elements to see the hierarchy"
                    color: "#999999"
                    font.pointSize: 10
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }
    
    // Context menu
    QQC2.Menu {
        id: contextMenu
        property string elementId: ""
        
        QQC2.MenuItem {
            text: "Rename"
            icon.name: "edit-rename"
            onClicked: renameDialog.open()
        }
        
        QQC2.MenuSeparator {}
        
        QQC2.MenuItem {
            text: "Duplicate"
            icon.name: "edit-copy"
            onClicked: duplicateElement(contextMenu.elementId)
        }
        
        QQC2.MenuItem {
            text: "Delete"
            icon.name: "edit-delete"
            onClicked: {
                deleteConfirmDialog.elementId = contextMenu.elementId
                deleteConfirmDialog.open()
            }
        }
        
        QQC2.MenuSeparator {}
        
        QQC2.Menu {
            title: "Add Child"
            icon.name: "list-add"
            
            QQC2.MenuItem {
                text: "Rectangle"
                onClicked: addChildElement(contextMenu.elementId, "Rectangle")
            }
            
            QQC2.MenuItem {
                text: "Text"
                onClicked: addChildElement(contextMenu.elementId, "Text")
            }
            
            QQC2.MenuItem {
                text: "Button"
                onClicked: addChildElement(contextMenu.elementId, "Button")
            }
            
            QQC2.MenuItem {
                text: "Layout"
                onClicked: addChildElement(contextMenu.elementId, "ColumnLayout")
            }
        }
        
        QQC2.MenuSeparator {}
        
        QQC2.MenuItem {
            text: "Move Up"
            icon.name: "arrow-up"
            onClicked: moveElement(contextMenu.elementId, -1)
        }
        
        QQC2.MenuItem {
            text: "Move Down" 
            icon.name: "arrow-down"
            onClicked: moveElement(contextMenu.elementId, 1)
        }
    }
    
    // Rename dialog
    Kirigami.PromptDialog {
        id: renameDialog
        title: "Rename Element"
        
        standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
        
        QQC2.TextField {
            id: nameField
            placeholderText: "Enter new name..."
        }
        
        onOpened: {
            var element = findElementById(contextMenu.elementId)
            nameField.text = element ? element.name : ""
            nameField.selectAll()
            nameField.forceActiveFocus()
        }
        
        onAccepted: {
            if (nameField.text.trim().length > 0) {
                root.elementRenamed(contextMenu.elementId, nameField.text.trim())
                updateElementName(contextMenu.elementId, nameField.text.trim())
            }
        }
    }
    
    // Delete confirmation dialog
    Kirigami.PromptDialog {
        id: deleteConfirmDialog
        title: "Delete Element"
        subtitle: "This action cannot be undone"
        
        property string elementId: ""
        
        standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
        
        QQC2.Label {
            text: "Are you sure you want to delete this element and all its children?"
        }
        
        onAccepted: {
            root.elementDeleted(elementId)
            deleteElement(elementId)
        }
    }
    
    // Keyboard shortcuts
    QQC2.Shortcut {
        sequence: "Ctrl+F"
        onActivated: {
            root.searchMode = true
            searchField.forceActiveFocus()
        }
    }
    
    QQC2.Shortcut {
        sequence: "F2"
        enabled: root.selectedElementId !== ""
        onActivated: {
            contextMenu.elementId = root.selectedElementId
            renameDialog.open()
        }
    }
    
    QQC2.Shortcut {
        sequence: "Delete"
        enabled: root.selectedElementId !== ""
        onActivated: {
            deleteConfirmDialog.elementId = root.selectedElementId
            deleteConfirmDialog.open()
        }
    }
    
    // Functions
    function selectElement(elementId) {
        root.selectedElementId = elementId
        
        // Ensure element is visible by expanding parents
        expandToElement(elementId)
        
        // Scroll to element
        scrollToElement(elementId)
    }
    
    function flattenTree(nodes, depth) {
        depth = depth || 0
        var result = []
        
        for (var i = 0; i < nodes.length; i++) {
            var node = Object.assign({}, nodes[i])  // Clone
            node.depth = depth
            node.index = i
            
            // Apply search filter
            if (root.searchText === "" || matchesSearch(node)) {
                result.push(node)
            }
            
            // Include children if expanded (and visible)
            if (node.expanded && node.children && node.children.length > 0) {
                var childResults = flattenTree(node.children, depth + 1)
                result = result.concat(childResults)
            }
        }
        
        return result
    }
    
    function matchesSearch(node) {
        if (root.searchText === "") return true
        
        var search = root.searchText.toLowerCase()
        return node.name.toLowerCase().includes(search) ||
               node.type.toLowerCase().includes(search) ||
               node.id.toLowerCase().includes(search)
    }
    
    function toggleExpanded(elementId) {
        var element = findElementById(elementId)
        if (element) {
            element.expanded = !element.expanded
            // Trigger model update
            treeView.model = flattenTree(root.treeModel)
        }
    }
    
    function findElementById(elementId, nodes) {
        nodes = nodes || root.treeModel
        
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === elementId) {
                return nodes[i]
            }
            
            if (nodes[i].children) {
                var result = findElementById(elementId, nodes[i].children)
                if (result) return result
            }
        }
        
        return null
    }
    
    function updateElementVisibility(elementId, visible) {
        var element = findElementById(elementId)
        if (element) {
            element.visible = visible
            treeView.model = flattenTree(root.treeModel)
        }
    }
    
    function updateElementName(elementId, newName) {
        var element = findElementById(elementId)
        if (element) {
            element.name = newName
            treeView.model = flattenTree(root.treeModel)
        }
    }
    
    function deleteElement(elementId) {
        removeElementFromTree(elementId, root.treeModel)
        treeView.model = flattenTree(root.treeModel)
        
        // Clear selection if deleted element was selected
        if (root.selectedElementId === elementId) {
            root.selectedElementId = ""
        }
    }
    
    function removeElementFromTree(elementId, nodes) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === elementId) {
                nodes.splice(i, 1)
                return true
            }
            
            if (nodes[i].children && removeElementFromTree(elementId, nodes[i].children)) {
                return true
            }
        }
        return false
    }
    
    function duplicateElement(elementId) {
        var element = findElementById(elementId)
        if (element) {
            var duplicate = JSON.parse(JSON.stringify(element))
            duplicate.id = "dup_" + Date.now()
            duplicate.name = element.name + " Copy"
            
            // Add to parent
            var parent = findParentOf(elementId)
            if (parent && parent.children) {
                parent.children.push(duplicate)
                treeView.model = flattenTree(root.treeModel)
            }
        }
    }
    
    function addChildElement(parentId, elementType) {
        var parent = findElementById(parentId)
        if (parent) {
            if (!parent.children) {
                parent.children = []
            }
            
            var newElement = {
                "id": elementType.toLowerCase() + "_" + Date.now(),
                "name": "New " + elementType,
                "type": elementType,
                "visible": true,
                "expanded": false,
                "children": []
            }
            
            parent.children.push(newElement)
            parent.expanded = true  // Expand parent to show new child
            treeView.model = flattenTree(root.treeModel)
        }
    }
    
    function moveElement(elementId, direction) {
        var parent = findParentOf(elementId)
        if (parent && parent.children) {
            var index = -1
            for (var i = 0; i < parent.children.length; i++) {
                if (parent.children[i].id === elementId) {
                    index = i
                    break
                }
            }
            
            if (index >= 0) {
                var newIndex = index + direction
                if (newIndex >= 0 && newIndex < parent.children.length) {
                    var element = parent.children.splice(index, 1)[0]
                    parent.children.splice(newIndex, 0, element)
                    treeView.model = flattenTree(root.treeModel)
                    root.elementMoved(elementId, parent.id, newIndex)
                }
            }
        }
    }
    
    function findParentOf(elementId, nodes, parent) {
        nodes = nodes || root.treeModel
        
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === elementId) {
                return parent
            }
            
            if (nodes[i].children) {
                var result = findParentOf(elementId, nodes[i].children, nodes[i])
                if (result) return result
            }
        }
        
        return null
    }
    
    function expandToElement(elementId) {
        var path = getPathToElement(elementId)
        for (var i = 0; i < path.length - 1; i++) {  // Don't expand the element itself
            var element = findElementById(path[i])
            if (element) {
                element.expanded = true
            }
        }
        treeView.model = flattenTree(root.treeModel)
    }
    
    function getPathToElement(elementId, nodes, currentPath) {
        nodes = nodes || root.treeModel
        currentPath = currentPath || []
        
        for (var i = 0; i < nodes.length; i++) {
            var newPath = currentPath.concat([nodes[i].id])
            
            if (nodes[i].id === elementId) {
                return newPath
            }
            
            if (nodes[i].children) {
                var result = getPathToElement(elementId, nodes[i].children, newPath)
                if (result) return result
            }
        }
        
        return null
    }
    
    function scrollToElement(elementId) {
        // Find element in flattened model and scroll to it
        var flatModel = treeView.model
        for (var i = 0; i < flatModel.length; i++) {
            if (flatModel[i].id === elementId) {
                treeView.positionViewAtIndex(i, ListView.Center)
                break
            }
        }
    }
    
    function selectFirstMatch() {
        if (root.searchText && treeView.count > 0) {
            var firstItem = treeView.model[0]
            if (firstItem) {
                root.selectedElementId = firstItem.id
                root.elementSelected(firstItem.id)
            }
        }
    }
    
    function filterTree() {
        treeView.model = flattenTree(root.treeModel)
    }
}