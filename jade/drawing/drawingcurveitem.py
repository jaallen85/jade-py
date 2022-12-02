# drawingcurveitem.py
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
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint


class DrawingCurveItem(DrawingItem):
    class PointIndex(Enum):
        StartPoint = 0
        StartControlPoint = 1
        EndControlPoint = 2
        EndPoint = 3

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._curveStartPosition: QPointF = QPointF()
        self._curveStartControlPosition: QPointF = QPointF()
        self._curveEndControlPosition: QPointF = QPointF()
        self._curveEndPosition: QPointF = QPointF()

        self._pen: QPen = QPen()
        self._startArrow: DrawingArrow = DrawingArrow()
        self._endArrow: DrawingArrow = DrawingArrow()

        self._curvePath: QPainterPath = QPainterPath()
        self._curvePathBoundingRect: QRectF = QRectF()
        self._cachedBoundingRect: QRectF = QRectF()
        self._cachedShape: QPainterPath = QPainterPath()

        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.FreeControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.FreeControlAndConnection))

    # ==================================================================================================================

    def key(self) -> str:
        return 'curve'

    def clone(self) -> 'DrawingCurveItem':
        clonedItem = DrawingCurveItem()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setPen(QPen(self.pen()))
        clonedItem.setStartArrow(DrawingArrow(self.startArrow().style(), self.startArrow().size()))
        clonedItem.setEndArrow(DrawingArrow(self.endArrow().style(), self.endArrow().size()))
        clonedItem.setCurve(QPointF(self.curveStartPosition()), QPointF(self.curveStartControlPosition()),
                            QPointF(self.curveEndControlPosition()), QPointF(self.curveEndPosition()))
        return clonedItem

    def setInitialGeometry(self, sceneRect: QRectF, grid: float) -> None:
        size = 4 * grid
        if (size <= 0):
            size = sceneRect.width() / 40
        self.setCurve(QPointF(-size, -size), QPointF(0, -size), QPointF(0, size), QPointF(size, size))

    # ==================================================================================================================

    def setCurve(self, startPosition: QPointF, startControlPosition: QPointF, endControlPosition: QPointF,
                 endPosition: QPointF) -> None:
        points = self.points()
        if (len(points) >= 4):
            self._curveStartPosition = startPosition
            self._curveStartControlPosition = startControlPosition
            self._curveEndControlPosition = endControlPosition
            self._curveEndPosition = endPosition

            points[DrawingCurveItem.PointIndex.StartPoint.value].setPosition(self._curveStartPosition)
            points[DrawingCurveItem.PointIndex.StartControlPoint.value].setPosition(self._curveStartControlPosition)
            points[DrawingCurveItem.PointIndex.EndControlPoint.value].setPosition(self._curveEndControlPosition)
            points[DrawingCurveItem.PointIndex.EndPoint.value].setPosition(self._curveEndPosition)

            self._updateGeometry()

    def curveStartPosition(self) -> QPointF:
        return self._curveStartPosition

    def curveStartControlPosition(self) -> QPointF:
        return self._curveStartControlPosition

    def curveEndControlPosition(self) -> QPointF:
        return self._curveEndControlPosition

    def curveEndPosition(self) -> QPointF:
        return self._curveEndPosition

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
        if (name == 'curve'):
            polygon = QPolygonF()
            polygon.append(self.mapToScene(self._curveStartPosition))
            polygon.append(self.mapToScene(self._curveStartControlPosition))
            polygon.append(self.mapToScene(self._curveEndControlPosition))
            polygon.append(self.mapToScene(self._curveEndPosition))
            return polygon
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
        return (self._curvePathBoundingRect.width() != 0 or self._curvePathBoundingRect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        if (self.isValid()):
            # Draw line
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.setPen(self._pen)
            painter.drawPath(self._curvePath)

            # Draw arrows
            curveLength = self._curveLength()
            curveStartArrowAngle = self._curveStartArrowAngle()
            curveEndArrowAngle = self._curveEndArrowAngle()

            if (curveLength >= self._startArrow.size()):
                self._startArrow.paint(painter, self._pen, self._curveStartPosition, curveStartArrowAngle)
            if (curveLength >= self._endArrow.size()):
                self._endArrow.paint(painter, self._pen, self._curveEndPosition, curveEndArrowAngle)

            # Draw control lines
            if (self.isSelected() and len(self.points()) >= 4):
                pen = QPen(self._pen)
                pen.setStyle(Qt.PenStyle.DotLine)
                pen.setWidthF(pen.widthF() * 0.75)

                painter.setBrush(QBrush(Qt.GlobalColor.transparent))
                painter.setPen(pen)
                painter.drawLine(self._curveStartPosition, self._curveStartControlPosition)
                painter.drawLine(self._curveEndPosition, self._curveEndControlPosition)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        # Move the point to its new position
        super().resize(point, position, False)

        points = self.points()
        if (len(points) >= 4):
            # Keep the item's position equal to the position of its first point
            pointDelta = -points[0].position()
            for itemPoint in points:
                itemPoint.setPosition(itemPoint.position() + pointDelta)    # type: ignore
            self.setPosition(self.mapToScene(-pointDelta))

            # If the start or end point is moved, also move the corresponding control point
            p1 = points[DrawingCurveItem.PointIndex.StartPoint.value].position()
            p1Control = points[DrawingCurveItem.PointIndex.StartControlPoint.value].position()
            p2Control = points[DrawingCurveItem.PointIndex.EndControlPoint.value].position()
            p2 = points[DrawingCurveItem.PointIndex.EndPoint.value].position()

            if (point == points[DrawingCurveItem.PointIndex.StartPoint.value]):
                p1Control = p1 + (self._curveStartControlPosition - self._curveStartPosition)   # type: ignore
            elif (point == points[DrawingCurveItem.PointIndex.EndPoint.value]):
                p2Control = p2 + (self._curveEndControlPosition - self._curveEndPosition)       # type: ignore

            # Move all points to their final positions
            self.setCurve(p1, p1Control, p2Control, p2)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)

        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startArrow.setSize(self._startArrow.size() * scale)
        self._endArrow.setSize(self._endArrow.size() * scale)

        self.setCurve(
            QPointF(self._curveStartPosition.x() * scale, self._curveStartPosition.y() * scale),
            QPointF(self._curveStartControlPosition.x() * scale, self._curveStartControlPosition.y() * scale),
            QPointF(self._curveEndControlPosition.x() * scale, self._curveEndControlPosition.y() * scale),
            QPointF(self._curveEndPosition.x() * scale, self._curveEndPosition.y() * scale))

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Curve
        self.writeFloatAttribute(element, 'x1', self._curveStartPosition.x())
        self.writeFloatAttribute(element, 'y1', self._curveStartPosition.y())
        self.writeFloatAttribute(element, 'cx1', self._curveStartControlPosition.x())
        self.writeFloatAttribute(element, 'cy1', self._curveStartControlPosition.y())
        self.writeFloatAttribute(element, 'cx2', self._curveEndControlPosition.x())
        self.writeFloatAttribute(element, 'cy2', self._curveEndControlPosition.y())
        self.writeFloatAttribute(element, 'x2', self._curveEndPosition.x())
        self.writeFloatAttribute(element, 'y2', self._curveEndPosition.y())

        # Pen and arrows
        self.writePenToXml(element, 'pen', self._pen)
        self.writeArrowToXml(element, 'startArrow', self._startArrow)
        self.writeArrowToXml(element, 'endArrow', self._endArrow)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        super().readFromXml(element)

        # Curve
        self.setCurve(
            QPointF(self.readFloatAttribute(element, 'x1', 0.0), self.readFloatAttribute(element, 'y1', 0.0)),
            QPointF(self.readFloatAttribute(element, 'cx1', 0.0), self.readFloatAttribute(element, 'cy1', 0.0)),
            QPointF(self.readFloatAttribute(element, 'cx2', 0.0), self.readFloatAttribute(element, 'cy2', 0.0)),
            QPointF(self.readFloatAttribute(element, 'x2', 0.0), self.readFloatAttribute(element, 'y2', 0.0)))

        # Pen and arrows
        self.setPen(self.readPenFromXml(element, 'pen'))
        self.setStartArrow(self.readArrowFromXml(element, 'startArrow'))
        self.setEndArrow(self.readArrowFromXml(element, 'endArrow'))

    # ==================================================================================================================

    def _updateGeometry(self):
        self._curvePath.clear()
        self._curvePathBoundingRect = QRectF()
        self._cachedBoundingRect = QRectF()
        self._cachedShape.clear()

        # Update curve path and its bounding rect
        self._curvePath.moveTo(self._curveStartPosition)
        self._curvePath.cubicTo(self._curveStartControlPosition, self._curveEndControlPosition, self._curveEndPosition)
        self._curvePathBoundingRect = self._curvePath.boundingRect().normalized()

        if (self.isValid()):
            # Update bounding rect (bounding rect doesn't include arrows)
            self._cachedBoundingRect = QRectF(self._curvePathBoundingRect)

            halfPenWidth = self._pen.widthF() / 2
            self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

            # Update shape (shape does include arrows if applicable)
            self._cachedShape = self.strokePath(self._curvePath, self._pen)

            curveLength = self._curveLength()
            curveStartArrowAngle = self._curveStartArrowAngle()
            curveEndArrowAngle = self._curveEndArrowAngle()

            if (curveLength >= self._startArrow.size()):
                self._cachedShape.addPath(self._startArrow.shape(self._pen, self._curveStartPosition,
                                                                 curveStartArrowAngle))
            if (curveLength >= self._endArrow.size()):
                self._cachedShape.addPath(self._endArrow.shape(self._pen, self._curveEndPosition, curveEndArrowAngle))

    # ==================================================================================================================

    def _curveLength(self) -> float:
        p1 = self._curveStartPosition
        p2 = self._curveEndPosition
        return math.sqrt((p2.x() - p1.x()) * (p2.x() - p1.x()) + (p2.y() - p1.y()) * (p2.y() - p1.y()))

    def _curveStartArrowAngle(self) -> float:
        return 180 - QLineF(self._curveStartPosition, self._pointFromRatio(0.05)).angle()

    def _curveEndArrowAngle(self) -> float:
        return 180 - QLineF(self._curveEndPosition, self._pointFromRatio(0.95)).angle()

    def _pointFromRatio(self, ratio: float) -> QPointF:
        x = ((1 - ratio) * (1 - ratio) * (1 - ratio) * self._curveStartPosition.x() +
             3 * ratio * (1 - ratio) * (1 - ratio) * self._curveStartControlPosition.x() +
             3 * ratio * ratio * (1 - ratio) * self._curveEndControlPosition.x() +
             ratio * ratio * ratio * self._curveEndPosition.x())
        y = ((1 - ratio) * (1 - ratio) * (1 - ratio) * self._curveStartPosition.y() +
             3 * ratio * (1 - ratio) * (1 - ratio) * self._curveStartControlPosition.y() +
             3 * ratio * ratio * (1 - ratio) * self._curveEndControlPosition.y() +
             ratio * ratio * ratio * self._curveEndPosition.y())
        return QPointF(x, y)
