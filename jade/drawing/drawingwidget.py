# drawingwidget.py
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
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, Signal
from PySide6.QtGui import QAction, QActionGroup, QBrush, QColor, QFont, QIcon, QKeySequence, QPen, QUndoCommand, \
                        QUndoStack
from PySide6.QtWidgets import QMenu, QStackedWidget, QVBoxLayout, QWidget
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint
from .drawingpagewidget import DrawingItemsUndoCommand, DrawingUndoCommand, DrawingPageWidget
from .drawingxmlinterface import DrawingXmlInterface


class DrawingWidget(QWidget, DrawingXmlInterface):
    propertyChanged = Signal(str, object)

    pageInserted = Signal(DrawingPageWidget, int)
    pageRemoved = Signal(DrawingPageWidget, int)
    currentPageChanged = Signal(DrawingPageWidget)
    currentPageIndexChanged = Signal(int)
    currentPagePropertyChanged = Signal(str, object)

    scaleChanged = Signal(float)
    modeChanged = Signal(int)
    modeStringChanged = Signal(str)
    mouseInfoChanged = Signal(str)
    currentItemsChanged = Signal(list)
    currentItemsPropertyChanged = Signal(list)

    cleanChanged = Signal(bool)
    modifiedStringChanged = Signal(str)

    def __init__(self) -> None:
        super().__init__()

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

        self._grid: float = self._defaultGrid
        self._gridVisible: bool = self._defaultGridVisible
        self._gridBrush: QBrush = self._defaultGridBrush
        self._gridSpacingMajor: int = self._defaultGridSpacingMajor
        self._gridSpacingMinor: int = self._defaultGridSpacingMinor

        self._pages: list[DrawingPageWidget] = []
        self._currentPage: DrawingPageWidget | None = None
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
        self._createContextMenus()
        self.currentItemsChanged.connect(self._updateActionsFromSelection)
        self.currentItemsPropertyChanged.connect(self._updateActionsFromSelection)

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

        self.rotateAction: QAction = self._addNormalAction('Rotate', self.rotateCurrentItems,
                                                           'icons:object-rotate-right.png', 'R')
        self.rotateBackAction: QAction = self._addNormalAction('Rotate Back', self.rotateBackCurrentItems,
                                                               'icons:object-rotate-left.png', 'Shift+R')
        self.flipHorizontalAction: QAction = self._addNormalAction('Flip Horizontal', self.flipCurrentItemsHorizontal,
                                                                   'icons:object-flip-horizontal.png', 'F')
        self.flipVerticalAction: QAction = self._addNormalAction('Flip Vertical', self.flipCurrentItemsVertical,
                                                                 'icons:object-flip-vertical.png', 'Shift+F')

        self.bringForwardAction: QAction = self._addNormalAction('Bring Forward', self.bringCurrentItemsForward,
                                                                 'icons:object-bring-forward.png')
        self.sendBackwardAction: QAction = self._addNormalAction('Send Backward', self.sendCurrentItemsBackward,
                                                                 'icons:object-send-backward.png')
        self.bringToFrontAction: QAction = self._addNormalAction('Bring to Front', self.bringCurrentItemsToFront,
                                                                 'icons:object-bring-to-front.png')
        self.sendToBackAction: QAction = self._addNormalAction('Send to Back', self.sendCurrentItemsToBack,
                                                               'icons:object-send-to-back.png')

        self.groupAction: QAction = self._addNormalAction('Group', self.groupCurrentItems, 'icons:merge.png', 'Ctrl+G')
        self.ungroupAction: QAction = self._addNormalAction('Ungroup', self.ungroupCurrentItem, 'icons:split.png',
                                                            'Ctrl+Shift+G')

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

    def _createContextMenus(self) -> None:
        self._noItemContextMenu: QMenu = QMenu()
        self._noItemContextMenu.addAction(self.undoAction)
        self._noItemContextMenu.addAction(self.redoAction)
        self._noItemContextMenu.addSeparator()
        self._noItemContextMenu.addAction(self.cutAction)
        self._noItemContextMenu.addAction(self.copyAction)
        self._noItemContextMenu.addAction(self.pasteAction)
        self._noItemContextMenu.addSeparator()
        self._noItemContextMenu.addAction(self.zoomInAction)
        self._noItemContextMenu.addAction(self.zoomOutAction)
        self._noItemContextMenu.addAction(self.zoomFitAction)

        self._singleItemContextMenu: QMenu = QMenu()
        self._singleItemContextMenu.addAction(self.cutAction)
        self._singleItemContextMenu.addAction(self.copyAction)
        self._singleItemContextMenu.addAction(self.pasteAction)
        self._singleItemContextMenu.addAction(self.deleteAction)
        self._singleItemContextMenu.addSeparator()
        self._singleItemContextMenu.addAction(self.rotateAction)
        self._singleItemContextMenu.addAction(self.rotateBackAction)
        self._singleItemContextMenu.addAction(self.flipHorizontalAction)
        self._singleItemContextMenu.addAction(self.flipVerticalAction)
        self._singleItemContextMenu.addSeparator()
        self._singleItemContextMenu.addAction(self.bringForwardAction)
        self._singleItemContextMenu.addAction(self.sendBackwardAction)
        self._singleItemContextMenu.addAction(self.bringToFrontAction)
        self._singleItemContextMenu.addAction(self.sendToBackAction)

        self._singlePolyItemContextMenu: QMenu = QMenu()
        self._singlePolyItemContextMenu.addAction(self.cutAction)
        self._singlePolyItemContextMenu.addAction(self.copyAction)
        self._singlePolyItemContextMenu.addAction(self.pasteAction)
        self._singlePolyItemContextMenu.addAction(self.deleteAction)
        self._singlePolyItemContextMenu.addSeparator()
        self._singlePolyItemContextMenu.addAction(self.insertPointAction)
        self._singlePolyItemContextMenu.addAction(self.removePointAction)
        self._singlePolyItemContextMenu.addSeparator()
        self._singlePolyItemContextMenu.addAction(self.rotateAction)
        self._singlePolyItemContextMenu.addAction(self.rotateBackAction)
        self._singlePolyItemContextMenu.addAction(self.flipHorizontalAction)
        self._singlePolyItemContextMenu.addAction(self.flipVerticalAction)
        self._singlePolyItemContextMenu.addSeparator()
        self._singlePolyItemContextMenu.addAction(self.bringForwardAction)
        self._singlePolyItemContextMenu.addAction(self.sendBackwardAction)
        self._singlePolyItemContextMenu.addAction(self.bringToFrontAction)
        self._singlePolyItemContextMenu.addAction(self.sendToBackAction)

        self._singleGroupItemContextMenu: QMenu = QMenu()
        self._singleGroupItemContextMenu.addAction(self.cutAction)
        self._singleGroupItemContextMenu.addAction(self.copyAction)
        self._singleGroupItemContextMenu.addAction(self.pasteAction)
        self._singleGroupItemContextMenu.addAction(self.deleteAction)
        self._singleGroupItemContextMenu.addSeparator()
        self._singleGroupItemContextMenu.addAction(self.rotateAction)
        self._singleGroupItemContextMenu.addAction(self.rotateBackAction)
        self._singleGroupItemContextMenu.addAction(self.flipHorizontalAction)
        self._singleGroupItemContextMenu.addAction(self.flipVerticalAction)
        self._singleGroupItemContextMenu.addSeparator()
        self._singleGroupItemContextMenu.addAction(self.bringForwardAction)
        self._singleGroupItemContextMenu.addAction(self.sendBackwardAction)
        self._singleGroupItemContextMenu.addAction(self.bringToFrontAction)
        self._singleGroupItemContextMenu.addAction(self.sendToBackAction)
        self._singleGroupItemContextMenu.addSeparator()
        self._singleGroupItemContextMenu.addAction(self.groupAction)
        self._singleGroupItemContextMenu.addAction(self.ungroupAction)

        self._multipleItemContextMenu: QMenu = QMenu()
        self._multipleItemContextMenu.addAction(self.cutAction)
        self._multipleItemContextMenu.addAction(self.copyAction)
        self._multipleItemContextMenu.addAction(self.pasteAction)
        self._multipleItemContextMenu.addAction(self.deleteAction)
        self._multipleItemContextMenu.addSeparator()
        self._multipleItemContextMenu.addAction(self.rotateAction)
        self._multipleItemContextMenu.addAction(self.rotateBackAction)
        self._multipleItemContextMenu.addAction(self.flipHorizontalAction)
        self._multipleItemContextMenu.addAction(self.flipVerticalAction)
        self._multipleItemContextMenu.addSeparator()
        self._multipleItemContextMenu.addAction(self.bringForwardAction)
        self._multipleItemContextMenu.addAction(self.sendBackwardAction)
        self._multipleItemContextMenu.addAction(self.bringToFrontAction)
        self._multipleItemContextMenu.addAction(self.sendToBackAction)
        self._multipleItemContextMenu.addSeparator()
        self._multipleItemContextMenu.addAction(self.groupAction)
        self._multipleItemContextMenu.addAction(self.ungroupAction)

    # ==================================================================================================================

    def setDefaultSceneRect(self, rect: QRectF) -> None:
        self._defaultSceneRect = QRectF(rect)

    def setDefaultBackgroundBrush(self, brush: QBrush) -> None:
        self._defaultBackgroundBrush = QBrush(brush)

    def setDefaultGrid(self, grid: float) -> None:
        self._defaultGrid = grid

    def setDefaultGridVisible(self, visible: bool) -> None:
        self._defaultGridVisible = visible

    def seDefaultGridBrush(self, brush: QBrush) -> None:
        self._defaultGridBrush = QBrush(brush)

    def setDefaultGridSpacingMajor(self, spacing: int) -> None:
        self._defaultGridSpacingMajor = spacing

    def setDefaultGridSpacingMinor(self, spacing: int) -> None:
        self._defaultGridSpacingMinor = spacing

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
        self._defaultPen = QPen(pen)

    def setDefaultBrush(self, brush: QBrush) -> None:
        self._defaultBrush = QBrush(brush)

    def setDefaultStartArrow(self, arrow: DrawingArrow) -> None:
        self._defaultStartArrow = DrawingArrow(arrow.style(), arrow.size())

    def setDefaultEndArrow(self, arrow: DrawingArrow) -> None:
        self._defaultEndArrow = DrawingArrow(arrow.style(), arrow.size())

    def setDefaultFont(self, font: QFont) -> None:
        self._defaultFont = QFont(font)

    def setDefaultTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._defaultTextAlignment = alignment

    def setDefaultTextBrush(self, brush: QBrush) -> None:
        self._defaultTextBrush = QBrush(brush)

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
            self._gridBrush = QBrush(brush)

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

    def addPage(self, page: DrawingPageWidget) -> None:
        self.insertPage(len(self._pages), page)

    def insertPage(self, index: int, page: DrawingPageWidget) -> None:
        if (page not in self._pages):
            self._pages.insert(index, page)
            self._stackedWidget.insertWidget(index, page)

            self.pageInserted.emit(page, index)

            page.undoCommandCreated.connect(self._pushUndoCommand)
            page.scaleChanged.connect(self._emitScaleChanged)
            page.modeChanged.connect(self._emitModeChanged)
            page.modeStringChanged.connect(self._emitModeStringChanged)
            page.mouseInfoChanged.connect(self._emitMouseInfoChanged)
            page.currentItemsChanged.connect(self._emitCurrentItemsChanged)
            page.currentItemsPropertyChanged.connect(self._emitCurrentItemsPropertyChanged)
            page.propertyChanged.connect(self._emitCurrentPagePropertyChanged)
            page.contextMenuTriggered.connect(self._contextMenuEvent)

            self.setCurrentPage(page)

    def removePage(self, page: DrawingPageWidget) -> None:
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

            page.undoCommandCreated.disconnect(self._pushUndoCommand)
            page.scaleChanged.disconnect(self._emitScaleChanged)
            page.modeChanged.disconnect(self._emitModeChanged)
            page.modeStringChanged.disconnect(self._emitModeStringChanged)
            page.mouseInfoChanged.disconnect(self._emitMouseInfoChanged)
            page.currentItemsChanged.disconnect(self._emitCurrentItemsChanged)
            page.currentItemsPropertyChanged.disconnect(self._emitCurrentItemsPropertyChanged)
            page.propertyChanged.disconnect(self._emitCurrentPagePropertyChanged)
            page.contextMenuTriggered.disconnect(self._contextMenuEvent)

            self.pageRemoved.emit(page, index)

            self.setCurrentPageIndex(newCurrentPageIndex)

    def movePage(self, page: DrawingPageWidget, newIndex: int) -> None:
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

    def pages(self) -> list[DrawingPageWidget]:
        return self._pages

    # ==================================================================================================================

    def setCurrentPage(self, page: DrawingPageWidget | None) -> None:
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

    def currentPage(self) -> DrawingPageWidget | None:
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
            self.setGrid(self.readFloat(drawingElement, 'grid'))
            self.setGridVisible(self.readBool(drawingElement, 'gridVisible'))
            self.setGridBrush(QBrush(self.readColor(drawingElement, 'gridColor')))
            self.setGridSpacingMajor(self.readInt(drawingElement, 'gridSpacingMajor'))
            self.setGridSpacingMinor(self.readInt(drawingElement, 'gridSpacingMinor'))

            for pageElement in drawingElement.findall('page'):
                newPage = DrawingPageWidget()

                newPage.setGrid(self._grid)
                newPage.setGridVisible(self._gridVisible)
                newPage.setGridBrush(self._gridBrush)
                newPage.setGridSpacingMajor(self._gridSpacingMajor)
                newPage.setGridSpacingMinor(self._gridSpacingMinor)

                newPage.readFromXml(pageElement)

                self.addPage(newPage)
                self.zoomFit()

            self._undoStack.setClean()
            return True

        return False

    def saveToFile(self, path: str) -> bool:
        drawingElement = ElementTree.Element('jade-drawing')

        self.writeFloat(drawingElement, 'grid', self.grid(), writeIfDefault=True)
        self.writeBool(drawingElement, 'gridVisible', self.isGridVisible(), writeIfDefault=True)
        self.writeColor(drawingElement, 'gridColor', self.gridBrush().color(), writeIfDefault=True)
        self.writeInt(drawingElement, 'gridSpacingMajor', self.gridSpacingMajor())
        self.writeInt(drawingElement, 'gridSpacingMinor', self.gridSpacingMinor())

        for page in self._pages:
            pageElement = ElementTree.SubElement(drawingElement, 'page')
            page.writeToXml(pageElement)

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

        self._grid = self._defaultGrid
        self._gridVisible = self._defaultGridVisible
        self._gridBrush = self._defaultGridBrush
        self._gridSpacingMajor = self._defaultGridSpacingMajor
        self._gridSpacingMinor = self._defaultGridSpacingMinor

    # ==================================================================================================================

    def undo(self) -> None:
        if (self.mode() == DrawingPageWidget.Mode.SelectMode):
            # Get the command that will be undone by the call to self._undoStack.undo()
            command = self._undoStack.command(self._undoStack.index() - 1)
            if (isinstance(command, DrawingUndoCommand)):
                self.setCurrentPage(command.page())
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
        if (self.mode() == DrawingPageWidget.Mode.SelectMode):
            # Get the command that will be redone by the call to self._undoStack.redo()
            command = self._undoStack.command(self._undoStack.index())
            if (isinstance(command, DrawingUndoCommand)):
                self.setCurrentPage(command.page())
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

    def rotateCurrentItems(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.rotateCurrentItems()

    def rotateBackCurrentItems(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.rotateBackCurrentItems()

    def flipCurrentItemsHorizontal(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.flipCurrentItemsHorizontal()

    def flipCurrentItemsVertical(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.flipCurrentItemsVertical()

    # ==================================================================================================================

    def bringCurrentItemsForward(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.bringCurrentItemsForward()

    def sendCurrentItemsBackward(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.sendCurrentItemsBackward()

    def bringCurrentItemsToFront(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.bringCurrentItemsToFront()

    def sendCurrentItemsToBack(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.sendCurrentItemsToBack()

    # ==================================================================================================================

    def groupCurrentItems(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.groupCurrentItems()

    def ungroupCurrentItem(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.ungroupCurrentItem()

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
        newPage = DrawingPageWidget()
        newPage.setName(name)
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

    def mode(self) -> DrawingPageWidget.Mode:
        if (self._currentPage is not None):
            return self._currentPage.mode()
        return DrawingPageWidget.Mode.SelectMode

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

    def _contextMenuEvent(self, position: QPoint) -> None:
        if (self._currentPage is not None and self.mode() == DrawingPageWidget.Mode.SelectMode):
            # Show context menu depending on whether or not the right-click occurred on a selected item
            # and if so, what kind of item it was.
            mouseDownItem = self._currentPage.mouseDownItem()
            selectedItems = self._currentPage.selectedItems()

            if (mouseDownItem is not None and mouseDownItem.isSelected()):
                if (len(selectedItems) == 1):
                    if (self.insertPointAction.isEnabled()):
                        self._singlePolyItemContextMenu.popup(self.mapToGlobal(position))
                    elif (self.groupAction.isEnabled() or self.ungroupAction.isEnabled()):
                        self._singleGroupItemContextMenu.popup(self.mapToGlobal(position))
                    else:
                        self._singleItemContextMenu.popup(self.mapToGlobal(position))
                else:
                    self._multipleItemContextMenu.popup(self.mapToGlobal(position))
            else:
                self.setSelectedItems([])
                self._noItemContextMenu.popup(self.mapToGlobal(position))

    # ==================================================================================================================

    def _emitScaleChanged(self, scale: float) -> None:
        self.scaleChanged.emit(scale)

    def _emitModeChanged(self, mode: DrawingPageWidget.Mode) -> None:
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
                item = DrawingItem.createItemFromFactory(action.property('key'))
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

                    # Begin place mode
                    self.setPlaceMode([item])
                else:
                    # Revert back to select mode if no new item was able to be created
                    self.setSelectMode()

    def _updateActionsFromMode(self, mode: int):
        if (mode == DrawingPageWidget.Mode.SelectMode.value and not self.selectModeAction.isChecked()):
            self.selectModeAction.setChecked(True)

    def _updateActionsFromSelection(self, items: list[DrawingItem]) -> None:
        canGroup = (len(items) > 1)
        canUngroup = False
        canInsertPoints = False
        canRemovePoints = False
        if (len(items) == 1):
            item = items[0]
            canUngroup = (item.key() == 'group')
            canInsertPoints = item.canInsertPoints()
            canRemovePoints = item.canRemovePoints()

        self.groupAction.setEnabled(canGroup)
        self.ungroupAction.setEnabled(canUngroup)
        self.insertPointAction.setEnabled(canInsertPoints)
        self.removePointAction.setEnabled(canRemovePoints)


# ======================================================================================================================

class DrawingInsertPageCommand(QUndoCommand):
    def __init__(self, widget: DrawingWidget, page: DrawingPageWidget, index: int,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__('Insert Page', parent)

        # Assumes page is not already a member of widget.pages()
        self._widget: DrawingWidget = widget
        self._page: DrawingPageWidget = page
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
    def __init__(self, widget: DrawingWidget, page: DrawingPageWidget, parent: QUndoCommand | None = None) -> None:
        super().__init__('Remove Page', parent)

        # Assumes page is a member of widget.pages()
        self._widget: DrawingWidget = widget
        self._page: DrawingPageWidget = page
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
    def __init__(self, widget: DrawingWidget, page: DrawingPageWidget, newIndex: int,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__('Remove Page', parent)

        # Assumes page is a member of widget.pages()
        self._widget: DrawingWidget = widget
        self._page: DrawingPageWidget = page
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
    def __init__(self, widget: DrawingWidget, name: str, value: typing.Any,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__('Set Property', parent)

        self._widget: DrawingWidget = widget
        self._name: str = name
        self._value: typing.Any = value

        self._originalValue: typing.Any = self._widget.property(self._name)

    def redo(self) -> None:
        self._widget.setProperty(self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.setProperty(self._name, self._originalValue)
