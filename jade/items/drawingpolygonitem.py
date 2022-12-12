# drawingpolygonitem.py
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
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingPolygonItem(DrawingItem):
    def __init__(self) -> None:
        super().__init__()

        self._polygon: QPolygonF = QPolygonF()

        self._brush: QBrush = QBrush()
        self._pen: QPen = QPen()

        for _ in range(3):
            self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))

    def __copy__(self) -> 'DrawingPolygonItem':
        copiedItem = DrawingPolygonItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setPolygon(self.polygon())
        copiedItem.setBrush(self.brush())
        copiedItem.setPen(self.pen())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'polygon'

    def prettyName(self) -> str:
        return 'Polygon'

    # ==================================================================================================================

    def setPolygon(self, polygon: QPolygonF) -> None:
        if (polygon.size() >= 3):
            self._polygon = QPolygonF(polygon)

            # Ensure that len(self._points) == self._polygon.size()
            while (len(self._points) < self._polygon.size()):
                self.insertPoint(1, DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
            while (len(self._points) > self._polygon.size()):
                point = self._points[-1]
                self.removePoint(point)
                del point

            # Set point positions to match self._polygon
            for index, point in enumerate(self._points):
                point.setPosition(self._polygon.at(index))

    def polygon(self) -> QPolygonF:
        return self._polygon

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
        if (name == 'polygon'):
            return self.mapPolygonToScene(self.polygon())
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
        rect = self._polygon.boundingRect()

        # Adjust for pen width
        if (self._pen.style() != Qt.PenStyle.NoPen):
            halfPenWidth = self._pen.widthF() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()
        if (self._pen.style() != Qt.PenStyle.NoPen):
            polygonPath = QPainterPath()
            polygonPath.addPolygon(self._polygon)
            polygonPath.closeSubpath()

            shape = self._strokePath(polygonPath, self._pen)
            if (self._brush.color().alpha() > 0):
                shape = shape.united(polygonPath)
        else:
            shape.addPolygon(self._polygon)
            shape.closeSubpath()
        return shape

    def isValid(self) -> bool:
        rect = self._polygon.boundingRect()
        return (rect.width() != 0 or rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPolygon(self._polygon)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            polygon = QPolygonF(self._polygon)
            if (0 <= pointIndex < polygon.size()):
                polygon.takeAt(pointIndex)
                polygon.insert(pointIndex, position)

            # Keep the item's position at the first point of the polygon
            firstPointPosition = polygon.at(0)
            self.setPosition(self.mapToScene(firstPointPosition))
            polygon.translate(-firstPointPosition)

            self.setPolygon(polygon)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return True

    def canRemovePoints(self) -> bool:
        return (len(self._points) > 3)

    def insertNewPoint(self, position: QPointF) -> bool:
        if (len(self._points) >= 2):
            itemPosition = self.mapFromScene(position)

            distance = 0.0
            minimumDistance = self._distanceFromPointToLineSegment(
                itemPosition, QLineF(self._points[-1].position(), self._points[0].position()))
            insertIndex = 1

            for index in range(0, len(self._points) - 1):
                distance = self._distanceFromPointToLineSegment(
                    itemPosition, QLineF(self._points[index].position(), self._points[index + 1].position()))
                if (distance < minimumDistance):
                    insertIndex = index + 1
                    minimumDistance = distance

            polygon = QPolygonF(self._polygon)
            polygon.insert(insertIndex, itemPosition)
            self.setPolygon(polygon)
            return True
        return False

    def removeExistingPoint(self, position: QPointF) -> bool:
        if (self.canRemovePoints()):
            point = self._pointNearest(self.mapFromScene(position))
            if (point is not None):
                removeIndex = self._points.index(point)
                polygon = QPolygonF(self._polygon)
                polygon.takeAt(removeIndex)
                self.setPolygon(polygon)
                return True
        return False

    # ==================================================================================================================

    def placeStartEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = 4 * grid
        if (size <= 0):
            size = sceneRect.width() / 40

        polygon = QPolygonF()
        polygon.append(QPointF(-size, -size))
        polygon.append(QPointF(size, 0))
        polygon.append(QPointF(-size, size))
        self.setPolygon(polygon)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        # Polygon
        self.writePoints(element, 'points', self._polygon)

        # Pen and brush
        self.writePen(element, 'pen', self._pen)
        self.writeBrush(element, 'brush', self._brush)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        # Polygon
        self.setPolygon(self.readPoints(element, 'points'))

        # Pen and brush
        self.setPen(self.readPen(element, 'pen'))
        self.setBrush(self.readBrush(element, 'brush'))
