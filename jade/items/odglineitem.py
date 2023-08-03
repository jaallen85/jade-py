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
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath
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

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Connection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'OdgLineItem':
        copiedItem = OdgLineItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setLine(self.line())
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

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'penStyle' and isinstance(value, Qt.PenStyle)):
            self._style.setPenStyleIfUnique(Qt.PenStyle(value))
        elif (name == 'penWidth' and isinstance(value, float)):
            self._style.setPenWidthIfUnique(value)
        elif (name == 'penColor' and isinstance(value, QColor)):
            self._style.setPenColorIfUnique(value)
        elif (name == 'startMarkerStyle' and isinstance(value, OdgMarker.Style)):
            self._style.setStartMarkerStyleIfUnique(OdgMarker.Style(value))
        elif (name == 'startMarkerSize' and isinstance(value, float)):
            self._style.setStartMarkerSizeIfUnique(value)
        elif (name == 'endMarkerStyle' and isinstance(value, OdgMarker.Style)):
            self._style.setEndMarkerStyleIfUnique(OdgMarker.Style(value))
        elif (name == 'endMarkerSize' and isinstance(value, float)):
            self._style.setEndMarkerSizeIfUnique(value)

    def property(self, name: str) -> Any:
        if (name == 'line'):
            return self.line()
        if (name == 'penStyle'):
            return self._style.lookupPenStyle()
        if (name == 'penWidth'):
            return self._style.lookupPenWidth()
        if (name == 'penColor'):
            return self._style.lookupPenColor()
        if (name == 'startMarkerStyle'):
            return self._style.lookupStartMarkerStyle()
        if (name == 'startMarkerSize'):
            return self._style.lookupStartMarkerSize()
        if (name == 'endMarkerStyle'):
            return self._style.lookupEndMarkerStyle()
        if (name == 'endMarkerSize'):
            return self._style.lookupEndMarkerSize()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = QRectF(self._line.p1(), self._line.p2()).normalized()

        # Adjust for pen width
        halfPenWidth = self.style().lookupPenWidth() / 2
        rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()

        # Calculate line shape
        pen = self.style().lookupPen()

        linePath = QPainterPath()
        linePath.moveTo(self._line.p1())
        linePath.lineTo(self._line.p2())
        shape = self._strokePath(linePath, pen)

        # Add shape for each marker, if necessary
        startMarker = self.style().lookupStartMarker()
        if (self._shouldShowStartMarker(startMarker.size())):
            shape.addPath(startMarker.shape(pen, self._line.p1(), self._startMarkerAngle()))

        endMarker = self.style().lookupEndMarker()
        if (self._shouldShowEndMarker(endMarker.size())):
            shape.addPath(endMarker.shape(pen, self._line.p2(), self._endMarkerAngle()))

        return shape

    def isValid(self) -> bool:
        return (self._line.x1() != self._line.x2() or self._line.y1() != self._line.y2())

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw line
        pen = self.style().lookupPen()

        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(pen)
        painter.drawLine(self._line)

        # Draw markers if necessary
        startMarker = self.style().lookupStartMarker()
        if (self._shouldShowStartMarker(startMarker.size())):
            startMarker.paint(painter, pen, self._line.p1(), self._startMarkerAngle())

        endMarker = self.style().lookupEndMarker()
        if (self._shouldShowEndMarker(endMarker.size())):
            endMarker.paint(painter, pen, self._line.p2(), self._endMarkerAngle())

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
