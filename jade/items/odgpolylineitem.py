# odgpolylineitem.py
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
from typing import Any
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgmarker import OdgMarker


class OdgPolylineItem(OdgItem):
    def __init__(self) -> None:
        super().__init__()

        self._polyline: QPolygonF = QPolygonF()

        self._pen: QPen = QPen()
        self._startMarker: OdgMarker = OdgMarker()
        self._endMarker: OdgMarker = OdgMarker()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'OdgPolylineItem':
        copiedItem = OdgPolylineItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setPolyline(self.polyline())
        copiedItem.setPen(self.pen())
        copiedItem.setStartMarker(self.startMarker())
        copiedItem.setEndMarker(self.endMarker())
        return copiedItem

    # ==================================================================================================================

    def setPolyline(self, polyline: QPolygonF) -> None:
        if (polyline.size() >= 2):
            self._polyline = QPolygonF(polyline)

            # Put the item's position at the center of the polyline
            offset = polyline.boundingRect().center()
            self.setPosition(self.mapToScene(offset))
            self._polyline.translate(-offset)

            # Ensure that len(self._points) == self._polyline.size()
            while (len(self._points) < self._polyline.size()):
                self.insertPoint(1, OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
            while (len(self._points) > self._polyline.size()):
                point = self._points[-1]
                self.removePoint(point)
                del point

            # Set point positions to match self._polyline
            for index, point in enumerate(self._points):
                point.setPosition(self._polyline.at(index))

    def polyline(self) -> QPolygonF:
        return self._polyline

    # ==================================================================================================================

    def setPen(self, pen: QPen) -> None:
        self._pen = QPen(pen)

    def setStartMarker(self, marker: OdgMarker) -> None:
        self._startMarker = OdgMarker(marker.style(), marker.size())

    def setEndMarker(self, marker: OdgMarker) -> None:
        self._endMarker = OdgMarker(marker.style(), marker.size())

    def pen(self) -> QPen:
        return self._pen

    def startMarker(self) -> OdgMarker:
        return self._startMarker

    def endMarker(self) -> OdgMarker:
        return self._endMarker

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
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
        elif (name == 'startMarker' and isinstance(value, OdgMarker)):
            self.setStartMarker(value)
        elif (name == 'startMarkerStyle' and isinstance(value, int)):
            marker = self.startMarker()
            marker.setStyle(OdgMarker.Style(value))
            self.setStartMarker(marker)
        elif (name == 'startMarkerSize' and isinstance(value, float)):
            marker = self.startMarker()
            marker.setSize(value)
            self.setStartMarker(marker)
        elif (name == 'endMarker' and isinstance(value, OdgMarker)):
            self.setEndMarker(value)
        elif (name == 'endMarkerStyle' and isinstance(value, int)):
            marker = self.endMarker()
            marker.setStyle(OdgMarker.Style(value))
            self.setEndMarker(marker)
        elif (name == 'endMarkerSize' and isinstance(value, float)):
            marker = self.endMarker()
            marker.setSize(value)
            self.setEndMarker(marker)

    def property(self, name: str) -> Any:
        if (name == 'polyline'):
            return self.polyline()
        if (name == 'pen'):
            return self.pen()
        if (name == 'penStyle'):
            return self.pen().style().value
        if (name == 'penWidth'):
            return self.pen().widthF()
        if (name == 'penColor'):
            return self.pen().brush().color()
        if (name == 'startMarker'):
            return self.startMarker()
        if (name == 'startMarkerStyle'):
            return self.startMarker().style().value
        if (name == 'startMarkerSize'):
            return self.startMarker().size()
        if (name == 'endMarker'):
            return self.endMarker()
        if (name == 'endMarkerStyle'):
            return self.endMarker().style().value
        if (name == 'endMarkerSize'):
            return self.endMarker().size()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = self._polyline.boundingRect()

        # Adjust for pen width
        halfPenWidth = self._pen.widthF() / 2
        rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()

        # Calculate polyline shape
        polylinePath = QPainterPath()
        polylinePath.moveTo(self._polyline.at(0))
        for index in range(1, self._polyline.size()):
            polylinePath.lineTo(self._polyline.at(index))
        shape = self._strokePath(polylinePath, self._pen)

        # Add shape for each marker, if necessary
        if (self._shouldShowStartMarker(self._startMarker.size())):
            shape.addPath(self._startMarker.shape(self._pen, self._polyline.at(0), self._startMarkerAngle()))
        if (self._shouldShowEndMarker(self._endMarker.size())):
            shape.addPath(self._endMarker.shape(self._pen, self._polyline.at(self._polyline.size() - 1),
                                                self._endMarkerAngle()))

        return shape

    def isValid(self) -> bool:
        rect = self._polyline.boundingRect()
        return (rect.width() != 0 or rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw line
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.drawPolyline(self._polyline)

        # Draw markers if necessary
        if (self._shouldShowStartMarker(self._startMarker.size())):
            self._startMarker.paint(painter, self._pen, self._polyline.at(0), self._startMarkerAngle())
        if (self._shouldShowEndMarker(self._endMarker.size())):
            self._endMarker.paint(painter, self._pen, self._polyline.at(self._polyline.size() - 1),
                                  self._endMarkerAngle())

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            if (snapTo45Degrees and len(self._points) == 2):
                position = self._snapResizeTo45Degrees(point, position, self._points[0], self._points[-1])

            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            polyline = QPolygonF(self._polyline)
            if (0 <= pointIndex < polyline.size()):
                polyline.takeAt(pointIndex)
                polyline.insert(pointIndex, position)

            self.setPolyline(polyline)

    def scale(self, scale: float) -> None:
        super().scale(scale)

        scaledPolyline = QPolygonF()
        for index in range(self._polyline.count()):
            point = self._polyline.at(index)
            scaledPolyline.append(QPointF(point.x() * scale, point.y() * scale))
        self.setPolyline(scaledPolyline)

        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startMarker.setSize(self._startMarker.size() * scale)
        self._endMarker.setSize(self._endMarker.size() * scale)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return True

    def canRemovePoints(self) -> bool:
        return (len(self._points) > 2)

    def insertNewPoint(self, position: QPointF) -> None:
        if (len(self._points) >= 2):
            itemPosition = self.mapFromScene(position)

            distance = 0.0
            minimumDistance = self._distanceFromPointToLineSegment(
                itemPosition, QLineF(self._points[0].position(), self._points[1].position()))
            insertIndex = 1

            for index in range(1, len(self._points) - 1):
                distance = self._distanceFromPointToLineSegment(
                    itemPosition, QLineF(self._points[index].position(), self._points[index + 1].position()))
                if (distance < minimumDistance):
                    insertIndex = index + 1
                    minimumDistance = distance

            polyline = QPolygonF(self._polyline)
            polyline.insert(insertIndex, itemPosition)
            self.setPolyline(polyline)

    def removeExistingPoint(self, position: QPointF) -> None:
        if (self.canRemovePoints()):
            point = self._pointNearest(self.mapFromScene(position))
            # The user cannot remove the end points of the polyline
            if (point == self.placeResizeStartPoint() or point == self.placeResizeEndPoint()):
                point = None
            if (point is not None):
                removeIndex = self._points.index(point)
                polyline = QPolygonF(self._polyline)
                polyline.takeAt(removeIndex)
                self.setPolyline(polyline)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        polyline = QPolygonF()
        polyline.append(QPointF())
        polyline.append(QPointF())
        self.setPolyline(polyline)

    def placeResizeStartPoint(self) -> OdgItemPoint | None:
        return self._points[0] if (len(self._points) >= 2) else None

    def placeResizeEndPoint(self) -> OdgItemPoint | None:
        return self._points[-1] if (len(self._points) >= 2) else None

    # ==================================================================================================================

    def _shouldShowStartMarker(self, markerSize: float) -> bool:
        if (self._polyline.size() >= 2):
            length = QLineF(self._polyline.at(0),
                            self._polyline.at(1)).length()
            return (length >= markerSize)
        return False

    def _shouldShowEndMarker(self, markerSize: float) -> bool:
        if (self._polyline.size() >= 2):
            length = QLineF(self._polyline.at(self._polyline.size() - 2),
                            self._polyline.at(self._polyline.size() - 1)).length()
            return (length >= markerSize)
        return False

    def _startMarkerAngle(self) -> float:
        if (self._polyline.size() >= 2):
            p1 = self._polyline.at(0)
            p2 = self._polyline.at(1)
            return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi
        return 0

    def _endMarkerAngle(self) -> float:
        if (self._polyline.size() >= 2):
            p1 = self._polyline.at(self._polyline.size() - 1)
            p2 = self._polyline.at(self._polyline.size() - 2)
            return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi
        return 0
