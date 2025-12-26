import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    
    property alias text: input.text
    property alias placeholderText: input.placeholderText
    property bool loading: false
    
    signal submitted(string url)
    
    height: 52
    radius: Theme.radiusMd
    color: Theme.cardBg
    border.width: 2
    border.color: input.activeFocus ? Theme.accent : Theme.elevated
    
    Behavior on border.color {
        ColorAnimation { duration: Theme.animNormal }
    }
    
    // Glow effect when focused
    Rectangle {
        anchors.fill: parent
        anchors.margins: -4
        radius: parent.radius + 4
        color: "transparent"
        border.width: input.activeFocus ? 2 : 0
        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
        opacity: input.activeFocus ? 1 : 0
        
        Behavior on opacity {
            NumberAnimation { duration: Theme.animNormal }
        }
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingMd
        anchors.rightMargin: Theme.spacingSm
        spacing: Theme.spacingSm
        
        // Search icon
        Text {
            text: "🔍"
            font.pixelSize: Theme.fontSizeLg
            opacity: 0.7
        }
        
        // Input field
        TextField {
            id: input
            
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            placeholderText: "Enter harmony-scan.fr manga URL..."
            placeholderTextColor: Theme.textMuted
            color: Theme.textPrimary
            font.pixelSize: Theme.fontSizeMd
            font.family: Theme.fontFamily
            verticalAlignment: TextInput.AlignVCenter
            
            background: Item {}
            
            selectByMouse: true
            
            onAccepted: {
                if (text.trim().length > 0 && !root.loading) {
                    root.submitted(text.trim())
                }
            }
            
            Keys.onEscapePressed: {
                text = ""
                focus = false
            }
        }
        
        // GO Button
        Rectangle {
            id: goButton
            
            width: 70
            height: 36
            radius: Theme.radiusSm
            
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: goMouseArea.containsMouse ? Qt.lighter(Theme.accent, 1.1) : Theme.accent }
                GradientStop { position: 1.0; color: goMouseArea.containsMouse ? Qt.lighter(Theme.accentSecondary, 1.1) : Theme.accentSecondary }
            }
            
            // Scale animation
            scale: goMouseArea.pressed ? 0.95 : (goMouseArea.containsMouse ? 1.02 : 1.0)
            
            Behavior on scale {
                NumberAnimation { duration: Theme.animFast }
            }
            
            Text {
                anchors.centerIn: parent
                text: root.loading ? "..." : "GO"
                font.pixelSize: Theme.fontSizeMd
                font.bold: true
                color: Theme.textPrimary
            }
            
            // Loading spinner overlay
            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: Qt.rgba(0, 0, 0, 0.3)
                visible: root.loading
                
                Text {
                    anchors.centerIn: parent
                    text: "⏳"
                    font.pixelSize: Theme.fontSizeMd
                    
                    RotationAnimation on rotation {
                        from: 0
                        to: 360
                        duration: 1500
                        loops: Animation.Infinite
                        running: root.loading
                    }
                }
            }
            
            MouseArea {
                id: goMouseArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: root.loading ? Qt.BusyCursor : Qt.PointingHandCursor
                
                onClicked: {
                    if (input.text.trim().length > 0 && !root.loading) {
                        root.submitted(input.text.trim())
                    }
                }
            }
        }
    }
}
