# odgdrawingview.py
# Copyright (C) 2023  Jason Allen
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
from enum import Enum, IntEnum
from typing import Any
from PySide6.QtCore import Qt, QLineF, QMarginsF, QPoint, QPointF, QRect, QRectF, QSizeF, QTimer, Signal
from PySide6.QtGui import (QBrush, QColor, QCursor, QMouseEvent, QPainter, QPainterPath, QPaintEvent, QPalette, QPen,
                           QResizeEvent, QTransform, QWheelEvent)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QRubberBand, QStyle, QStyleHintReturnMask,
                               QStyleOptionRubberBand)
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgItemStyle
from .odgpage import OdgPage
from .odgreader import OdgReader
from .odgunits import OdgUnits


class OdgDrawingView(QAbstractScrollArea):
    class Mode(IntEnum):
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

    propertyChanged = Signal(str, object)

    pageInserted = Signal(OdgPage, int)
    pageRemoved = Signal(OdgPage, int)
    currentPageChanged = Signal(OdgPage)
    currentPageIndexChanged = Signal(int)

    scaleChanged = Signal(float)
    modeChanged = Signal(int)
    modeTextChanged = Signal(str)
    mouseInfoChanged = Signal(str)

    currentItemsChanged = Signal(list)

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMouseTracking(True)

        # Master page properties
        self._units: OdgUnits = OdgUnits.Inches
        self._pageSize: QSizeF = QSizeF(8.2, 6.2)
        self._pageMargins: QMarginsF = QMarginsF(0.1, 0.1, 0.1, 0.1)
        self._backgroundColor: QColor = QColor(255, 255, 255)

        self._grid: float = 0.05
        self._gridVisible: bool = True
        self._gridColor: QColor = QColor(0, 128, 128)
        self._gridSpacingMajor: int = 8
        self._gridSpacingMinor: int = 2

        # Item styles
        self._defaultItemStyle: OdgItemStyle = OdgItemStyle.createDefaultStyle(self._units)
        self._itemStyles: list[OdgItemStyle] = []

        # Pages
        self._pages: list[OdgPage] = []
        self._currentPage: OdgPage | None = None

        # Selection
        self._selectedItems: list[OdgItem] = []
        self._selectMouseDownItem: OdgItem | None = None
        self._selectMouseDownPoint: OdgItemPoint | None = None
        self._selectFocusItem: OdgItem | None = None

        # Internal state variables
        self._transform = QTransform()
        self._transformInverse = QTransform()

        self._mode: OdgDrawingView.Mode = OdgDrawingView.Mode.SelectMode

        self._mouseState: OdgDrawingView.MouseState = OdgDrawingView.MouseState.Idle
        self._mouseButtonDownPosition: QPoint = QPoint()
        self._mouseButtonDownScenePosition: QPointF = QPointF()
        self._mouseDragged: bool = False

        self._selectMouseState: OdgDrawingView.SelectModeMouseState = OdgDrawingView.SelectModeMouseState.Idle
        self._selectRubberBandRect: QRect = QRect()

        self._scrollInitialHorizontalValue: int = 0
        self._scrollInitialVerticalValue: int = 0

        self._zoomRubberBandRect: QRect = QRect()

        self._placeModeItems: list[OdgItem] = []
        self._placeByMousePressAndRelease: bool = False

        self._panOriginalCursor: Qt.CursorShape = Qt.CursorShape.ArrowCursor
        self._panStartPosition: QPoint = QPoint()
        self._panCurrentPosition: QPoint = QPoint()
        self._panTimer: QTimer = QTimer()
        self._panTimer.setInterval(5)
        self._panTimer.timeout.connect(self._mousePanEvent)     # type: ignore

    def __del__(self) -> None:
        self.clearPages()
        self.clearItemStyles()
        del self._defaultItemStyle

    # ==================================================================================================================

    def setUnits(self, units: OdgUnits) -> None:
        if (units != self._units):
            oldUnits = self._units

            self._units = units
            self._pageSize.setWidth(OdgUnits.convert(self._pageSize.width(), oldUnits, self._units))
            self._pageSize.setHeight(OdgUnits.convert(self._pageSize.height(), oldUnits, self._units))
            self._pageMargins.setLeft(OdgUnits.convert(self._pageMargins.left(), oldUnits, self._units))
            self._pageMargins.setTop(OdgUnits.convert(self._pageMargins.top(), oldUnits, self._units))
            self._pageMargins.setRight(OdgUnits.convert(self._pageMargins.right(), oldUnits, self._units))
            self._pageMargins.setBottom(OdgUnits.convert(self._pageMargins.bottom(), oldUnits, self._units))
            self._grid = OdgUnits.convert(self._grid, oldUnits, self._units)

            scaleFactor = OdgUnits.convert(1, oldUnits, self._units)

            self._defaultItemStyle.scale(scaleFactor)
            for style in self._itemStyles:
                style.scale(scaleFactor)

            for page in self._pages:
                for item in page.items():
                    item.scale(scaleFactor)

            self.propertyChanged.emit('units', self._units)

            self.setScale(self.scale() / scaleFactor)

    def units(self) -> OdgUnits:
        return self._units

    # ==================================================================================================================

    def setPageSize(self, size: QSizeF) -> None:
        if (self._pageSize != size and size.width() > 0 and size.height() > 0):
            self._pageSize = QSizeF(size)
            self.propertyChanged.emit('pageSize', self._pageSize)
            self.zoomFit()

    def setPageMargins(self, margins: QMarginsF) -> None:
        if (self._pageMargins != margins and (margins.left() >= 0 and margins.top() >= 0 and
                                              margins.right() >= 0 and margins.bottom() >= 0)):
            self._pageMargins = QMarginsF(margins)
            self.propertyChanged.emit('pageMargins', self._pageMargins)
            self.zoomFit()

    def setBackgroundColor(self, color: QColor) -> None:
        if (self._backgroundColor != color):
            self._backgroundColor = QColor(color)
            self.propertyChanged.emit('backgroundColor', self._backgroundColor)
            self.viewport().update()

    def pageSize(self) -> QSizeF:
        return self._pageSize

    def pageMargins(self) -> QMarginsF:
        return self._pageMargins

    def backgroundColor(self) -> QColor:
        return self._backgroundColor

    def pageRect(self) -> QRectF:
        return QRectF(-self._pageMargins.left(), -self._pageMargins.top(),
                      self._pageSize.width(), self._pageSize.height())

    def contentRect(self) -> QRectF:
        return QRectF(0, 0, self._pageSize.width() - self._pageMargins.left() - self._pageMargins.right(),
                      self._pageSize.height() - self._pageMargins.top() - self._pageMargins.bottom())

    # ==================================================================================================================

    def setGrid(self, grid: float) -> None:
        if (self._grid != grid and grid >= 0):
            self._grid = grid
            self.propertyChanged.emit('grid', self._grid)
            self.viewport().update()

    def setGridVisible(self, visible: bool) -> None:
        if (self._gridVisible != visible):
            self._gridVisible = visible
            self.propertyChanged.emit('gridVisible', self._gridVisible)
            self.viewport().update()

    def setGridColor(self, color: QColor) -> None:
        if (self._gridColor != color):
            self._gridColor = QColor(color)
            self.propertyChanged.emit('gridColor', self._gridColor)
            self.viewport().update()

    def setGridSpacingMajor(self, spacing: int) -> None:
        if (self._gridSpacingMajor != spacing and spacing >= 0):
            self._gridSpacingMajor = spacing
            self.propertyChanged.emit('gridSpacingMajor', self._gridSpacingMajor)
            self.viewport().update()

    def setGridSpacingMinor(self, spacing: int) -> None:
        if (self._gridSpacingMinor != spacing and spacing >= 0):
            self._gridSpacingMinor = spacing
            self.propertyChanged.emit('gridSpacingMinor', self._gridSpacingMinor)
            self.viewport().update()

    def grid(self) -> float:
        return self._grid

    def isGridVisible(self) -> bool:
        return self._gridVisible

    def gridColor(self) -> QColor:
        return self._gridColor

    def gridSpacingMajor(self) -> int:
        return self._gridSpacingMajor

    def gridSpacingMinor(self) -> int:
        return self._gridSpacingMinor

    def roundToGrid(self, value: float) -> float:
        return self._grid * round(value / self._grid) if (self._grid != 0) else value

    def roundPointToGrid(self, position: QPointF) -> QPointF:
        return QPointF(self.roundToGrid(position.x()), self.roundToGrid(position.y()))

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> bool:
        match (name):
            case 'units':
                if (isinstance(value, OdgUnits)):
                    self.setUnits(value)
            case 'pageSize':
                if (isinstance(value, QSizeF)):
                    self.setPageSize(value)
            case 'pageMargins':
                if (isinstance(value, QMarginsF)):
                    self.setPageMargins(value)
            case 'backgroundColor':
                if (isinstance(value, QColor)):
                    self.setBackgroundColor(value)
            case 'grid':
                if (isinstance(value, float)):
                    self.setGrid(value)
            case 'gridVisible':
                if (isinstance(value, bool)):
                    self.setGridVisible(value)
            case 'gridColor':
                if (isinstance(value, QColor)):
                    self.setGridColor(value)
            case 'gridSpacingMajor':
                if (isinstance(value, int)):
                    self.setGridSpacingMajor(value)
            case 'gridSpacingMinor':
                if (isinstance(value, int)):
                    self.setGridSpacingMinor(value)
        return True

    def property(self, name: str) -> Any:
        match (name):
            case 'units':
                return self.units()
            case 'pageSize':
                return self.pageSize()
            case 'pageMargins':
                return self.pageMargins()
            case 'backgroundColor':
                return self.backgroundColor()
            case 'grid':
                return self.grid()
            case 'gridVisible':
                return self.isGridVisible()
            case 'gridColor':
                return self.gridColor()
            case 'gridSpacingMajor':
                return self.gridSpacingMajor()
            case 'gridSpacingMinor':
                return self.gridSpacingMinor()
        return None

    # ==================================================================================================================

    def clearItemStyles(self) -> None:
        del self._itemStyles[:]

    def defaultItemStyle(self) -> OdgItemStyle:
        return self._defaultItemStyle

    # ==================================================================================================================

    def addPage(self, page: OdgPage) -> None:
        self.insertPage(len(self._pages), page)

    def insertPage(self, index: int, page: OdgPage) -> None:
        if (page not in self._pages):
            self._pages.insert(index, page)
            # pylint: disable-next=W0212
            page._parent = self
            self.pageInserted.emit(page, index)
            self.setCurrentPage(page)

    def removePage(self, page: OdgPage) -> None:
        if (page in self._pages):
            index = self._pages.index(page)

            newCurrentPageIndex = -1
            if (index > 0):
                newCurrentPageIndex = index - 1
            elif (index < len(self._pages) - 1):
                newCurrentPageIndex = index + 1

            self._pages.remove(page)
            # pylint: disable-next=W0212
            page._parent = None
            self.pageRemoved.emit(page, index)
            self.setCurrentPageIndex(newCurrentPageIndex)

    def movePage(self, page: OdgPage, newIndex: int) -> None:
        if (page in self._pages):
            index = self._pages.index(page)

            self._pages.remove(page)
            self.pageRemoved.emit(page, index)

            self._pages.insert(newIndex, page)
            self.pageInserted.emit(page, newIndex)

            self.setCurrentPage(page)

    def clearPages(self) -> None:
        self.setSelectMode()
        self.setSelectedItems([])

        while (len(self._pages) > 0):
            page = self._pages[-1]
            self.removePage(page)
            del page

    def pages(self) -> list[OdgPage]:
        return self._pages

    # ==================================================================================================================

    def setCurrentPage(self, page: OdgPage | None) -> None:
        # Only allow us to use a page that is part of the view as the current page, but also allow None
        if ((page is None or page in self._pages) and page != self._currentPage):
            self.setSelectMode()
            self.setSelectedItems([])

            self._currentPage = page
            self.currentPageChanged.emit(self._currentPage)
            self.currentPageIndexChanged.emit(self.currentPageIndex())

            self.viewport().update()

    def setCurrentPageIndex(self, index: int) -> None:
        if (0 <= index < len(self._pages)):
            self.setCurrentPage(self._pages[index])
        else:
            self.setCurrentPage(None)

    def currentPage(self) -> OdgPage | None:
        return self._currentPage

    def currentPageIndex(self) -> int:
        if (self._currentPage is not None and self._currentPage in self._pages):
            return self._pages.index(self._currentPage)
        return -1

    # ==================================================================================================================

    def currentPageItems(self) -> list[OdgItem]:
        if (isinstance(self._currentPage, OdgPage)):
            return self._currentPage.items()
        return []

    def currentPageItemsInRect(self, rect: QRectF) -> list[OdgItem]:
        items = []
        for item in self.currentPageItems():
            if (self._isItemInRect(item, rect)):
                items.append(item)
        return items

    def currentPageItemAt(self, position: QPointF) -> OdgItem | None:
        # Favor selected items; if not found in the selected items, search all items in the scene
        for item in reversed(self._selectedItems):
            if (self._isPointInItem(item, position)):
                return item
        for item in reversed(self.currentPageItems()):
            if (self._isPointInItem(item, position)):
                return item
        return None

    # ==================================================================================================================

    def setSelectedItems(self, items: list[OdgItem]) -> None:
        if (self._selectedItems != items):
            for item in self._selectedItems:
                item.setSelected(False)

            self._selectedItems = items

            for item in self._selectedItems:
                item.setSelected(True)

            if (self._mode == OdgDrawingView.Mode.SelectMode):
                self.currentItemsChanged.emit(self._selectedItems)

            self.viewport().update()

    def selectedItems(self) -> list[OdgItem]:
        return self._selectedItems

    def mouseDownItem(self) -> OdgItem | None:
        return self._selectMouseDownItem

    def mouseDownPoint(self) -> OdgItemPoint | None:
        return self._selectMouseDownPoint

    def focusItem(self) -> OdgItem | None:
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
                self.centerOn(self.pageRect().center())

    def zoomToRect(self, rect: QRectF = QRectF()) -> None:
        if (rect.width() <= 0 or rect.height() <= 0):
            rect = self.pageRect()

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
        return self._transformInverse.map(QPointF(position + scrollPosition))

    def mapRectToScene(self, rect: QRect) -> QRectF:
        return QRectF(self.mapToScene(rect.topLeft()), self.mapToScene(rect.bottomRight()))

    def mapFromScene(self, position: QPointF) -> QPoint:
        scrollPosition = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
        return self._transform.map(position).toPoint() - scrollPosition

    def mapRectFromScene(self, rect: QRectF) -> QRect:
        return QRect(self.mapFromScene(rect.topLeft()), self.mapFromScene(rect.bottomRight()))

    # ==================================================================================================================

    def setMode(self, mode: 'OdgDrawingView.Mode', placeItems: list[OdgItem],
                placeByMousePressAndRelease: bool) -> None:
        previousMode = self._mode
        if (previousMode != mode or mode == OdgDrawingView.Mode.PlaceMode):
            # Clear any selected items, place items, and mode-related state variables
            self.setSelectedItems([])
            del self._placeModeItems[:]

            self._selectMouseDownItem = None
            self._selectMouseDownPoint = None
            self._selectFocusItem = None

            # Update the mode
            self._mode = mode
            self.modeChanged.emit(self._mode.value)
            match (self._mode):
                case OdgDrawingView.Mode.SelectMode:
                    self.modeTextChanged.emit('Select Mode')
                case OdgDrawingView.Mode.ScrollMode:
                    self.modeTextChanged.emit('Scroll Mode')
                case OdgDrawingView.Mode.ZoomMode:
                    self.modeTextChanged.emit('Zoom Mode')
                case OdgDrawingView.Mode.PlaceMode:
                    if (len(placeItems) == 1):
                        self.modeTextChanged.emit(f'Place {placeItems[0].prettyType()}')
                    else:
                        self.modeTextChanged.emit('Place Mode')

            # Update cursor
            match (self._mode):
                case OdgDrawingView.Mode.SelectMode:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                case OdgDrawingView.Mode.ScrollMode:
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                case OdgDrawingView.Mode.ZoomMode:
                    self.setCursor(Qt.CursorShape.CrossCursor)
                case OdgDrawingView.Mode.PlaceMode:
                    self.setCursor(Qt.CursorShape.CrossCursor)

            # Update the place items, if applicable
            self._placeModeItems = placeItems
            self._placeByMousePressAndRelease = placeByMousePressAndRelease

            # Center the items under the mouse cursor
            centerPosition = self.roundPointToGrid(self._itemsCenter(self._placeModeItems))
            deltaPosition = self.roundPointToGrid(self.mapToScene(
                self.mapFromGlobal(QCursor.pos())) - centerPosition)
            for item in self._placeModeItems:
                item.setPosition(item.position() + deltaPosition)

            # pylint: disable-next=R1714
            if (previousMode == OdgDrawingView.Mode.PlaceMode or self._mode == OdgDrawingView.Mode.PlaceMode):
                self.currentItemsChanged.emit(self._placeModeItems)

            # Update the viewport
            self.viewport().update()

    def mode(self) -> 'OdgDrawingView.Mode':
        return self._mode

    def placeItems(self) -> list[OdgItem]:
        return self._placeModeItems

    # ==================================================================================================================

    def save(self, path: str) -> bool:
        # Saving to file is disabled for OdgDrawingView
        return False

    def load(self, path: str) -> bool:
        self.clear()
        reader = OdgReader(path)
        self._read(reader)
        return True

    def clear(self) -> None:
        self.clearPages()
        self.clearItemStyles()
        OdgItem.resetFactoryCounts()

    def _read(self, reader: OdgReader) -> None:
        reader.startSettingsDocument()
        self._readSettings(reader)
        reader.endDocument()

        reader.startStylesDocument()
        self._readStyles(reader)
        reader.endDocument()

        reader.startContentDocument()
        self._readContent(reader)
        reader.endDocument()

    def _readSettings(self, reader: OdgReader) -> None:
        while (reader.readNextStartElement()):
            if (reader.qualifiedName() == 'office:settings'):
                while (reader.readNextStartElement()):
                    if (reader.qualifiedName() == 'config:config-item-set'):
                        attr = reader.attributes()
                        if (attr.hasAttribute('config:name') and attr.value('config:name') == 'jade:settings'):
                            while (reader.readNextStartElement()):
                                if (reader.qualifiedName() == 'config:config-item'):
                                    attr = reader.attributes()
                                    text = reader.readElementText()
                                    if (attr.hasAttribute('config:name') and attr.hasAttribute('config:type')):
                                        name = attr.value('config:name')
                                        typeStr = attr.value('config:type')
                                        if (name == 'units' and typeStr == 'string'):
                                            self.setUnits(OdgUnits.fromStr(text))
                                            reader.setUnits(self._units)
                                        elif (name == 'grid' and typeStr == 'double'):
                                            self.setGrid(float(text))
                                        elif (name == 'gridVisible' and typeStr == 'boolean'):
                                            self.setGridVisible(text.strip().lower() == 'true')
                                        elif (name == 'gridColor' and typeStr == 'string'):
                                            self.setGridColor(QColor.fromString(text))
                                        elif (name == 'gridSpacingMajor' and typeStr == 'int'):
                                            self.setGridSpacingMajor(int(text))
                                        elif (name == 'gridSpacingMinor' and typeStr == 'int'):
                                            self.setGridSpacingMinor(int(text))
                                else:
                                    reader.skipCurrentElement()
                            reader.setPageSize(self._pageSize)
                            reader.setPageMargins(self._pageMargins)
                    else:
                        reader.skipCurrentElement()
            else:
                reader.skipCurrentElement()

    def _readStyles(self, reader: OdgReader) -> None:
        styles: list[OdgItemStyle] = [self._defaultItemStyle]

        while (reader.readNextStartElement()):
            if (reader.qualifiedName() == 'office:styles'):
                while (reader.readNextStartElement()):
                    if (reader.qualifiedName() == 'style:default-style'):
                        self._defaultItemStyle.read(reader, [])
                    elif (reader.qualifiedName() == 'style:style'):
                        attr = reader.attributes()
                        if (attr.hasAttribute('style:name') and attr.value('style:name') == 'standard'):
                            self._defaultItemStyle.read(reader, [])
                        else:
                            newStyle = OdgItemStyle('')
                            newStyle.read(reader, styles)
                            self._itemStyles.append(newStyle)
                            styles.append(newStyle)
                    else:
                        reader.skipCurrentElement()
            elif (reader.qualifiedName() == 'office:automatic-styles'):
                while (reader.readNextStartElement()):
                    if (reader.qualifiedName() == 'style:page-layout'):
                        self._readPageLayout(reader)
                    elif (reader.qualifiedName() == 'style:style'):
                        self._readPageStyle(reader)
                    else:
                        reader.skipCurrentElement()
            else:
                reader.skipCurrentElement()

    def _readPageLayout(self, reader: OdgReader) -> None:
        reader.skipCurrentElement()

    def _readPageStyle(self, reader: OdgReader) -> None:
        reader.skipCurrentElement()

    def _readContent(self, reader: OdgReader) -> None:
        automaticStyles: list[OdgItemStyle] = []
        styles: list[OdgItemStyle] = [self._defaultItemStyle]
        styles.extend(self._itemStyles)

        while (reader.readNextStartElement()):
            if (reader.qualifiedName() == 'office:automatic-styles'):
                while (reader.readNextStartElement()):
                    if (reader.qualifiedName() == 'style:style'):
                        newStyle = OdgItemStyle('')
                        newStyle.read(reader, styles)
                        automaticStyles.append(newStyle)
                    else:
                        reader.skipCurrentElement()
            elif (reader.qualifiedName() == 'office:body'):
                while (reader.readNextStartElement()):
                    if (reader.qualifiedName() == 'office:drawing'):
                        while (reader.readNextStartElement()):
                            if (reader.qualifiedName() == 'draw:page'):
                                newPage = OdgPage('')
                                newPage.read(reader, automaticStyles)
                                self.addPage(newPage)
                            else:
                                reader.skipCurrentElement()
                    else:
                        reader.skipCurrentElement()
            else:
                reader.skipCurrentElement()

    # ==================================================================================================================

    def selectAll(self) -> None:
        if (self._mode == OdgDrawingView.Mode.SelectMode):
            self.setSelectedItems(self.currentPageItems())

    def selectNone(self) -> None:
        if (self._mode == OdgDrawingView.Mode.SelectMode):
            self.setSelectedItems([])

    # ==================================================================================================================

    def zoomIn(self) -> None:
        self.setScale(self.scale() * math.sqrt(math.sqrt(2)))

    def zoomOut(self) -> None:
        self.setScale(self.scale() / math.sqrt(math.sqrt(2)))

    def zoomFit(self) -> None:
        self.zoomToRect(self.pageRect())

    # ==================================================================================================================

    def setSelectMode(self) -> None:
        self.setMode(OdgDrawingView.Mode.SelectMode, [], False)

    def setScrollMode(self) -> None:
        self.setMode(OdgDrawingView.Mode.ScrollMode, [], False)

    def setZoomMode(self) -> None:
        self.setMode(OdgDrawingView.Mode.ZoomMode, [], False)

    def setPlaceMode(self, items: list[OdgItem], placeByMousePressAndRelease: bool) -> None:
        if (len(items) > 0):
            self.setMode(OdgDrawingView.Mode.PlaceMode, items, placeByMousePressAndRelease)
        else:
            self.setMode(OdgDrawingView.Mode.SelectMode, [], False)

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
        if (isinstance(self._currentPage, OdgPage)):
            self._drawBackground(painter, export)
            self._drawItems(painter, self._currentPage.items())

            if (not export):
                self._drawItems(painter, self._placeModeItems)
                self._drawItemPoints(painter, self._selectedItems)
                self._drawHotpoints(painter, self._selectedItems + self._placeModeItems)
                self._drawRubberBand(painter, self._selectRubberBandRect)
                self._drawRubberBand(painter, self._zoomRubberBandRect)

    def _drawBackground(self, painter: QPainter, export: bool) -> None:
        bgColor = self._backgroundColor
        pageBorderColor = QColor(255 - bgColor.red(), 255 - bgColor.green(), 255 - bgColor.blue())
        contentBorderColor = QColor(128, 128, 128)

        if (not export):
            # Draw background
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
            painter.setBackground(QBrush(self._backgroundColor))
            painter.setBrush(QBrush(self._backgroundColor))
            painter.setPen(QPen(QBrush(pageBorderColor), 0))
            painter.drawRect(self.pageRect())

            # Draw content border
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.setPen(QPen(QBrush(contentBorderColor), 0))
            painter.drawRect(self.contentRect())
        else:
            # Draw background
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
            painter.setBackground(QBrush(self._backgroundColor))
            painter.setBrush(QBrush(self._backgroundColor))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(self.pageRect())

        # Draw grid
        if (not export and self._gridVisible and self._grid > 0):
            gridRect = self.contentRect()

            # Minor grid lines
            if (self._gridSpacingMinor > 0):
                painter.setPen(QPen(QBrush(self._gridColor), 0, Qt.PenStyle.DotLine))

                gridInterval = self._grid * self._gridSpacingMinor
                gridLeftIndex = math.ceil(gridRect.left() / gridInterval)
                gridRightIndex = math.floor(gridRect.right() / gridInterval)
                gridTopIndex = math.ceil(gridRect.top() / gridInterval)
                gridBottomIndex = math.floor(gridRect.bottom() / gridInterval)
                for xIndex in range(gridLeftIndex, gridRightIndex + 1):
                    x = xIndex * gridInterval
                    painter.drawLine(QLineF(x, gridRect.top(), x, gridRect.bottom()))
                for yIndex in range(gridTopIndex, gridBottomIndex + 1):
                    y = yIndex * gridInterval
                    painter.drawLine(QLineF(gridRect.left(), y, gridRect.right(), y))

            # Major grid lines
            if (self._gridSpacingMajor > 0):
                painter.setPen(QPen(QBrush(self._gridColor), 0, Qt.PenStyle.SolidLine))

                gridInterval = self._grid * self._gridSpacingMajor
                gridLeftIndex = math.ceil(gridRect.left() / gridInterval)
                gridRightIndex = math.floor(gridRect.right() / gridInterval)
                gridTopIndex = math.ceil(gridRect.top() / gridInterval)
                gridBottomIndex = math.floor(gridRect.bottom() / gridInterval)
                for xIndex in range(gridLeftIndex, gridRightIndex + 1):
                    x = xIndex * gridInterval
                    painter.drawLine(QLineF(x, gridRect.top(), x, gridRect.bottom()))
                for yIndex in range(gridTopIndex, gridBottomIndex + 1):
                    y = yIndex * gridInterval
                    painter.drawLine(QLineF(gridRect.left(), y, gridRect.right(), y))

            # Draw content border again
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.setPen(QPen(QBrush(self._gridColor), 0))
            painter.drawRect(self.contentRect())

    def _drawItems(self, painter: QPainter, items: list[OdgItem]) -> None:
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, True)

        for item in items:
            painter.translate(item.position())
            painter.setTransform(item.transform(), True)

            item.paint(painter)

            # For shape testing
            # painter.setBrush(QBrush(QColor(255, 0, 255, 128)))
            # painter.setPen(QPen(Qt.PenStyle.NoPen))
            # painter.drawPath(self._itemAdjustedShape(item))

            painter.setTransform(item.transformInverse(), True)
            painter.translate(-item.position())

    def _drawItemPoints(self, painter: QPainter, items: list[OdgItem]) -> None:
        bgColor = self._backgroundColor
        borderColor = QColor(255 - bgColor.red(), 255 - bgColor.green(), 255 - bgColor.blue())

        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
        painter.setPen(QPen(borderColor, 0))

        for item in items:
            for point in item.points():
                controlPoint = (point.isControlPoint() or point.type() == OdgItemPoint.Type.NoType)
                connectionPoint = point.isConnectionPoint()
                if (controlPoint or connectionPoint):
                    if (connectionPoint and not controlPoint):
                        painter.setBrush(QColor(255, 255, 0))
                    else:
                        painter.setBrush(QColor(0, 224, 0))
                    painter.drawRect(self._pointRect(point))

    def _drawHotpoints(self, painter: QPainter, items: list[OdgItem]) -> None:
        if (len(items) > 0):
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, False)
            painter.setBrush(QBrush(QColor(255, 128, 0, 192)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))

            for item in items:
                for point in item.points():
                    for otherItem in self.currentPageItems():
                        for otherPoint in otherItem.points():
                            if (self._shouldConnect(point, otherPoint)):
                                rect = self._pointRect(point)
                                rect.adjust(-rect.width(), -rect.height(), rect.width(), rect.height())
                                painter.drawEllipse(rect)

    def _drawRubberBand(self, painter: QPainter, rect: QRect) -> None:
        if (rect.width() > 0 and rect.height() > 0):
            painter.save()
            painter.resetTransform()
            painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing, True)

            option = QStyleOptionRubberBand()
            option.initFrom(self.viewport())
            option.rect = rect                              # type: ignore
            option.shape = QRubberBand.Shape.Rectangle      # type: ignore

            mask = QStyleHintReturnMask()
            if (self.viewport().style().styleHint(QStyle.StyleHint.SH_RubberBand_Mask, option, self.viewport(), mask)):
                painter.setClipRegion(mask.region, Qt.ClipOperation.IntersectClip)      # type: ignore

            self.viewport().style().drawControl(QStyle.ControlElement.CE_RubberBand, option, painter, self.viewport())

            painter.restore()

    # ==================================================================================================================

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._updateTransformAndScrollBars()

    def _updateTransformAndScrollBars(self, scale: float = 0.0) -> None:
        if (scale <= 0):
            scale = self.scale()

        pageRect = self.pageRect()
        contentWidth = round(pageRect.width() * scale) + 1
        contentHeight = round(pageRect.height() * scale) + 1
        viewportWidth = self.maximumViewportSize().width()
        viewportHeight = self.maximumViewportSize().height()

        scrollBarExtent = self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent, None, self)
        if (contentWidth > viewportWidth and self.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded):
            viewportWidth = viewportWidth - scrollBarExtent
        if (contentHeight > viewportHeight and self.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded):   # noqa
            viewportHeight = viewportHeight - scrollBarExtent

        # Update transform
        self._transform.reset()
        self._transform.translate(-pageRect.left() * scale, -pageRect.top() * scale)
        if (contentWidth < viewportWidth):
            self._transform.translate(-(pageRect.width() * scale - viewportWidth + 1) / 2, 0)
        if (contentHeight < viewportHeight):
            self._transform.translate(0, -(pageRect.height() * scale - viewportHeight + 1) / 2)
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
        if (event.button() == Qt.MouseButton.LeftButton and self._mouseState == OdgDrawingView.MouseState.Idle):
            self._mouseState = OdgDrawingView.MouseState.HandlingLeftButtonEvent
            self._mouseButtonDownPosition = event.pos()
            self._mouseButtonDownScenePosition = self.mapToScene(self._mouseButtonDownPosition)

            # Handle the left mouse press event depending on the current mode
            match (self._mode):
                case OdgDrawingView.Mode.SelectMode:
                    self._selectModeLeftMousePressEvent(event)
                case OdgDrawingView.Mode.ScrollMode:
                    self._scrollModeLeftMousePressEvent(event)
                case OdgDrawingView.Mode.ZoomMode:
                    self._zoomModeLeftMousePressEvent(event)
                case OdgDrawingView.Mode.PlaceMode:
                    self._placeModeLeftMousePressEvent(event)

        elif (event.button() == Qt.MouseButton.RightButton and self._mouseState == OdgDrawingView.MouseState.Idle):
            self._mouseState = OdgDrawingView.MouseState.HandlingRightButtonEvent
            self._mouseButtonDownPosition = event.pos()
            self._mouseButtonDownScenePosition = self.mapToScene(self._mouseButtonDownPosition)

            # Handle the right mouse press event depending on the current mode. Modes other than SelectMode ignore
            # this event.
            if (self._mode == OdgDrawingView.Mode.SelectMode):
                self._selectModeRightMousePressEvent(event)

        elif (event.button() == Qt.MouseButton.MiddleButton and self._mouseState == OdgDrawingView.MouseState.Idle):
            self._mouseState = OdgDrawingView.MouseState.HandlingMiddleButtonEvent
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
        if ((event.buttons() & Qt.MouseButton.LeftButton) and self._mouseState == OdgDrawingView.MouseState.HandlingLeftButtonEvent):        # noqa
            dragDistance = (self._mouseButtonDownPosition - event.pos()).manhattanLength()      # type:ignore
            self._mouseDragged = (self._mouseDragged or dragDistance >= QApplication.startDragDistance())

            if (self._mouseDragged):
                # Handle the left mouse drag event depending on the current mode
                match (self._mode):
                    case OdgDrawingView.Mode.SelectMode:
                        self._selectModeLeftMouseDragEvent(event)
                    case OdgDrawingView.Mode.ScrollMode:
                        self._scrollModeLeftMouseDragEvent(event)
                    case OdgDrawingView.Mode.ZoomMode:
                        self._zoomModeLeftMouseDragEvent(event)
                    case OdgDrawingView.Mode.PlaceMode:
                        self._placeModeLeftMouseDragEvent(event)

        elif ((event.buttons() & Qt.MouseButton.RightButton) and self._mouseState == OdgDrawingView.MouseState.HandlingRightButtonEvent):    # noqa
            # In all modes, right mouse drag events are ignored
            pass

        elif ((event.buttons() & Qt.MouseButton.MiddleButton) and self._mouseState == OdgDrawingView.MouseState.HandlingMiddleButtonEvent):  # noqa
            # Update current position for mouse pan events
            self._panCurrentPosition = event.pos()

        else:
            # Handle the left mouse move event (with no buttons held down) depending on the current mode
            match (self._mode):
                case OdgDrawingView.Mode.SelectMode:
                    self._selectModeNoButtonMouseMoveEvent(event)
                case OdgDrawingView.Mode.ScrollMode:
                    self._scrollModeNoButtonMouseMoveEvent(event)
                case OdgDrawingView.Mode.ZoomMode:
                    self._zoomModeNoButtonMouseMoveEvent(event)
                case OdgDrawingView.Mode.PlaceMode:
                    self._placeModeNoButtonMouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton and self._mouseState == OdgDrawingView.MouseState.HandlingLeftButtonEvent):         # noqa
            # Handle the left mouse release event depending on the current mode
            match (self._mode):
                case OdgDrawingView.Mode.SelectMode:
                    self._selectModeLeftMouseReleaseEvent(event)
                case OdgDrawingView.Mode.ScrollMode:
                    self._scrollModeLeftMouseReleaseEvent(event)
                case OdgDrawingView.Mode.ZoomMode:
                    self._zoomModeLeftMouseReleaseEvent(event)
                case OdgDrawingView.Mode.PlaceMode:
                    self._placeModeLeftMouseReleaseEvent(event)

            self._mouseState = OdgDrawingView.MouseState.Idle
            self._mouseDragged = False

        elif (event.button() == Qt.MouseButton.RightButton and self._mouseState == OdgDrawingView.MouseState.HandlingRightButtonEvent):     # noqa
            # Handle the right mouse press event depending on the current mode. Modes other than SelectMode will
            # trigger the view to go to SelectMode.
            if (self._mode == OdgDrawingView.Mode.SelectMode):
                self._selectModeRightMouseReleaseEvent(event)
            else:
                self.setSelectMode()

            self._mouseState = OdgDrawingView.MouseState.Idle

        elif (event.button() == Qt.MouseButton.MiddleButton and self._mouseState == OdgDrawingView.MouseState.HandlingMiddleButtonEvent):   # noqa
            # Stop mouse pan events.
            self.setCursor(self._panOriginalCursor)
            self._panTimer.stop()

            self._mouseState = OdgDrawingView.MouseState.Idle

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
        self._selectMouseState = OdgDrawingView.SelectModeMouseState.Select

        # Update mouse down item
        self._selectMouseDownItem = self.currentPageItemAt(self._mouseButtonDownScenePosition)

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
            case OdgDrawingView.SelectModeMouseState.Select:
                # If we clicked on a control point within a selected item and the item can be resized, then resize the
                # item.  Otherwise, if we clicked on a selected item, move the item. Otherwise we didn't click on a
                # selected item, so start drawing a rubber band for item selection.
                if (self._selectMouseDownItem is not None and self._selectMouseDownItem.isSelected()):
                    canResize = (len(self._selectedItems) == 1 and len(self._selectMouseDownItem.points()) >= 2 and
                                 self._selectMouseDownPoint is not None and self._selectMouseDownPoint.isControlPoint())
                    if (canResize):
                        self._selectMouseState = OdgDrawingView.SelectModeMouseState.ResizeItem
                        self._selectModeResizeItemStartEvent(event)
                    else:
                        self._selectMouseState = OdgDrawingView.SelectModeMouseState.MoveItems
                        self._selectModeMoveItemsStartEvent(event)
                else:
                    self._selectMouseState = OdgDrawingView.SelectModeMouseState.RubberBand
                    self._selectModeRubberBandStartEvent(event)
            case OdgDrawingView.SelectModeMouseState.MoveItems:
                # Move the selected items within the scene
                self._selectModeMoveItemsUpdateEvent(event)
            case OdgDrawingView.SelectModeMouseState.ResizeItem:
                # Resize the selected item within the scene
                self._selectModeResizeItemUpdateEvent(event)
            case OdgDrawingView.SelectModeMouseState.RubberBand:
                # Update the rubber band rect to be used for item selection
                self._selectModeRubberBandUpdateEvent(event)
            case _:
                # Do nothing
                pass

    def _selectModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        match (self._selectMouseState):
            case OdgDrawingView.SelectModeMouseState.Select:
                # Select or deselect item as needed
                self._selectModeSingleSelectEvent(event)
            case OdgDrawingView.SelectModeMouseState.MoveItems:
                # Move the selected items within the scene
                self._selectModeMoveItemsEndEvent(event)
            case OdgDrawingView.SelectModeMouseState.ResizeItem:
                # Resize the selected item within the scene
                self._selectModeResizeItemEndEvent(event)
            case OdgDrawingView.SelectModeMouseState.RubberBand:
                # Update the rubber band rect to be used for item selection
                self._selectModeRubberBandEndEvent(event)
            case _:
                # Do nothing
                pass

        # Reset the select mode left mouse event variables
        self._selectMouseState = OdgDrawingView.SelectModeMouseState.Idle
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
        # Moving items with the mouse is disabled for OdgDrawingView
        pass

    def _selectModeMoveItemsUpdateEvent(self, event: QMouseEvent) -> None:
        # Moving items with the mouse is disabled for OdgDrawingView
        pass

    def _selectModeMoveItemsEndEvent(self, event: QMouseEvent) -> None:
        # Moving items with the mouse is disabled for OdgDrawingView
        pass

    def _selectModeResizeItemStartEvent(self, event: QMouseEvent) -> None:
        # Resizing items with the mouse is disabled for OdgDrawingView
        pass

    def _selectModeResizeItemUpdateEvent(self, event: QMouseEvent) -> None:
        # Resizing items with the mouse is disabled for OdgDrawingView
        pass

    def _selectModeResizeItemEndEvent(self, event: QMouseEvent) -> None:
        # Resizing items with the mouse is disabled for OdgDrawingView
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
            itemsInRubberBand = self.currentPageItemsInRect(
                self.mapRectToScene(self._selectRubberBandRect).normalized())

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
        self._selectMouseDownItem = self.currentPageItemAt(self._mouseButtonDownScenePosition)

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
        # Placing items with the mouse is disabled for OdgDrawingView
        pass

    def _placeModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for OdgDrawingView
        pass

    def _placeModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for OdgDrawingView
        pass

    def _placeModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        # Placing items with the mouse is disabled for OdgDrawingView
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

    def _itemsRect(self, items: list[OdgItem]) -> QRectF:
        rect = QRectF()
        for item in items:
            rect = rect.united(item.mapRectToScene(item.boundingRect()))
        return rect

    def _itemsCenter(self, items: list[OdgItem]) -> QPointF:
        if (len(items) > 1):
            return self._itemsRect(items).center()
        if (len(items) == 1):
            return items[0].position()
        return QPointF()

    def _isItemInRect(self, item: OdgItem, rect: QRectF) -> bool:
        return rect.contains(item.mapRectToScene(item.boundingRect()))

    def _isPointInItem(self, item: OdgItem, position: QPointF) -> bool:
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

    def _itemAdjustedShape(self, item: OdgItem) -> QPainterPath:
        adjustedShape = QPainterPath()

        # Determine minimum pen width
        mappedPenSize = self.mapToScene(QPoint(8, 8)) - self.mapToScene(QPoint(0, 0))
        minimumPenWidth = max(abs(mappedPenSize.x()), abs(mappedPenSize.y()))

        # Override item's default pen width if needed
        penWidth = item.style().lookupPenWidth()

        if (0 < penWidth < minimumPenWidth):
            originalPenWidth = item.style().penWidth()
            item.style().setPenWidth(minimumPenWidth)
            adjustedShape = QPainterPath(item.shape())
            item.style().setPenWidth(originalPenWidth)
        else:
            adjustedShape = QPainterPath(item.shape())

        return adjustedShape

    # ==================================================================================================================

    def _shouldConnect(self, point1: OdgItemPoint, point2: OdgItemPoint) -> bool:
        # The points should be connected if both are members of different valid items, both are connection points,
        # at least one point is free to be resized when the other point is moved, the points are not already connected,
        # and the points are at the same location within the scene.
        item1 = point1.item()
        item2 = point2.item()
        if (isinstance(item1, OdgItem) and isinstance(item2, OdgItem) and item1 != item2 and
                point1.isConnectionPoint() and point2.isConnectionPoint() and (point1.isFree() or point2.isFree()) and
                not point1.isConnected(point2) and not point2.isConnected(point1)):
            vec = item1.mapToScene(point1.position()) - item2.mapToScene(point2.position())
            return (math.sqrt(vec.x() * vec.x() + vec.y() * vec.y()) <= 1E-6)
        return False

    def _shouldDisconnect(self, point1: OdgItemPoint, point2: OdgItemPoint) -> bool:
        # The points should be disconnected if they are already connected to each other and if they are not at the
        # same location within the scene and point2 cannot be resized to move it to the same location as point1.
        item1 = point1.item()
        item2 = point2.item()
        if (isinstance(item1, OdgItem) and isinstance(item2, OdgItem) and
                point1.isConnected(point2) and point2.isConnected(point1)):
            return (item1.mapToScene(point1.position()) != item2.mapToScene(point2.position()) and not point2.isFree())
        return False

    def _pointRect(self, point: OdgItemPoint) -> QRectF:
        item = point.item()
        if (isinstance(item, OdgItem)):
            position = item.mapToScene(point.position())
            size = 8 / self.scale()
            return QRectF(position.x() - size / 2, position.y() - size / 2, size, size)
        return QRectF()

    # ==================================================================================================================

    def _createMouseInfo1(self, position: QPointF) -> str:
        return f'({position.x():.2f},{position.y():.2f})'

    def _createMouseInfo2(self, position1: QPointF, position2: QPointF) -> str:
        return (f'({position1.x():.2f},{position1.y():.2f}) - ({position2.x():.2f},{position2.y():.2f})  '
                f'\u0394 = ({position2.x() - position1.x():.2f},{position2.y() - position1.y():.2f})')
