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

import typing
from enum import IntEnum
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingCurveItem(DrawingItem):
    class PointIndex(IntEnum):
        StartPoint = 0
        StartControlPoint = 1
        EndControlPoint = 2
        EndPoint = 3

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._curve: QPolygonF = QPolygonF()
        for _ in range(4):
            self._curve.append(QPointF())
        self._curvePath: QPainterPath = QPainterPath()

        self._pen: QPen = QPen()
        self._startArrow: DrawingArrow = DrawingArrow()
        self._endArrow: DrawingArrow = DrawingArrow()

        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.FreeControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'DrawingCurveItem':
        copiedItem = DrawingCurveItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setCurve(self.curve())
        copiedItem.setPen(self.pen())
        copiedItem.setStartArrow(self.startArrow())
        copiedItem.setEndArrow(self.endArrow())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'curve'

    # ==================================================================================================================

    def setCurve(self, curve: QPolygonF) -> None:
        if (curve.size() == 4):
            self._curve = QPolygonF(curve)

            # Update curve path
            self._curvePath.clear()
            self._curvePath.moveTo(self._curve.at(DrawingCurveItem.PointIndex.StartPoint))
            self._curvePath.cubicTo(self._curve.at(DrawingCurveItem.PointIndex.StartControlPoint),
                                    self._curve.at(DrawingCurveItem.PointIndex.EndControlPoint),
                                    self._curve.at(DrawingCurveItem.PointIndex.EndPoint))

            # Set point positions to match self._curve
            for index, point in enumerate(self._points):
                point.setPosition(self._curve.at(index))

    def curve(self) -> QPolygonF:
        return self._curve

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
        if (name == 'curve'):
            return self.mapPolygonToScene(self.curve())
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
        rect = self._curvePath.boundingRect()

        # Adjust for pen width
        halfPenWidth = self._pen.widthF() / 2
        rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()

        # Calculate curve shape
        shape = self._strokePath(self._curvePath, self._pen)

        # Add shape for each arrow, if necessary
        if (self._curve.size() >= 2):
            curveLength = self._curveLength()
            if (curveLength >= self._startArrow.size()):
                shape.addPath(self._startArrow.shape(self._pen, self._curve.at(DrawingCurveItem.PointIndex.StartPoint),
                                                     self._startArrowAngle()))
            if (curveLength >= self._endArrow.size()):
                shape.addPath(self._endArrow.shape(self._pen, self._curve.at(DrawingCurveItem.PointIndex.EndPoint),
                                                   self._endArrowAngle()))

        return shape

    def isValid(self) -> bool:
        rect = self._curvePath.boundingRect()
        return (rect.width() != 0 or rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw curve
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.drawPath(self._curvePath)

        # Draw arrows if necessary
        if (self._curve.size() >= 2):
            curveLength = self._curveLength()
            if (curveLength >= self._startArrow.size()):
                self._startArrow.paint(painter, self._pen, self._curve.at(DrawingCurveItem.PointIndex.StartPoint),
                                       self._startArrowAngle())
            if (curveLength >= self._endArrow.size()):
                self._endArrow.paint(painter, self._pen, self._curve.at(DrawingCurveItem.PointIndex.EndPoint),
                                     self._endArrowAngle())

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            curve = QPolygonF(self._curve)
            if (0 <= pointIndex < curve.size()):
                curve.takeAt(pointIndex)
                curve.insert(pointIndex, position)

            # Keep the item's position at the first point of the curve
            firstPointPosition = curve.at(0)
            self.setPosition(self.mapToScene(firstPointPosition))
            curve.translate(-firstPointPosition)

            self.setCurve(curve)

    # ==================================================================================================================

    def placeStartEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = 4 * grid
        if (size <= 0):
            size = sceneRect.width() / 40

        curve = QPolygonF()
        curve.append(QPointF(-size, -size))
        curve.append(QPointF(0, -size))
        curve.append(QPointF(0, size))
        curve.append(QPointF(size, size))
        self.setCurve(curve)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        # Curve
        self.writeFloat(element, 'x1', self._curve.at(0).x(), writeIfDefault=True)
        self.writeFloat(element, 'y1', self._curve.at(0).y(), writeIfDefault=True)
        self.writeFloat(element, 'cx1', self._curve.at(1).x(), writeIfDefault=True)
        self.writeFloat(element, 'cy1', self._curve.at(1).y(), writeIfDefault=True)
        self.writeFloat(element, 'cx2', self._curve.at(2).x(), writeIfDefault=True)
        self.writeFloat(element, 'cy2', self._curve.at(2).y(), writeIfDefault=True)
        self.writeFloat(element, 'x2', self._curve.at(3).x(), writeIfDefault=True)
        self.writeFloat(element, 'y2', self._curve.at(3).y(), writeIfDefault=True)

        # Pen and arrows
        self.writePen(element, 'pen', self._pen)
        self.writeArrow(element, 'startArrow', self._startArrow)
        self.writeArrow(element, 'endArrow', self._endArrow)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        # Line
        curve = QPolygonF()
        curve.append(QPointF(self.readFloat(element, 'x1'), self.readFloat(element, 'y1')))
        curve.append(QPointF(self.readFloat(element, 'cx1'), self.readFloat(element, 'cy1')))
        curve.append(QPointF(self.readFloat(element, 'cx2'), self.readFloat(element, 'cy2')))
        curve.append(QPointF(self.readFloat(element, 'x2'), self.readFloat(element, 'y2')))
        self.setCurve(curve)

        # Pen and arrows
        self.setPen(self.readPen(element, 'pen'))
        self.setStartArrow(self.readArrow(element, 'startArrow'))
        self.setEndArrow(self.readArrow(element, 'endArrow'))

    # ==================================================================================================================

    def _curveLength(self) -> float:
        return QLineF(self._curve.at(DrawingCurveItem.PointIndex.StartPoint),
                      self._curve.at(DrawingCurveItem.PointIndex.EndPoint)).length()

    def _startArrowAngle(self) -> float:
        return QLineF(self._curve.at(DrawingCurveItem.PointIndex.StartPoint), self._pointFromRatio(0.05)).angle()

    def _endArrowAngle(self) -> float:
        return QLineF(self._curve.at(DrawingCurveItem.PointIndex.EndPoint), self._pointFromRatio(0.95)).angle()

    def _pointFromRatio(self, ratio: float) -> QPointF:
        curveStartPosition = self._curve.at(DrawingCurveItem.PointIndex.StartPoint)
        curveStartControlPosition = self._curve.at(DrawingCurveItem.PointIndex.StartControlPoint)
        curveEndControlPosition = self._curve.at(DrawingCurveItem.PointIndex.EndControlPoint)
        curveEndPosition = self._curve.at(DrawingCurveItem.PointIndex.EndPoint)
        x = ((1 - ratio) * (1 - ratio) * (1 - ratio) * curveStartPosition.x() +
             3 * ratio * (1 - ratio) * (1 - ratio) * curveStartControlPosition.x() +
             3 * ratio * ratio * (1 - ratio) * curveEndControlPosition.x() +
             ratio * ratio * ratio * curveEndPosition.x())
        y = ((1 - ratio) * (1 - ratio) * (1 - ratio) * curveStartPosition.y() +
             3 * ratio * (1 - ratio) * (1 - ratio) * curveStartControlPosition.y() +
             3 * ratio * ratio * (1 - ratio) * curveEndControlPosition.y() +
             ratio * ratio * ratio * curveEndPosition.y())
        return QPointF(x, y)
