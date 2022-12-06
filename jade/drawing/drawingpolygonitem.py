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

import math
import typing
from xml.etree import ElementTree
from PyQt6.QtCore import Qt, QLineF, QPointF, QRectF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint


class DrawingPolygonItem(DrawingItem):
    def __init__(self) -> None:
        super().__init__()

        self._pen: QPen = QPen()
        self._brush: QBrush = QBrush()

        self._cachedBoundingRect: QRectF = QRectF()
        self._cachedShape: QPainterPath = QPainterPath()

        for _ in range(3):
            self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.ControlAndConnection))

    # ==================================================================================================================

    def key(self) -> str:
        return 'polygon'

    def clone(self) -> 'DrawingPolygonItem':
        clonedItem = DrawingPolygonItem()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setPen(QPen(self.pen()))
        clonedItem.setBrush(QBrush(self.brush()))
        clonedItem.setPolygon(self.polygon())
        return clonedItem

    def setInitialGeometry(self, sceneRect: QRectF, grid: float) -> None:
        size = 4 * grid
        if (size <= 0):
            size = sceneRect.width() / 40

        polygon = QPolygonF()
        polygon.append(QPointF(-size, -size))
        polygon.append(QPointF(size, 0))
        polygon.append(QPointF(-size, size))
        self.setPolygon(polygon)

    # ==================================================================================================================

    def setPolygon(self, polygon: QPolygonF) -> None:
        if (len(polygon) >= 3):
            # Ensure that self._points is the same size as polyline
            while (len(self._points) < polygon.size()):
                self.insertPoint(1, DrawingItemPoint(QPointF(), DrawingItemPoint.Type.ControlAndConnection))
            while (len(self._points) > polygon.size()):
                point = self._points[1]
                self.removePoint(point)
                del point

            # Update point positions based on polyline
            for index, point in enumerate(self._points):
                point.setPosition(QPointF(polygon[index]))

            self._updateGeometry()

    def polygon(self) -> QPolygonF:
        polygon = QPolygonF()
        for point in self._points:
            polygon.append(QPointF(point.position()))
        return polygon

    # ==================================================================================================================

    def setPen(self, pen: QPen) -> None:
        self._pen = pen
        self._updateGeometry()

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def setBrush(self, brush: QBrush) -> None:
        self._brush = brush
        self._updateGeometry()

    def brush(self) -> QBrush:
        return self._brush

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
        return self._cachedBoundingRect

    def shape(self) -> QPainterPath:
        return self._cachedShape

    def isValid(self) -> bool:
        rect = self.polygon().boundingRect()
        return (rect.width() != 0 and rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        if (self.isValid()):
            painter.setBrush(self._brush)
            painter.setPen(self._pen)
            painter.drawPolygon(self.polygon())

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (len(self._points) >= 3):
            # Move just the one point to its new position
            super().resize(point, position, False)

            # Keep the item's position as the location of the first item point
            polygon = self.polygon()

            firstPointPosition = polygon[0]
            self.setPosition(self.mapToScene(firstPointPosition))
            polygon.translate(-firstPointPosition)

            # Set final point positions
            self.setPolygon(polygon)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)

        self._pen.setWidthF(self._pen.widthF() * scale)

        newPolygon = QPolygonF()
        polygon = self.polygon()
        for index in range(polygon.size()):
            newPolygon.append(QPointF(polygon[index].x() * scale, polygon[index].y() * scale))
        self.setPolygon(newPolygon)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return True

    def canRemovePoints(self) -> bool:
        return (len(self._points) > 3)

    def insertNewPoint(self, position: QPointF) -> DrawingItemPoint | None:
        point = DrawingItemPoint(self.mapFromScene(position), DrawingItemPoint.Type.ControlAndConnection)

        distance = 0.0
        minimumDistance = self._distanceFromPointToLineSegment(
            point.position(), QLineF(self._points[-1].position(), self._points[0].position()))
        insertIndex = 1

        for index in range(0, len(self._points) - 1):
            distance = self._distanceFromPointToLineSegment(
                point.position(), QLineF(self._points[index].position(), self._points[index + 1].position()))
            if (distance < minimumDistance):
                insertIndex = index + 1
                minimumDistance = distance

        self.insertPoint(insertIndex, point)
        self._updateGeometry()

        return point

    def removeExistingPoint(self, position: QPointF) -> tuple[DrawingItemPoint | None, int]:
        point = None
        removeIndex = -1
        if (self.canRemovePoints()):
            point = self._pointNearest(self.mapFromScene(position))
        if (point is not None):
            removeIndex = self._points.index(point)
            self.removePoint(point)
            self._updateGeometry()

        return (point, removeIndex)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Polygon
        self.writePointsAttribute(element, 'points', self.polygon())

        # Pen and brush
        self.writePenToXml(element, 'pen', self._pen)
        self.writeBrushToXml(element, 'brush', self._brush)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        super().readFromXml(element)

        # Polygon
        self.setPolygon(self.readPointsAttribute(element, 'points'))

        # Pen and brush
        self.setPen(self.readPenFromXml(element, 'pen'))
        self.setBrush(self.readBrushFromXml(element, 'brush'))

    # ==================================================================================================================

    def _updateGeometry(self) -> None:
        self._cachedBoundingRect = QRectF()
        self._cachedShape.clear()

        if (self.isValid()):
            polygon = self.polygon()

            # Update bounding rect
            self._cachedBoundingRect = polygon.boundingRect().normalized()
            if (self._pen.style() != Qt.PenStyle.NoPen):
                halfPenWidth = self._pen.widthF() / 2
                self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

            # Update shape
            if (self._pen.style() != Qt.PenStyle.NoPen):
                drawPath = QPainterPath()
                drawPath.addPolygon(polygon)
                drawPath.closeSubpath()

                self._cachedShape = self.strokePath(drawPath, self._pen)
                if (self._brush.color().alpha() > 0):
                    self._cachedShape = self._cachedShape.united(drawPath)
            else:
                self._cachedShape.addPolygon(polygon)
                self._cachedShape.closeSubpath()

    # ==================================================================================================================

    def _distanceFromPointToLineSegment(self, point: QPointF, line: QLineF) -> float:
        # Let A = line point 0, B = line point 1, and C = point
        dotAbBc = (line.x2() - line.x1()) * (point.x() - line.x2()) + (line.y2() - line.y1()) * (point.y() - line.y2())
        dotBaAc = (line.x1() - line.x2()) * (point.x() - line.x1()) + (line.y1() - line.y2()) * (point.y() - line.y1())
        crossABC = (line.x2() - line.x1()) * (point.y() - line.y1()) - (line.y2() - line.y1()) * (point.x() - line.x1())
        distanceAB = math.sqrt((line.x2() - line.x1()) * (line.x2() - line.x1()) + (line.y2() - line.y1()) * (line.y2() - line.y1()))   # noqa
        distanceAC = math.sqrt((point.x() - line.x1()) * (point.x() - line.x1()) + (point.y() - line.y1()) * (point.y() - line.y1()))   # noqa
        distanceBC = math.sqrt((point.x() - line.x2()) * (point.x() - line.x2()) + (point.y() - line.y2()) * (point.y() - line.y2()))   # noqa

        if (distanceAB != 0):
            if (dotAbBc > 0):
                return distanceBC
            if (dotBaAc > 0):
                return distanceAC
            return abs(crossABC) / distanceAB
        return 1.0E12

    def _pointNearest(self, position: QPointF) -> DrawingItemPoint | None:
        if (len(self._points) > 0):
            point = self._points[0]

            vec = point.position() - position           # type: ignore
            minimumDistanceSquared = vec.x() * vec.x() + vec.y() * vec.y()

            for itemPoint in self._points[1:]:
                vec = itemPoint.position() - position   # type: ignore
                distanceSquared = vec.x() * vec.x() + vec.y() * vec.y()
                if (distanceSquared < minimumDistanceSquared):
                    point = itemPoint
                    minimumDistanceSquared = distanceSquared

            return point
        return None
