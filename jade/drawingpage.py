# drawingpage.py
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

import math
import typing
from enum import Enum
from PyQt6.QtCore import pyqtSignal, Qt, QLineF, QPoint, QPointF, QRect, QRectF, QTimer
from PyQt6.QtGui import QBrush, QColor, QCursor, QPaintEvent, QPainter, QPainterPath, QPalette, QPen, QResizeEvent, QTransform
from PyQt6.QtWidgets import QAbstractScrollArea, QRubberBand, QStyle, QStyleHintReturnMask, QStyleOptionRubberBand
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint
from .drawingtypes import DrawingMode, DrawingUnits


class DrawingPage(QAbstractScrollArea):
    class MouseState(Enum):
        Idle = 0
        HandlingLeftButtonEvent = 1
        HandlingRightButtonEvent = 2
        HandlingMiddleButtonEvent = 3

    class SelectModeMouseState(Enum):
        Idle = 0
        Select = 1
        MoveItems = 2
        ResizeItem = 3
        RubberBand = 4

    # ==================================================================================================================

    propertyChanged = pyqtSignal(str, object)
    scaleChanged = pyqtSignal(float)
    modeChanged = pyqtSignal(DrawingMode)
    currentItemsChanged = pyqtSignal(list)
    currentItemsPropertyChanged = pyqtSignal(list)

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMouseTracking(True)

        self._units: DrawingUnits = DrawingUnits.Millimeters
        self._sceneRect: QRectF = QRectF()
        self._backgroundBrush: QBrush = QBrush()

        self._grid: float = 0
        self._gridVisible: bool = False
        self._gridBrush: QBrush = QBrush()
        self._gridSpacingMajor: int = 0
        self._gridSpacingMinor: int = 0

        self._items: list[DrawingItem] = []

        self._selectedItems: list[DrawingItem] = []
        self._selectMouseDownItem: DrawingItem | None = None
        self._selectMouseDownPoint: DrawingItemPoint | None = None
        self._selectFocusItem: DrawingItem | None = None

        self._transform = QTransform()
        self._transformInverse = QTransform()

        self._mode: DrawingMode = DrawingMode.SelectMode
        self._placeItems: list[DrawingItem] = []

        self._mouseState: DrawingPage.MouseState = DrawingPage.MouseState.Idle
        self._mouseButtonDownPosition: QPoint = QPoint()
        self._mouseButtonDownScenePosition: QPointF = QPointF()
        self._mouseDragged: bool = False

        self._selectMouseState: DrawingPage.SelectModeMouseState = DrawingPage.SelectModeMouseState.Idle
        self._selectMoveItemsInitialPositions: dict[DrawingItem, QPointF] = {}
        self._selectMoveItemsPreviousDeltaPosition: QPointF = QPointF()
        self._selectResizeItemInitialPosition: QPointF = QPointF()
        self._selectResizeItemPreviousPosition: QPointF = QPointF()
        self._selectedItemsCenter: QPointF = QPointF()
        self._selectRubberBandRect: QRect = QRect()

        self._scrollInitialHorizontalValue: int = 0
        self._scrollInitialVerticalValue: int = 0

        self._zoomRubberBandRect: QRect = QRect()

        self._panStartPos: QPoint = QPoint()
        self._panCurrentPos: QPoint = QPoint()
        self._panTimer: QTimer = QTimer()
        self._panTimer.setInterval(16)
        self._panTimer.timeout.connect(self._mousePanEvent)     # type: ignore

        self.currentItemsChanged.connect(self._updateSelectionCenter)
        self.currentItemsPropertyChanged.connect(self._updateSelectionCenter)

    def __del__(self):
        self.setSelectMode()
        while (len(self._items) > 0):
            item = self._items[-1]
            self.removeItem(item)
            del item

    # ==================================================================================================================

    def setName(self, name: str) -> None:
        if (self.objectName() != name):
            self.setObjectName(name)
            self.propertyChanged.emit('name', self.objectName())

    def name(self) -> str:
        return self.objectName()

    # ==================================================================================================================

    def setUnits(self, units: DrawingUnits) -> None:
        if (self._units != units):
            self._units = units
            self.propertyChanged.emit('units', self._units)

    def setSceneRect(self, rect: QRectF) -> None:
        if (self._sceneRect != rect and rect.isValid()):
            self._sceneRect = rect
            self.propertyChanged.emit('sceneRect', self._sceneRect)

    def setBackgroundBrush(self, brush: QBrush) -> None:
        if (self._backgroundBrush != brush):
            self._backgroundBrush = brush
            self.propertyChanged.emit('backgroundBrush', self._backgroundBrush)

    def units(self) -> DrawingUnits:
        return self._units

    def sceneRect(self) -> QRectF:
        return self._sceneRect

    def backgroundBrush(self) -> QBrush:
        return self._backgroundBrush

    # ==================================================================================================================

    def setGrid(self, grid: float) -> None:
        if (self._grid != grid and grid >= 0):
            self._grid = grid
            self.propertyChanged.emit('grid', self._grid)

    def setGridVisible(self, visible: bool) -> None:
        if (self._gridVisible != visible):
            self._gridVisible = visible
            self.propertyChanged.emit('gridVisible', self._gridVisible)

    def setGridBrush(self, brush: QBrush) -> None:
        if (self._gridBrush != brush):
            self._gridBrush = brush
            self.propertyChanged.emit('gridBrush', self._gridBrush)

    def setGridSpacingMajor(self, spacing: int) -> None:
        if (self._gridSpacingMajor != spacing and spacing >= 0):
            self._gridSpacingMajor = spacing
            self.propertyChanged.emit('gridSpacingMajor', self._gridSpacingMajor)

    def setGridSpacingMinor(self, spacing: int) -> None:
        if (self._gridSpacingMinor != spacing and spacing >= 0):
            self._gridSpacingMinor = spacing
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

    def roundToGrid(self, value: float) -> float:
        return self._grid * round(value / self._grid)

    def roundPointToGrid(self, position: QPointF) -> QPointF:
        return QPointF(self.roundToGrid(position.x()), self.roundToGrid(position.y()))

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> bool:
        match (name):
            case 'name':
                if (isinstance(value, str)):
                    self.setName(value)
            case 'units':
                if (isinstance(value, int)):
                    self.setUnits(DrawingUnits(value))
            case 'sceneRect':
                if (isinstance(value, QRectF)):
                    self.setSceneRect(value)
            case 'backgroundBrush':
                if (isinstance(value, QBrush)):
                    self.setBackgroundBrush(value)
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
            case 'name':
                return self.name()
            case 'units':
                return self.units().value
            case 'sceneRect':
                return self.sceneRect()
            case 'backgroundBrush':
                return self.backgroundBrush()
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

    def addItem(self, item: DrawingItem) -> None:
        # Assumes item is not already a member of self._items
        self._items.append(item)
        item._parent = self

    def insertItem(self, index: int, item: DrawingItem) -> None:
        # Assumes item is not already a member of self._items
        self._items.insert(index, item)
        item._parent = self

    def removeItem(self, item: DrawingItem) -> None:
        # Assumes item is a member of self._items
        self._items.remove(item)
        item._parent = None

    def items(self) -> list[DrawingItem]:
        return self._items

    def itemsInRect(self, rect: QRectF) -> list[DrawingItem]:
        items = []
        for item in self._items:
            if (self._isItemInRect(item, rect)):
                items.append(item)
        return items

    def itemAt(self, position: QPointF) -> DrawingItem | None:
        # Favor selected items; if not found in the selected items, search all items in the scene
        for item in reversed(self._selectedItems):
            if (self._isPointInItem(item, position)):
                return item
        for item in reversed(self._items):
            if (self._isPointInItem(item, position)):
                return item
        return None

    # ==================================================================================================================

    def setSelectedItems(self, items: list[DrawingItem]):
        if (self._selectedItems != items):
            for item in self._selectedItems:
                item.setSelected(False)

            self._selectedItems = items

            for item in self._selectedItems:
                item.setSelected(True)

            if (self._mode == DrawingMode.SelectMode):
                self.currentItemsChanged.emit(self._selectedItems)

            self.viewport().update()

    def selectedItems(self) -> list[DrawingItem]:
        return self._selectedItems

    def mouseDownItem(self) -> DrawingItem | None:
        return self._selectMouseDownItem

    def mouseDownPoint(self) -> DrawingItemPoint | None:
        return self._selectMouseDownPoint

    def focusItem(self) -> DrawingItem | None:
        return self._selectFocusItem

    # ==================================================================================================================

    def setScale(self, scale: float) -> None:
        if (scale > 0):
            previousMousePosition = self.mapFromGlobal(QCursor.pos())
            previousMouseScenePosition = self.mapToScene(previousMousePosition)

            self._updateTransformAndScrollBars(scale)
            self.scaleChanged.emit(scale)

            if (self.viewport().rect().contains(previousMousePosition)):
                self.mouseCursorOn(previousMouseScenePosition)
            else:
                self.centerOn(self._sceneRect.center())

    def zoomToRect(self, rect: QRectF) -> None:
        if (not rect.isValid()):
            rect = self._sceneRect

        scaleX = self.maximumViewportSize().width() / rect.width()
        scaleY = self.maximumViewportSize().height() / rect.height()
        scale = min(scaleX, scaleY)

        self._updateTransformAndScrollBars(scale)
        self.scaleChanged.emit(scale)

        self.centerOn(rect.center())

    def centerOn(self, position: QPointF) -> None:
        oldPosition = self.mapToScene(self.viewport().rect().center())
        scale = self.scale()

        horizontalDelta = round((position.x() - oldPosition.x()) * scale)
        verticalDelta = round((position.y() - oldPosition.y()) * scale)

        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + horizontalDelta)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + verticalDelta)

        self.viewport().update()

    def mouseCursorOn(self, position: QPointF) -> None:
        oldPosition = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        scale = self.scale()

        horizontalDelta = round((position.x() - oldPosition.x()) * scale)
        verticalDelta = round((position.y() - oldPosition.y()) * scale)

        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + horizontalDelta)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + verticalDelta)

        self.viewport().update()

    def scale(self) -> float:
        return self._transform.m11()

    def visibleRect(self) -> QRectF:
        return QRectF(self.mapToScene(QPoint(0, 0)),
                      self.mapToScene(QPoint(self.viewport().width(), self.viewport().height())))

    def mapToScene(self, position: QPoint) -> QPointF:
        scrollPosition = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
        return self._transformInverse.map(QPointF(position + scrollPosition))   # type: ignore

    def mapRectToScene(self, rect: QRect) -> QRectF:
        return QRectF(self.mapToScene(rect.topLeft()), self.mapToScene(rect.bottomRight()))

    def mapFromScene(self, position: QPointF) -> QPoint:
        scrollPosition = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
        return self._transform.map(position).toPoint() - scrollPosition         # type: ignore

    def mapRectFromScene(self, rect: QRectF) -> QRect:
        return QRect(self.mapFromScene(rect.topLeft()), self.mapFromScene(rect.bottomRight()))

    # ==================================================================================================================

    def mode(self) -> DrawingMode:
        return self._mode

    def placeItems(self) -> list[DrawingItem]:
        return self._placeItems

    # ==================================================================================================================

    # addItems, insertItems, removeItems, moveItems, resizeItem...

    # ==================================================================================================================

    def cut(self) -> None:
        pass

    def copy(self) -> None:
        pass

    def paste(self) -> None:
        pass

    def delete(self) -> None:
        pass

    # ==================================================================================================================

    def selectAll(self) -> None:
        pass

    def selectNone(self) -> None:
        pass

    # ==================================================================================================================

    def rotate(self) -> None:
        pass

    def rotateBack(self) -> None:
        pass

    def flipHorizontal(self) -> None:
        pass

    def flipVertical(self) -> None:
        pass

    # ==================================================================================================================

    def bringForward(self) -> None:
        pass

    def sendBackward(self) -> None:
        pass

    def bringToFront(self) -> None:
        pass

    def sendToBack(self) -> None:
        pass

    # ==================================================================================================================

    def group(self) -> None:
        pass

    def ungroup(self) -> None:
        pass

    # ==================================================================================================================

    def insertItemPoint(self) -> None:
        pass

    def removeItemPoint(self) -> None:
        pass

    # ==================================================================================================================

    def zoomIn(self) -> None:
        self.setScale(self.scale() * math.sqrt(2))

    def zoomOut(self) -> None:
        self.setScale(self.scale() * math.sqrt(2) / 2)

    def zoomFit(self) -> None:
        self.zoomToRect(self._sceneRect)

    # ==================================================================================================================

    def setSelectMode(self) -> None:
        self._setMode(DrawingMode.SelectMode)

    def setScrollMode(self) -> None:
        self._setMode(DrawingMode.ScrollMode)

    def setZoomMode(self) -> None:
        self._setMode(DrawingMode.ZoomMode)

    def setPlaceMode(self, items: list[DrawingItem]) -> None:
        if (len(items) > 0):
            self._setMode(DrawingMode.PlaceMode, items)
        else:
            self._setMode(DrawingMode.SelectMode)

    def _setMode(self, mode: DrawingMode, placeItems: list[DrawingItem] = []) -> None:
        previousMode = self._mode
        if (previousMode != mode or mode == DrawingMode.PlaceMode):

            # Clear any selected items and place items
            self.setSelectedItems([])
            del self._placeItems[:]

            # Update the mode
            self._mode = mode
            self._updateCursorFromMode()
            self.modeChanged.emit(self._mode)

            # Update the place items, if applicable
            self._placeItems = placeItems
            if (previousMode == DrawingMode.PlaceMode or self._mode == DrawingMode.PlaceMode):
                self.currentItemsChanged.emit(self._placeItems)

            # Update the viewport
            self.viewport().update()

    def _updateCursorFromMode(self) -> None:
        match (self._mode):
            case DrawingMode.SelectMode:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            case DrawingMode.ScrollMode:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            case DrawingMode.ZoomMode:
                self.setCursor(Qt.CursorShape.CrossCursor)
            case DrawingMode.PlaceMode:
                self.setCursor(Qt.CursorShape.CrossCursor)

    # ==================================================================================================================

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self.viewport()) as painter:
            painter.setBrush(self.palette().brush(QPalette.ColorRole.Dark))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(self.rect())

            painter.translate(-self.horizontalScrollBar().value(), self.verticalScrollBar().value())
            painter.setTransform(self._transform, True)

            self.paint(painter)

    def paint(self, painter: QPainter, export: bool = False) -> None:
        self._drawBackground(painter, export)
        self._drawItems(painter, self._items)

        if (not export):
            self._drawItems(painter, self._placeItems)
            self._drawItemPoints(painter, self._selectedItems)
            self._drawHotpoints(painter, self._selectedItems + self._placeItems)
            self._drawRubberBand(painter, self._selectRubberBandRect)
            self._drawRubberBand(painter, self._zoomRubberBandRect)

    def _drawBackground(self, painter: QPainter, forceHideGrid: bool) -> None:
        bgColor = self._backgroundBrush.color()
        borderColor = QColor(255 - bgColor.red(), 255 - bgColor.green(), 255 - bgColor.blue())

        # Draw background
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
        painter.setBackground(self._backgroundBrush)
        painter.setBrush(self._backgroundBrush)
        painter.setPen(QPen(borderColor, 0))
        painter.drawRect(self._sceneRect)

        # Draw grid
        if (not forceHideGrid and self._gridVisible and self._grid > 0):
            # Minor grid lines
            if (self._gridSpacingMinor > 0):
                painter.setPen(QPen(self._gridBrush, 0, Qt.PenStyle.DotLine))

                gridInterval = self._grid * self._gridSpacingMinor
                gridLeftIndex = math.ceil(self._sceneRect.left() / gridInterval)
                gridRightIndex = math.floor(self._sceneRect.right() / gridInterval)
                gridTopIndex = math.ceil(self._sceneRect.top() / gridInterval)
                gridBottomIndex = math.floor(self._sceneRect.bottom() / gridInterval)
                for xIndex in range(gridLeftIndex, gridRightIndex + 1):
                    x = xIndex * gridInterval
                    painter.drawLine(QLineF(x, self._sceneRect.top(), x, self._sceneRect.bottom()))
                for yIndex in range(gridTopIndex, gridBottomIndex + 1):
                    y= yIndex * gridInterval
                    painter.drawLine(QLineF(self._sceneRect.left(), y, self._sceneRect.right(), y))

            # Major grid lines
            if (self._gridSpacingMajor > 0):
                painter.setPen(QPen(self._gridBrush, 0, Qt.PenStyle.SolidLine))

                gridInterval = self._grid * self._gridSpacingMajor
                gridLeftIndex = math.ceil(self._sceneRect.left() / gridInterval)
                gridRightIndex = math.floor(self._sceneRect.right() / gridInterval)
                gridTopIndex = math.ceil(self._sceneRect.top() / gridInterval)
                gridBottomIndex = math.floor(self._sceneRect.bottom() / gridInterval)
                for xIndex in range(gridLeftIndex, gridRightIndex + 1):
                    x = xIndex * gridInterval
                    painter.drawLine(QLineF(x, self._sceneRect.top(), x, self._sceneRect.bottom()))
                for yIndex in range(gridTopIndex, gridBottomIndex + 1):
                    y= yIndex * gridInterval
                    painter.drawLine(QLineF(self._sceneRect.left(), y, self._sceneRect.right(), y))

            # Redraw the border
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.setPen(QPen(borderColor, 0))
            painter.drawRect(self._sceneRect)

    def _drawItems(self, painter: QPainter, items: list[DrawingItem]) -> None:
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, True)

        for item in items:
            painter.translate(item.position())
            painter.setTransform(item.transform(), True)

            item.paint(painter)

            painter.setBrush(QBrush(QColor(255, 0, 255, 128)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPath(self._itemAdjustedShape(item))

            painter.setTransform(item.transformInverse(), True)
            painter.translate(-item.position())

    def _drawItemPoints(self, painter: QPainter, items: list[DrawingItem]) -> None:
        bgColor = self._backgroundBrush.color()
        borderColor = QColor(255 - bgColor.red(), 255 - bgColor.green(), 255 - bgColor.blue())

        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
        painter.setPen(QPen(borderColor, 0))

        for item in items:
            for point in item.points():
                controlPoint = (point.isControlPoint() or point.type() == DrawingItemPoint.Type.NoType)
                connectionPoint = point.isConnectionPoint()
                if (controlPoint or connectionPoint):
                    if (connectionPoint and not controlPoint):
                        painter.setBrush(QColor(255, 255, 0))
                    else:
                        painter.setBrush(QColor(0, 224, 0))
                    painter.drawRect(self._pointRect(point))

    def _drawHotpoints(self, painter: QPainter, items: list[DrawingItem]) -> None:
        if (len(items) > 0):
            hotpointItem = items[0]

            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, True)
            painter.setBrush(QBrush(QColor(255, 128, 0, 192)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))

            for point in hotpointItem.points():
                for otherItem in self._items:
                    for otherPoint in otherItem.points():
                        if (self._shouldConnect(point, otherPoint)):
                            rect = self._pointRect(point)
                            rect.adjust(-rect.width(), -rect.height(), rect.width(), rect.height())
                            painter.drawEllipse(rect)

    def _drawRubberBand(self, painter: QPainter, rect: QRect) -> None:
        if (rect.isValid()):
            painter.save()
            painter.resetTransform()
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)

            option = QStyleOptionRubberBand()
            option.initFrom(self.viewport())
            option.rect = rect
            option.shape = QRubberBand.Shape.Rectangle

            mask = QStyleHintReturnMask()
            if (self.viewport().style().styleHint(QStyle.StyleHint.SH_RubberBand_Mask, option, self.viewport(), mask)):
                painter.setClipRegion(mask.region, Qt.ClipOperation.IntersectClip)

            self.viewport().style().drawControl(QStyle.ControlElement.CE_RubberBand, option, painter, self.viewport())

            painter.restore()

    # ==================================================================================================================

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._updateTransformAndScrollBars()

    def _updateTransformAndScrollBars(self, scale: float = 0) -> None:
        if (scale <= 0):
            scale = self.scale()

        contentWidth = round(self._sceneRect.width() * scale)
        contentHeight = round(self._sceneRect.height() * scale)
        viewportWidth = self.maximumViewportSize().width()
        viewportHeight = self.maximumViewportSize().height()
        scrollBarExtent = self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent, None, self)
        if (contentWidth > viewportWidth and self.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded):
            viewportWidth = viewportWidth - scrollBarExtent
        if (contentHeight > viewportHeight and self.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded):
            viewportHeight = viewportHeight - scrollBarExtent

        # Update transform
        self._transform.reset()
        self._transform.translate(-self._sceneRect.left() * scale, -self._sceneRect.top() * scale)
        if (contentWidth <= viewportWidth):
            self._transform.translate(-(self._sceneRect.width() * scale - viewportWidth) / 2, 0)
        if (contentHeight <= viewportHeight):
            self._transform.translate(0, -(self._sceneRect.height() * scale - viewportHeight) / 2)
        self._transform.scale(scale, scale)

        self._transformInverse = self._transform.inverted()[0]

        # Update scroll bars
        if (contentWidth > viewportWidth):
            self.horizontalScrollBar().setRange(-1, contentWidth - viewportWidth + 1)
            self.horizontalScrollBar().setSingleStep(round(viewportWidth / 80))
            self.horizontalScrollBar().setPageStep(viewportWidth)
        else:
            self.horizontalScrollBar().setRange(0, 0)

        if (contentHeight > viewportHeight):
            self.verticalScrollBar().setRange(-1, contentHeight - viewportHeight + 1)
            self.verticalScrollBar().setSingleStep(round(viewportHeight / 80))
            self.verticalScrollBar().setPageStep(viewportHeight)
        else:
            self.verticalScrollBar().setRange(0, 0)

    # ==================================================================================================================

    def _mousePanEvent(self) -> None:
        pass

    # ==================================================================================================================

    def _updateSelectionCenter(self) -> None:
        pass

    # ==================================================================================================================

    def _itemsRect(self, items: list[DrawingItem]) -> QRectF:
        rect = QRectF()
        for item in items:
            rect = rect.united(item.mapRectToScene(item.boundingRect()))
        return rect

    def _itemsCenter(self, items: list[DrawingItem]) -> QPointF:
        if (len(items) > 1):
            return self._itemsRect(items).center()
        elif (len(items) == 1):
            return items[0].mapToScene(items[0].centerPosition())
        return QPointF()

    def _isItemInRect(self, item: DrawingItem, rect: QRectF) -> bool:
        return rect.contains(item.mapRectToScene(item.boundingRect()))

    def _isPointInItem(self, item: DrawingItem, position: QPointF) -> bool:
        # Check item shape
        match = self._itemAdjustedShape(item).contains(item.mapFromScene(position))
        if (match):
            return True

        # Check item points if selected
        if (item.isSelected()):
            for point in item.points():
                if (self._pointRect(point).contains(position)):
                    return True

        return False

    def _itemAdjustedShape(self, item: DrawingItem) -> QPainterPath:
        adjustedShape = QPainterPath()

        pen = item.property('pen')
        if (pen is not None):
            # Determine minimum pen width
            penWidthHint = 8
            mappedPenSize = item.mapFromScene(
                item.position() +
                self.mapToScene(QPoint(penWidthHint, penWidthHint)) -     # type: ignore
                self.mapToScene(QPoint(0, 0)))                            # type: ignore
            minimumPenWidth = max(abs(mappedPenSize.x()), abs(mappedPenSize.y()))

            # Override item's default pen width if needed
            if (0 < pen.widthF() < minimumPenWidth):
                originalPenWidth = pen.widthF()

                pen.setWidthF(minimumPenWidth)
                item.setProperty('pen', pen)

                adjustedShape = QPainterPath(item.shape())

                pen.setWidthF(originalPenWidth)
                item.setProperty('pen', pen)
            else:
                adjustedShape = QPainterPath(item.shape())
        else:
            adjustedShape = QPainterPath(item.shape())

        return adjustedShape

    def _pointRect(self, point: DrawingItemPoint) -> QRectF:
        if (point.item()):
            position = point.item().mapToScene(point.position())
            size = 8 / self.scale()
            return QRectF(position.x() - size / 2, position.y() - size / 2, size, size)
        return QRectF()
