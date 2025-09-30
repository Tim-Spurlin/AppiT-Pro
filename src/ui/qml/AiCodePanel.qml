import QtQuick 2.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.19 as Kirigami

Kirigami.Card {
    id: root

    signal generateCode(string prompt, string language)
    signal analyzeCode()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Kirigami.Units.smallSpacing
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading {
            text: "AI Code Assistant"
            level: 4
        }

        // Language selector
        RowLayout {
            Layout.fillWidth: true

            QQC2.Label { text: "Language:" }

            QQC2.ComboBox {
                id: languageCombo
                Layout.fillWidth: true
                model: ["cpp", "qml", "python", "rust", "javascript"]
                currentIndex: 0
            }
        }

        // Code prompt input
        QQC2.TextArea {
            id: promptInput
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            placeholderText: "Describe the code you want to generate..."
            wrapMode: TextEdit.Wrap
        }

        // Action buttons
        RowLayout {
            Layout.fillWidth: true

            QQC2.Button {
                text: "Generate"
                Layout.fillWidth: true
                enabled: promptInput.text.trim()
                onClicked: {
                    root.generateCode(promptInput.text, languageCombo.currentText)
                }
            }

            QQC2.Button {
                text: "Analyze"
                Layout.fillWidth: true
                onClicked: root.analyzeCode()
            }
        }

        // Recent prompts
        Kirigami.Separator { Layout.fillWidth: true }

        QQC2.Label {
            text: "Recent Prompts:"
            font.bold: true
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: ListModel {
                ListElement { prompt: "Create a Qt Quick Button component" }
                ListElement { prompt: "Implement a C++ class for data management" }
                ListElement { prompt: "Generate Python ML pipeline code" }
            }
            clip: true

            delegate: QQC2.ItemDelegate {
                width: parent.width
                text: model.prompt
                onClicked: {
                    promptInput.text = model.prompt
                }
            }
        }
    }
}