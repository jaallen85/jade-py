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

from enum import Enum
from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, QTimer
from PyQt6.QtGui import QBrush, QTransform
from PyQt6.QtWidgets import QAbstractScrollArea
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

    def __init__(self) -> None:
        super().__init__()

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
        self._selectedItemsCenter: QPointF = QPointF()
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
        self._selectRubberBandRect: QRect = QRect()

        self._scrollInitialHorizontalValue: int = 0
        self._scrollInitialVerticalValue: int = 0

        self._zoomRubberBandRect: QRect = QRect()

        self._panStartPos: QPoint = QPoint()
        self._panCurrentPos: QPoint = QPoint()
        self._panTimer: QTimer = QTimer()

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
        pass

    def zoomOut(self) -> None:
        pass

    def zoomFit(self) -> None:
        pass
