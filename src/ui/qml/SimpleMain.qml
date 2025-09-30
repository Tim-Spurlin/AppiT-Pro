import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: root
    
    title: "HAASP - Development Platform" 
    visible: true
    width: 1200
    height: 800
    minimumWidth: 800
    minimumHeight: 600
    
    color: "#1e1e1e"
    
    Component.onCompleted: {
        console.log("✅ HAASP QML Application Started Successfully!")
    }
    
    // Main content
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: "#2d2d2d"
            radius: 8
            
            ColumnLayout {
                anchors.centerIn: parent
                
                Text {
                    text: "🚀 HAASP"
                    color: "#00ff00"
                    font.pixelSize: 24
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: "Hyper-Advanced Associative Application Synthesis Platform"
                    color: "#ffffff"
                    font.pixelSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Main working area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#2d2d2d"
            radius: 8
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20
                
                Text {
                    text: "🎉 Application Successfully Loaded!"
                    color: "#00ff00"
                    font.pixelSize: 20
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: "• QML Engine: ✅ Working\n• Resource System: ✅ Working\n• Qt6 Components: ✅ Working"
                    color: "#ffffff"
                    font.pixelSize: 14
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Button {
                    text: "Test Functionality"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        statusText.text = "Button clicked at " + new Date().toLocaleTimeString()
                        statusText.color = "#ffff00"
                    }
                }
                
                Text {
                    id: statusText
                    text: "Ready to test..."
                    color: "#ffffff"
                    font.pixelSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Footer status
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#2d2d2d"
            radius: 8
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                
                Text {
                    text: "Status: ✅ Ready"
                    color: "#00ff00"
                    font.pixelSize: 12
                }
                
                Item { Layout.fillWidth: true }
                
                Text {
                    text: "HAASP v1.0.0"
                    color: "#ffffff"
                    font.pixelSize: 10
                }
            }
        }
    }
}