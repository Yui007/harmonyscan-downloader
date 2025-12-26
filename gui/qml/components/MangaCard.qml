import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    
    // Now we read directly from backend properties
    property bool hasInfo: backend.hasMangaInfo
    
    radius: Theme.radiusLg
    color: Theme.cardBg
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        spacing: Theme.spacingMd
        
        // Cover image - fixed square aspect ratio
        Rectangle {
            id: coverContainer
            Layout.preferredWidth: 160
            Layout.preferredHeight: 160  // Square aspect ratio
            Layout.alignment: Qt.AlignTop
            radius: Theme.radiusMd
            color: Theme.secondaryBg
            clip: true
            
            Image {
                id: coverImage
                anchors.fill: parent
                source: backend.mangaCoverUrl
                fillMode: Image.PreserveAspectCrop  // Crop to fit square
                asynchronous: true
                
                opacity: status === Image.Ready ? 1 : 0
                
                Behavior on opacity {
                    NumberAnimation { duration: Theme.animNormal }
                }
            }
            
            // Loading placeholder
            Rectangle {
                anchors.fill: parent
                color: Theme.secondaryBg
                visible: coverImage.status !== Image.Ready
                
                Text {
                    anchors.centerIn: parent
                    text: "📖"
                    font.pixelSize: 48
                    opacity: 0.5
                }
                
                // Shimmer effect when loading
                Rectangle {
                    id: shimmer
                    width: parent.width
                    height: parent.height
                    opacity: 0.3
                    visible: coverImage.status === Image.Loading
                    
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.5; color: Theme.elevated }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                    
                    SequentialAnimation on x {
                        loops: Animation.Infinite
                        running: shimmer.visible
                        
                        PropertyAnimation {
                            from: -shimmer.width
                            to: shimmer.width
                            duration: 1500
                        }
                    }
                }
            }
            
            // Gradient overlay at bottom
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 40
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.5) }
                }
            }
        }
        
        // Info panel
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingSm
            
            // Title
            Text {
                Layout.fillWidth: true
                text: root.hasInfo ? backend.mangaTitle : "Loading..."
                font.pixelSize: Theme.fontSizeLg
                font.bold: true
                color: Theme.textPrimary
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }
            
            // Rating row
            Row {
                spacing: Theme.spacingXs
                visible: backend.mangaRating > 0
                
                Text {
                    text: "⭐"
                    font.pixelSize: Theme.fontSizeSm
                }
                
                Text {
                    text: backend.mangaRating.toFixed(1)
                    font.pixelSize: Theme.fontSizeSm
                    font.bold: true
                    color: Theme.warning
                }
                
                Text {
                    text: "(" + backend.mangaRatingCount + " votes)"
                    font.pixelSize: Theme.fontSizeXs
                    color: Theme.textMuted
                }
            }
            
            // Author row
            Row {
                spacing: Theme.spacingSm
                visible: backend.mangaAuthors.length > 0
                
                Text {
                    text: "✍️"
                    font.pixelSize: Theme.fontSizeSm
                }
                
                Text {
                    text: backend.mangaAuthors
                    font.pixelSize: Theme.fontSizeSm
                    color: Theme.textSecondary
                    elide: Text.ElideRight
                }
            }
            
            // Status badge
            Row {
                spacing: Theme.spacingSm
                visible: backend.mangaStatus.length > 0
                
                Rectangle {
                    id: statusBadge
                    width: statusText.implicitWidth + Theme.spacingSm * 2
                    height: statusText.implicitHeight + Theme.spacingXs
                    radius: Theme.radiusFull
                    color: backend.mangaStatus.toLowerCase().indexOf("ongoing") >= 0 ? Theme.success : Theme.info
                    opacity: 0.2
                    
                    Text {
                        id: statusText
                        anchors.centerIn: parent
                        text: backend.mangaStatus
                        font.pixelSize: Theme.fontSizeXs
                        font.weight: Font.Medium
                        color: backend.mangaStatus.toLowerCase().indexOf("ongoing") >= 0 ? Theme.success : Theme.info
                    }
                }
            }
            
            // Genres
            Flow {
                Layout.fillWidth: true
                spacing: Theme.spacingXs
                visible: backend.mangaGenres.length > 0
                
                Repeater {
                    model: backend.mangaGenres.length > 0 ? backend.mangaGenres.split(", ").slice(0, 4) : []
                    
                    delegate: Rectangle {
                        width: genreText.implicitWidth + Theme.spacingSm * 2
                        height: genreText.implicitHeight + Theme.spacingXs
                        radius: Theme.radiusSm
                        color: Theme.elevated
                        
                        Text {
                            id: genreText
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: Theme.fontSizeXs
                            color: Theme.textSecondary
                        }
                    }
                }
            }
            
            Item { Layout.fillHeight: true }
        }
    }
}
