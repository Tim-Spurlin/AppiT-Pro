import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3 as Dialogs
import org.kde.kirigami 2.19 as Kirigami

Kirigami.OverlaySheet {
    id: root

    title: "New Project"

    signal projectCreated(string projectPath)

    ColumnLayout {
        Layout.fillWidth: true
        spacing: Kirigami.Units.largeSpacing

        QQC2.TextField {
            id: projectNameField
            Layout.fillWidth: true
            placeholderText: "Project name"
        }

        QQC2.TextField {
            id: projectPathField
            Layout.fillWidth: true
            placeholderText: "Project path"
        }

        QQC2.Button {
            text: "Browse..."
            onClicked: folderDialog.open()
        }

        QQC2.Button {
            text: "Create Project"
            Layout.fillWidth: true
            enabled: projectNameField.text && projectPathField.text
            onClicked: {
                var fullPath = projectPathField.text + "/" + projectNameField.text
                root.projectCreated(fullPath)
                root.close()
            }
        }
    }

    Dialogs.FileDialog {
        id: folderDialog
        selectFolder: true
        onAccepted: {
            projectPathField.text = folderDialog.fileUrl.toString().replace("file://", "")
        }
    }
}