# drawingrectitem.py
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
from enum import IntEnum
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingRectItem(DrawingItem):
    class PointIndex(IntEnum):
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

        self._cornerRadius: float = 0.0
        self._brush: QBrush = QBrush()
        self._pen: QPen = QPen()

        for _ in range(8):
            self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.ControlAndConnection))

    def __copy__(self) -> 'DrawingRectItem':
        copiedItem = DrawingRectItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setRect(self.rect())
        copiedItem.setCornerRadius(self.cornerRadius())
        copiedItem.setBrush(self.brush())
        copiedItem.setPen(self.pen())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'rect'

    def prettyName(self) -> str:
        return 'Rect'

    # ==================================================================================================================

    def setRect(self, rect: QRectF) -> None:
        self._rect = QRectF(rect)

        # Set point positions to match self._rect
        if (len(self._points) >= 8):
            center = self._rect.center()
            self._points[DrawingRectItem.PointIndex.TopLeft].setPosition(QPointF(rect.left(), rect.top()))
            self._points[DrawingRectItem.PointIndex.TopMiddle].setPosition(QPointF(center.x(), rect.top()))
            self._points[DrawingRectItem.PointIndex.TopRight].setPosition(QPointF(rect.right(), rect.top()))
            self._points[DrawingRectItem.PointIndex.MiddleRight].setPosition(QPointF(rect.right(), center.y()))
            self._points[DrawingRectItem.PointIndex.BottomRight].setPosition(QPointF(rect.right(), rect.bottom()))
            self._points[DrawingRectItem.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), rect.bottom()))
            self._points[DrawingRectItem.PointIndex.BottomLeft].setPosition(QPointF(rect.left(), rect.bottom()))
            self._points[DrawingRectItem.PointIndex.MiddleLeft].setPosition(QPointF(rect.left(), center.y()))

    def rect(self) -> QRectF:
        return self._rect

    # ==================================================================================================================

    def setCornerRadius(self, radius: float) -> None:
        self._cornerRadius = radius

    def cornerRadius(self) -> float:
        return self._cornerRadius

    # ==================================================================================================================

    def setBrush(self, brush: QBrush) -> None:
        self._brush = QBrush(brush)

    def setPen(self, pen: QPen) -> None:
        self._pen = QPen(pen)

    def brush(self) -> QBrush:
        return self._brush

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
        if (name == 'cornerRadius' and isinstance(value, float)):
            self.setCornerRadius(value)
        elif (name == 'pen' and isinstance(value, QPen)):
            self.setPen(value)
        elif (name == 'penStyle' and isinstance(value, int)):
            pen = self.pen()
            pen.setStyle(Qt.PenStyle(value))
            self.setPen(pen)
        elif (name == 'penWidth' and isinstance(value, float)):
            pen = self.pen()
            pen.setWidthF(value)
            self.setPen(pen)
        elif (name == 'penColor' and isinstance(value, QColor)):
            pen = self.pen()
            pen.setBrush(QBrush(QColor(value)))
            self.setPen(pen)
        elif (name == 'brush' and isinstance(value, QBrush)):
            self.setBrush(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self.setBrush(QBrush(QColor(value)))

    def property(self, name: str) -> typing.Any:
        if (name == 'rect'):
            return self.mapRectToScene(self.rect())
        if (name == 'cornerRadius'):
            return self.cornerRadius()
        if (name == 'pen'):
            return self.pen()
        if (name == 'penStyle'):
            return self.pen().style().value
        if (name == 'penWidth'):
            return self.pen().widthF()
        if (name == 'penColor'):
            return self.pen().brush().color()
        if (name == 'brush'):
            return self.brush()
        if (name == 'brushColor'):
            return self.brush().color()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = QRectF(self._rect.normalized())

        # Adjust for pen width
        if (self._pen.style() != Qt.PenStyle.NoPen):
            halfPenWidth = self._pen.widthF() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        normalizedRect = self._rect.normalized()

        shape = QPainterPath()
        if (self._pen.style() != Qt.PenStyle.NoPen):
            rectPath = QPainterPath()
            rectPath.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)

            shape = self._strokePath(rectPath, self._pen)
            if (self._brush.color().alpha() > 0):
                shape = shape.united(rectPath)
        else:
            shape.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)

        return shape

    def isValid(self) -> bool:
        return (self._rect.width() != 0 or self._rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawRoundedRect(self._rect.normalized(), self._cornerRadius, self._cornerRadius)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (snapTo45Degrees and len(self._points) >= 8):
            position = self._snapResizeTo45Degrees(point, position, self._points[DrawingRectItem.PointIndex.TopLeft],
                                                   self._points[DrawingRectItem.PointIndex.BottomRight])

        if (point in self._points):
            position = self.mapFromScene(position)
            rect = QRectF(self._rect)
            match (self._points.index(point)):
                case DrawingRectItem.PointIndex.TopLeft:
                    rect.setTopLeft(position)
                case DrawingRectItem.PointIndex.TopMiddle:
                    rect.setTop(position.y())
                case DrawingRectItem.PointIndex.TopRight:
                    rect.setTopRight(position)
                case DrawingRectItem.PointIndex.MiddleRight:
                    rect.setRight(position.x())
                case DrawingRectItem.PointIndex.BottomRight:
                    rect.setBottomRight(position)
                case DrawingRectItem.PointIndex.BottomMiddle:
                    rect.setBottom(position.y())
                case DrawingRectItem.PointIndex.BottomLeft:
                    rect.setBottomLeft(position)
                case DrawingRectItem.PointIndex.MiddleLeft:
                    rect.setLeft(position.x())

            # Keep the item's position as the center of the rect
            center = rect.center()
            self.setPosition(self.mapToScene(center))
            rect.translate(-center)

            self.setRect(rect)

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        return self._points[DrawingRectItem.PointIndex.TopLeft] if (len(self._points) >= 8) else None

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        return self._points[DrawingRectItem.PointIndex.BottomRight] if (len(self._points) >= 8) else None

    # ==================================================================================================================

    def placeStartEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setRect(QRectF())

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        element.set('x', self._toPositionStr(self._rect.left()))
        element.set('y', self._toPositionStr(self._rect.top()))
        element.set('width', self._toSizeStr(self._rect.width()))
        element.set('height', self._toSizeStr(self._rect.height()))

        if (self._cornerRadius > 0):
            element.set('cornerRadius', self._toSizeStr(self._cornerRadius))

        self._writeBrush(element, 'brush', self._brush)
        self._writePen(element, 'pen', self._pen)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        self.setRect(QRectF(self._fromPositionStr(element.get('x', '0')),
                            self._fromPositionStr(element.get('y', '0')),
                            self._fromSizeStr(element.get('width', '0')),
                            self._fromSizeStr(element.get('height', '0'))))
        self.setCornerRadius(self._fromSizeStr(element.get('cornerRadius', '0')))

        self.setBrush(self._readBrush(element, 'brush'))
        self.setPen(self._readPen(element, 'pen'))
