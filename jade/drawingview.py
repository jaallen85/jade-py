# drawingview.py
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
from PyQt6.QtGui import QBrush, QColor, QCursor, QMouseEvent, QPaintEvent, QPainter, QPainterPath, QPalette, QPen, \
                        QResizeEvent, QTransform, QWheelEvent
from PyQt6.QtWidgets import QAbstractScrollArea, QApplication, QRubberBand, QStyle, QStyleHintReturnMask, \
                            QStyleOptionRubberBand
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint
from .drawingtypes import DrawingUnits


class DrawingView(QAbstractScrollArea):
    class Mode(Enum):
        SelectMode = 0
        ScrollMode = 1
        ZoomMode = 2
        PlaceMode = 3

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
    modeChanged = pyqtSignal(int)
    modeStringChanged = pyqtSignal(str)
    mouseInfoChanged = pyqtSignal(str)
    currentItemsChanged = pyqtSignal(list)

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMouseTracking(True)

        self._units: DrawingUnits = DrawingUnits.Millimeters
        self._sceneRect: QRectF = QRectF()
        self._backgroundBrush: QBrush = QBrush()

        self._grid: float = 0.0
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

        self._mode: DrawingView.Mode = DrawingView.Mode.SelectMode
        self._placeModeItems: list[DrawingItem] = []

        self._mouseState: DrawingView.MouseState = DrawingView.MouseState.Idle
        self._mouseButtonDownPosition: QPoint = QPoint()
        self._mouseButtonDownScenePosition: QPointF = QPointF()
        self._mouseDragged: bool = False

        self._selectMouseState: DrawingView.SelectModeMouseState = DrawingView.SelectModeMouseState.Idle
        self._selectRubberBandRect: QRect = QRect()

        self._scrollInitialHorizontalValue: int = 0
        self._scrollInitialVerticalValue: int = 0

        self._zoomRubberBandRect: QRect = QRect()

        self._panOriginalCursor: Qt.CursorShape = Qt.CursorShape.ArrowCursor
        self._panStartPosition: QPoint = QPoint()
        self._panCurrentPosition: QPoint = QPoint()
        self._panTimer: QTimer = QTimer()
        self._panTimer.setInterval(5)
        self._panTimer.timeout.connect(self._mousePanEvent)     # type: ignore

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
        return self._grid * round(value / self._grid) if (self._grid != 0) else value

    def roundPointToGrid(self, position: QPointF) -> QPointF:
        return QPointF(self.roundToGrid(position.x()), self.roundToGrid(position.y()))

    # ==================================================================================================================

    def addItem(self, item: DrawingItem) -> None:
        self.insertItem(len(self._items), item)

    def insertItem(self, index: int, item: DrawingItem) -> None:
        if (item not in self._items):
            self._items.insert(index, item)
            item._parent = self

    def removeItem(self, item: DrawingItem) -> None:
        if (item in self._items):
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
        # Assumes each item in items is a member of self._items
        if (self._selectedItems != items):
            for item in self._selectedItems:
                item.setSelected(False)

            self._selectedItems = items

            for item in self._selectedItems:
                item.setSelected(True)

            if (self._mode == DrawingView.Mode.SelectMode):
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

            # Update view to the new scale
            self._updateTransformAndScrollBars(scale)
            self.scaleChanged.emit(scale)

            # Keep mouse cursor on the same position, if possible.  Otherwise keep the center of the scene rect in the
            # center of the view.
            if (self.viewport().rect().contains(previousMousePosition)):
                self.mouseCursorOn(previousMouseScenePosition)
            else:
                self.centerOn(self._sceneRect.center())

    def zoomToRect(self, rect: QRectF) -> None:
        if (not rect.isValid()):
            rect = self._sceneRect

        # Update view to the new scale
        scaleX = (self.maximumViewportSize().width() - 1) / rect.width()
        scaleY = (self.maximumViewportSize().height() - 1) / rect.height()
        scale = min(scaleX, scaleY)

        self._updateTransformAndScrollBars(scale)
        self.scaleChanged.emit(scale)

        # Put the center of the rect in the center of the view
        self.centerOn(rect.center())

    def centerOn(self, position: QPointF) -> None:
        # Scroll the scroll bars so the specified position is in the center of the view
        oldPosition = self.mapToScene(self.viewport().rect().center())
        scale = self.scale()

        horizontalDelta = round((position.x() - oldPosition.x()) * scale)
        verticalDelta = round((position.y() - oldPosition.y()) * scale)

        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + horizontalDelta)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + verticalDelta)

        self.viewport().update()

    def mouseCursorOn(self, position: QPointF) -> None:
        # Scroll the scroll bars so the specified position is beneath the mouse cursor
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
                      self.mapToScene(QPoint(self.viewport().width() - 1, self.viewport().height() - 1)))

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

    def mode(self) -> 'DrawingView.Mode':
        return self._mode

    def placeItems(self) -> list[DrawingItem]:
        return self._placeModeItems

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

    def selectAll(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            self.setSelectedItems(self._items)

    def selectNone(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            self.setSelectedItems([])

    # ==================================================================================================================

    def zoomIn(self) -> None:
        self.setScale(self.scale() * math.sqrt(2))

    def zoomOut(self) -> None:
        self.setScale(self.scale() * math.sqrt(2) / 2)

    def zoomFit(self) -> None:
        self.zoomToRect(self._sceneRect)

    # ==================================================================================================================

    def setSelectMode(self) -> None:
        self._setMode(DrawingView.Mode.SelectMode, [])

    def setScrollMode(self) -> None:
        self._setMode(DrawingView.Mode.ScrollMode, [])

    def setZoomMode(self) -> None:
        self._setMode(DrawingView.Mode.ZoomMode, [])

    def setPlaceMode(self, items: list[DrawingItem]) -> None:
        if (len(items) > 0):
            self._setMode(DrawingView.Mode.PlaceMode, items)
        else:
            self._setMode(DrawingView.Mode.SelectMode, [])

    def _setMode(self, mode: 'DrawingView.Mode', placeItems: list[DrawingItem]) -> None:
        previousMode = self._mode
        if (previousMode != mode or mode == DrawingView.Mode.PlaceMode):

            # Clear any selected items and place items
            self.setSelectedItems([])
            del self._placeModeItems[:]

            # Update the mode
            self._mode = mode
            self.modeChanged.emit(self._mode.value)
            match (self._mode):
                case DrawingView.Mode.SelectMode:
                    self.modeStringChanged.emit('Select Mode')
                case DrawingView.Mode.ScrollMode:
                    self.modeStringChanged.emit('Scroll Mode')
                case DrawingView.Mode.ZoomMode:
                    self.modeStringChanged.emit('Zoom Mode')
                case DrawingView.Mode.PlaceMode:
                    self.modeStringChanged.emit('Place Mode')

            # Update cursor
            match (self._mode):
                case DrawingView.Mode.SelectMode:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                case DrawingView.Mode.ScrollMode:
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                case DrawingView.Mode.ZoomMode:
                    self.setCursor(Qt.CursorShape.CrossCursor)
                case DrawingView.Mode.PlaceMode:
                    self.setCursor(Qt.CursorShape.CrossCursor)

            # Update the place items, if applicable
            self._placeModeItems = placeItems
            if (previousMode == DrawingView.Mode.PlaceMode or self._mode == DrawingView.Mode.PlaceMode):
                self.currentItemsChanged.emit(self._placeModeItems)

            # Update the viewport
            self.viewport().update()

    # ==================================================================================================================

    def clear(self) -> None:
        # Reset properties to default values
        self._units = DrawingUnits.Millimeters
        self._sceneRect = QRectF()
        self._backgroundBrush = QBrush()

        self._grid = 0
        self._gridVisible = False
        self._gridBrush = QBrush()
        self._gridSpacingMajor = 0
        self._gridSpacingMinor = 0

        # Clear items from the scene
        self.setSelectMode()
        self.setSelectedItems([])
        while (len(self._items) > 0):
            item = self._items[-1]
            self.removeItem(item)
            del item

    # ==================================================================================================================

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self.viewport()) as painter:
            painter.setBrush(self.palette().brush(QPalette.ColorRole.Dark))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(self.rect())

            painter.translate(-self.horizontalScrollBar().value(), -self.verticalScrollBar().value())
            painter.setTransform(self._transform, True)

            self.paint(painter)

    def paint(self, painter: QPainter, export: bool = False) -> None:
        self._drawBackground(painter, export)
        self._drawItems(painter, self._items)

        if (not export):
            self._drawItems(painter, self._placeModeItems)
            self._drawItemPoints(painter, self._selectedItems)
            self._drawHotpoints(painter, self._selectedItems + self._placeModeItems)
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
                    y = yIndex * gridInterval
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
                    y = yIndex * gridInterval
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

            # painter.setBrush(QBrush(QColor(255, 0, 255, 128)))
            # painter.setPen(QPen(Qt.PenStyle.NoPen))
            # painter.drawPath(self._itemAdjustedShape(item))

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

            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
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

    def _updateTransformAndScrollBars(self, scale: float = 0.0) -> None:
        if (scale <= 0):
            scale = self.scale()

        contentWidth = round(self._sceneRect.width() * scale)
        contentHeight = round(self._sceneRect.height() * scale)
        viewportWidth = self.maximumViewportSize().width()
        viewportHeight = self.maximumViewportSize().height()
        scrollBarExtent = self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent, None, self)
        if (contentWidth > viewportWidth and self.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded):
            viewportWidth = viewportWidth - scrollBarExtent
        if (contentHeight > viewportHeight and self.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded):   # noqa
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton and self._mouseState == DrawingView.MouseState.Idle):
            self._mouseState = DrawingView.MouseState.HandlingLeftButtonEvent
            self._mouseButtonDownPosition = event.pos()
            self._mouseButtonDownScenePosition = self.mapToScene(self._mouseButtonDownPosition)

            # Handle the left mouse press event depending on the current mode
            match (self._mode):
                case DrawingView.Mode.SelectMode:
                    self._selectModeLeftMousePressEvent(event)
                case DrawingView.Mode.ScrollMode:
                    self._scrollModeLeftMousePressEvent(event)
                case DrawingView.Mode.ZoomMode:
                    self._zoomModeLeftMousePressEvent(event)
                case DrawingView.Mode.PlaceMode:
                    self._placeModeLeftMousePressEvent(event)

        elif (event.button() == Qt.MouseButton.RightButton and self._mouseState == DrawingView.MouseState.Idle):
            self._mouseState = DrawingView.MouseState.HandlingRightButtonEvent
            self._mouseButtonDownPosition = event.pos()
            self._mouseButtonDownScenePosition = self.mapToScene(self._mouseButtonDownPosition)

            # Handle the right mouse press event depending on the current mode. Modes other than SelectMode ignore
            # this event.
            if (self._mode == DrawingView.Mode.SelectMode):
                self._selectModeRightMousePressEvent(event)

        elif (event.button() == Qt.MouseButton.MiddleButton and self._mouseState == DrawingView.MouseState.Idle):
            self._mouseState = DrawingView.MouseState.HandlingMiddleButtonEvent
            self._mouseButtonDownPosition = event.pos()
            self._mouseButtonDownScenePosition = self.mapToScene(self._mouseButtonDownPosition)

            # Prepare for mouse pan events
            self._panOriginalCursor = self.cursor().shape()
            self.setCursor(Qt.CursorShape.SizeAllCursor)

            self._panStartPosition = event.pos()
            self._panCurrentPosition = event.pos()
            self._panTimer.start()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if ((event.buttons() & Qt.MouseButton.LeftButton) and self._mouseState == DrawingView.MouseState.HandlingLeftButtonEvent):       # noqa
            dragDistance = (self._mouseButtonDownPosition - event.pos()).manhattanLength()      # type:ignore
            self._mouseDragged = (self._mouseDragged or dragDistance >= QApplication.startDragDistance())

            if (self._mouseDragged):
                # Handle the left mouse drag event depending on the current mode
                match (self._mode):
                    case DrawingView.Mode.SelectMode:
                        self._selectModeLeftMouseDragEvent(event)
                    case DrawingView.Mode.ScrollMode:
                        self._scrollModeLeftMouseDragEvent(event)
                    case DrawingView.Mode.ZoomMode:
                        self._zoomModeLeftMouseDragEvent(event)
                    case DrawingView.Mode.PlaceMode:
                        self._placeModeLeftMouseDragEvent(event)

        elif ((event.buttons() & Qt.MouseButton.RightButton) and self._mouseState == DrawingView.MouseState.HandlingRightButtonEvent):   # noqa
            # In all modes, right mouse drag events are ignored
            pass

        elif ((event.buttons() & Qt.MouseButton.MiddleButton) and self._mouseState == DrawingView.MouseState.HandlingMiddleButtonEvent): # noqa
            # Update current position for mouse pan events
            self._panCurrentPosition = event.pos()

        else:
            # Handle the left mouse move event (with no buttons held down) depending on the current mode
            match (self._mode):
                case DrawingView.Mode.SelectMode:
                    self._selectModeNoButtonMouseMoveEvent(event)
                case DrawingView.Mode.ScrollMode:
                    self._scrollModeNoButtonMouseMoveEvent(event)
                case DrawingView.Mode.ZoomMode:
                    self._zoomModeNoButtonMouseMoveEvent(event)
                case DrawingView.Mode.PlaceMode:
                    self._placeModeNoButtonMouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton and self._mouseState == DrawingView.MouseState.HandlingLeftButtonEvent):        # noqa
            # Handle the left mouse release event depending on the current mode
            match (self._mode):
                case DrawingView.Mode.SelectMode:
                    self._selectModeLeftMouseReleaseEvent(event)
                case DrawingView.Mode.ScrollMode:
                    self._scrollModeLeftMouseReleaseEvent(event)
                case DrawingView.Mode.ZoomMode:
                    self._zoomModeLeftMouseReleaseEvent(event)
                case DrawingView.Mode.PlaceMode:
                    self._placeModeLeftMouseReleaseEvent(event)

            self._mouseState = DrawingView.MouseState.Idle
            self._mouseDragged = False

        elif (event.button() == Qt.MouseButton.RightButton and self._mouseState == DrawingView.MouseState.HandlingRightButtonEvent):    # noqa
            # Handle the right mouse press event depending on the current mode. Modes other than SelectMode will
            # trigger the view to go to SelectMode.
            if (self._mode == DrawingView.Mode.SelectMode):
                self._selectModeRightMouseReleaseEvent(event)
            else:
                self.setSelectMode()

            self._mouseState = DrawingView.MouseState.Idle

        elif (event.button() == Qt.MouseButton.MiddleButton and self._mouseState == DrawingView.MouseState.HandlingMiddleButtonEvent):  # noqa
            # Stop mouse pan events.
            self.setCursor(self._panOriginalCursor)
            self._panTimer.stop()

            self._mouseState = DrawingView.MouseState.Idle

    def wheelEvent(self, event: QWheelEvent) -> None:
        if (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            # Zoom in or out on a mouse wheel vertical event if the control key is held down.
            if (event.angleDelta().y() > 0):
                self.zoomIn()
            elif (event.angleDelta().y() < 0):
                self.zoomOut()
        else:
            super().wheelEvent(event)

    # ==================================================================================================================

    def _selectModeNoButtonMouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouseInfoChanged.emit(self._createMouseInfo1(self.mapToScene(event.pos())))

    def _selectModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        self._selectMouseState = DrawingView.SelectModeMouseState.Select

        # Update mouse down item
        self._selectMouseDownItem = self.itemAt(self._mouseButtonDownScenePosition)

        # Determine if the user clicked on one of the mouse down item's control points
        self._selectMouseDownPoint = None
        if (self._selectMouseDownItem is not None and
                self._selectMouseDownItem.isSelected() and len(self._selectedItems) == 1):
            for point in self._selectMouseDownItem.points():
                if (self._pointRect(point).contains(self._mouseButtonDownScenePosition)):
                    self._selectMouseDownPoint = point
                    break
            if (self._selectMouseDownPoint is not None and not self._selectMouseDownPoint.isControlPoint()):
                self._selectMouseDownPoint = None

        # Update focus item
        self._selectFocusItem = self._selectMouseDownItem

        self.viewport().update()

    def _selectModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        match (self._selectMouseState):
            case DrawingView.SelectModeMouseState.Select:
                # If we clicked on a control point within a selected item and the item can be resized, then resize the
                # item.  Otherwise, if we clicked on a selected item, move the item. Otherwise we didn't click on a
                # selected item, so start drawing a rubber band for item selection.
                if (self._selectMouseDownItem is not None and self._selectMouseDownItem.isSelected()):
                    canResize = (len(self._selectedItems) == 1 and len(self._selectMouseDownItem.points()) >= 2 and
                                 self._selectMouseDownPoint is not None and self._selectMouseDownPoint.isControlPoint())
                    if (canResize):
                        self._selectMouseState = DrawingView.SelectModeMouseState.ResizeItem
                        self._selectModeResizeItemStartEvent(event)
                    else:
                        self._selectMouseState = DrawingView.SelectModeMouseState.MoveItems
                        self._selectModeMoveItemsStartEvent(event)
                else:
                    self._selectMouseState = DrawingView.SelectModeMouseState.RubberBand
                    self._selectModeRubberBandStartEvent(event)
            case DrawingView.SelectModeMouseState.MoveItems:
                # Move the selected items within the scene
                self._selectModeMoveItemsUpdateEvent(event)
            case DrawingView.SelectModeMouseState.ResizeItem:
                # Resize the selected item within the scene
                self._selectModeResizeItemUpdateEvent(event)
            case DrawingView.SelectModeMouseState.RubberBand:
                # Update the rubber band rect to be used for item selection
                self._selectModeRubberBandUpdateEvent(event)
            case _:
                # Do nothing
                pass

    def _selectModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        match (self._selectMouseState):
            case DrawingView.SelectModeMouseState.Select:
                # Select or deselect item as needed
                self._selectModeSingleSelectEvent(event)
            case DrawingView.SelectModeMouseState.MoveItems:
                # Move the selected items within the scene
                self._selectModeMoveItemsEndEvent(event)
            case DrawingView.SelectModeMouseState.ResizeItem:
                # Resize the selected item within the scene
                self._selectModeResizeItemEndEvent(event)
            case DrawingView.SelectModeMouseState.RubberBand:
                # Update the rubber band rect to be used for item selection
                self._selectModeRubberBandEndEvent(event)
            case _:
                # Do nothing
                pass

        # Reset the select mode left mouse event variables
        self._selectMouseState = DrawingView.SelectModeMouseState.Idle
        self._selectMouseDownItem = None
        self._selectMouseDownPoint = None

    # ==================================================================================================================

    def _selectModeSingleSelectEvent(self, event: QMouseEvent) -> None:
        # Add or remove the selectMouseDownItem from the current selection as appropriate
        controlDown = ((event.modifiers() & Qt.KeyboardModifier.ControlModifier) == Qt.KeyboardModifier.ControlModifier)

        newSelection = self._selectedItems.copy() if (controlDown) else []
        if (self._selectMouseDownItem is not None):
            if (controlDown and self._selectMouseDownItem in newSelection):
                newSelection.remove(self._selectMouseDownItem)
            else:
                newSelection.append(self._selectMouseDownItem)
        self.setSelectedItems(newSelection)

        self.mouseInfoChanged.emit('')
        self.viewport().update()

    def _selectModeMoveItemsStartEvent(self, event: QMouseEvent) -> None:
        # Moving items with the mouse is disabled for DrawingView
        pass

    def _selectModeMoveItemsUpdateEvent(self, event: QMouseEvent) -> None:
        # Moving items with the mouse is disabled for DrawingView
        pass

    def _selectModeMoveItemsEndEvent(self, event: QMouseEvent) -> None:
        # Moving items with the mouse is disabled for DrawingView
        pass

    def _selectModeResizeItemStartEvent(self, event: QMouseEvent) -> None:
        # Resizing items with the mouse is disabled for DrawingView
        pass

    def _selectModeResizeItemUpdateEvent(self, event: QMouseEvent) -> None:
        # Resizing items with the mouse is disabled for DrawingView
        pass

    def _selectModeResizeItemEndEvent(self, event: QMouseEvent) -> None:
        # Resizing items with the mouse is disabled for DrawingView
        pass

    def _selectModeRubberBandStartEvent(self, event: QMouseEvent) -> None:
        self._selectRubberBandRect = QRect()

    def _selectModeRubberBandUpdateEvent(self, event: QMouseEvent) -> None:
        # Update the selectRubberBandRect based on the mouse event
        self._selectRubberBandRect = QRect(event.pos(), self._mouseButtonDownPosition).normalized()
        self.mouseInfoChanged.emit(self._createMouseInfo2(self._mouseButtonDownScenePosition,
                                                          self.mapToScene(event.pos())))
        self.viewport().update()

    def _selectModeRubberBandEndEvent(self, event: QMouseEvent) -> None:
        # Select the items in the selectRubberBandRect if the rect's width/height are sufficiently large
        if (abs(self._selectRubberBandRect.width()) > QApplication.startDragDistance() and
                abs(self._selectRubberBandRect.height()) > QApplication.startDragDistance()):
            itemsInRubberBand = self.itemsInRect(self.mapRectToScene(self._selectRubberBandRect).normalized())

            controlDown = ((event.modifiers() & Qt.KeyboardModifier.ControlModifier) ==
                           Qt.KeyboardModifier.ControlModifier)
            if (controlDown):
                itemsToSelect = self._selectedItems.copy()
                for item in itemsInRubberBand:
                    if (item not in itemsToSelect):
                        itemsToSelect.append(item)
                self.setSelectedItems(itemsToSelect)
            else:
                self.setSelectedItems(itemsInRubberBand)

        # Reset the select rubber band event variables
        self._selectRubberBandRect = QRect()
        self.mouseInfoChanged.emit('')
        self.viewport().update()

    # ==================================================================================================================

    def _selectModeRightMousePressEvent(self, event: QMouseEvent) -> None:
        # Update the mouse down item
        self._selectMouseDownItem = self.itemAt(self._mouseButtonDownScenePosition)

    def _selectModeRightMouseReleaseEvent(self, event: QMouseEvent) -> None:
        # Clear the mouse down item
        self._selectMouseDownItem = None

    # ==================================================================================================================

    def _scrollModeNoButtonMouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouseInfoChanged.emit(self._createMouseInfo1(self.mapToScene(event.pos())))

    def _scrollModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._scrollInitialHorizontalValue = self.horizontalScrollBar().value()
        self._scrollInitialVerticalValue = self.verticalScrollBar().value()

    def _scrollModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        # Scroll the scroll bars to keep the mouse cursor over the same view position (when possible)
        deltaX = self._mouseButtonDownPosition.x() - event.pos().x()
        deltaY = self._mouseButtonDownPosition.y() - event.pos().y()
        self.horizontalScrollBar().setValue(self._scrollInitialHorizontalValue + deltaX)
        self.verticalScrollBar().setValue(self._scrollInitialVerticalValue + deltaY)

    def _scrollModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.mouseInfoChanged.emit('')

    # ==================================================================================================================

    def _zoomModeNoButtonMouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouseInfoChanged.emit(self._createMouseInfo1(self.mapToScene(event.pos())))

    def _zoomModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        self._zoomRubberBandRect = QRect()

    def _zoomModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        # Update the zoomRubberBandRect based on the mouse event
        self._zoomRubberBandRect = QRect(event.pos(), self._mouseButtonDownPosition).normalized()
        self.mouseInfoChanged.emit(self._createMouseInfo2(self._mouseButtonDownScenePosition,
                                                          self.mapToScene(event.pos())))
        self.viewport().update()

    def _zoomModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        # Zoom the view to the zoomRubberBandRect if the rect's width/height are sufficiently large
        if (abs(self._zoomRubberBandRect.width()) > QApplication.startDragDistance() and
                abs(self._zoomRubberBandRect.height()) > QApplication.startDragDistance()):
            self.zoomToRect(self.mapRectToScene(self._zoomRubberBandRect).normalized())
            self.setSelectMode()

        # Reset the zoom mode variables
        self._zoomRubberBandRect = QRect()
        self.mouseInfoChanged.emit('')
        self.viewport().update()

    # ==================================================================================================================

    def _placeModeNoButtonMouseMoveEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for DrawingView
        pass

    def _placeModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for DrawingView
        pass

    def _placeModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for DrawingView
        pass

    def _placeModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for DrawingView
        pass

    # ==================================================================================================================

    def _mousePanEvent(self) -> None:
        if (self._panCurrentPosition.x() - self._panStartPosition.x() < 0):
            # Scroll to the left, adjusting the horizontal scroll bar minimum if necessary
            delta = round((self._panCurrentPosition.x() - self._panStartPosition.x()) / 64)
            if (self.horizontalScrollBar().value() + delta < self.horizontalScrollBar().minimum()):
                self.horizontalScrollBar().setMinimum(self.horizontalScrollBar().value() + delta)
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().minimum())
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)
        elif (self._panCurrentPosition.x() - self._panStartPosition.x() > 0):
            # Scroll to the right, adjusting the horizontal scroll bar maximum if necessary
            delta = round((self._panCurrentPosition.x() - self._panStartPosition.x()) / 64)
            if (self.horizontalScrollBar().value() + delta > self.horizontalScrollBar().maximum()):
                self.horizontalScrollBar().setMaximum(self.horizontalScrollBar().value() + delta)
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().maximum())
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)

        if (self._panCurrentPosition.y() - self._panStartPosition.y() < 0):
            # Scroll up, adjusting the vertical scroll bar minimum if necessary
            delta = round((self._panCurrentPosition.y() - self._panStartPosition.y()) / 64)
            if (self.verticalScrollBar().value() + delta < self.verticalScrollBar().minimum()):
                self.verticalScrollBar().setMinimum(self.verticalScrollBar().value() + delta)
                self.verticalScrollBar().setValue(self.verticalScrollBar().minimum())
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta)
        elif (self._panCurrentPosition.y() - self._panStartPosition.y() > 0):
            # Scroll down, adjusting the vertical scroll bar maximum if necessary
            delta = round((self._panCurrentPosition.y() - self._panStartPosition.y()) / 64)
            if (self.verticalScrollBar().value() + delta > self.verticalScrollBar().maximum()):
                self.verticalScrollBar().setMaximum(self.verticalScrollBar().value() + delta)
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta)

        self.viewport().update()

    # ==================================================================================================================

    def _itemsRect(self, items: list[DrawingItem]) -> QRectF:
        rect = QRectF()
        for item in items:
            rect = rect.united(item.mapRectToScene(item.boundingRect()))
        return rect

    def _itemsCenter(self, items: list[DrawingItem]) -> QPointF:
        if (len(items) > 1):
            return self._itemsRect(items).center()
        if (len(items) == 1):
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
            mappedPenSize = self.mapToScene(QPoint(8, 8)) - self.mapToScene(QPoint(0, 0))    # type: ignore
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

    # ==================================================================================================================

    def _shouldConnect(self, point1: DrawingItemPoint, point2: DrawingItemPoint) -> bool:
        # The points should be connected if both are members of different valid items, both are connection points,
        # at least one point is free to be resized when the other point is moved, the points are not already connected,
        # and the points are at the same location within the scene.
        if (point1.item() is not None and point2.item() is not None and point1.item() != point2.item() and
                point1.isConnectionPoint() and point2.isConnectionPoint() and (point1.isFree() or point2.isFree()) and
                not point1.isConnected(point2) and not point2.isConnected(point1)):
            vec = point1.item().mapToScene(point1.position()) - point2.item().mapToScene(point2.position())
            return (math.sqrt(vec.x() * vec.x() + vec.y() * vec.y()) <= 1E-6)
        return False

    def _shouldDisconnect(self, point1: DrawingItemPoint, point2: DrawingItemPoint) -> bool:
        # The points should be disconnected if they are already connected to each other and if they are not at the
        # same location within the scene and point2 cannot be resized to move it to the same location as point1.
        if (point1.item() is not None and point2.item() is not None and
                point1.isConnected(point2) and point2.isConnected(point1)):
            return (point1.item().mapToScene(point1.position()) != point2.item().mapToScene(point2.position()) and
                    not point2.isFree())
        return False

    def _pointRect(self, point: DrawingItemPoint) -> QRectF:
        if (point.item() is not None):
            position = point.item().mapToScene(point.position())
            size = 8 / self.scale()
            return QRectF(position.x() - size / 2, position.y() - size / 2, size, size)
        return QRectF()

    # ==================================================================================================================

    def _createMouseInfo1(self, position: QPointF) -> str:
        return f'({position.x():.2f},{position.y():.2f})'

    def _createMouseInfo2(self, position1: QPointF, position2: QPointF) -> str:
        return (f'({position1.x():.2f},{position1.y():.2f}) - ({position2.x():.2f},{position2.y():.2f})  '
                f'\u0394 = ({position2.x() - position1.x():.2f},{position2.y() - position1.y():.2f})')
