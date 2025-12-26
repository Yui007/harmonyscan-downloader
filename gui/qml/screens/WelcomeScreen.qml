import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "../components"

Item {
    id: root
    
    signal fetchRequested(string url)
    
    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(600, parent.width - Theme.spacingXl * 2)
        spacing: Theme.spacingXl
        
        // Logo and title
        Column {
            Layout.alignment: Qt.AlignHCenter
            spacing: Theme.spacingMd
            
            // Animated logo
            Rectangle {
                width: 80
                height: 80
                radius: Theme.radiusLg
                anchors.horizontalCenter: parent.horizontalCenter
                
                gradient: Gradient {
                    orientation: Gradient.Vertical
                    GradientStop { position: 0.0; color: Theme.accent }
                    GradientStop { position: 1.0; color: Theme.accentSecondary }
                }
                
                Text {
                    anchors.centerIn: parent
                    text: "📖"
                    font.pixelSize: 40
                }
                
                // Subtle floating animation
                SequentialAnimation on y {
                    loops: Animation.Infinite
                    running: true
                    NumberAnimation { to: -8; duration: 2000; easing.type: Easing.InOutQuad }
                    NumberAnimation { to: 0; duration: 2000; easing.type: Easing.InOutQuad }
                }
                
                // Glow
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -8
                    radius: parent.radius + 8
                    color: "transparent"
                    border.width: 3
                    border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.2)
                    
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        running: true
                        NumberAnimation { to: 0.5; duration: 1500 }
                        NumberAnimation { to: 1; duration: 1500 }
                    }
                }
            }
            
            // Title
            Text {
                text: "HarmonyScan Downloader"
                font.pixelSize: Theme.fontSize2Xl
                font.bold: true
                color: Theme.textPrimary
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            // Subtitle
            Text {
                text: "Download your favorite manga from harmony-scan.fr"
                font.pixelSize: Theme.fontSizeMd
                color: Theme.textSecondary
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
        
        // URL Input
        UrlInput {
            id: urlInput
            Layout.fillWidth: true
            loading: backend.loading
            
            onSubmitted: function(url) {
                root.fetchRequested(url)
            }
        }
        
        // Quick tips
        Rectangle {
            Layout.fillWidth: true
            Layout.topMargin: Theme.spacingLg
            height: tipsColumn.implicitHeight + Theme.spacingMd * 2
            radius: Theme.radiusMd
            color: Theme.cardBg
            border.width: 1
            border.color: Theme.elevated
            
            ColumnLayout {
                id: tipsColumn
                anchors.fill: parent
                anchors.margins: Theme.spacingMd
                spacing: Theme.spacingSm
                
                Text {
                    text: "💡 Quick Tips"
                    font.pixelSize: Theme.fontSizeSm
                    font.bold: true
                    color: Theme.textSecondary
                }
                
                TipItem { text: "Paste a manga URL from harmony-scan.fr" }
                TipItem { text: "Select chapters and choose your preferred format" }
                TipItem { text: "Downloads are saved to your configured folder" }
            }
        }
        
        // Example URL hint
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "Example: https://harmony-scan.fr/manga/manga-name/"
            font.pixelSize: Theme.fontSizeXs
            font.family: "Consolas, monospace"
            color: Theme.textMuted
            
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    urlInput.text = "https://harmony-scan.fr/manga/"
                }
            }
        }
    }
    
    // Tip item component
    component TipItem: Row {
        property string text: ""
        
        spacing: Theme.spacingSm
        
        Text {
            text: "•"
            font.pixelSize: Theme.fontSizeSm
            color: Theme.accent
        }
        
        Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeSm
            color: Theme.textMuted
        }
    }
}
