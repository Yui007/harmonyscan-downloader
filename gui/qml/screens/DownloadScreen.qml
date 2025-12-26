import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "../components"

Item {
    id: root
    
    property bool isDownloading: backend.downloading
    
    signal backRequested()
    
    // Download progress tracking
    property var chapterProgress: ({})
    property int completedChapters: 0
    property int totalChapters: 0
    
    // Track selected count for button state
    property int selectedCount: 0
    
    Connections {
        target: backend
        
        function onDownloadProgress(chapter, current, total) {
            root.completedChapters = current
            root.totalChapters = total
        }
        
        function onChapterComplete(chapter, success, message) {
            root.chapterProgress[chapter] = { success: success, message: message }
        }
    }
    
    Connections {
        target: chapterModel
        
        function onSelectionChanged() {
            root.selectedCount = chapterModel.selectedCount()
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLg
        spacing: Theme.spacingMd
        
        // Back button
        Row {
            spacing: Theme.spacingSm
            
            Rectangle {
                width: 36
                height: 36
                radius: Theme.radiusSm
                color: backMouseArea.containsMouse ? Theme.elevated : "transparent"
                
                Text {
                    anchors.centerIn: parent
                    text: "←"
                    font.pixelSize: Theme.fontSizeLg
                    color: Theme.textSecondary
                }
                
                MouseArea {
                    id: backMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    enabled: !root.isDownloading
                    onClicked: root.backRequested()
                }
            }
            
            Text {
                text: "Back to search"
                font.pixelSize: Theme.fontSizeSm
                color: Theme.textMuted
                anchors.verticalCenter: parent.verticalCenter
            }
        }
        
        // Main content area - Split layout
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingMd
            
            // Left column - Manga info (65% width - much larger)
            MangaCard {
                Layout.preferredWidth: parent.width * 0.65
                Layout.minimumWidth: 550
                Layout.fillHeight: true
            }
            
            // Right column - Chapter list (55% width)
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacingMd
                
                // Chapter list
                ChapterList {
                    id: chapterList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    onSelectionChanged: {
                        root.selectedCount = chapterModel.selectedCount()
                    }
                }
                
                // Download progress (when downloading)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    radius: Theme.radiusMd
                    color: Theme.cardBg
                    visible: root.isDownloading
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingMd
                        spacing: Theme.spacingSm
                        
                        Text {
                            text: "📥 Downloading..."
                            font.pixelSize: Theme.fontSizeSm
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        ProgressBar {
                            Layout.fillWidth: true
                            value: root.totalChapters > 0 ? root.completedChapters / root.totalChapters : 0
                            label: root.completedChapters + "/" + root.totalChapters + " chapters"
                        }
                    }
                }
                
                // Action buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingSm
                    
                    // Selection info
                    Text {
                        text: root.selectedCount > 0 ? root.selectedCount + " chapter(s) selected" : "Select chapters to download"
                        font.pixelSize: Theme.fontSizeSm
                        color: root.selectedCount > 0 ? Theme.accent : Theme.textMuted
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    SecondaryButton {
                        text: "Cancel"
                        visible: root.isDownloading
                        onClicked: backend.cancelDownload()
                    }
                    
                    PrimaryButton {
                        text: root.isDownloading ? "Downloading..." : "Download"
                        icon: "📥"
                        enabled: !root.isDownloading && root.selectedCount > 0
                        loading: root.isDownloading
                        
                        onClicked: {
                            var selected = chapterModel.getSelectedChapters()
                            backend.downloadChapters(selected, backend.outputFormat, backend.keepImages)
                        }
                    }
                }
            }
        }
    }
}
