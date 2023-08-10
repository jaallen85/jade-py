# odglineitem.py
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
from enum import IntEnum
from typing import Any
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgmarker import OdgMarker


class OdgLineItem(OdgItem):
    class PointIndex(IntEnum):
        StartPoint = 0
        MidPoint = 1
        EndPoint = 2

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._line: QLineF = QLineF()

        self._pen: QPen = QPen()
        self._startMarker: OdgMarker = OdgMarker()
        self._endMarker: OdgMarker = OdgMarker()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Connection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'OdgLineItem':
        copiedItem = OdgLineItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setLine(self.line())
        copiedItem.setPen(self.pen())
        copiedItem.setStartMarker(self.startMarker())
        copiedItem.setEndMarker(self.endMarker())
        return copiedItem

    # ==================================================================================================================

    def setLine(self, line: QLineF) -> None:
        self._line = QLineF(line)

        # Put the item's position at the center of the line
        offset = line.center()
        self.setPosition(self.mapToScene(offset))
        self._line.translate(-offset)

        # Set point positions to match self._line
        if (len(self._points) >= 3):
            self._points[OdgLineItem.PointIndex.StartPoint].setPosition(self._line.p1())
            self._points[OdgLineItem.PointIndex.MidPoint].setPosition(self._line.center())
            self._points[OdgLineItem.PointIndex.EndPoint].setPosition(self._line.p2())

    def line(self) -> QLineF:
        return self._line

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
        if (name == 'line'):
            return self.line()
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

        # Add shape for each marker, if necessary
        if (self._shouldShowStartMarker(self._startMarker.size())):
            shape.addPath(self._startMarker.shape(self._pen, self._line.p1(), self._startMarkerAngle()))

        if (self._shouldShowEndMarker(self._endMarker.size())):
            shape.addPath(self._endMarker.shape(self._pen, self._line.p2(), self._endMarkerAngle()))

        return shape

    def isValid(self) -> bool:
        return (self._line.x1() != self._line.x2() or self._line.y1() != self._line.y2())

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw line
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.drawLine(self._line)

        # Draw markers if necessary
        if (self._shouldShowStartMarker(self._startMarker.size())):
            self._startMarker.paint(painter, self._pen, self._line.p1(), self._startMarkerAngle())
        if (self._shouldShowEndMarker(self._endMarker.size())):
            self._endMarker.paint(painter, self._pen, self._line.p2(), self._endMarkerAngle())

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            if (snapTo45Degrees and len(self._points) >= 3):
                position = self._snapResizeTo45Degrees(point, position,
                                                       self._points[OdgLineItem.PointIndex.StartPoint],
                                                       self._points[OdgLineItem.PointIndex.EndPoint])
            position = self.mapFromScene(position)

            line = QLineF(self._line)
            match (self._points.index(point)):
                case OdgLineItem.PointIndex.StartPoint:
                    line.setP1(position)
                case OdgLineItem.PointIndex.EndPoint:
                    line.setP2(position)
            self.setLine(line)

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self.setLine(QLineF(self._line.x1() * scale, self._line.y1() * scale,
                            self._line.x2() * scale, self._line.y2() * scale))
        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startMarker.setSize(self._startMarker.size() * scale)
        self._endMarker.setSize(self._endMarker.size() * scale)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setLine(QLineF())

    def placeResizeStartPoint(self) -> OdgItemPoint | None:
        return self._points[OdgLineItem.PointIndex.StartPoint] if (len(self._points) >= 3) else None

    def placeResizeEndPoint(self) -> OdgItemPoint | None:
        return self._points[OdgLineItem.PointIndex.EndPoint] if (len(self._points) >= 3) else None

    # ==================================================================================================================

    def _shouldShowStartMarker(self, markerSize: float) -> bool:
        return (self._line.length() >= markerSize)

    def _shouldShowEndMarker(self, markerSize: float) -> bool:
        return (self._line.length() >= markerSize)

    def _startMarkerAngle(self) -> float:
        return math.atan2(self._line.y1() - self._line.y2(), self._line.x1() - self._line.x2()) * 180 / math.pi

    def _endMarkerAngle(self) -> float:
        return math.atan2(self._line.y2() - self._line.y1(), self._line.x2() - self._line.x1()) * 180 / math.pi
