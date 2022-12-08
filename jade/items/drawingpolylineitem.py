# drawingpolylineitem.py
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
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingPolylineItem(DrawingItem):
    def __init__(self) -> None:
        super().__init__()

        self._polyline: QPolygonF = QPolygonF()

        self._pen: QPen = QPen()
        self._startArrow: DrawingArrow = DrawingArrow()
        self._endArrow: DrawingArrow = DrawingArrow()

        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.FreeControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'DrawingPolylineItem':
        copiedItem = DrawingPolylineItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setPolyline(self.polyline())
        copiedItem.setPen(self.pen())
        copiedItem.setStartArrow(self.startArrow())
        copiedItem.setEndArrow(self.endArrow())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'polyline'

    # ==================================================================================================================

    def setPolyline(self, polyline: QPolygonF) -> None:
        if (polyline.size() >= 2):
            self._polyline = QPolygonF(polyline)

            # Ensure that len(self._points) == self._polyline.size()
            while (len(self._points) < self._polyline.size()):
                self.insertPoint(1, DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
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

    def setStartArrow(self, arrow: DrawingArrow) -> None:
        self._startArrow = DrawingArrow(arrow.style(), arrow.size())

    def setEndArrow(self, arrow: DrawingArrow) -> None:
        self._endArrow = DrawingArrow(arrow.style(), arrow.size())

    def pen(self) -> QPen:
        return self._pen

    def startArrow(self) -> DrawingArrow:
        return self._startArrow

    def endArrow(self) -> DrawingArrow:
        return self._endArrow

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
        elif (name == 'startArrow' and isinstance(value, DrawingArrow)):
            self.setStartArrow(value)
        elif (name == 'startArrowStyle' and isinstance(value, int)):
            arrow = self.startArrow()
            arrow.setStyle(DrawingArrow.Style(value))
            self.setStartArrow(arrow)
        elif (name == 'startArrowSize' and isinstance(value, float)):
            arrow = self.startArrow()
            arrow.setSize(value)
            self.setStartArrow(arrow)
        elif (name == 'endArrow' and isinstance(value, DrawingArrow)):
            self.setEndArrow(value)
        elif (name == 'endArrowStyle' and isinstance(value, int)):
            arrow = self.endArrow()
            arrow.setStyle(DrawingArrow.Style(value))
            self.setEndArrow(arrow)
        elif (name == 'endArrowSize' and isinstance(value, float)):
            arrow = self.endArrow()
            arrow.setSize(value)
            self.setEndArrow(arrow)

    def property(self, name: str) -> typing.Any:
        if (name == 'polyline'):
            return self.mapPolygonToScene(self.polyline())
        if (name == 'pen'):
            return self.pen()
        if (name == 'penStyle'):
            return self.pen().style().value
        if (name == 'penWidth'):
            return self.pen().widthF()
        if (name == 'penColor'):
            return self.pen().brush().color()
        if (name == 'startArrow'):
            return self.startArrow()
        if (name == 'startArrowStyle'):
            return self.startArrow().style().value
        if (name == 'startArrowSize'):
            return self.startArrow().size()
        if (name == 'endArrow'):
            return self.endArrow()
        if (name == 'endArrowStyle'):
            return self.endArrow().style().value
        if (name == 'endArrowSize'):
            return self.endArrow().size()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = self._polyline.boundingRect()

        # Adjust for pen width
        if (self._pen.style() != Qt.PenStyle.NoPen):
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
        polylinePath.lineTo(self._polyline.at(0))
        shape = self._strokePath(polylinePath, self._pen)

        # Add shape for each arrow, if necessary
        if (self._polyline.size() >= 2):
            if (self._firstSegmentLength() >= self._startArrow.size()):
                shape.addPath(self._startArrow.shape(self._pen, self._polyline.at(0), self._startArrowAngle()))
            if (self._lastSegmentLength() >= self._endArrow.size()):
                shape.addPath(self._endArrow.shape(self._pen, self._polyline.at(self._polyline.size() - 1),
                                                   self._endArrowAngle()))

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

        # Draw arrows if necessary
        if (self._polyline.size() >= 2):
            if (self._firstSegmentLength() >= self._startArrow.size()):
                self._startArrow.paint(painter, self._pen, self._polyline.at(0), self._startArrowAngle())
            if (self._lastSegmentLength() >= self._endArrow.size()):
                self._endArrow.paint(painter, self._pen, self._polyline.at(self._polyline.size() - 1),
                                     self._endArrowAngle())

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (snapTo45Degrees and len(self._points) == 2):
            position = self._snapResizeTo45Degrees(point, position, self._points[0], self._points[-1])

        if (point in self._points):
            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            polyline = QPolygonF(self._polyline)
            if (0 <= pointIndex < polyline.size()):
                polyline.takeAt(pointIndex)
                polyline.insert(pointIndex, position)

            # Keep the item's position at the first point of the polyline
            firstPointPosition = polyline.at(0)
            self.setPosition(self.mapToScene(firstPointPosition))
            polyline.translate(-firstPointPosition)

            self.setPolyline(polyline)

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        return self._points[0] if (len(self._points) >= 2) else None

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        return self._points[-1] if (len(self._points) >= 2) else None

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return True

    def canRemovePoints(self) -> bool:
        return (len(self._points) > 2)

    def insertNewPoint(self, position: QPointF) -> bool:
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
            return True
        return False

    def removeExistingPoint(self, position: QPointF) -> bool:
        if (self.canRemovePoints()):
            point = self._pointNearest(self.mapFromScene(position))
            # The user cannot remove the end points of the polyline
            if (point == self.resizeStartPoint() or point == self.resizeEndPoint()):
                point = None
            if (point is not None):
                removeIndex = self._points.index(point)
                polyline = QPolygonF(self._polyline)
                polyline.takeAt(removeIndex)
                self.setPolyline(polyline)
                return True
        return False

    # ==================================================================================================================

    def placeStartEvent(self, sceneRect: QRectF, grid: float) -> None:
        polyline = QPolygonF()
        polyline.append(QPointF())
        polyline.append(QPointF())
        self.setPolyline(polyline)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        # Polyline
        self.writePoints(element, 'points', self._polyline)

        # Pen and arrows
        self.writePen(element, 'pen', self._pen)
        self.writeArrow(element, 'startArrow', self._startArrow)
        self.writeArrow(element, 'endArrow', self._endArrow)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        # Polyline
        self.setPolyline(self.readPoints(element, 'points'))

        # Pen and arrows
        self.setPen(self.readPen(element, 'pen'))
        self.setStartArrow(self.readArrow(element, 'startArrow'))
        self.setEndArrow(self.readArrow(element, 'endArrow'))

    # ==================================================================================================================

    def _firstSegmentLength(self) -> float:
        return QLineF(self._polyline.at(0), self._polyline.at(1)).length()

    def _lastSegmentLength(self) -> float:
        return QLineF(self._polyline.at(-1), self._polyline.at(-2)).length()

    def _startArrowAngle(self) -> float:
        return QLineF(self._polyline.at(0), self._polyline.at(1)).angle()

    def _endArrowAngle(self) -> float:
        return QLineF(self._polyline.at(-1), self._polyline.at(-2)).angle()
