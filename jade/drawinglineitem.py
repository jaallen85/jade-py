# drawinglineitem.py
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
from enum import Enum
from xml.etree import ElementTree
from PyQt6.QtCore import Qt, QLineF, QPointF, QRectF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint


class DrawingLineItem(DrawingItem):
    class PointIndex(Enum):
        StartPoint = 0
        MidPoint = 1
        EndPoint = 2

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._line: QLineF = QLineF()
        self._pen: QPen = QPen()
        self._startArrow: DrawingArrow = DrawingArrow()
        self._endArrow: DrawingArrow = DrawingArrow()

        self._cachedBoundingRect: QRectF = QRectF()
        self._cachedShape: QPainterPath = QPainterPath()

        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.FreeControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.Connection))
        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.FreeControlAndConnection))

        self.setPlaceType(DrawingItem.PlaceType.PlaceByMousePressAndRelease)

    # ==================================================================================================================

    def key(self) -> str:
        return 'line'

    def clone(self) -> 'DrawingLineItem':
        clonedItem = DrawingLineItem()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setPen(QPen(self.pen()))
        clonedItem.setStartArrow(DrawingArrow(self.startArrow().style(), self.startArrow().size()))
        clonedItem.setEndArrow(DrawingArrow(self.endArrow().style(), self.endArrow().size()))
        clonedItem.setLine(QLineF(self.line()))
        return clonedItem

    # ==================================================================================================================

    def setLine(self, line: QLineF) -> None:
        points = self.points()
        if (len(points) >= 3):
            self._line = line

            points[DrawingLineItem.PointIndex.StartPoint.value].setPosition(line.p1())
            points[DrawingLineItem.PointIndex.MidPoint.value].setPosition((line.p1() + line.p2()) / 2)  # type: ignore
            points[DrawingLineItem.PointIndex.EndPoint.value].setPosition(line.p2())

            self._updateGeometry()

    def line(self) -> QLineF:
        return self._line

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
        if (name == 'line'):
            return QLineF(self.mapToScene(self._line.p1()), self.mapToScene(self._line.p2()))
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
        return (self._line.x1() != self._line.x2() or self._line.y1() != self._line.y2())

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        if (self.isValid()):
            # Draw line
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.setPen(self._pen)
            painter.drawLine(self._line)

            # Draw arrows
            lineLength = self._line.length()
            lineAngle = self._line.angle()

            if (lineLength >= self._startArrow.size()):
                self._startArrow.paint(painter, self._pen, self._line.p1(), -lineAngle + 180)
            if (lineLength >= self._endArrow.size()):
                self._endArrow.paint(painter, self._pen, self._line.p2(), -lineAngle)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        points = self.points()
        if (len(points) >= 3):
            # Force the line to be orthogonal or at 45 degrees, if applicable
            if (snapTo45Degrees):
                otherEndPoint = None
                if (point == points[DrawingLineItem.PointIndex.StartPoint.value]):
                    otherEndPoint = points[DrawingLineItem.PointIndex.EndPoint.value]
                elif (point == points[DrawingLineItem.PointIndex.EndPoint.value]):
                    otherEndPoint = points[DrawingLineItem.PointIndex.StartPoint.value]

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

            # Keep the item's position as the center of the line
            line = QLineF(points[DrawingLineItem.PointIndex.StartPoint.value].position(),
                          points[DrawingLineItem.PointIndex.EndPoint.value].position())
            center = line.center()
            self.setPosition(self.mapToScene(center))
            line.translate(-center)

            # Move all points to their final positions
            self.setLine(line)

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        return self.points()[DrawingLineItem.PointIndex.StartPoint.value]

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        return self.points()[DrawingLineItem.PointIndex.EndPoint.value]

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)

        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startArrow.setSize(self._startArrow.size() * scale)
        self._endArrow.setSize(self._endArrow.size() * scale)

        self.setLine(QLineF(QPointF(self._line.x1() * scale, self._line.y1() * scale),
                            QPointF(self._line.x2() * scale, self._line.y2() * scale)))

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Line
        self.writeFloatAttribute(element, 'x1', self._line.x1())
        self.writeFloatAttribute(element, 'y1', self._line.y1())
        self.writeFloatAttribute(element, 'x2', self._line.x2())
        self.writeFloatAttribute(element, 'y2', self._line.y2())

        # Pen and arrows
        self.writePenToXml(element, 'pen', self._pen)
        self.writeArrowToXml(element, 'startArrow', self._startArrow)
        self.writeArrowToXml(element, 'endArrow', self._endArrow)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        super().readFromXml(element)

        # Line
        self.setLine(QLineF(self.readFloatAttribute(element, 'x1', 0),
                            self.readFloatAttribute(element, 'y1', 0),
                            self.readFloatAttribute(element, 'x2', 0),
                            self.readFloatAttribute(element, 'y2', 0)))

        # Pen and arrows
        self.setPen(self.readPenFromXml(element, 'pen'))
        self.setStartArrow(self.readArrowFromXml(element, 'startArrow'))
        self.setEndArrow(self.readArrowFromXml(element, 'endArrow'))

    # ==================================================================================================================

    def _updateGeometry(self):
        self._cachedBoundingRect = QRectF()
        self._cachedShape.clear()

        if (self.isValid()):
            # Update bounding rect (bounding rect doesn't include arrows)
            self._cachedBoundingRect = QRectF(self._line.p1(), self._line.p2()).normalized()

            halfPenWidth = self._pen.widthF() / 2
            self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

            # Update shape (shape does include arrows if applicable)
            drawPath = QPainterPath()
            drawPath.moveTo(self._line.p1())
            drawPath.lineTo(self._line.p2())
            self._cachedShape = self.strokePath(drawPath, self._pen)

            lineLength = self._line.length()
            lineAngle = self._line.angle()

            if (lineLength >= self._startArrow.size()):
                self._cachedShape.addPath(self._startArrow.shape(self._pen, self._line.p1(), -lineAngle + 180))
            if (lineLength >= self._endArrow.size()):
                self._cachedShape.addPath(self._endArrow.shape(self._pen, self._line.p2(), -lineAngle))
