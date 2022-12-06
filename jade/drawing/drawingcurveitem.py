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
        clonedItem.setCurve(self.curveStartPosition(), self.curveStartControlPosition(),
                            self.curveEndControlPosition(), self.curveEndPosition())
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
            points[DrawingCurveItem.PointIndex.StartPoint.value].setPosition(startPosition)
            points[DrawingCurveItem.PointIndex.StartControlPoint.value].setPosition(startControlPosition)
            points[DrawingCurveItem.PointIndex.EndControlPoint.value].setPosition(endControlPosition)
            points[DrawingCurveItem.PointIndex.EndPoint.value].setPosition(endPosition)
            self._updateGeometry()

    def curveStartPosition(self) -> QPointF:
        if (len(self._points) >= 4):
            return QPointF(self._points[DrawingCurveItem.PointIndex.StartPoint.value].position())
        return QPointF()

    def curveStartControlPosition(self) -> QPointF:
        if (len(self._points) >= 4):
            return QPointF(self._points[DrawingCurveItem.PointIndex.StartControlPoint.value].position())
        return QPointF()

    def curveEndControlPosition(self) -> QPointF:
        if (len(self._points) >= 4):
            return QPointF(self._points[DrawingCurveItem.PointIndex.EndControlPoint.value].position())
        return QPointF()

    def curveEndPosition(self) -> QPointF:
        if (len(self._points) >= 4):
            return QPointF(self._points[DrawingCurveItem.PointIndex.EndPoint.value].position())
        return QPointF()

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
            polygon.append(self.mapToScene(self.curveStartPosition()))
            polygon.append(self.mapToScene(self.curveStartControlPosition()))
            polygon.append(self.mapToScene(self.curveEndControlPosition()))
            polygon.append(self.mapToScene(self.curveEndPosition()))
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
            curveStartPosition = self.curveStartPosition()
            curveStartControlPosition = self.curveStartControlPosition()
            curveEndControlPosition = self.curveEndControlPosition()
            curveEndPosition = self.curveEndPosition()

            curveLength = self._curveLength()
            if (curveLength >= self._startArrow.size()):
                self._startArrow.paint(painter, self._pen, curveStartPosition, self._curveStartArrowAngle())
            if (curveLength >= self._endArrow.size()):
                self._endArrow.paint(painter, self._pen, curveEndPosition, self._curveEndArrowAngle())

            # Draw control lines
            if (self.isSelected() and len(self._points) >= 4):
                pen = QPen(self._pen)
                pen.setStyle(Qt.PenStyle.DotLine)
                pen.setWidthF(pen.widthF() * 0.75)

                painter.setBrush(QBrush(Qt.GlobalColor.transparent))
                painter.setPen(pen)
                painter.drawLine(curveStartPosition, curveStartControlPosition)
                painter.drawLine(curveEndPosition, curveEndControlPosition)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (len(self._points) >= 4):
            previousStartControlDelta = self.curveStartControlPosition() - self.curveStartPosition()    # type: ignore
            previousEndControlDelta = self.curveEndControlPosition() - self.curveEndPosition()    # type: ignore

            # Move the point to its new position
            super().resize(point, position, False)

            # Keep the item's position equal to the position of its first point
            curveStartPosition = self.curveStartPosition()
            curveStartControlPosition = self.curveStartControlPosition()
            curveEndControlPosition = self.curveEndControlPosition()
            curveEndPosition = self.curveEndPosition()

            self.setPosition(self.mapToScene(curveStartPosition))
            curveStartControlPosition = curveStartControlPosition - curveStartPosition  # type: ignore
            curveEndControlPosition = curveEndControlPosition - curveStartPosition      # type: ignore
            curveEndPosition = curveEndPosition - curveStartPosition                    # type: ignore
            curveStartPosition = QPointF()

            # If the start or end point is moved, also move the corresponding control point
            if (point == self._points[DrawingCurveItem.PointIndex.StartPoint.value]):
                curveStartControlPosition = curveStartPosition + previousStartControlDelta  # type: ignore
            elif (point == self._points[DrawingCurveItem.PointIndex.EndPoint.value]):
                curveEndControlPosition = curveEndPosition + previousEndControlDelta        # type: ignore

            # Set final point positions
            self.setCurve(curveStartPosition, curveStartControlPosition, curveEndControlPosition, curveEndPosition)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)

        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startArrow.setSize(self._startArrow.size() * scale)
        self._endArrow.setSize(self._endArrow.size() * scale)

        curveStartPosition = self.curveStartPosition()
        curveStartControlPosition = self.curveStartControlPosition()
        curveEndControlPosition = self.curveEndControlPosition()
        curveEndPosition = self.curveEndPosition()
        self.setCurve(
            QPointF(curveStartPosition.x() * scale, curveStartPosition.y() * scale),
            QPointF(curveStartControlPosition.x() * scale, curveStartControlPosition.y() * scale),
            QPointF(curveEndControlPosition.x() * scale, curveEndControlPosition.y() * scale),
            QPointF(curveEndPosition.x() * scale, curveEndPosition.y() * scale))

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Curve
        curveStartPosition = self.curveStartPosition()
        curveStartControlPosition = self.curveStartControlPosition()
        curveEndControlPosition = self.curveEndControlPosition()
        curveEndPosition = self.curveEndPosition()
        self.writeFloatAttribute(element, 'x1', curveStartPosition.x())
        self.writeFloatAttribute(element, 'y1', curveStartPosition.y())
        self.writeFloatAttribute(element, 'cx1', curveStartControlPosition.x())
        self.writeFloatAttribute(element, 'cy1', curveStartControlPosition.y())
        self.writeFloatAttribute(element, 'cx2', curveEndControlPosition.x())
        self.writeFloatAttribute(element, 'cy2', curveEndControlPosition.y())
        self.writeFloatAttribute(element, 'x2', curveEndPosition.x())
        self.writeFloatAttribute(element, 'y2', curveEndPosition.y())

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

    def _updateGeometry(self) -> None:
        self._curvePath.clear()
        self._curvePathBoundingRect = QRectF()
        self._cachedBoundingRect = QRectF()
        self._cachedShape.clear()

        # Update curve path and its bounding rect
        curveStartPosition = self.curveStartPosition()
        curveStartControlPosition = self.curveStartControlPosition()
        curveEndControlPosition = self.curveEndControlPosition()
        curveEndPosition = self.curveEndPosition()

        self._curvePath.moveTo(curveStartPosition)
        self._curvePath.cubicTo(curveStartControlPosition, curveEndControlPosition, curveEndPosition)
        self._curvePathBoundingRect = self._curvePath.boundingRect().normalized()

        if (self.isValid()):
            # Update bounding rect (bounding rect doesn't include arrows)
            self._cachedBoundingRect = QRectF(self._curvePathBoundingRect)

            halfPenWidth = self._pen.widthF() / 2
            self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

            # Update shape (shape does include arrows if applicable)
            self._cachedShape = self.strokePath(self._curvePath, self._pen)

            curveLength = self._curveLength()
            if (curveLength >= self._startArrow.size()):
                self._cachedShape.addPath(self._startArrow.shape(self._pen, curveStartPosition,
                                                                 self._curveStartArrowAngle()))
            if (curveLength >= self._endArrow.size()):
                self._cachedShape.addPath(self._endArrow.shape(self._pen, curveEndPosition,
                                                               self._curveEndArrowAngle()))

    # ==================================================================================================================

    def _curveLength(self) -> float:
        p1 = self.curveStartPosition()
        p2 = self.curveEndPosition()
        return math.sqrt((p2.x() - p1.x()) * (p2.x() - p1.x()) + (p2.y() - p1.y()) * (p2.y() - p1.y()))

    def _curveStartArrowAngle(self) -> float:
        return 180 - QLineF(self.curveStartPosition(), self._pointFromRatio(0.05)).angle()

    def _curveEndArrowAngle(self) -> float:
        return 180 - QLineF(self.curveEndPosition(), self._pointFromRatio(0.95)).angle()

    def _pointFromRatio(self, ratio: float) -> QPointF:
        curveStartPosition = self.curveStartPosition()
        curveStartControlPosition = self.curveStartControlPosition()
        curveEndControlPosition = self.curveEndControlPosition()
        curveEndPosition = self.curveEndPosition()
        x = ((1 - ratio) * (1 - ratio) * (1 - ratio) * curveStartPosition.x() +
             3 * ratio * (1 - ratio) * (1 - ratio) * curveStartControlPosition.x() +
             3 * ratio * ratio * (1 - ratio) * curveEndControlPosition.x() +
             ratio * ratio * ratio * curveEndPosition.x())
        y = ((1 - ratio) * (1 - ratio) * (1 - ratio) * curveStartPosition.y() +
             3 * ratio * (1 - ratio) * (1 - ratio) * curveStartControlPosition.y() +
             3 * ratio * ratio * (1 - ratio) * curveEndControlPosition.y() +
             ratio * ratio * ratio * curveEndPosition.y())
        return QPointF(x, y)
