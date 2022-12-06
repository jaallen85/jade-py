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

import math
import typing
from xml.etree import ElementTree
from PyQt6.QtCore import Qt, QLineF, QPointF, QRectF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint


class DrawingPolylineItem(DrawingItem):
    def __init__(self) -> None:
        super().__init__()

        self._pen: QPen = QPen()
        self._startArrow: DrawingArrow = DrawingArrow()
        self._endArrow: DrawingArrow = DrawingArrow()

        self._cachedBoundingRect: QRectF = QRectF()
        self._cachedShape: QPainterPath = QPainterPath()

        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.FreeControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.FreeControlAndConnection))

        self.setPlaceType(DrawingItem.PlaceType.PlaceByMousePressAndRelease)

    # ==================================================================================================================

    def key(self) -> str:
        return 'polyline'

    def clone(self) -> 'DrawingPolylineItem':
        clonedItem = DrawingPolylineItem()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setPen(QPen(self.pen()))
        clonedItem.setStartArrow(DrawingArrow(self.startArrow().style(), self.startArrow().size()))
        clonedItem.setEndArrow(DrawingArrow(self.endArrow().style(), self.endArrow().size()))
        clonedItem.setPolyline(self.polyline())
        return clonedItem

    # ==================================================================================================================

    def setPolyline(self, polyline: QPolygonF) -> None:
        if (len(polyline) >= 2):
            # Ensure that self._points is the same size as polyline
            while (len(self._points) < polyline.size()):
                self.insertPoint(1, DrawingItemPoint(QPointF(), DrawingItemPoint.Type.Control))
            while (len(self._points) > polyline.size()):
                point = self._points[1]
                self.removePoint(point)
                del point

            # Update point positions based on polyline
            for index, point in enumerate(self._points):
                point.setPosition(QPointF(polyline[index]))

            self._updateGeometry()

    def polyline(self) -> QPolygonF:
        polyline = QPolygonF()
        for point in self._points:
            polyline.append(QPointF(point.position()))
        return polyline

    # ==================================================================================================================

    def setPen(self, pen: QPen) -> None:
        self._pen = pen
        self._updateGeometry()

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def setStartArrow(self, arrow: DrawingArrow) -> None:
        self._startArrow = arrow
        self._updateGeometry()

    def startArrow(self) -> DrawingArrow:
        return self._startArrow

    # ==================================================================================================================

    def setEndArrow(self, arrow: DrawingArrow) -> None:
        self._endArrow = arrow
        self._updateGeometry()

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
        return self._cachedBoundingRect

    def shape(self) -> QPainterPath:
        return self._cachedShape

    def isValid(self) -> bool:
        rect = self.polyline().boundingRect()
        return (rect.width() != 0 or rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        if (self.isValid()):
            polyline = self.polyline()

            # Draw line
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.setPen(self._pen)
            painter.drawPolyline(polyline)

            # Draw arrows
            if (polyline.size() >= 2):
                if (self._firstLineSegmentLength() >= self._startArrow.size()):
                    self._startArrow.paint(painter, self._pen, polyline[0], self._startArrowAngle())
                if (self._lastLineSegmentLength() >= self._endArrow.size()):
                    self._endArrow.paint(painter, self._pen, polyline[-1], self._endArrowAngle())

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (len(self._points) >= 2):
            # Force the line to be orthogonal or at 45 degrees, if applicable
            if (snapTo45Degrees and len(self._points) == 2):
                otherEndPoint = None
                if (point == self._points[0]):
                    otherEndPoint = self._points[1]
                elif (point == self._points[1]):
                    otherEndPoint = self._points[0]

                if (otherEndPoint is not None):
                    otherEndPosition = self.mapToScene(otherEndPoint.position())
                    delta = position - otherEndPosition      # type: ignore

                    angle = math.atan2(position.y() - otherEndPosition.y(), position.x() - otherEndPosition.x())
                    targetAngleDegrees = round(angle * 180 / math.pi / 45) * 45
                    targetAngle = targetAngleDegrees * math.pi / 180

                    length = max(abs(delta.x()), abs(delta.y()))
                    if (abs(targetAngleDegrees % 90) == 45):
                        length = length * math.sqrt(2)

                    position.setX(otherEndPosition.x() + length * math.cos(targetAngle))
                    position.setY(otherEndPosition.y() + length * math.sin(targetAngle))

            # Move the point to its new position
            super().resize(point, position, False)

            # Keep the item's position as the location of the first item point
            polyline = self.polyline()

            firstPointPosition = polyline[0]
            self.setPosition(self.mapToScene(firstPointPosition))
            polyline.translate(-firstPointPosition)

            # Set final point positions
            self.setPolyline(polyline)

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        if (len(self._points) >= 2):
            return self._points[0]
        return None

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        if (len(self._points) >= 2):
            return self._points[-1]
        return None

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)

        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startArrow.setSize(self._startArrow.size() * scale)
        self._endArrow.setSize(self._endArrow.size() * scale)

        newPolyline = QPolygonF()
        polyline = self.polyline()
        for index in range(polyline.size()):
            newPolyline.append(QPointF(polyline[index].x() * scale, polyline[index].y() * scale))
        self.setPolyline(newPolyline)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return True

    def canRemovePoints(self) -> bool:
        return (len(self._points) > 2)

    def insertNewPoint(self, position: QPointF) -> DrawingItemPoint | None:
        point = DrawingItemPoint(self.mapFromScene(position), DrawingItemPoint.Type.Control)

        distance = 0.0
        minimumDistance = self._distanceFromPointToLineSegment(
            point.position(), QLineF(self._points[0].position(), self._points[1].position()))
        insertIndex = 1

        for index in range(1, len(self._points) - 1):
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
            if (point in (self._points[0], self._points[-1])):
                point = None
        if (point is not None):
            removeIndex = self._points.index(point)
            self.removePoint(point)
            self._updateGeometry()

        return (point, removeIndex)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Polyline
        self.writePointsAttribute(element, 'points', self.polyline())

        # Pen and arrows
        self.writePenToXml(element, 'pen', self._pen)
        self.writeArrowToXml(element, 'startArrow', self._startArrow)
        self.writeArrowToXml(element, 'endArrow', self._endArrow)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        super().readFromXml(element)

        # Polyline
        self.setPolyline(self.readPointsAttribute(element, 'points'))

        # Pen and arrows
        self.setPen(self.readPenFromXml(element, 'pen'))
        self.setStartArrow(self.readArrowFromXml(element, 'startArrow'))
        self.setEndArrow(self.readArrowFromXml(element, 'endArrow'))

    # ==================================================================================================================

    def _updateGeometry(self) -> None:
        self._cachedBoundingRect = QRectF()
        self._cachedShape.clear()

        if (self.isValid()):
            polyline = self.polyline()

            # Update bounding rect (bounding rect doesn't include arrows)
            self._cachedBoundingRect = polyline.boundingRect().normalized()

            halfPenWidth = self._pen.widthF() / 2
            self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

            # Update shape (shape does include arrows if applicable)
            drawPath = QPainterPath()
            for index in range(polyline.size()):
                if (index == 0):
                    drawPath.moveTo(polyline[index])
                else:
                    drawPath.lineTo(polyline[index])
            self._cachedShape = self.strokePath(drawPath, self._pen)

            if (polyline.size() >= 2):
                if (self._firstLineSegmentLength() >= self._startArrow.size()):
                    self._cachedShape.addPath(self._startArrow.shape(self._pen, polyline[0], self._startArrowAngle()))
                if (self._lastLineSegmentLength() >= self._endArrow.size()):
                    self._cachedShape.addPath(self._endArrow.shape(self._pen, polyline[-1], self._endArrowAngle()))

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

    def _firstLineSegmentLength(self) -> float:
        p0 = self._points[0].position()
        p1 = self._points[1].position()
        return math.sqrt((p1.x() - p0.x()) * (p1.x() - p0.x()) + (p1.y() - p0.y()) * (p1.y() - p0.y()))

    def _lastLineSegmentLength(self) -> float:
        p0 = self._points[-1].position()
        p1 = self._points[-2].position()
        return math.sqrt((p1.x() - p0.x()) * (p1.x() - p0.x()) + (p1.y() - p0.y()) * (p1.y() - p0.y()))

    def _startArrowAngle(self) -> float:
        p0 = self._points[0].position()
        p1 = self._points[1].position()
        return 180 - QLineF(p0, p1).angle()

    def _endArrowAngle(self) -> float:
        p0 = self._points[-1].position()
        p1 = self._points[-2].position()
        return 180 - QLineF(p0, p1).angle()
