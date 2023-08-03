# odgpolygonitem.py
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

from typing import Any
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPolygonF
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint


class OdgPolygonItem(OdgItem):
    def __init__(self) -> None:
        super().__init__()

        self._polygon: QPolygonF = QPolygonF()

        for _ in range(3):
            self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))

        # All points are control and connection points
        for point in self._points:
            point.setType(OdgItemPoint.Type.ControlAndConnection)

    def __copy__(self) -> 'OdgPolygonItem':
        copiedItem = OdgPolygonItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setPolygon(self.polygon())
        return copiedItem

    # ==================================================================================================================

    def setPolygon(self, polygon: QPolygonF) -> None:
        if (polygon.size() >= 3):
            self._polygon = QPolygonF(polygon)

            # Put the item's position at the center of the polygon
            offset = polygon.boundingRect().center()
            self.setPosition(self.mapToScene(offset))
            self._polygon.translate(-offset)

            # Ensure that len(self._points) == self._polygon.size()
            while (len(self._points) < self._polygon.size()):
                self.insertPoint(1, OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
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

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'penStyle' and isinstance(value, Qt.PenStyle)):
            self._style.setPenStyleIfUnique(Qt.PenStyle(value))
        elif (name == 'penWidth' and isinstance(value, float)):
            self._style.setPenWidthIfUnique(value)
        elif (name == 'penColor' and isinstance(value, QColor)):
            self._style.setPenColorIfUnique(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self._style.setBrushColorIfUnique(value)

    def property(self, name: str) -> Any:
        if (name == 'polygon'):
            return self.polygon()
        if (name == 'penStyle'):
            return self._style.lookupPenStyle()
        if (name == 'penWidth'):
            return self._style.lookupPenWidth()
        if (name == 'penColor'):
            return self._style.lookupPenColor()
        if (name == 'brushColor'):
            return self._style.lookupBrushColor()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = self._polygon.boundingRect()

        # Adjust for pen width
        if (self.style().lookupPenStyle() != Qt.PenStyle.NoPen):
            halfPenWidth = self.style().lookupPenWidth() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        pen = self.style().lookupPen()
        brush = self.style().lookupBrush()

        shape = QPainterPath()
        if (pen.style() != Qt.PenStyle.NoPen):
            polygonPath = QPainterPath()
            polygonPath.addPolygon(self._polygon)
            polygonPath.closeSubpath()

            shape = self._strokePath(polygonPath, pen)
            if (brush.color().alpha() > 0):
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
        painter.setBrush(self.style().lookupBrush())
        painter.setPen(self.style().lookupPen())
        painter.drawPolygon(self._polygon)

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            polygon = QPolygonF(self._polygon)
            if (0 <= pointIndex < polygon.size()):
                polygon.takeAt(pointIndex)
                polygon.insert(pointIndex, position)

            self.setPolygon(polygon)

    def scale(self, scale: float) -> None:
        super().scale(scale)

        scaledPolygon = QPolygonF()
        for index in range(self._polygon.count()):
            point = self._polygon.at(index)
            scaledPolygon.append(QPointF(point.x() * scale, point.y() * scale))
        self.setPolygon(scaledPolygon)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return True

    def canRemovePoints(self) -> bool:
        return (len(self._points) > 3)

    def insertNewPoint(self, position: QPointF) -> None:
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

    def removeExistingPoint(self, position: QPointF) -> None:
        if (self.canRemovePoints()):
            point = self._pointNearest(self.mapFromScene(position))
            if (point is not None):
                removeIndex = self._points.index(point)
                polygon = QPolygonF(self._polygon)
                polygon.takeAt(removeIndex)
                self.setPolygon(polygon)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = 4 * grid
        if (size <= 0):
            size = sceneRect.width() / 40

        polygon = QPolygonF()
        polygon.append(QPointF(-size, -size))
        polygon.append(QPointF(size, 0))
        polygon.append(QPointF(-size, size))
        self.setPolygon(polygon)
