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
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QMarginsF, QRectF, QSize, QSizeF, SignalInstance
from PySide6.QtGui import (QAction, QBrush, QColor, QCloseEvent, QFontMetrics, QIcon, QImage, QKeySequence, QPainter,
                           QShowEvent)
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QDockWidget, QHBoxLayout, QLabel, QMainWindow,
                               QMenu, QMessageBox, QToolBar, QWidget)
from .drawing.drawingxmlinterface import DrawingXmlInterface
from .exporters.odgwriter import OdgWriter
from .exporters.svgwriter import SvgWriter
from .exporters.vsdxwriter import VsdxWriter
from .aboutdialog import AboutDialog
from .diagramwidget import DiagramWidget
from .exportoptionsdialog import OdgVsdxExportOptionsDialog, PngSvgExportOptionsDialog
from .pagesbrowser import PagesBrowser
from .preferencesdialog import PreferencesDialog
from .propertiesbrowser import PropertiesBrowser


class MainWindow(QMainWindow, DrawingXmlInterface):
    def __init__(self) -> None:
        super().__init__()

        self._filePath: str = ''
        self._newDrawingCount: int = 0
        self._workingDir: str = os.getcwd()
        self._promptOverwrite: bool = True
        self._promptCloseUnsaved: bool = True
        self._pagesDockVisibleOnClose: bool = True
        self._propertiesDockVisibleOnClose: bool = True

        self._pngSvgExportScale: float = 1.0

        self._odgVsdxUnits: str = 'mm'
        self._odgVsdxScale: float = 1.0
        self._odgVsdxPageSize: QSizeF = QSizeF()
        self._odgVsdxPageMargins: QMarginsF = QMarginsF(0, 0, 0, 0)
        self._odgVsdxBackgroundColor: QColor = QColor(255, 255, 255)

        # Main widget
        self._diagram: DiagramWidget = DiagramWidget()
        self.setCentralWidget(self._diagram)

        # Dock widgets
        self._pagesBrowser: PagesBrowser = PagesBrowser(self._diagram)
        self._pagesDock: QDockWidget = self._addDockWidget('Pages', self._pagesBrowser,
                                                           Qt.DockWidgetArea.LeftDockWidgetArea)

        self._propertiesBrowser: PropertiesBrowser = PropertiesBrowser(self._diagram)
        self._propertiesDock: QDockWidget = self._addDockWidget('Properties', self._propertiesBrowser,
                                                                Qt.DockWidgetArea.RightDockWidgetArea)
        # Status bar widgets
        self._modeLabel = self._addStatusBarLabel('Select Mode', 'Select Mode', self._diagram.modeStringChanged)
        self._modifiedLabel = self._addStatusBarLabel('', 'Modified', self._diagram.modifiedStringChanged)
        self._mouseInfoLabel = self._addStatusBarLabel('', '(XXXX.XX,XXXX.XX)', self._diagram.mouseInfoChanged)

        # Menus and toolbars
        self._createActions()
        self._createMenus()
        self._createToolBars()

        # Final window setup
        self.setWindowTitle('Jade')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(1624, 900)

        self._loadSettings()

    # ==================================================================================================================

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
        self._exportOdgAction: QAction = self._addNormalAction('Export ODG...', self.exportOdg, '')
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
        fileMenu.addAction(self._exportOdgAction)
        fileMenu.addAction(self._exportVsdxAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._preferencesAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self._exitAction)

        editMenu = self.menuBar().addMenu('Edit')
        editMenu.addAction(self._diagram.undoAction)
        editMenu.addAction(self._diagram.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self._diagram.cutAction)
        editMenu.addAction(self._diagram.copyAction)
        editMenu.addAction(self._diagram.pasteAction)
        editMenu.addAction(self._diagram.deleteAction)
        editMenu.addSeparator()
        editMenu.addAction(self._diagram.selectAllAction)
        editMenu.addAction(self._diagram.selectNoneAction)

        placeMenu = self.menuBar().addMenu('Place')
        placeMenu.addAction(self._diagram.selectModeAction)
        placeMenu.addAction(self._diagram.scrollModeAction)
        placeMenu.addAction(self._diagram.zoomModeAction)
        placeMenu.addSeparator()
        placeMenu.addAction(self._diagram.placeLineAction)
        placeMenu.addAction(self._diagram.placeCurveAction)
        placeMenu.addAction(self._diagram.placePolylineAction)
        placeMenu.addAction(self._diagram.placeRectAction)
        placeMenu.addAction(self._diagram.placeEllipseAction)
        placeMenu.addAction(self._diagram.placePolygonAction)
        placeMenu.addAction(self._diagram.placeTextAction)
        placeMenu.addAction(self._diagram.placeTextRectAction)
        placeMenu.addAction(self._diagram.placeTextEllipseAction)
        placeMenu.addSeparator()

        electricMenu = QMenu('Electric Items')
        for action in self._diagram.electricActions:
            electricMenu.addAction(action)
        electricMenu.setIcon(electricMenu.actions()[0].icon())
        placeMenu.addMenu(electricMenu)

        logicMenu = QMenu('Logic Items')
        for action in self._diagram.logicActions:
            logicMenu.addAction(action)
        logicMenu.setIcon(logicMenu.actions()[0].icon())
        placeMenu.addMenu(logicMenu)

        objectMenu = self.menuBar().addMenu('Object')
        objectMenu.addAction(self._diagram.rotateAction)
        objectMenu.addAction(self._diagram.rotateBackAction)
        objectMenu.addAction(self._diagram.flipHorizontalAction)
        objectMenu.addAction(self._diagram.flipVerticalAction)
        objectMenu.addSeparator()
        objectMenu.addAction(self._diagram.bringForwardAction)
        objectMenu.addAction(self._diagram.sendBackwardAction)
        objectMenu.addAction(self._diagram.bringToFrontAction)
        objectMenu.addAction(self._diagram.sendToBackAction)
        objectMenu.addSeparator()
        objectMenu.addAction(self._diagram.groupAction)
        objectMenu.addAction(self._diagram.ungroupAction)
        objectMenu.addSeparator()
        objectMenu.addAction(self._diagram.insertPointAction)
        objectMenu.addAction(self._diagram.removePointAction)

        viewMenu = self.menuBar().addMenu('View')
        viewMenu.addAction(self._viewPropertiesAction)
        viewMenu.addSeparator()
        viewMenu.addAction(self._diagram.insertPageAction)
        viewMenu.addAction(self._diagram.removePageAction)
        viewMenu.addAction(self._viewPagesAction)
        viewMenu.addSeparator()
        viewMenu.addAction(self._diagram.zoomInAction)
        viewMenu.addAction(self._diagram.zoomOutAction)
        viewMenu.addAction(self._diagram.zoomFitAction)

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
        self._zoomCombo.textActivated.connect(self._setZoomLevel)       # type: ignore
        self._diagram.scaleChanged.connect(self._setZoomComboText)

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
        placeToolBar.addAction(self._diagram.selectModeAction)
        placeToolBar.addAction(self._diagram.scrollModeAction)
        placeToolBar.addAction(self._diagram.zoomModeAction)
        placeToolBar.addSeparator()
        placeToolBar.addAction(self._diagram.placeLineAction)
        placeToolBar.addAction(self._diagram.placeCurveAction)
        placeToolBar.addAction(self._diagram.placePolylineAction)
        placeToolBar.addAction(self._diagram.placeRectAction)
        placeToolBar.addAction(self._diagram.placeEllipseAction)
        placeToolBar.addAction(self._diagram.placePolygonAction)
        placeToolBar.addAction(self._diagram.placeTextAction)
        placeToolBar.addAction(self._diagram.placeTextRectAction)
        placeToolBar.addAction(self._diagram.placeTextEllipseAction)
        self.addToolBar(placeToolBar)

        objectToolBar = QToolBar('Object Toolbar')
        objectToolBar.setObjectName('ObjectToolBar')
        objectToolBar.setIconSize(iconSize)
        objectToolBar.addAction(self._diagram.rotateAction)
        objectToolBar.addAction(self._diagram.rotateBackAction)
        objectToolBar.addAction(self._diagram.flipHorizontalAction)
        objectToolBar.addAction(self._diagram.flipVerticalAction)
        objectToolBar.addSeparator()
        objectToolBar.addAction(self._diagram.bringForwardAction)
        objectToolBar.addAction(self._diagram.sendBackwardAction)
        objectToolBar.addAction(self._diagram.bringToFrontAction)
        objectToolBar.addAction(self._diagram.sendToBackAction)
        objectToolBar.addSeparator()
        objectToolBar.addAction(self._diagram.groupAction)
        objectToolBar.addAction(self._diagram.ungroupAction)
        self.addToolBar(objectToolBar)

        viewToolBar = QToolBar('View Toolbar')
        viewToolBar.setObjectName('ViewToolBar')
        viewToolBar.setIconSize(iconSize)
        viewToolBar.addAction(self._diagram.zoomInAction)
        viewToolBar.addWidget(zoomWidget)
        viewToolBar.addAction(self._diagram.zoomOutAction)
        self.addToolBar(viewToolBar)

    # ==================================================================================================================

    def newDrawing(self) -> None:
        # Close any open drawing first
        self.closeDrawing()

        # Create a new drawing only if there is no open drawing (i.e. close was successful or unneeded)
        if (not self.isDrawingVisible()):
            self._diagram.createNew()
            self._newDrawingCount = self._newDrawingCount + 1
            self._setFilePath(f'Untitled {self._newDrawingCount}')
            self._setDrawingVisible(True)

    def openDrawing(self, path: str = '') -> None:
        # Prompt the user for the file path if none is passed as an argument
        if (path == ''):
            fileFilter = 'Jade Diagram (*.jdm);;All Files (*)'
            options = QFileDialog.Option(0) if (self._promptOverwrite) else QFileDialog.Option.DontConfirmOverwrite
            (path, _) = QFileDialog.getOpenFileName(self, 'Open File', self._workingDir, fileFilter, '', options)

        # If a valid path was selected or provided, proceed with the open operation
        if (path != ''):
            # Close any open drawing before proceeding
            self.closeDrawing()

            # Open an existing drawing only if there is no open drawing (i.e. close was successful or unneeded)
            if (not self.isDrawingVisible()):
                # Use the selected path to load the drawing from file
                if (self._diagram.loadFromFile(path)):
                    self._setFilePath(path)
                    self._setDrawingVisible(True)

                # Update the cached working directory
                self._workingDir = os.path.dirname(path)

    def saveDrawing(self, path: str = '') -> None:
        if (self.isDrawingVisible()):
            if (path == '' and self._filePath.startswith('Untitled')):
                # If no path is provided and self._filePath is invalid, then do a 'save-as' instead
                self.saveDrawingAs()
            else:
                # Use either the provided path or the cached self._filePath to save the drawing to file
                if (path == ''):
                    path = self._filePath
                if (self._diagram.saveToFile(path)):
                    self._setFilePath(path)

    def saveDrawingAs(self) -> None:
        if (self.isDrawingVisible()):
            # Prompt the user for a new file path
            path = self._workingDir if (self._filePath.startswith('Untitled')) else self._filePath
            fileFilter = 'Jade Diagram (*.jdm);;All Files (*)'
            options = QFileDialog.Option(0) if (self._promptOverwrite) else QFileDialog.Option.DontConfirmOverwrite
            (path, _) = QFileDialog.getSaveFileName(self, 'Save File', path, fileFilter, '', options)

            # If a valid path was selected, proceed with the save operation
            if (path != ''):
                # Ensure that the selected path ends with the proper file suffix
                if (not path.endswith('.jdm')):
                    path = f'{path}.jdm'

                # Use the selected path to save the drawing to file
                if (self._diagram.saveToFile(path)):
                    self._setFilePath(path)

                # Update the cached working directory
                self._workingDir = os.path.dirname(path)

    def closeDrawing(self) -> None:
        if (self.isDrawingVisible()):
            proceedToClose = True

            if (self._promptCloseUnsaved and not self._diagram.isClean()):
                # If drawing has unsaved changes, prompt the user whether to save before closing
                text = f'Save changes to {os.path.basename(self._filePath)} before closing?'
                buttons = (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                           QMessageBox.StandardButton.Cancel)
                defaultButton = QMessageBox.StandardButton.Yes
                selectedButton = QMessageBox.question(self, 'Save Changes', text, buttons, defaultButton)

                # If the Yes button was selected, so a 'save' or 'save-as' operation as needed
                if (selectedButton == QMessageBox.StandardButton.Yes):
                    if (self._filePath.startswith('Untitled')):
                        self.saveDrawingAs()
                    else:
                        self.saveDrawing()

                # Allow the close to proceed if the user clicked Yes and the save was successful or
                # if the user clicked No
                proceedToClose = ((selectedButton == QMessageBox.StandardButton.Yes and self._diagram.isClean()) or
                                  selectedButton == QMessageBox.StandardButton.No)

            if (proceedToClose):
                # Hide the drawing and clear it to its default state
                self._setDrawingVisible(False)
                self._setFilePath('')

    def isDrawingVisible(self) -> bool:
        return self._diagram.isVisible()

    def filePath(self) -> str:
        return self._filePath

    # ==================================================================================================================

    def exportPng(self) -> None:
        if (self.isDrawingVisible()):
            page = self._diagram.currentPage()
            if (page):
                # Prompt the user for a new file path
                if (self._filePath.startswith('Untitled')):
                    path = os.path.join(self._workingDir, f'{page.name()}.png')
                else:
                    path = os.path.join(os.path.dirname(self._filePath), f'{page.name()}.png')

                fileFilter = 'Portable Network Graphics (*.png);;All Files (*)'
                options = QFileDialog.Option(0) if (self._promptOverwrite) else QFileDialog.Option.DontConfirmOverwrite
                (path, _) = QFileDialog.getSaveFileName(self, 'Export PNG', path, fileFilter, '', options)

                # If a valid path was selected, proceed with the save operation
                if (path != ''):
                    # Ensure that the selected path ends with the proper file suffix
                    if (not path.endswith('.png')):
                        path = f'{path}.png'

                    # Use the selected path to export the drawing to a PNG image
                    exportOptionsDialog = PngSvgExportOptionsDialog(self._pngSvgExportScale, page.sceneRect().size(),
                                                                    self)
                    if (exportOptionsDialog.exec() == PngSvgExportOptionsDialog.DialogCode.Accepted):
                        self._pngSvgExportScale = exportOptionsDialog.scale()

                        pngImage = QImage(round(page.sceneRect().width() * self._pngSvgExportScale),
                                          round(page.sceneRect().height() * self._pngSvgExportScale),
                                          QImage.Format.Format_ARGB32)
                        with QPainter(pngImage) as painter:
                            painter.scale(self._pngSvgExportScale, self._pngSvgExportScale)
                            painter.translate(-page.sceneRect().left(), -page.sceneRect().top())
                            painter.setRenderHints((QPainter.RenderHint.Antialiasing |
                                                    QPainter.RenderHint.TextAntialiasing), True)
                            page.paint(painter, export=True)

                        pngImage.save(path)

    def exportSvg(self) -> None:
        if (self.isDrawingVisible()):
            page = self._diagram.currentPage()
            if (page):
                # Prompt the user for a new file path
                if (self._filePath.startswith('Untitled')):
                    path = os.path.join(self._workingDir, f'{page.name()}.svg')
                else:
                    path = os.path.join(os.path.dirname(self._filePath), f'{page.name()}.svg')

                fileFilter = 'Scalable Vector Graphics (*.svg);;All Files (*)'
                options = QFileDialog.Option(0) if (self._promptOverwrite) else QFileDialog.Option.DontConfirmOverwrite
                (path, _) = QFileDialog.getSaveFileName(self, 'Export SVG', path, fileFilter, '', options)

                # If a valid path was selected, proceed with the save operation
                if (path != ''):
                    # Ensure that the selected path ends with the proper file suffix
                    if (not path.endswith('.svg')):
                        path = f'{path}.svg'

                    # Use the selected path to export the drawing to an SVG image
                    exportOptionsDialog = PngSvgExportOptionsDialog(self._pngSvgExportScale, page.sceneRect().size(),
                                                                    self)
                    if (exportOptionsDialog.exec() == PngSvgExportOptionsDialog.DialogCode.Accepted):
                        self._pngSvgExportScale = exportOptionsDialog.scale()

                        svgWriter = SvgWriter(page, self._pngSvgExportScale)
                        svgWriter.write(path)

    def exportOdg(self) -> None:
        if (self.isDrawingVisible()):
            # Prompt the user for a new file path
            if (self._filePath.startswith('Untitled')):
                path = os.path.join(self._workingDir, f'{self._filePath}.odg')
            elif (self._filePath.lower().endswith('.jdm')):
                path = f'{self._filePath[:-4]}.odg'
            else:
                path = f'{self._filePath}.odg'

            fileFilter = 'OpenDocument Graphics (*.odg);;All Files (*)'
            options = QFileDialog.Option(0) if (self._promptOverwrite) else QFileDialog.Option.DontConfirmOverwrite
            (path, _) = QFileDialog.getSaveFileName(self, 'Export ODG', path, fileFilter, '', options)

            # If a valid path was selected, proceed with the save operation
            if (path != ''):
                # Ensure that the selected path ends with the proper file suffix
                if (not path.endswith('.odg')):
                    path = f'{path}.odg'

                # Allow user to change various ODG export options
                dialog = OdgVsdxExportOptionsDialog(self._diagram, self._odgVsdxUnits, self._odgVsdxScale,
                                                    self._odgVsdxPageSize, self._odgVsdxPageMargins,
                                                    self._odgVsdxBackgroundColor, self)
                if (dialog.exec() == OdgVsdxExportOptionsDialog.DialogCode.Accepted):
                    self._odgVsdxUnits = dialog.units()
                    self._odgVsdxScale = dialog.scale()
                    if (dialog.pageSize() != dialog.autoPageSize()):
                        self._odgVsdxPageSize = dialog.pageSize()
                    if (dialog.pageMargins() != dialog.autoPageMargins()):
                        self._odgVsdxPageMargins = dialog.pageMargins()
                    if (dialog.backgroundColor() != dialog.autoBackgroundColor()):
                        self._odgVsdxBackgroundColor = dialog.backgroundColor()

                # Use the selected path to export the drawing to an ODG document
                odgWriter = OdgWriter(self._diagram, self._odgVsdxUnits, self._odgVsdxScale,
                                      self._odgVsdxPageSize, self._odgVsdxPageMargins, self._odgVsdxBackgroundColor)
                odgWriter.write(path)

    def exportVsdx(self) -> None:
        if (self.isDrawingVisible()):
            # Prompt the user for a new file path
            if (self._filePath.startswith('Untitled')):
                path = os.path.join(self._workingDir, f'{self._filePath}.vsdx')
            elif (self._filePath.lower().endswith('.jdm')):
                path = f'{self._filePath[:-4]}.vsdx'
            else:
                path = f'{self._filePath}.vsdx'

            fileFilter = 'Visio Drawing (*.vsdx);;All Files (*)'
            options = QFileDialog.Option(0) if (self._promptOverwrite) else QFileDialog.Option.DontConfirmOverwrite
            (path, _) = QFileDialog.getSaveFileName(self, 'Export VSDX', path, fileFilter, '', options)

            # If a valid path was selected, proceed with the save operation
            if (path != ''):
                # Ensure that the selected path ends with the proper file suffix
                if (not path.endswith('.vsdx')):
                    path = f'{path}.vsdx'

                # Use the selected path to export the drawing to a Visio document
                vsdxWriter = VsdxWriter(self._diagram)
                vsdxWriter.write(path)

    # ==================================================================================================================

    def preferences(self) -> None:
        dialog = PreferencesDialog(self)

        dialog.setPromptWhenOverwriting(self._promptOverwrite)
        dialog.setPromptWhenClosingUnsaved(self._promptCloseUnsaved)

        dialog.setDefaultSceneRect(self._diagram.defaultSceneRect())
        dialog.setDefaultBackgroundBrush(self._diagram.defaultBackgroundBrush())
        dialog.setDefaultGrid(self._diagram.defaultGrid())
        dialog.setDefaultGridVisible(self._diagram.isDefaultGridVisible())
        dialog.setDefaultGridBrush(self._diagram.defaultGridBrush())
        dialog.setDefaultGridSpacingMajor(self._diagram.defaultGridSpacingMajor())
        dialog.setDefaultGridSpacingMinor(self._diagram.defaultGridSpacingMinor())

        dialog.setDefaultPen(self._diagram.defaultPen())
        dialog.setDefaultBrush(self._diagram.defaultBrush())
        dialog.setDefaultStartArrow(self._diagram.defaultStartArrow())
        dialog.setDefaultEndArrow(self._diagram.defaultEndArrow())
        dialog.setDefaultFont(self._diagram.defaultFont())
        dialog.setDefaultTextAlignment(self._diagram.defaultTextAlignment())
        dialog.setDefaultTextBrush(self._diagram.defaultTextBrush())

        if (dialog.exec() == PreferencesDialog.DialogCode.Accepted):
            self._promptOverwrite = dialog.shouldPromptWhenOverwriting()
            self._promptCloseUnsaved = dialog.shouldPromptWhenClosingUnsaved()

            self._diagram.setDefaultSceneRect(dialog.defaultSceneRect())
            self._diagram.setDefaultBackgroundBrush(dialog.defaultBackgroundBrush())
            self._diagram.setDefaultGrid(dialog.defaultGrid())
            self._diagram.setDefaultGridVisible(dialog.isDefaultGridVisible())
            self._diagram.setDefaultGridBrush(dialog.defaultGridBrush())
            self._diagram.setDefaultGridSpacingMajor(dialog.defaultGridSpacingMajor())
            self._diagram.setDefaultGridSpacingMinor(dialog.defaultGridSpacingMinor())

            self._diagram.setDefaultPen(dialog.defaultPen())
            self._diagram.setDefaultBrush(dialog.defaultBrush())
            self._diagram.setDefaultStartArrow(dialog.defaultStartArrow())
            self._diagram.setDefaultEndArrow(dialog.defaultEndArrow())
            self._diagram.setDefaultFont(dialog.defaultFont())
            self._diagram.setDefaultTextAlignment(dialog.defaultTextAlignment())
            self._diagram.setDefaultTextBrush(dialog.defaultTextBrush())

    def about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    # ==================================================================================================================

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if (not event.spontaneous()):
            self._diagram.zoomFit()

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
        self._diagram.setVisible(visible)

        # Update drawing
        if (visible):
            self._diagram.zoomFit()
        else:
            self._diagram.clear()

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
        self._exportOdgAction.setEnabled(visible)
        self._exportVsdxAction.setEnabled(visible)

        self._diagram.setActionsEnabled(visible)

        # Reset export settings
        self._odgVsdxPageSize = QSizeF()
        self._odgVsdxPageMargins = QMarginsF(0, 0, 0, 0)
        self._odgVsdxBackgroundColor = QColor(255, 255, 255)

    def _setFilePath(self, path: str) -> None:
        self._filePath = path

        # Update window title
        fileName = os.path.basename(self._filePath)
        self.setWindowTitle('Jade' if (len(fileName) == 0) else f'{fileName} - Jade')

    # ==================================================================================================================

    def _setZoomComboText(self, scale: float) -> None:
        self._zoomCombo.setCurrentText(f'{scale * 100:.2f}%')

    def _setZoomLevel(self, text: str) -> None:
        if (text == 'Fit to Page'):
            self._diagram.zoomFit()
        else:
            try:
                if (text.endswith('%')):
                    scale = float(text[:-1])
                else:
                    scale = float(text)
                self._diagram.setScale(scale / 100)
                self._zoomCombo.clearFocus()
            except ValueError:
                pass

    # ==================================================================================================================

    def _saveSettings(self) -> None:
        configElement = ElementTree.Element('jade-config')

        # Main window properties
        self.writeStr(configElement, 'workingDir', self._workingDir)
        self.writeBool(configElement, 'promptOverwrite', self._promptOverwrite)
        self.writeBool(configElement, 'promptCloseUnsaved', self._promptCloseUnsaved)

        # Default drawing properties
        diagramElement = ElementTree.SubElement(configElement, 'diagramDefaults')
        self.writeFloat(diagramElement, 'sceneLeft', self._diagram.defaultSceneRect().left(), writeIfDefault=True)
        self.writeFloat(diagramElement, 'sceneTop', self._diagram.defaultSceneRect().top(), writeIfDefault=True)
        self.writeFloat(diagramElement, 'sceneWidth', self._diagram.defaultSceneRect().width(), writeIfDefault=True)
        self.writeFloat(diagramElement, 'sceneHeight', self._diagram.defaultSceneRect().height(), writeIfDefault=True)
        self.writeColor(diagramElement, 'backgroundColor', self._diagram.defaultBackgroundBrush().color(),
                        writeIfDefault=True)
        self.writeFloat(diagramElement, 'grid', self._diagram.defaultGrid(), writeIfDefault=True)
        self.writeBool(diagramElement, 'gridVisible', self._diagram.isDefaultGridVisible(), writeIfDefault=True)
        self.writeColor(diagramElement, 'gridColor', self._diagram.defaultGridBrush().color(), writeIfDefault=True)
        self.writeInt(diagramElement, 'gridSpacingMajor', self._diagram.defaultGridSpacingMajor(), writeIfDefault=True)
        self.writeInt(diagramElement, 'gridSpacingMinor', self._diagram.defaultGridSpacingMinor(), writeIfDefault=True)

        # Default item properties
        itemElement = ElementTree.SubElement(configElement, 'itemDefaults')
        self.writePen(itemElement, 'pen', self._diagram.defaultPen())
        self.writeBrush(itemElement, 'brush', self._diagram.defaultBrush())
        self.writeArrow(itemElement, 'startArrow', self._diagram.defaultStartArrow())
        self.writeArrow(itemElement, 'endArrow', self._diagram.defaultEndArrow())
        self.writeFont(itemElement, 'font', self._diagram.defaultFont())
        self.writeAlignment(itemElement, 'textAlignment', self._diagram.defaultTextAlignment())
        self.writeBrush(itemElement, 'text', self._diagram.defaultTextBrush())

        # Export settings
        exportElement = ElementTree.SubElement(configElement, 'exportSettings')
        self.writeFloat(exportElement, 'pngSvgExportScale', self._pngSvgExportScale)
        self.writeStr(exportElement, 'odgVsdxUnits', self._odgVsdxUnits)
        self.writeFloat(exportElement, 'odgVsdxExportScale', self._odgVsdxScale)

        ElementTree.indent(configElement, space='  ')
        with open('./config.xml', 'w', encoding='utf-8') as file:
            file.write(ElementTree.tostring(configElement, encoding='unicode', xml_declaration=True))
            file.write('\n')

    def _loadSettings(self) -> None:
        try:
            xml = ElementTree.parse('./config.xml')
            configElement = xml.getroot()
            if (configElement.tag == 'jade-config'):
                # Main window properties
                self._workingDir = self.readStr(configElement, 'workingDir')
                self._promptOverwrite = self.readBool(configElement, 'promptOverwrite')
                self._promptCloseUnsaved = self.readBool(configElement, 'promptCloseUnsaved')

                # Default drawing properties
                for diagramElement in configElement.findall('diagramDefaults'):
                    self._diagram.setDefaultSceneRect(QRectF(self.readFloat(diagramElement, 'sceneLeft'),
                                                             self.readFloat(diagramElement, 'sceneTop'),
                                                             self.readFloat(diagramElement, 'sceneWidth'),
                                                             self.readFloat(diagramElement, 'sceneHeight')))
                    self._diagram.setDefaultBackgroundBrush(QBrush(self.readColor(diagramElement, 'backgroundColor')))
                    self._diagram.setDefaultGrid(self.readFloat(diagramElement, 'grid'))
                    self._diagram.setDefaultGridVisible(self.readBool(diagramElement, 'gridVisible'))
                    self._diagram.setDefaultGridBrush(QBrush(self.readColor(diagramElement, 'gridColor')))
                    self._diagram.setDefaultGridSpacingMajor(self.readInt(diagramElement, 'gridSpacingMajor'))
                    self._diagram.setDefaultGridSpacingMinor(self.readInt(diagramElement, 'gridSpacingMinor'))

                # Default item properties
                for itemElement in configElement.findall('itemDefaults'):
                    self._diagram.setDefaultPen(self.readPen(itemElement, 'pen'))
                    self._diagram.setDefaultBrush(self.readBrush(itemElement, 'brush'))
                    self._diagram.setDefaultStartArrow(self.readArrow(itemElement, 'startArrow'))
                    self._diagram.setDefaultEndArrow(self.readArrow(itemElement, 'endArrow'))
                    self._diagram.setDefaultFont(self.readFont(itemElement, 'font'))
                    self._diagram.setDefaultTextAlignment(self.readAlignment(itemElement, 'textAlignment'))
                    self._diagram.setDefaultTextBrush(self.readBrush(itemElement, 'text'))

                # Export settings
                for exportElement in configElement.findall('exportSettings'):
                    self._pngSvgExportScale = self.readFloat(exportElement, 'pngSvgExportScale')
                    self._odgVsdxUnits = self.readStr(exportElement, 'odgVsdxUnits')
                    self._odgVsdxScale = self.readFloat(exportElement, 'odgVsdxExportScale')

            self._diagram.clear()
        except FileNotFoundError:
            pass

    # ==================================================================================================================

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

    def _addStatusBarLabel(self, text: str, minimumWidthText: str, signal: SignalInstance):
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
