# drawingrectresizeitem.py
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
from enum import Enum
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint


class DrawingRectResizeItem(DrawingItem):
    class PointIndex(Enum):
        TopLeft = 0
        TopMiddle = 1
        TopRight = 2
        MiddleRight = 3
        BottomRight = 4
        BottomMiddle = 5
        BottomLeft = 6
        MiddleLeft = 7

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._rect: QRectF = QRectF()
        self._pen: QPen = QPen()

        self._cachedBoundingRect: QRectF = QRectF()

        for _ in range(8):
            self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.ControlAndConnection))

    # ==================================================================================================================

    def setRect(self, rect: QRectF) -> None:
        points = self.points()
        if (len(points) >= 8):
            self._rect = rect

            center = rect.center()
            points[DrawingRectResizeItem.PointIndex.TopLeft.value].setPosition(QPointF(rect.left(), rect.top()))
            points[DrawingRectResizeItem.PointIndex.TopMiddle.value].setPosition(QPointF(center.x(), rect.top()))
            points[DrawingRectResizeItem.PointIndex.TopRight.value].setPosition(QPointF(rect.right(), rect.top()))
            points[DrawingRectResizeItem.PointIndex.MiddleRight.value].setPosition(QPointF(rect.right(), center.y()))
            points[DrawingRectResizeItem.PointIndex.BottomRight.value].setPosition(QPointF(rect.right(), rect.bottom()))
            points[DrawingRectResizeItem.PointIndex.BottomMiddle.value].setPosition(QPointF(center.x(), rect.bottom()))
            points[DrawingRectResizeItem.PointIndex.BottomLeft.value].setPosition(QPointF(rect.left(), rect.bottom()))
            points[DrawingRectResizeItem.PointIndex.MiddleLeft.value].setPosition(QPointF(rect.left(), center.y()))

            self._updateGeometry()

    def rect(self) -> QRectF:
        return self._rect

    # ==================================================================================================================

    def setPen(self, pen: QPen) -> None:
        self._pen = pen
        self._updateGeometry()

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        return self._cachedBoundingRect

    def isValid(self) -> bool:
        return (self._rect.width() != 0 and self._rect.height() != 0)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        points = self.points()
        if (len(points) >= 8):
            # Force the rect to be square if resizing a corner, if applicable
            if (snapTo45Degrees):
                otherCornerPoint = None
                if (point == points[DrawingRectResizeItem.PointIndex.TopLeft.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.BottomRight.value]
                elif (point == points[DrawingRectResizeItem.PointIndex.TopRight.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.BottomLeft.value]
                elif (point == points[DrawingRectResizeItem.PointIndex.BottomRight.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.TopLeft.value]
                elif (point == points[DrawingRectResizeItem.PointIndex.BottomLeft.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.TopRight.value]

                if (otherCornerPoint is not None):
                    otherCornerPosition = self.mapToScene(otherCornerPoint.position())
                    delta = position - otherCornerPosition      # type: ignore

                    targetAngleDegrees = 0
                    if (delta.y() >= 0):
                        targetAngleDegrees = 45 if (delta.x() >= 0) else 135
                    else:
                        targetAngleDegrees = -45 if (delta.x() >= 0) else -135

                    if (targetAngleDegrees != 0):
                        targetAngle = targetAngleDegrees * math.pi / 180
                        length = max(abs(delta.x()), abs(delta.y())) * math.sqrt(2)
                        position.setX(otherCornerPosition.x() + length * math.cos(targetAngle))
                        position.setY(otherCornerPosition.y() + length * math.sin(targetAngle))

            # Move just the one point to its new position
            super().resize(point, position, False)

            # Adjust the other points as needed
            rect = QRectF(points[DrawingRectResizeItem.PointIndex.TopLeft.value].position(),
                          points[DrawingRectResizeItem.PointIndex.BottomRight.value].position())

            pointIndex = points.index(point)
            match (pointIndex):
                case DrawingRectResizeItem.PointIndex.TopLeft.value:
                    rect.setTopLeft(point.position())
                case DrawingRectResizeItem.PointIndex.TopMiddle.value:
                    rect.setTop(point.position().y())
                case DrawingRectResizeItem.PointIndex.TopRight.value:
                    rect.setTopRight(point.position())
                case DrawingRectResizeItem.PointIndex.MiddleRight.value:
                    rect.setRight(point.position().x())
                case DrawingRectResizeItem.PointIndex.BottomRight.value:
                    rect.setBottomRight(point.position())
                case DrawingRectResizeItem.PointIndex.BottomMiddle.value:
                    rect.setBottom(point.position().y())
                case DrawingRectResizeItem.PointIndex.BottomLeft.value:
                    rect.setBottomLeft(point.position())
                case DrawingRectResizeItem.PointIndex.MiddleLeft.value:
                    rect.setLeft(point.position().x())

            # Keep the item's position as the center of the rect
            center = rect.center()
            self.setPosition(self.mapToScene(center))
            rect.translate(-center)

            # Move all points to their final positions
            self.setRect(rect)

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        points = self.points()
        if (len(points) >= 8):
            return self.points()[DrawingRectResizeItem.PointIndex.TopLeft.value]
        return None

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        points = self.points()
        if (len(points) >= 8):
            return self.points()[DrawingRectResizeItem.PointIndex.BottomRight.value]
        return None

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        print(f'{self._pen.widthF() * scale} {self._pen.widthF()} {scale}')
        self._pen.setWidthF(self._pen.widthF() * scale)
        self.setRect(QRectF(QPointF(self._rect.left() * scale, self._rect.top() * scale),
                            QPointF(self._rect.right() * scale, self._rect.bottom() * scale)))

    # ==================================================================================================================

    def _updateGeometry(self):
        # Update bounding rect
        self._cachedBoundingRect = QRectF()
        if (self.isValid()):
            self._cachedBoundingRect = self._rect.normalized()
            if (self._pen.style() != Qt.PenStyle.NoPen):
                halfPenWidth = self._pen.widthF() / 2
                self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)
