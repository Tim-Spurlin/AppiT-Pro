import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.19 as Kirigami

Kirigami.OverlaySheet {
    id: root

    title: "Settings"

    ColumnLayout {
        Layout.fillWidth: true
        spacing: Kirigami.Units.largeSpacing

        Kirigami.Heading {
            text: "AI Configuration"
            level: 4
        }

        QQC2.TextField {
            id: grokApiKeyField
            Layout.fillWidth: true
            placeholderText: "Grok API Key"
            echoMode: TextInput.Password
        }

        QQC2.TextField {
            id: qwenApiKeyField
            Layout.fillWidth: true
            placeholderText: "Qwen API Key"
            echoMode: TextInput.Password
        }

        Kirigami.Separator { Layout.fillWidth: true }

        Kirigami.Heading {
            text: "Git Configuration"
            level: 4
        }

        QQC2.TextField {
            id: gitUserNameField
            Layout.fillWidth: true
            placeholderText: "Git User Name"
        }

        QQC2.TextField {
            id: gitUserEmailField
            Layout.fillWidth: true
            placeholderText: "Git User Email"
        }

        Kirigami.Separator { Layout.fillWidth: true }

        RowLayout {
            Layout.fillWidth: true

            QQC2.Button {
                text: "Save"
                onClicked: {
                    // Save settings to .env or config
                    root.close()
                }
            }

            QQC2.Button {
                text: "Cancel"
                onClicked: root.close()
            }
        }
    }
}