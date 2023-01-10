# drawingellipseitem.py
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


class DrawingEllipseItem(DrawingItem):
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

        self._ellipse: QRectF = QRectF()

        self._brush: QBrush = QBrush()
        self._pen: QPen = QPen()

        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.ControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.ControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.ControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.ControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))

    def __copy__(self) -> 'DrawingEllipseItem':
        copiedItem = DrawingEllipseItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setEllipse(self.ellipse())
        copiedItem.setBrush(self.brush())
        copiedItem.setPen(self.pen())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'ellipse'

    def prettyName(self) -> str:
        return 'Ellipse'

    # ==================================================================================================================

    def setEllipse(self, ellipse: QRectF) -> None:
        self._ellipse = QRectF(ellipse)

        # Set point positions to match self._ellipse
        if (len(self._points) >= 8):
            center = self._ellipse.center()
            self._points[DrawingEllipseItem.PointIndex.TopLeft].setPosition(QPointF(ellipse.left(), ellipse.top()))
            self._points[DrawingEllipseItem.PointIndex.TopMiddle].setPosition(QPointF(center.x(), ellipse.top()))
            self._points[DrawingEllipseItem.PointIndex.TopRight].setPosition(QPointF(ellipse.right(), ellipse.top()))
            self._points[DrawingEllipseItem.PointIndex.MiddleRight].setPosition(QPointF(ellipse.right(), center.y()))
            self._points[DrawingEllipseItem.PointIndex.BottomRight].setPosition(QPointF(ellipse.right(), ellipse.bottom()))     # noqa
            self._points[DrawingEllipseItem.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), ellipse.bottom()))
            self._points[DrawingEllipseItem.PointIndex.BottomLeft].setPosition(QPointF(ellipse.left(), ellipse.bottom()))       # noqa
            self._points[DrawingEllipseItem.PointIndex.MiddleLeft].setPosition(QPointF(ellipse.left(), center.y()))

    def ellipse(self) -> QRectF:
        return self._ellipse

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
        if (name == 'pen' and isinstance(value, QPen)):
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
        if (name == 'ellipse'):
            return self.mapRectToScene(self.ellipse())
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
        rect = QRectF(self._ellipse.normalized())

        # Adjust for pen width
        if (self._pen.style() != Qt.PenStyle.NoPen):
            halfPenWidth = self._pen.widthF() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        normalizedRect = self._ellipse.normalized()

        shape = QPainterPath()
        if (self._pen.style() != Qt.PenStyle.NoPen):
            ellipsePath = QPainterPath()
            ellipsePath.addEllipse(normalizedRect)

            shape = self._strokePath(ellipsePath, self._pen)
            if (self._brush.color().alpha() > 0):
                shape = shape.united(ellipsePath)
        else:
            shape.addEllipse(normalizedRect)

        return shape

    def isValid(self) -> bool:
        return (self._ellipse.width() != 0 or self._ellipse.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(self._ellipse.normalized())

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (snapTo45Degrees and len(self._points) >= 8):
            position = self._snapResizeTo45Degrees(point, position, self._points[DrawingEllipseItem.PointIndex.TopLeft],
                                                   self._points[DrawingEllipseItem.PointIndex.BottomRight])

        if (point in self._points):
            position = self.mapFromScene(position)
            ellipse = QRectF(self._ellipse)
            match (self._points.index(point)):
                case DrawingEllipseItem.PointIndex.TopLeft:
                    ellipse.setTopLeft(position)
                case DrawingEllipseItem.PointIndex.TopMiddle:
                    ellipse.setTop(position.y())
                case DrawingEllipseItem.PointIndex.TopRight:
                    ellipse.setTopRight(position)
                case DrawingEllipseItem.PointIndex.MiddleRight:
                    ellipse.setRight(position.x())
                case DrawingEllipseItem.PointIndex.BottomRight:
                    ellipse.setBottomRight(position)
                case DrawingEllipseItem.PointIndex.BottomMiddle:
                    ellipse.setBottom(position.y())
                case DrawingEllipseItem.PointIndex.BottomLeft:
                    ellipse.setBottomLeft(position)
                case DrawingEllipseItem.PointIndex.MiddleLeft:
                    ellipse.setLeft(position.x())

            # Keep the item's position as the center of the ellipse
            center = ellipse.center()
            self.setPosition(self.mapToScene(center))
            ellipse.translate(-center)

            self.setEllipse(ellipse)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setEllipse(QRectF())

    def placeResizeStartPoint(self) -> DrawingItemPoint | None:
        return self._points[DrawingEllipseItem.PointIndex.TopLeft] if (len(self._points) >= 8) else None

    def placeResizeEndPoint(self) -> DrawingItemPoint | None:
        return self._points[DrawingEllipseItem.PointIndex.BottomRight] if (len(self._points) >= 8) else None

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        element.set('x', self._toPositionStr(self._ellipse.left()))
        element.set('y', self._toPositionStr(self._ellipse.top()))
        element.set('width', self._toSizeStr(self._ellipse.width()))
        element.set('height', self._toSizeStr(self._ellipse.height()))

        self._writeBrush(element, 'brush', self._brush)
        self._writePen(element, 'pen', self._pen)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        self.setEllipse(QRectF(self._fromPositionStr(element.get('x', '0')),
                               self._fromPositionStr(element.get('y', '0')),
                               self._fromSizeStr(element.get('width', '0')),
                               self._fromSizeStr(element.get('height', '0'))))

        self.setBrush(self._readBrush(element, 'brush'))
        self.setPen(self._readPen(element, 'pen'))
