import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3 as Dialogs
import org.kde.kirigami 2.19 as Kirigami

Kirigami.OverlaySheet {
    id: root

    title: "Open Repository"

    signal repositorySelected(string repoPath)

    ColumnLayout {
        Layout.fillWidth: true
        spacing: Kirigami.Units.largeSpacing

        QQC2.TextField {
            id: repoPathField
            Layout.fillWidth: true
            placeholderText: "Repository path"
        }

        QQC2.Button {
            text: "Browse..."
            onClicked: folderDialog.open()
        }

        QQC2.Button {
            text: "Open Repository"
            Layout.fillWidth: true
            enabled: repoPathField.text
            onClicked: {
                root.repositorySelected(repoPathField.text)
                root.close()
            }
        }
    }

    Dialogs.FileDialog {
        id: folderDialog
        selectFolder: true
        onAccepted: {
            repoPathField.text = folderDialog.fileUrl.toString().replace("file://", "")
        }
    }
}