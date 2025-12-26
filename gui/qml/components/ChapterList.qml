import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    
    signal selectionChanged()
    
    radius: Theme.radiusMd
    color: Theme.cardBg
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMd
        spacing: Theme.spacingSm
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSm
            
            Text {
                text: "📋"
                font.pixelSize: Theme.fontSizeMd
            }
            
            Text {
                text: "Chapters"
                font.pixelSize: Theme.fontSizeMd
                font.bold: true
                color: Theme.textPrimary
            }
            
            Text {
                text: "(" + chapterModel.rowCount() + ")"
                font.pixelSize: Theme.fontSizeSm
                color: Theme.textSecondary
            }
            
            Item { Layout.fillWidth: true }
            
            // Selection count
            Text {
                text: chapterModel.selectedCount() + " selected"
                font.pixelSize: Theme.fontSizeSm
                color: Theme.accent
                visible: chapterModel.selectedCount() > 0
            }
        }
        
        // Action buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSm
            
            SecondaryButton {
                text: "Select All"
                icon: "☑"
                onClicked: {
                    chapterModel.selectAll()
                    root.selectionChanged()
                }
            }
            
            SecondaryButton {
                text: "Clear"
                icon: "☐"
                onClicked: {
                    chapterModel.clearSelection()
                    root.selectionChanged()
                }
            }
            
            Item { Layout.fillWidth: true }
        }
        
        // Chapter list with custom styled scrollbar
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ListView {
                id: listView
                anchors.fill: parent
                anchors.rightMargin: 12  // Space for scrollbar
                clip: true
                spacing: Theme.spacingXs
                
                model: chapterModel
                
                delegate: ChapterItem {
                    width: listView.width
                    chapterTitle: model.title
                    chapterNumber: model.number
                    views: model.views
                    selected: model.selected
                    
                    onToggled: {
                        chapterModel.toggleSelection(index)
                        root.selectionChanged()
                    }
                }
                
                // Empty state
                Rectangle {
                    anchors.fill: parent
                    color: "transparent"
                    visible: listView.count === 0
                    
                    Column {
                        anchors.centerIn: parent
                        spacing: Theme.spacingSm
                        
                        Text {
                            text: "📭"
                            font.pixelSize: 48
                            opacity: 0.5
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        
                        Text {
                            text: "No chapters available"
                            font.pixelSize: Theme.fontSizeMd
                            color: Theme.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }
            
            // Custom beautiful scrollbar
            Rectangle {
                id: scrollTrack
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 8
                radius: 4
                color: Theme.secondaryBg
                visible: listView.contentHeight > listView.height
                
                Rectangle {
                    id: scrollThumb
                    anchors.right: parent.right
                    width: parent.width
                    radius: 4
                    
                    // Calculate thumb position and size
                    property real viewRatio: listView.height / listView.contentHeight
                    property real thumbHeight: Math.max(40, scrollTrack.height * viewRatio)
                    
                    height: thumbHeight
                    y: {
                        if (listView.contentHeight <= listView.height) return 0
                        var scrollRange = scrollTrack.height - thumbHeight
                        var contentRange = listView.contentHeight - listView.height
                        return (listView.contentY / contentRange) * scrollRange
                    }
                    
                    // Gradient thumb
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Theme.accent }
                        GradientStop { position: 1.0; color: Theme.accentSecondary }
                    }
                    
                    // Hover effect
                    opacity: scrollMouseArea.containsMouse || scrollMouseArea.pressed ? 1.0 : 0.7
                    
                    Behavior on opacity {
                        NumberAnimation { duration: 150 }
                    }
                    
                    // Glow effect on hover
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -2
                        radius: parent.radius + 2
                        color: "transparent"
                        border.width: 2
                        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
                        visible: scrollMouseArea.containsMouse
                    }
                }
                
                // Mouse interaction
                MouseArea {
                    id: scrollMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    
                    property real dragStartY: 0
                    property real dragStartContentY: 0
                    
                    onPressed: function(mouse) {
                        dragStartY = mouse.y
                        dragStartContentY = listView.contentY
                    }
                    
                    onPositionChanged: function(mouse) {
                        if (pressed) {
                            var dy = mouse.y - dragStartY
                            var scrollRange = scrollTrack.height - scrollThumb.height
                            var contentRange = listView.contentHeight - listView.height
                            var ratio = contentRange / scrollRange
                            
                            var newContentY = dragStartContentY + (dy * ratio)
                            listView.contentY = Math.max(0, Math.min(contentRange, newContentY))
                        }
                    }
                    
                    // Click to scroll
                    onClicked: function(mouse) {
                        var contentRange = listView.contentHeight - listView.height
                        var clickRatio = mouse.y / scrollTrack.height
                        listView.contentY = clickRatio * contentRange
                    }
                }
            }
        }
    }
}
