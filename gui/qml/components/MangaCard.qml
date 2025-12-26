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
    
    ScrollView {
        id: scrollView
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        clip: true
        
        ColumnLayout {
            width: scrollView.availableWidth
            spacing: Theme.spacingMd
            
            // Top section with cover and basic info
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingLg
                
                // Cover image - Large square
                Rectangle {
                    id: coverContainer
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 280
                    Layout.alignment: Qt.AlignTop
                    radius: Theme.radiusMd
                    color: Theme.secondaryBg
                    clip: true
                    
                    Image {
                        id: coverImage
                        anchors.fill: parent
                        source: backend.mangaCoverUrl
                        fillMode: Image.PreserveAspectCrop
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
                    }
                    
                    // Gradient overlay
                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: 60
                        
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.6) }
                        }
                    }
                }
                
                // Basic info panel
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingSm
                    
                    // Title
                    Text {
                        Layout.fillWidth: true
                        text: root.hasInfo ? backend.mangaTitle : "Loading..."
                        font.pixelSize: 22
                        font.bold: true
                        color: Theme.textPrimary
                        wrapMode: Text.WordWrap
                        maximumLineCount: 3
                        elide: Text.ElideRight
                    }
                    
                    // Rating row
                    Row {
                        spacing: Theme.spacingSm
                        visible: backend.mangaRating > 0
                        
                        Text {
                            text: "⭐"
                            font.pixelSize: 16
                        }
                        
                        Text {
                            text: backend.mangaRating.toFixed(1)
                            font.pixelSize: 16
                            font.bold: true
                            color: Theme.warning
                        }
                        
                        Text {
                            text: "(" + backend.mangaRatingCount + " votes)"
                            font.pixelSize: 14
                            color: Theme.textMuted
                        }
                        
                        // Favorites badge
                        Rectangle {
                            width: favText.implicitWidth + Theme.spacingSm * 2
                            height: favText.implicitHeight + 6
                            radius: Theme.radiusSm
                            color: Theme.accent
                            opacity: 0.2
                            visible: backend.mangaFavoritesCount > 0
                            
                            Text {
                                id: favText
                                anchors.centerIn: parent
                                text: "❤️ " + backend.mangaFavoritesCount
                                font.pixelSize: 12
                                color: Theme.accent
                            }
                        }
                    }
                    
                    // Type, year, status row
                    Flow {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSm
                        
                        // Type badge
                        Rectangle {
                            width: typeText.implicitWidth + Theme.spacingSm * 2
                            height: typeText.implicitHeight + 6
                            radius: Theme.radiusSm
                            color: Theme.info
                            opacity: 0.2
                            visible: backend.mangaType.length > 0
                            
                            Text {
                                id: typeText
                                anchors.centerIn: parent
                                text: backend.mangaType
                                font.pixelSize: 13
                                font.weight: Font.Medium
                                color: Theme.info
                            }
                        }
                        
                        // Year badge
                        Rectangle {
                            width: yearText.implicitWidth + Theme.spacingSm * 2
                            height: yearText.implicitHeight + 6
                            radius: Theme.radiusSm
                            color: Theme.elevated
                            visible: backend.mangaReleaseYear.length > 0
                            
                            Text {
                                id: yearText
                                anchors.centerIn: parent
                                text: "📅 " + backend.mangaReleaseYear
                                font.pixelSize: 13
                                color: Theme.textSecondary
                            }
                        }
                        
                        // Status badge
                        Rectangle {
                            id: statusBadge
                            width: statusText.implicitWidth + Theme.spacingSm * 2
                            height: statusText.implicitHeight + 6
                            radius: Theme.radiusSm
                            color: statusBadge.isOngoing ? Theme.success : Theme.info
                            opacity: 0.2
                            visible: backend.mangaStatus.length > 0
                            
                            property bool isOngoing: backend.mangaStatus.toLowerCase().indexOf("ongoing") >= 0 || backend.mangaStatus.toLowerCase().indexOf("en cours") >= 0
                            
                            Text {
                                id: statusText
                                anchors.centerIn: parent
                                text: backend.mangaStatus
                                font.pixelSize: 13
                                font.weight: Font.Medium
                                color: statusBadge.isOngoing ? Theme.success : Theme.info
                            }
                        }
                    }
                    
                    // Author row
                    Row {
                        spacing: Theme.spacingSm
                        visible: backend.mangaAuthors.length > 0
                        
                        Text {
                            text: "✍️ Author:"
                            font.pixelSize: 14
                            color: Theme.textMuted
                        }
                        
                        Text {
                            text: backend.mangaAuthors
                            font.pixelSize: 14
                            color: Theme.textPrimary
                        }
                    }
                    
                    // Artist row
                    Row {
                        spacing: Theme.spacingSm
                        visible: backend.mangaArtists.length > 0
                        
                        Text {
                            text: "🎨 Artist:"
                            font.pixelSize: 14
                            color: Theme.textMuted
                        }
                        
                        Text {
                            text: backend.mangaArtists
                            font.pixelSize: 14
                            color: Theme.textPrimary
                        }
                    }
                }
            }
            
            // Genres row
            Flow {
                Layout.fillWidth: true
                spacing: Theme.spacingXs
                visible: backend.mangaGenres.length > 0
                
                Repeater {
                    model: backend.mangaGenres.length > 0 ? backend.mangaGenres.split(", ").slice(0, 8) : []
                    
                    delegate: Rectangle {
                        width: genreText.implicitWidth + Theme.spacingSm * 2
                        height: genreText.implicitHeight + 6
                        radius: Theme.radiusSm
                        color: Theme.elevated
                        
                        Text {
                            id: genreText
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: 12
                            color: Theme.textSecondary
                        }
                    }
                }
            }
            
            // Synopsis section
            Rectangle {
                Layout.fillWidth: true
                height: synopsisCol.implicitHeight + Theme.spacingMd * 2
                radius: Theme.radiusMd
                color: Theme.secondaryBg
                visible: backend.mangaSynopsis.length > 0
                
                ColumnLayout {
                    id: synopsisCol
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMd
                    spacing: Theme.spacingSm
                    
                    Text {
                        text: "📝 Synopsis"
                        font.pixelSize: 16
                        font.bold: true
                        color: Theme.textPrimary
                    }
                    
                    Text {
                        Layout.fillWidth: true
                        text: backend.mangaSynopsis
                        font.pixelSize: 14
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                        lineHeight: 1.4
                    }
                }
            }
            
            // Total views
            Row {
                spacing: Theme.spacingSm
                visible: backend.mangaTotalViews.length > 0
                
                Text {
                    text: "👁️ Views:"
                    font.pixelSize: 14
                    color: Theme.textMuted
                }
                
                Text {
                    text: backend.mangaTotalViews
                    font.pixelSize: 14
                    color: Theme.textSecondary
                }
            }
        }
    }
}
