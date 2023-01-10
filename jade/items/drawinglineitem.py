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
from enum import IntEnum
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingLineItem(DrawingItem):
    class PointIndex(IntEnum):
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

        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.FreeControlAndConnection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Connection))
        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'DrawingLineItem':
        copiedItem = DrawingLineItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setLine(self.line())
        copiedItem.setPen(self.pen())
        copiedItem.setStartArrow(self.startArrow())
        copiedItem.setEndArrow(self.endArrow())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'line'

    def prettyName(self) -> str:
        return 'Line'

    # ==================================================================================================================

    def setLine(self, line: QLineF) -> None:
        self._line = QLineF(line)

        # Set point positions to match self._line
        if (len(self._points) >= 3):
            self._points[DrawingLineItem.PointIndex.StartPoint].setPosition(line.p1())
            self._points[DrawingLineItem.PointIndex.MidPoint].setPosition(line.center())
            self._points[DrawingLineItem.PointIndex.EndPoint].setPosition(line.p2())

    def line(self) -> QLineF:
        return self._line

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
        rect = QRectF(self._line.p1(), self._line.p2()).normalized()

        # Adjust for pen width
        halfPenWidth = self._pen.widthF() / 2
        rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()

        # Calculate line shape
        linePath = QPainterPath()
        linePath.moveTo(self._line.p1())
        linePath.lineTo(self._line.p2())
        shape = self._strokePath(linePath, self._pen)

        # Add shape for each arrow, if necessary
        if (self._shouldShowStartArrow()):
            shape.addPath(self._startArrow.shape(self._pen, self._line.p1(), self._startArrowAngle()))
        if (self._shouldShowEndArrow()):
            shape.addPath(self._endArrow.shape(self._pen, self._line.p2(), self._endArrowAngle()))

        return shape

    def isValid(self) -> bool:
        return (self._line.x1() != self._line.x2() or self._line.y1() != self._line.y2())

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw line
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.drawLine(self._line)

        # Draw arrows if necessary
        if (self._shouldShowStartArrow()):
            self._startArrow.paint(painter, self._pen, self._line.p1(), self._startArrowAngle())
        if (self._shouldShowEndArrow()):
            self._endArrow.paint(painter, self._pen, self._line.p2(), self._endArrowAngle())

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (snapTo45Degrees and len(self._points) >= 3):
            position = self._snapResizeTo45Degrees(point, position, self._points[DrawingLineItem.PointIndex.StartPoint],
                                                   self._points[DrawingLineItem.PointIndex.EndPoint])

        if (point in self._points):
            position = self.mapFromScene(position)
            line = QLineF(self._line)
            match (self._points.index(point)):
                case DrawingLineItem.PointIndex.StartPoint:
                    line.setP1(position)
                case DrawingLineItem.PointIndex.EndPoint:
                    line.setP2(position)

            # Keep the item's position as the center of the line
            center = line.center()
            self.setPosition(self.mapToScene(center))
            line.translate(-center)

            self.setLine(line)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setLine(QLineF())

    def placeResizeStartPoint(self) -> DrawingItemPoint | None:
        return self._points[DrawingLineItem.PointIndex.StartPoint] if (len(self._points) >= 3) else None

    def placeResizeEndPoint(self) -> DrawingItemPoint | None:
        return self._points[DrawingLineItem.PointIndex.EndPoint] if (len(self._points) >= 3) else None

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        element.set('x1', self._toPositionStr(self._line.x1()))
        element.set('y1', self._toPositionStr(self._line.y1()))
        element.set('x2', self._toPositionStr(self._line.x2()))
        element.set('y2', self._toPositionStr(self._line.y2()))

        self._writePen(element, 'pen', self._pen)
        self._writeArrow(element, 'startArrow', self._startArrow)
        self._writeArrow(element, 'endArrow', self._endArrow)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        self.setLine(QLineF(self._fromPositionStr(element.get('x1', '0')),
                            self._fromPositionStr(element.get('y1', '0')),
                            self._fromPositionStr(element.get('x2', '0')),
                            self._fromPositionStr(element.get('y2', '0'))))

        self.setPen(self._readPen(element, 'pen'))
        self.setStartArrow(self._readArrow(element, 'startArrow'))
        self.setEndArrow(self._readArrow(element, 'endArrow'))

    # ==================================================================================================================

    def _shouldShowStartArrow(self) -> bool:
        return (self._line.length() >= self._startArrow.size())

    def _shouldShowEndArrow(self) -> bool:
        return (self._line.length() >= self._endArrow.size())

    def _startArrowAngle(self) -> float:
        return math.atan2(self._line.y1() - self._line.y2(), self._line.x1() - self._line.x2()) * 180 / math.pi

    def _endArrowAngle(self) -> float:
        return math.atan2(self._line.y2() - self._line.y1(), self._line.x2() - self._line.x1()) * 180 / math.pi
