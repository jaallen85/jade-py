# mainwindow.py
# Copyright (C) 2022  Jason Allen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import typing
from PyQt6.QtCore import pyqtBoundSignal, Qt, QSize
from PyQt6.QtGui import QAction, QBrush, QCloseEvent, QFont, QFontMetrics, QIcon, QKeySequence, QPen, QShowEvent
from PyQt6.QtWidgets import QApplication, QComboBox, QDockWidget, QHBoxLayout, QLabel, QMainWindow, QToolBar, QWidget
from .drawing import Drawing
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawinglineitem import DrawingLineItem
from .drawingrectitem import DrawingRectItem
from .pagesbrowser import PagesBrowser
from .propertiesbrowser import PropertiesBrowser


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._filePath: str = ''
        self._newDrawingCount: int = 0
        self._workingDir: str = os.getcwd()
        self._promptOverwrite: bool = True
        self._promptCloseUnsaved: bool = True
        self._pagesDockVisibleOnClose: bool = True
        self._propertiesDockVisibleOnClose: bool = True

        # Main widget
        self._registerItemsWithFactory()

        self._drawing: Drawing = Drawing()
        self.setCentralWidget(self._drawing)

        # Dock widgets
        self._pagesBrowser: PagesBrowser = PagesBrowser()
        self._pagesDock: QDockWidget = self._addDockWidget('Pages', self._pagesBrowser,
                                                           Qt.DockWidgetArea.LeftDockWidgetArea)

        self._propertiesBrowser: PropertiesBrowser = PropertiesBrowser()
        self._propertiesDock: QDockWidget = self._addDockWidget('Properties', self._propertiesBrowser,
                                                                Qt.DockWidgetArea.RightDockWidgetArea)
        # Status bar widgets
        self._modeLabel = self._addStatusBarLabel('Select Mode', 'Select Mode', self._drawing.modeChanged)
        self._modifiedLabel = self._addStatusBarLabel('', 'Modified', self._drawing.modifiedChanged)
        self._mouseInfoLabel = self._addStatusBarLabel('', '(XXXX.XX,XXXX.XX)', self._drawing.mouseInfoChanged)

        # Menus and toolbars
        self._createActions()
        self._createMenus()
        self._createToolBars()

        # Final window setup
        self.setWindowTitle('Jade')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(1690, 900)

        self._loadSettings()

    def _createActions(self) -> None:
        self._newAction: QAction = self._addNormalAction('New...', self.newDrawing, 'icons:document-new.png', 'Ctrl+N')
        self._openAction: QAction = self._addNormalAction('Open...', self._openDrawing, 'icons:document-open.png',
                                                          'Ctrl+O')
        self._saveAction: QAction = self._addNormalAction('Save', self._saveDrawing, 'icons:document-save.png',
                                                          'Ctrl+S')
        self._saveAsAction: QAction = self._addNormalAction('Save As...', self.saveDrawingAs,
                                                            'icons:document-save-as.png', 'Ctrl+Shift+S')
        self._closeAction: QAction = self._addNormalAction('Close', self.closeDrawing, 'icons:document-close.png',
                                                           'Ctrl+W')
        self._exportPngAction: QAction = self._addNormalAction('Export PNG...', self.exportPng,
                                                               'icons:image-x-generic.png')
        self._exportSvgAction: QAction = self._addNormalAction('Export SVG...', self.exportSvg,
                                                               'icons:image-svg+xml.png')
        self._exportVsdxAction: QAction = self._addNormalAction('Export VSDX...', self.exportVsdx, '')
        self._preferencesAction: QAction = self._addNormalAction('Preferences...', self.preferences,
                                                                 'icons:configure.png')
        self._exitAction: QAction = self._addNormalAction('Exit', self.close, 'icons:application-exit.png')

        self._viewPropertiesAction: QAction = self._addNormalAction('Properties...', self._propertiesDock.show,
                                                                    'icons:games-config-board.png')
        self._viewPagesAction: QAction = self._addNormalAction('Pages...', self._pagesDock.show, '')

        self._aboutAction: QAction = self._addNormalAction('About...', self.about, 'icons:help-about.png')
        self._aboutQtAction: QAction = self._addNormalAction('About Qt...', QApplication.aboutQt)

    def _createMenus(self) -> None:
        fileMenu = self.menuBar().addMenu('File')
        fileMenu.addAction(self._newAction)
        fileMenu.addAction(self._openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._saveAction)
        fileMenu.addAction(self._saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._closeAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._exportPngAction)
        fileMenu.addAction(self._exportSvgAction)
        fileMenu.addAction(self._exportVsdxAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._preferencesAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._exitAction)

        editMenu = self.menuBar().addMenu('Edit')
        editMenu.addAction(self._drawing.undoAction)
        editMenu.addAction(self._drawing.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self._drawing.cutAction)
        editMenu.addAction(self._drawing.copyAction)
        editMenu.addAction(self._drawing.pasteAction)
        editMenu.addAction(self._drawing.deleteAction)
        editMenu.addSeparator()
        editMenu.addAction(self._drawing.selectAllAction)
        editMenu.addAction(self._drawing.selectNoneAction)

        placeMenu = self.menuBar().addMenu('Place')
        placeMenu.addAction(self._drawing.selectModeAction)
        placeMenu.addAction(self._drawing.scrollModeAction)
        placeMenu.addAction(self._drawing.zoomModeAction)
        placeMenu.addSeparator()
        placeMenu.addAction(self._drawing.placeLineAction)
        placeMenu.addAction(self._drawing.placeCurveAction)
        placeMenu.addAction(self._drawing.placePolylineAction)
        placeMenu.addAction(self._drawing.placeRectAction)
        placeMenu.addAction(self._drawing.placeEllipseAction)
        placeMenu.addAction(self._drawing.placePolygonAction)
        placeMenu.addAction(self._drawing.placeTextAction)
        placeMenu.addAction(self._drawing.placeTextRectAction)
        placeMenu.addAction(self._drawing.placeTextEllipseAction)

        objectMenu = self.menuBar().addMenu('Object')
        objectMenu.addAction(self._drawing.rotateAction)
        objectMenu.addAction(self._drawing.rotateBackAction)
        objectMenu.addAction(self._drawing.flipHorizontalAction)
        objectMenu.addAction(self._drawing.flipVerticalAction)
        objectMenu.addSeparator()
        objectMenu.addAction(self._drawing.bringForwardAction)
        objectMenu.addAction(self._drawing.sendBackwardAction)
        objectMenu.addAction(self._drawing.bringToFrontAction)
        objectMenu.addAction(self._drawing.sendToBackAction)
        objectMenu.addSeparator()
        objectMenu.addAction(self._drawing.groupAction)
        objectMenu.addAction(self._drawing.ungroupAction)
        objectMenu.addSeparator()
        objectMenu.addAction(self._drawing.insertPointAction)
        objectMenu.addAction(self._drawing.removePointAction)

        viewMenu = self.menuBar().addMenu('View')
        viewMenu.addAction(self._viewPropertiesAction)
        viewMenu.addSeparator()
        viewMenu.addAction(self._drawing.insertPageAction)
        viewMenu.addAction(self._drawing.removePageAction)
        viewMenu.addAction(self._viewPagesAction)
        viewMenu.addSeparator()
        viewMenu.addAction(self._drawing.zoomInAction)
        viewMenu.addAction(self._drawing.zoomOutAction)
        viewMenu.addAction(self._drawing.zoomFitAction)

        aboutMenu = self.menuBar().addMenu('About')
        aboutMenu.addAction(self._aboutAction)
        aboutMenu.addAction(self._aboutQtAction)

    def _createToolBars(self) -> None:
        # Zoom combo box
        self._zoomCombo: QComboBox = QComboBox()
        self._zoomCombo.setMinimumWidth(QFontMetrics(self._zoomCombo.font()).boundingRect('XXXXXX.XX%').width() + 48)
        self._zoomCombo.addItems(['Fit to Page', '25%', '50%', '100%', '150%', '200%', '300%', '400%'])
        self._zoomCombo.setEditable(True)
        self._zoomCombo.setCurrentIndex(3)
        self._zoomCombo.textActivated.connect(self._setZoomLevel)   # type: ignore
        self._drawing.scaleChanged.connect(self._setZoomComboText)

        zoomWidget = QWidget()
        zoomLayout = QHBoxLayout()
        zoomLayout.addWidget(self._zoomCombo)
        zoomLayout.setContentsMargins(0, 0, 0, 0)
        zoomWidget.setLayout(zoomLayout)

        # Toolbars
        size = self._zoomCombo.sizeHint().height()
        iconSize = QSize(size, size)

        fileToolBar = QToolBar('File Toolbar')
        fileToolBar.setObjectName('FileToolBar')
        fileToolBar.setIconSize(iconSize)
        fileToolBar.addAction(self._newAction)
        fileToolBar.addAction(self._openAction)
        fileToolBar.addAction(self._saveAction)
        fileToolBar.addAction(self._closeAction)
        self.addToolBar(fileToolBar)

        placeToolBar = QToolBar('Place Toolbar')
        placeToolBar.setObjectName('PlaceToolBar')
        placeToolBar.setIconSize(iconSize)
        placeToolBar.addAction(self._drawing.selectModeAction)
        placeToolBar.addAction(self._drawing.scrollModeAction)
        placeToolBar.addAction(self._drawing.zoomModeAction)
        placeToolBar.addSeparator()
        placeToolBar.addAction(self._drawing.placeLineAction)
        placeToolBar.addAction(self._drawing.placeCurveAction)
        placeToolBar.addAction(self._drawing.placePolylineAction)
        placeToolBar.addAction(self._drawing.placeRectAction)
        placeToolBar.addAction(self._drawing.placeEllipseAction)
        placeToolBar.addAction(self._drawing.placePolygonAction)
        placeToolBar.addAction(self._drawing.placeTextAction)
        placeToolBar.addAction(self._drawing.placeTextRectAction)
        placeToolBar.addAction(self._drawing.placeTextEllipseAction)
        self.addToolBar(placeToolBar)

        objectToolBar = QToolBar('Object Toolbar')
        objectToolBar.setObjectName('ObjectToolBar')
        objectToolBar.setIconSize(iconSize)
        objectToolBar.addAction(self._drawing.rotateAction)
        objectToolBar.addAction(self._drawing.rotateBackAction)
        objectToolBar.addAction(self._drawing.flipHorizontalAction)
        objectToolBar.addAction(self._drawing.flipVerticalAction)
        objectToolBar.addSeparator()
        objectToolBar.addAction(self._drawing.bringForwardAction)
        objectToolBar.addAction(self._drawing.sendBackwardAction)
        objectToolBar.addAction(self._drawing.bringToFrontAction)
        objectToolBar.addAction(self._drawing.sendToBackAction)
        objectToolBar.addSeparator()
        objectToolBar.addAction(self._drawing.groupAction)
        objectToolBar.addAction(self._drawing.ungroupAction)
        self.addToolBar(objectToolBar)

        viewToolBar = QToolBar('View Toolbar')
        viewToolBar.setObjectName('ViewToolBar')
        viewToolBar.setIconSize(iconSize)
        viewToolBar.addAction(self._drawing.zoomInAction)
        viewToolBar.addWidget(zoomWidget)
        viewToolBar.addAction(self._drawing.zoomOutAction)
        self.addToolBar(viewToolBar)

    # ==================================================================================================================

    def newDrawing(self) -> None:
        # Close any open drawing first
        self.closeDrawing()

        # Create a new drawing only if there is no open drawing (i.e. close was successful or unneeded)
        if (not self.isDrawingVisible()):
            self._drawing.createNew()
            self._newDrawingCount = self._newDrawingCount + 1
            self._setFilePath(f'Untitled {self._newDrawingCount}')
            self._setDrawingVisible(True)

    def openDrawing(self, path: str = '') -> None:
        pass

    def saveDrawing(self, path: str = '') -> None:
        pass

    def saveDrawingAs(self) -> None:
        pass

    def closeDrawing(self) -> None:
        # Todo: fill out close method
        proceedToClose = self.isDrawingVisible()
        if (proceedToClose):
            self._setDrawingVisible(False)
            self._setFilePath('')

    def isDrawingVisible(self) -> bool:
        return self._drawing.isVisible()

    def filePath(self) -> str:
        return self._filePath

    # ==================================================================================================================

    def exportPng(self) -> None:
        pass

    def exportSvg(self) -> None:
        pass

    def exportVsdx(self) -> None:
        pass

    # ==================================================================================================================

    def preferences(self) -> None:
        pass

    def about(self) -> None:
        pass

    # ==================================================================================================================

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if (not event.spontaneous()):
            self._drawing.zoomFit()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closeDrawing()
        if (not self.isDrawingVisible()):
            self._saveSettings()
            event.accept()
        else:
            event.ignore()

    # ==================================================================================================================

    def _openDrawing(self) -> None:
        self.openDrawing()

    def _saveDrawing(self) -> None:
        self.saveDrawing()

    def _setDrawingVisible(self, visible: bool) -> None:
        self._drawing.setVisible(visible)

        # Update drawing
        if (visible):
            self._drawing.zoomFit()
        else:
            self._drawing.clear()

        # Update dock widget visibility
        if (visible):
            self._pagesDock.setVisible(self._pagesDockVisibleOnClose)
            self._propertiesDock.setVisible(self._propertiesDockVisibleOnClose)
        else:
            self._pagesDockVisibleOnClose = self._pagesDock.isVisibleTo(self)
            self._propertiesDockVisibleOnClose = self._propertiesDock.isVisibleTo(self)
            self._pagesDock.setVisible(False)
            self._propertiesDock.setVisible(False)

        # Update actions
        self._saveAction.setEnabled(visible)
        self._saveAsAction.setEnabled(visible)
        self._closeAction.setEnabled(visible)
        self._exportPngAction.setEnabled(visible)
        self._exportSvgAction.setEnabled(visible)
        self._exportVsdxAction.setEnabled(visible)
        for action in self._drawing.actions():
            action.setEnabled(visible)
        for action in self._drawing.modeActions():
            action.setEnabled(visible)

    def _setFilePath(self, path: str) -> None:
        self._filePath = path

        # Update window title
        fileName = os.path.basename(self._filePath)
        self.setWindowTitle('Jade' if (len(fileName) == 0) else f'{fileName} - Jade')

    # ==================================================================================================================

    def _setZoomComboText(self, scale: float) -> None:
        pass

    def _setZoomLevel(self, text: str) -> None:
        pass

    # ==================================================================================================================

    def _saveSettings(self) -> None:
        pass

    def _loadSettings(self) -> None:
        # Todo: try to load settings from file
        font = QFont('Arial')
        font.setPointSizeF(100)

        DrawingItem.setDefaultProperty(
           'pen', QPen(QBrush(Qt.GlobalColor.black), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin))
        DrawingItem.setDefaultProperty('brush', QBrush(Qt.GlobalColor.white))
        DrawingItem.setDefaultProperty('startArrow', DrawingArrow(DrawingArrow.Style.NoStyle, 100))
        DrawingItem.setDefaultProperty('endArrow', DrawingArrow(DrawingArrow.Style.NoStyle, 100))
        DrawingItem.setDefaultProperty('font', font)
        DrawingItem.setDefaultProperty('textAlignment', Qt.AlignmentFlag.AlignCenter)
        DrawingItem.setDefaultProperty('textBrush', QBrush(Qt.GlobalColor.black))

    # ==================================================================================================================

    def _registerItemsWithFactory(self):
        DrawingItem.register(DrawingLineItem())
        # DrawingItem.register(DrawingCurveItem())
        # DrawingItem.register(DrawingPolylineItem())
        DrawingItem.register(DrawingRectItem())
        # DrawingItem.register(DrawingEllipseItem())
        # DrawingItem.register(DrawingPolygonItem())
        # DrawingItem.register(DrawingTextItem())
        # DrawingItem.register(DrawingTextRectItem())
        # DrawingItem.register(DrawingTextEllipseItem())
        # DrawingItem.register(DrawingPathItem())
        # DrawingItem.register(DrawingItemGroup())

    def _addDockWidget(self, text: str, widget: QWidget, area: Qt.DockWidgetArea) -> QDockWidget:
        dockWidget = QDockWidget(text)
        dockWidget.setObjectName(f'{text}Dock')
        dockWidget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dockWidget.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                               QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                               QDockWidget.DockWidgetFeature.DockWidgetClosable)
        dockWidget.setWidget(widget)
        self.addDockWidget(area, dockWidget)
        return dockWidget

    def _addStatusBarLabel(self, text: str, minimumWidthText: str, signal: pyqtBoundSignal):
        label = QLabel(text)
        label.setMinimumWidth(QFontMetrics(label.font()).boundingRect(minimumWidthText).width() + 64)
        signal.connect(label.setText)
        self.statusBar().addWidget(label)
        return label

    def _addNormalAction(self, text: str, slot: typing.Callable, iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)      # type: ignore
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        self.addAction(action)
        return action
