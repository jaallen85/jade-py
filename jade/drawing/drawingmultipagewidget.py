# drawingmultipagewidget.py
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

import typing
from xml.etree import ElementTree
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QRectF
from PyQt6.QtGui import QAction, QActionGroup, QBrush, QColor, QFont, QIcon, QKeySequence, QPen, QUndoCommand, \
                        QUndoStack
from PyQt6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint
from .drawingtypes import DrawingUnits
from .drawingwidget import DrawingItemsUndoCommand, DrawingUndoCommand, DrawingWidget


class DrawingMultiPageWidget(QWidget):
    propertyChanged = pyqtSignal(str, object)

    pageInserted = pyqtSignal(DrawingWidget, int)
    pageRemoved = pyqtSignal(DrawingWidget, int)
    currentPageChanged = pyqtSignal(DrawingWidget)
    currentPageIndexChanged = pyqtSignal(int)
    currentPagePropertyChanged = pyqtSignal(str, object)

    scaleChanged = pyqtSignal(float)
    modeChanged = pyqtSignal(int)
    modeStringChanged = pyqtSignal(str)
    mouseInfoChanged = pyqtSignal(str)
    currentItemsChanged = pyqtSignal(list)
    currentItemsPropertyChanged = pyqtSignal(list)

    cleanChanged = pyqtSignal(bool)
    modifiedStringChanged = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self._defaultUnits: DrawingUnits = DrawingUnits.Millimeters
        self._defaultSceneRect: QRectF = QRectF(-20, -20, 800, 600)
        self._defaultBackgroundBrush: QBrush = QBrush(QColor(255, 255, 255))
        self._defaultGrid: float = 5.0
        self._defaultGridVisible: bool = True
        self._defaultGridBrush: QBrush = QBrush(QColor(0, 128, 128))
        self._defaultGridSpacingMajor: int = 8
        self._defaultGridSpacingMinor: int = 2

        self._defaultPen: QPen = QPen(QBrush(Qt.GlobalColor.black), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                      Qt.PenJoinStyle.RoundJoin)
        self._defaultBrush: QBrush = QBrush(Qt.GlobalColor.white)
        self._defaultStartArrow: DrawingArrow = DrawingArrow(DrawingArrow.Style.NoStyle, 10.0)
        self._defaultEndArrow: DrawingArrow = DrawingArrow(DrawingArrow.Style.NoStyle, 10.0)
        self._defaultFont: QFont = QFont('Arial')
        self._defaultFont.setPointSizeF(10)
        self._defaultTextAlignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
        self._defaultTextBrush: QBrush = QBrush(Qt.GlobalColor.black)

        self._units: DrawingUnits = self._defaultUnits
        self._grid: float = self._defaultGrid
        self._gridVisible: bool = self._defaultGridVisible
        self._gridBrush: QBrush = self._defaultGridBrush
        self._gridSpacingMajor: int = self._defaultGridSpacingMajor
        self._gridSpacingMinor: int = self._defaultGridSpacingMinor

        self._pages: list[DrawingWidget] = []
        self._currentPage: DrawingWidget | None = None
        self._newPageCount: int = 0

        self._stackedWidget: QStackedWidget = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self._stackedWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._undoStack: QUndoStack = QUndoStack()
        self._undoStack.setUndoLimit(64)
        self._undoStack.cleanChanged.connect(self.cleanChanged)                 # type: ignore
        self._undoStack.cleanChanged.connect(self._emitModifiedStringChanged)   # type: ignore

        self._createActions()
        self.currentItemsChanged.connect(self._updateActionsFromSelection)

    def _createActions(self) -> None:
        # Normal actions
        self.undoAction: QAction = self._addNormalAction('Undo', self.undo, 'icons:edit-undo.png', 'Ctrl+Z')
        self.redoAction: QAction = self._addNormalAction('Redo', self.redo, 'icons:edit-redo.png', 'Ctrl+Shift+Z')

        self.cutAction: QAction = self._addNormalAction('Cut', self.cut, 'icons:edit-cut.png', 'Ctrl+X')
        self.copyAction: QAction = self._addNormalAction('Copy', self.copy, 'icons:edit-copy.png', 'Ctrl+C')
        self.pasteAction: QAction = self._addNormalAction('Paste', self.paste, 'icons:edit-paste.png', 'Ctrl+V')
        self.deleteAction: QAction = self._addNormalAction('Delete', self.delete, 'icons:edit-delete.png', 'Delete')

        self.selectAllAction: QAction = self._addNormalAction('Select All', self.selectAll,
                                                              'icons:edit-select-all.png', 'Ctrl+A')
        self.selectNoneAction: QAction = self._addNormalAction('Select None', self.selectNone, '', 'Ctrl+Shift+A')

        self.rotateAction: QAction = self._addNormalAction('Rotate', self.rotate,
                                                           'icons:object-rotate-right.png', 'R')
        self.rotateBackAction: QAction = self._addNormalAction('Rotate Back', self.rotateBack,
                                                               'icons:object-rotate-left.png', 'Shift+R')
        self.flipHorizontalAction: QAction = self._addNormalAction('Flip Horizontal', self.flipHorizontal,
                                                                   'icons:object-flip-horizontal.png', 'F')
        self.flipVerticalAction: QAction = self._addNormalAction('Flip Vertical', self.flipVertical,
                                                                 'icons:object-flip-vertical.png', 'Shift+F')

        self.bringForwardAction: QAction = self._addNormalAction('Bring Forward', self.bringForward,
                                                                 'icons:object-bring-forward.png')
        self.sendBackwardAction: QAction = self._addNormalAction('Send Backward', self.sendBackward,
                                                                 'icons:object-send-backward.png')
        self.bringToFrontAction: QAction = self._addNormalAction('Bring to Front', self.bringToFront,
                                                                 'icons:object-bring-to-front.png')
        self.sendToBackAction: QAction = self._addNormalAction('Send to Back', self.sendToBack,
                                                               'icons:object-send-to-back.png')

        self.groupAction: QAction = self._addNormalAction('Group', self.group, 'icons:merge.png', 'Ctrl+G')
        self.ungroupAction: QAction = self._addNormalAction('Ungroup', self.ungroup, 'icons:split.png', 'Ctrl+Shift+G')

        self.insertPointAction: QAction = self._addNormalAction('Insert Point', self.insertNewItemPoint)
        self.removePointAction: QAction = self._addNormalAction('Remove Point', self.removeCurrentItemPoint)

        self.insertPageAction: QAction = self._addNormalAction('Insert Page', self.insertNewPage)
        self.removePageAction: QAction = self._addNormalAction('Remove Page', self.removeCurrentPage)

        self.zoomInAction: QAction = self._addNormalAction('Zoom In', self.zoomIn, 'icons:zoom-in.png', '.')
        self.zoomOutAction: QAction = self._addNormalAction('Zoom Out', self.zoomOut, 'icons:zoom-out.png', ',')
        self.zoomFitAction: QAction = self._addNormalAction('Zoom Fit', self.zoomFit, 'icons:zoom-fit-best.png', '/')

        # Mode actions
        self._modeActionGroup: QActionGroup = QActionGroup(self)
        self._modeActionGroup.triggered.connect(self._setModeFromAction)    # type: ignore
        self.modeChanged.connect(self._updateActionsFromMode)

        self.selectModeAction: QAction = self._addModeAction('Select Mode', '', 'icons:edit-select.png', 'Escape')
        self.scrollModeAction: QAction = self._addModeAction('Scroll Mode', '', 'icons:transform-move.png')
        self.zoomModeAction: QAction = self._addModeAction('Zoom Mode', '', 'icons:page-zoom.png')

        self.placeLineAction: QAction = self._addModeAction('Place Line', 'line', 'icons:draw-line.png')
        self.placeCurveAction: QAction = self._addModeAction('Place Curve', 'curve', 'icons:draw-curve.png')
        self.placePolylineAction: QAction = self._addModeAction('Place Polyline', 'polyline', 'icons:draw-polyline.png')
        self.placeRectAction: QAction = self._addModeAction('Place Rectangle', 'rect', 'icons:draw-rectangle.png')
        self.placeEllipseAction: QAction = self._addModeAction('Place Ellipse', 'ellipse', 'icons:draw-ellipse.png')
        self.placePolygonAction: QAction = self._addModeAction('Place Polygon', 'polygon', 'icons:draw-polygon.png')
        self.placeTextAction: QAction = self._addModeAction('Place Text', 'text', 'icons:draw-text.png')
        self.placeTextRectAction: QAction = self._addModeAction('Place Text Rectangle', 'textRect',
                                                                'icons:text-rect.png')
        self.placeTextEllipseAction: QAction = self._addModeAction('Place Text Ellipse', 'textEllipse',
                                                                   'icons:text-ellipse.png')

        self.selectModeAction.setChecked(True)

    # ==================================================================================================================

    def setDefaultUnits(self, units: DrawingUnits) -> None:
        self._defaultUnits = units

    def setDefaultSceneRect(self, rect: QRectF) -> None:
        self._defaultSceneRect = rect

    def setDefaultBackgroundBrush(self, brush: QBrush) -> None:
        self._defaultBackgroundBrush = brush

    def setDefaultGrid(self, grid: float) -> None:
        self._defaultGrid = grid

    def setDefaultGridVisible(self, visible: bool) -> None:
        self._defaultGridVisible = visible

    def seDefaultGridBrush(self, brush: QBrush) -> None:
        self._defaultGridBrush = brush

    def setDefaultGridSpacingMajor(self, spacing: int) -> None:
        self._defaultGridSpacingMajor = spacing

    def setDefaultGridSpacingMinor(self, spacing: int) -> None:
        self._defaultGridSpacingMinor = spacing

    def defaultUnits(self) -> DrawingUnits:
        return self._defaultUnits

    def defaultSceneRect(self) -> QRectF:
        return self._defaultSceneRect

    def defaultBackgroundBrush(self) -> QBrush:
        return self._defaultBackgroundBrush

    def defaultGrid(self) -> float:
        return self._defaultGrid

    def defaultGridVisible(self) -> bool:
        return self._defaultGridVisible

    def defaultGridBrush(self) -> QBrush:
        return self._defaultGridBrush

    def defaultGridSpacingMajor(self) -> int:
        return self._defaultGridSpacingMajor

    def defaultGridSpacingMinor(self) -> int:
        return self._defaultGridSpacingMinor

    # ==================================================================================================================

    def setDefaultPen(self, pen: QPen) -> None:
        self._defaultPen = pen

    def setDefaultBrush(self, brush: QBrush) -> None:
        self._defaultBrush = brush

    def setDefaultStartArrow(self, arrow: DrawingArrow) -> None:
        self._defaultStartArrow = arrow

    def setDefaultEndArrow(self, arrow: DrawingArrow) -> None:
        self._defaultEndArrow = arrow

    def setDefaultFont(self, font: QFont) -> None:
        self._defaultFont = font

    def setDefaultTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._defaultTextAlignment = alignment

    def setDefaultTextBrush(self, brush: QBrush) -> None:
        self._defaultTextBrush = brush

    def defaultPen(self) -> QPen:
        return self._defaultPen

    def defaultBrush(self) -> QBrush:
        return self._defaultBrush

    def defaultStartArrow(self) -> DrawingArrow:
        return self._defaultStartArrow

    def defaultEndArrow(self) -> DrawingArrow:
        return self._defaultEndArrow

    def defaultFont(self) -> QFont:
        return self._defaultFont

    def defaultTextAlignment(self) -> Qt.AlignmentFlag:
        return self._defaultTextAlignment

    def defaultTextBrush(self) -> QBrush:
        return self._defaultTextBrush

    # ==================================================================================================================

    def setUnits(self, units: DrawingUnits) -> None:
        if (self._units != units):
            scale = DrawingUnits.convert(1, self._units, units)

            self._units = units

            self.blockSignals(True)
            self._defaultPen.setWidthF(self._defaultPen.widthF() * scale)
            self._defaultStartArrow.setSize(self._defaultStartArrow.size() * scale)
            self._defaultEndArrow.setSize(self._defaultEndArrow.size() * scale)
            self._defaultFont.setPointSizeF(self._defaultFont.pointSizeF() * scale)
            self._grid = self._grid * scale
            for page in self._pages:
                page.setUnits(self._units)
            self.blockSignals(False)

            self.propertyChanged.emit('units', self._units)

    def setGrid(self, grid: float) -> None:
        if (self._grid != grid and grid >= 0):
            self._grid = grid

            self.blockSignals(True)
            for page in self._pages:
                page.setGrid(self._grid)
            self.blockSignals(False)

            self.propertyChanged.emit('grid', self._grid)

    def setGridVisible(self, visible: bool) -> None:
        if (self._gridVisible != visible):
            self._gridVisible = visible

            self.blockSignals(True)
            for page in self._pages:
                page.setGridVisible(self._gridVisible)
            self.blockSignals(False)

            self.propertyChanged.emit('gridVisible', self._gridVisible)

    def setGridBrush(self, brush: QBrush) -> None:
        if (self._gridBrush != brush):
            self._gridBrush = brush

            self.blockSignals(True)
            for page in self._pages:
                page.setGridBrush(self._gridBrush)
            self.blockSignals(False)

            self.propertyChanged.emit('gridBrush', self._gridBrush)

    def setGridSpacingMajor(self, spacing: int) -> None:
        if (self._gridSpacingMajor != spacing and spacing >= 0):
            self._gridSpacingMajor = spacing

            self.blockSignals(True)
            for page in self._pages:
                page.setGridSpacingMajor(self._gridSpacingMajor)
            self.blockSignals(False)

            self.propertyChanged.emit('gridSpacingMajor', self._gridSpacingMajor)

    def setGridSpacingMinor(self, spacing: int) -> None:
        if (self._gridSpacingMinor != spacing and spacing >= 0):
            self._gridSpacingMinor = spacing

            self.blockSignals(True)
            for page in self._pages:
                page.setGridSpacingMinor(self._gridSpacingMinor)
            self.blockSignals(False)

            self.propertyChanged.emit('gridSpacingMinor', self._gridSpacingMinor)

    def units(self) -> DrawingUnits:
        return self._units

    def grid(self) -> float:
        return self._grid

    def isGridVisible(self) -> bool:
        return self._gridVisible

    def gridBrush(self) -> QBrush:
        return self._gridBrush

    def gridSpacingMajor(self) -> int:
        return self._gridSpacingMajor

    def gridSpacingMinor(self) -> int:
        return self._gridSpacingMinor

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> bool:
        match (name):
            case 'units':
                if (isinstance(value, int)):
                    self.setUnits(DrawingUnits(value))
            case 'grid':
                if (isinstance(value, float)):
                    self.setGrid(value)
            case 'gridVisible':
                if (isinstance(value, bool)):
                    self.setGridVisible(value)
            case 'gridBrush':
                if (isinstance(value, QBrush)):
                    self.setGridBrush(value)
            case 'gridSpacingMajor':
                if (isinstance(value, int)):
                    self.setGridSpacingMajor(value)
            case 'gridSpacingMinor':
                if (isinstance(value, int)):
                    self.setGridSpacingMinor(value)
        return True

    def property(self, name: str) -> typing.Any:
        match (name):
            case 'units':
                return self.units().value
            case 'grid':
                return self.grid()
            case 'gridVisible':
                return self.isGridVisible()
            case 'gridBrush':
                return self.gridBrush()
            case 'gridSpacingMajor':
                return self.gridSpacingMajor()
            case 'gridSpacingMinor':
                return self.gridSpacingMinor()
        return None

    # ==================================================================================================================

    def addPage(self, page: DrawingWidget) -> None:
        self.insertPage(len(self._pages), page)

    def insertPage(self, index: int, page: DrawingWidget) -> None:
        if (page not in self._pages):
            self._pages.insert(index, page)
            self._stackedWidget.insertWidget(index, page)

            self.pageInserted.emit(page, index)

            page.setUndoForwarding(True)
            page.undoCommandCreated.connect(self._pushUndoCommand)

            page.scaleChanged.connect(self._emitScaleChanged)
            page.modeChanged.connect(self._emitModeChanged)
            page.modeStringChanged.connect(self._emitModeStringChanged)
            page.mouseInfoChanged.connect(self._emitMouseInfoChanged)
            page.currentItemsChanged.connect(self._emitCurrentItemsChanged)
            page.currentItemsPropertyChanged.connect(self._emitCurrentItemsPropertyChanged)
            page.propertyChanged.connect(self._emitCurrentPagePropertyChanged)

            self.setCurrentPage(page)

    def removePage(self, page: DrawingWidget) -> None:
        if (page in self._pages):
            index = self._pages.index(page)

            newCurrentPageIndex = -1
            if (index > 0):
                newCurrentPageIndex = index - 1
            elif (index < len(self._pages) - 1):
                newCurrentPageIndex = index + 1

            self._pages.remove(page)
            self._stackedWidget.removeWidget(page)
            page.setParent(None)    # type: ignore

            page.scaleChanged.disconnect(self._emitScaleChanged)
            page.modeChanged.disconnect(self._emitModeChanged)
            page.modeStringChanged.disconnect(self._emitModeStringChanged)
            page.mouseInfoChanged.disconnect(self._emitMouseInfoChanged)
            page.currentItemsChanged.disconnect(self._emitCurrentItemsChanged)
            page.currentItemsPropertyChanged.disconnect(self._emitCurrentItemsPropertyChanged)
            page.propertyChanged.disconnect(self._emitCurrentPagePropertyChanged)

            self.pageRemoved.emit(page, index)

            self.setCurrentPageIndex(newCurrentPageIndex)

    def movePage(self, page: DrawingWidget, newIndex: int) -> None:
        if (page in self._pages):
            index = self._pages.index(page)

            self._pages.remove(page)
            self._stackedWidget.removeWidget(page)
            page.setParent(None)    # type: ignore

            self.pageRemoved.emit(page, index)

            self._pages.insert(newIndex, page)
            self._stackedWidget.insertWidget(newIndex, page)

            self.pageInserted.emit(page, newIndex)

            self.setCurrentPage(page)

    def pages(self) -> list[DrawingWidget]:
        return self._pages

    # ==================================================================================================================

    def setCurrentPage(self, page: DrawingWidget | None) -> None:
        # Only allow us to use a page that is part of the view as the current page, but also allow None
        if (page is None or page in self._pages):
            self.setSelectMode()
            self.setSelectedItems([])

            self._currentPage = page
            if (self._currentPage is not None):
                self._stackedWidget.setCurrentWidget(self._currentPage)
            else:
                self._stackedWidget.setCurrentIndex(-1)

            self.currentPageChanged.emit(self._currentPage)
            self.currentPageIndexChanged.emit(self.currentPageIndex())

            self.scaleChanged.emit(self.scale())
            self.mouseInfoChanged.emit('')

    def setCurrentPageIndex(self, index: int) -> None:
        if (0 <= index < len(self._pages)):
            self.setCurrentPage(self._pages[index])
        else:
            self.setCurrentPage(None)

    def currentPage(self) -> DrawingWidget | None:
        return self._currentPage

    def currentPageIndex(self) -> int:
        if (self._currentPage is not None and self._currentPage in self._pages):
            return self._pages.index(self._currentPage)
        return -1

    # ==================================================================================================================

    def createNew(self) -> None:
        self.insertNewPage()
        self._undoStack.clear()

    def loadFromFile(self, path: str) -> bool:
        self.clear()

        xml = ElementTree.parse(path)
        drawingElement = xml.getroot()
        if (drawingElement.tag == 'jade-drawing'):
            self.setUnits(DrawingUnits(DrawingItem.readIntAttribute(drawingElement, 'units', 0)))
            self.setGrid(DrawingItem.readFloatAttribute(drawingElement, 'grid', 0))
            self.setGridVisible(DrawingItem.readBoolAttribute(drawingElement, 'gridVisible', False))
            self.setGridBrush(QBrush(DrawingItem.readColorAttribute(drawingElement, 'gridColor')))
            self.setGridSpacingMajor(DrawingItem.readIntAttribute(drawingElement, 'gridSpacingMajor', 0))
            self.setGridSpacingMinor(DrawingItem.readIntAttribute(drawingElement, 'gridSpacingMinor', 0))

            for index, pageElement in enumerate(drawingElement.findall('page')):
                newPage = DrawingWidget()

                newPage.setName(DrawingItem.readStrAttribute(pageElement, 'name', f'Page{index}'))
                newPage.setSceneRect(QRectF(DrawingItem.readFloatAttribute(pageElement, 'sceneLeft', 0.0),
                                            DrawingItem.readFloatAttribute(pageElement, 'sceneTop', 0.0),
                                            DrawingItem.readFloatAttribute(pageElement, 'sceneWidth', 0.0),
                                            DrawingItem.readFloatAttribute(pageElement, 'sceneHeight', 0.0)))
                newPage.setBackgroundBrush(QBrush(DrawingItem.readColorAttribute(pageElement, 'backgroundColor')))

                newPage.setUnits(self._units)
                newPage.setGrid(self._grid)
                newPage.setGridVisible(self._gridVisible)
                newPage.setGridBrush(self._gridBrush)
                newPage.setGridSpacingMajor(self._gridSpacingMajor)
                newPage.setGridSpacingMinor(self._gridSpacingMinor)

                items = DrawingItem.readItemsFromXml(pageElement)
                for item in items:
                    newPage.addItem(item)

                self.addPage(newPage)
                self.zoomFit()

            self._undoStack.setClean()
            return True

        return False

    def saveToFile(self, path: str) -> bool:
        drawingElement = ElementTree.Element('jade-drawing')

        DrawingItem.writeIntAttribute(drawingElement, 'units', self.units().value)
        DrawingItem.writeFloatAttribute(drawingElement, 'grid', self.grid())
        DrawingItem.writeBoolAttribute(drawingElement, 'gridVisible', self.isGridVisible())
        DrawingItem.writeColorAttribute(drawingElement, 'gridColor', self.gridBrush().color())
        DrawingItem.writeIntAttribute(drawingElement, 'gridSpacingMajor', self.gridSpacingMajor())
        DrawingItem.writeIntAttribute(drawingElement, 'gridSpacingMinor', self.gridSpacingMinor())

        for page in self._pages:
            pageElement = ElementTree.SubElement(drawingElement, 'page')
            DrawingItem.writeStrAttribute(pageElement, 'name', page.name())
            DrawingItem.writeFloatAttribute(pageElement, 'sceneLeft', page.sceneRect().left())
            DrawingItem.writeFloatAttribute(pageElement, 'sceneTop', page.sceneRect().top())
            DrawingItem.writeFloatAttribute(pageElement, 'sceneWidth', page.sceneRect().width())
            DrawingItem.writeFloatAttribute(pageElement, 'sceneHeight', page.sceneRect().height())
            DrawingItem.writeColorAttribute(pageElement, 'backgroundColor', page.backgroundBrush().color())

            DrawingItem.writeItemsToXml(pageElement, page.items())

        with open(path, 'w', encoding='utf-8') as file:
            file.write(ElementTree.tostring(drawingElement, encoding='unicode', xml_declaration=True))

        self._undoStack.setClean()
        return True

    def clear(self) -> None:
        self._undoStack.clear()

        while (len(self._pages) > 0):
            page = self._pages[-1]
            self.removePage(page)
            del page
        self._newPageCount = 0

        self._units = self._defaultUnits
        self._grid = self._defaultGrid
        self._gridVisible = self._defaultGridVisible
        self._gridBrush = self._defaultGridBrush
        self._gridSpacingMajor = self._defaultGridSpacingMajor
        self._gridSpacingMinor = self._defaultGridSpacingMinor

    # ==================================================================================================================

    def undo(self) -> None:
        if (self.mode() == DrawingWidget.Mode.SelectMode):
            # Get the command that will be undone by the call to self._undoStack.undo()
            command = self._undoStack.command(self._undoStack.index() - 1)
            if (isinstance(command, DrawingUndoCommand)):
                self.setCurrentPage(command.widget())
                if (command.viewRect().isValid()):
                    self.zoomToRect(command.viewRect())
                if (isinstance(command, DrawingItemsUndoCommand)):
                    self.setSelectedItems(command.items())
                else:
                    self.setSelectedItems([])
            else:
                self.setSelectedItems([])

            self._undoStack.undo()
        else:
            self.setSelectMode()

    def redo(self) -> None:
        if (self.mode() == DrawingWidget.Mode.SelectMode):
            # Get the command that will be redone by the call to self._undoStack.redo()
            command = self._undoStack.command(self._undoStack.index())
            if (isinstance(command, DrawingUndoCommand)):
                self.setCurrentPage(command.widget())
                if (command.viewRect().isValid()):
                    self.zoomToRect(command.viewRect())
                if (isinstance(command, DrawingItemsUndoCommand)):
                    self.setSelectedItems(command.items())
                else:
                    self.setSelectedItems([])
            else:
                self.setSelectedItems([])

            self._undoStack.redo()
        else:
            self.setSelectMode()

    def isClean(self) -> bool:
        return self._undoStack.isClean()

    def _pushUndoCommand(self, command: QUndoCommand) -> None:
        self._undoStack.push(command)

    # ==================================================================================================================

    def cut(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.cut()

    def copy(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.copy()

    def paste(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.paste()

    def delete(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.delete()

    # ==================================================================================================================

    def setSelectedItems(self, items: list[DrawingItem]):
        if (self._currentPage is not None):
            self._currentPage.setSelectedItems(items)

    def selectAll(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.selectAll()

    def selectNone(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.selectNone()

    def selectedItems(self) -> list[DrawingItem]:
        if (self._currentPage is not None):
            return self._currentPage.selectedItems()
        return []

    # ==================================================================================================================

    def moveCurrentItemsDelta(self, delta: QPointF) -> None:
        if (self._currentPage is not None):
            self._currentPage.moveCurrentItemsDelta(delta)

    def moveCurrentItem(self, position: QPointF) -> None:
        if (self._currentPage is not None):
            self._currentPage.moveCurrentItem(position)

    def resizeCurrentItem(self, point: DrawingItemPoint, position: QPointF) -> None:
        if (self._currentPage is not None):
            self._currentPage.resizeCurrentItem(point, position)

    # ==================================================================================================================

    def rotate(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.rotate()

    def rotateBack(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.rotateBack()

    def flipHorizontal(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.flipHorizontal()

    def flipVertical(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.flipVertical()

    # ==================================================================================================================

    def bringForward(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.bringForward()

    def sendBackward(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.sendBackward()

    def bringToFront(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.bringToFront()

    def sendToBack(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.sendToBack()

    # ==================================================================================================================

    def group(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.group()

    def ungroup(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.ungroup()

    # ==================================================================================================================

    def insertNewItemPoint(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.insertNewItemPoint()

    def removeCurrentItemPoint(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.removeCurrentItemPoint()

    # ==================================================================================================================

    def insertNewPage(self) -> None:
        # Determine a unique name for the new page
        name = ''
        nameIsUnique = False
        while (not nameIsUnique):
            self._newPageCount = self._newPageCount + 1
            name = f'Page{self._newPageCount}'
            nameIsUnique = True
            for page in self._pages:
                if (name == page.name()):
                    nameIsUnique = False
                    break

        # Create the new page and add it to the view
        newPage = DrawingWidget()
        newPage.setName(name)
        newPage.setUnits(self._units)
        newPage.setSceneRect(self._defaultSceneRect)
        newPage.setBackgroundBrush(self._defaultBackgroundBrush)
        newPage.setGrid(self._grid)
        newPage.setGridVisible(self._gridVisible)
        newPage.setGridBrush(self._gridBrush)
        newPage.setGridSpacingMajor(self._gridSpacingMajor)
        newPage.setGridSpacingMinor(self._gridSpacingMinor)
        self._pushUndoCommand(DrawingInsertPageCommand(self, newPage, self.currentPageIndex() + 1))
        self.zoomFit()

    def removeCurrentPage(self) -> None:
        if (self._currentPage is not None):
            self._pushUndoCommand(DrawingRemovePageCommand(self, self._currentPage))

    def moveCurrentPage(self, newIndex: int) -> None:
        if (self._currentPage is not None):
            self._pushUndoCommand(DrawingMovePageCommand(self, self._currentPage, newIndex))

    def renameCurrentPage(self, name: str) -> None:
        if (self._currentPage is not None):
            self._currentPage.updateProperty('name', name)

    # ==================================================================================================================

    def setScale(self, scale: float) -> None:
        if (self._currentPage is not None):
            self._currentPage.setScale(scale)

    def zoomToRect(self, rect: QRectF = QRectF()) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomToRect(rect)

    def zoomIn(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomIn()

    def zoomOut(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomOut()

    def zoomFit(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomFit()

    def scale(self) -> float:
        if (self._currentPage is not None):
            return self._currentPage.scale()
        return 1.0

    # ==================================================================================================================

    def setSelectMode(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.setSelectMode()

    def setScrollMode(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.setScrollMode()

    def setZoomMode(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.setZoomMode()

    def setPlaceMode(self, items: list[DrawingItem]) -> None:
        if (self._currentPage is not None):
            self._currentPage.setPlaceMode(items)

    def mode(self) -> DrawingWidget.Mode:
        if (self._currentPage is not None):
            return self._currentPage.mode()
        return DrawingWidget.Mode.SelectMode

    # ==================================================================================================================

    def updateProperty(self, name: str, value: typing.Any) -> None:
        self._pushUndoCommand(DrawingSetPropertyCommand(self, name, value))

    def updateCurrentPageProperty(self, name: str, value: typing.Any) -> None:
        if (self._currentPage is not None):
            self._currentPage.updateProperty(name, value)

    def updateCurrentItemsProperty(self, name: str, value: typing.Any) -> None:
        if (self._currentPage is not None):
            self._currentPage.updateCurrentItemsProperty(name, value)

    # ==================================================================================================================

    def _emitScaleChanged(self, scale: float) -> None:
        self.scaleChanged.emit(scale)

    def _emitModeChanged(self, mode: DrawingWidget.Mode) -> None:
        self.modeChanged.emit(mode)

    def _emitModeStringChanged(self, modeStr: str) -> None:
        self.modeStringChanged.emit(modeStr)

    def _emitMouseInfoChanged(self, mouseInfo: str) -> None:
        self.mouseInfoChanged.emit(mouseInfo)

    def _emitCurrentItemsChanged(self, items: list[DrawingItem]) -> None:
        self.currentItemsChanged.emit(items)

    def _emitCurrentItemsPropertyChanged(self, items: list[DrawingItem]) -> None:
        self.currentItemsPropertyChanged.emit(items)

    def _emitCurrentPagePropertyChanged(self, name: str, value: typing.Any) -> None:
        self.currentPagePropertyChanged.emit(name, value)

    def _emitModifiedStringChanged(self, clean: bool) -> None:
        self.modifiedStringChanged.emit('Modified' if (not clean) else '')

    # ==================================================================================================================

    def setActionsEnabled(self, enable: bool) -> None:
        for action in self.actions():
            action.setEnabled(enable)
        for action in self._modeActionGroup.actions():
            action.setEnabled(enable)

    def _addNormalAction(self, text: str, slot: typing.Callable, iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)      # type: ignore
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        self.addAction(action)
        return action

    def _addModeAction(self, text: str, itemKey: str = '', iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self._modeActionGroup)
        action.setProperty('key', itemKey)
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        action.setCheckable(True)
        action.setActionGroup(self._modeActionGroup)
        return action

    def _setModeFromAction(self, action: QAction) -> None:
        if (action == self.selectModeAction):
            self.setSelectMode()
        elif (action == self.scrollModeAction):
            self.setScrollMode()
        elif (action == self.zoomModeAction):
            self.setZoomMode()
        else:
            if (self._currentPage is not None):
                item = DrawingItem.createItem(action.property('key'))
                if (item is not None):
                    # Set default item properties
                    item.setProperty('pen', QPen(self._defaultPen))
                    item.setProperty('brush', QBrush(self._defaultBrush))
                    item.setProperty('startArrow', DrawingArrow(self._defaultStartArrow.style(),
                                                                self._defaultStartArrow.size()))
                    item.setProperty('endArrow', DrawingArrow(self._defaultEndArrow.style(),
                                                              self._defaultEndArrow.size()))
                    item.setProperty('font', QFont(self._defaultFont))
                    item.setProperty('textAlignment', Qt.AlignmentFlag(self._defaultTextAlignment))
                    item.setProperty('textBrush', QBrush(self._defaultTextBrush))

                    # Set default item geometry, if necessary
                    if (item.placeType() == DrawingItem.PlaceType.PlaceByMouseRelease):
                        item.setInitialGeometry(self._currentPage.sceneRect(), self._grid)

                    # Begin place mode
                    self.setPlaceMode([item])
                else:
                    # Revert back to select mode if no new item was able to be created
                    self.setSelectMode()

    def _updateActionsFromMode(self, mode: int):
        if (mode == DrawingWidget.Mode.SelectMode.value and not self.selectModeAction.isChecked()):
            self.selectModeAction.setChecked(True)

    def _updateActionsFromSelection(self) -> None:
        if (self._currentPage is not None):
            self.groupAction.setEnabled(self._currentPage.groupAction.isEnabled())
            self.ungroupAction.setEnabled(self._currentPage.ungroupAction.isEnabled())
            self.insertPointAction.setEnabled(self._currentPage.insertPointAction.isEnabled())
            self.removePointAction.setEnabled(self._currentPage.removePointAction.isEnabled())


# ======================================================================================================================

class DrawingInsertPageCommand(QUndoCommand):
    def __init__(self, widget: DrawingMultiPageWidget, page: DrawingWidget, index: int,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__('Insert Page', parent)

        # Assumes page is not already a member of widget.pages()
        self._widget: DrawingMultiPageWidget = widget
        self._page: DrawingWidget = page
        self._index: int = index
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._page

    def redo(self) -> None:
        self._undone = False
        self._widget.insertPage(self._index, self._page)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.removePage(self._page)
        self._undone = True


# ======================================================================================================================

class DrawingRemovePageCommand(QUndoCommand):
    def __init__(self, widget: DrawingMultiPageWidget, page: DrawingWidget, parent: QUndoCommand | None = None) -> None:
        super().__init__('Remove Page', parent)

        # Assumes page is a member of widget.pages()
        self._widget: DrawingMultiPageWidget = widget
        self._page: DrawingWidget = page
        self._index: int = self._widget.pages().index(self._page)
        self._undone: bool = True

    def __del__(self) -> None:
        if (not self._undone):
            del self._page

    def redo(self) -> None:
        self._undone = False
        self._widget.removePage(self._page)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.insertPage(self._index, self._page)
        self._undone = True


# ======================================================================================================================

class DrawingMovePageCommand(QUndoCommand):
    def __init__(self, widget: DrawingMultiPageWidget, page: DrawingWidget, newIndex: int,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__('Remove Page', parent)

        # Assumes page is a member of widget.pages()
        self._widget: DrawingMultiPageWidget = widget
        self._page: DrawingWidget = page
        self._newIndex: int = newIndex
        self._originalIndex: int = self._widget.pages().index(self._page)

    def redo(self) -> None:
        self._widget.movePage(self._page, self._newIndex)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.movePage(self._page, self._originalIndex)


# ======================================================================================================================

class DrawingSetPropertyCommand(QUndoCommand):
    def __init__(self, widget: DrawingMultiPageWidget, name: str, value: typing.Any,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__('Set Property', parent)

        self._widget: DrawingMultiPageWidget = widget
        self._name: str = name
        self._value: typing.Any = value

        self._originalValue: typing.Any = self._widget.property(self._name)

    def redo(self) -> None:
        self._widget.setProperty(self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.setProperty(self._name, self._originalValue)
