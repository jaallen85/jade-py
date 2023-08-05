# odgcurveitem.py
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


class OdgCurve:
    def __init__(self, p1: QPointF = QPointF(), cp1: QPointF = QPointF(), cp2: QPointF = QPointF(),
                 p2: QPointF = QPointF()) -> None:
        self._p1: QPointF = QPointF(p1)
        self._cp1: QPointF = QPointF(cp1)
        self._cp2: QPointF = QPointF(cp2)
        self._p2: QPointF = QPointF(p2)

    def __eq__(self, other: object) -> bool:
        if (isinstance(other, OdgCurve)):
            return (self._p1 == other.p1() and self._cp1 == other.cp1() and
                    self._cp2 == other.cp2() and self._p2 == other.p2())
        return False

    # ==================================================================================================================

    def setP1(self, p1: QPointF) -> None:
        self._p1 = QPointF(p1)

    def setCP1(self, cp1: QPointF) -> None:
        self._cp1 = QPointF(cp1)

    def setCP2(self, cp2: QPointF) -> None:
        self._cp2 = QPointF(cp2)

    def setP2(self, p2: QPointF) -> None:
        self._p2 = QPointF(p2)

    def p1(self) -> QPointF:
        return self._p1

    def cp1(self) -> QPointF:
        return self._cp1

    def cp2(self) -> QPointF:
        return self._cp2

    def p2(self) -> QPointF:
        return self._p2

    # ==================================================================================================================

    def center(self) -> QPointF:
        return QLineF(self._p1, self._p2).center()

    def length(self) -> float:
        return QLineF(self._p1, self._p2).length()

    def startAngle(self) -> float:
        p1 = self._p1
        p2 = self._pointFromRatio(0.05)
        return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi

    def endAngle(self) -> float:
        p1 = self._p2
        p2 = self._pointFromRatio(0.95)
        return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi

    # ==================================================================================================================

    def translate(self, offset: QPointF) -> None:
        self._p1.setX(self._p1.x() + offset.x())
        self._p1.setY(self._p1.y() + offset.y())
        self._cp1.setX(self._cp1.x() + offset.x())
        self._cp1.setY(self._cp1.y() + offset.y())
        self._cp2.setX(self._cp2.x() + offset.x())
        self._cp2.setY(self._cp2.y() + offset.y())
        self._p2.setX(self._p2.x() + offset.x())
        self._p2.setY(self._p2.y() + offset.y())

    def scale(self, scale: float) -> None:
        self._p1.setX(self._p1.x() * scale)
        self._p1.setY(self._p1.y() * scale)
        self._cp1.setX(self._cp1.x() * scale)
        self._cp1.setY(self._cp1.y() * scale)
        self._cp2.setX(self._cp2.x() * scale)
        self._cp2.setY(self._cp2.y() * scale)
        self._p2.setX(self._p2.x() * scale)
        self._p2.setY(self._p2.y() * scale)

    # ==================================================================================================================

    def _pointFromRatio(self, ratio: float) -> QPointF:
        x = ((1 - ratio) * (1 - ratio) * (1 - ratio) * self._p1.x() +
             3 * ratio * (1 - ratio) * (1 - ratio) * self._cp1.x() +
             3 * ratio * ratio * (1 - ratio) * self._cp2.x() +
             ratio * ratio * ratio * self._p2.x())
        y = ((1 - ratio) * (1 - ratio) * (1 - ratio) * self._p1.y() +
             3 * ratio * (1 - ratio) * (1 - ratio) * self._cp1.y() +
             3 * ratio * ratio * (1 - ratio) * self._cp2.y() +
             ratio * ratio * ratio * self._p2.y())
        return QPointF(x, y)

    # ==================================================================================================================

    @classmethod
    def copy(cls, other: 'OdgCurve') -> 'OdgCurve':
        newCurve = cls()
        newCurve.setP1(other.p1())
        newCurve.setCP1(other.cp1())
        newCurve.setCP2(other.cp2())
        newCurve.setP2(other.p2())
        return newCurve


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgCurveItem(OdgItem):
    class PointIndex(IntEnum):
        StartPoint = 0
        StartControlPoint = 1
        EndControlPoint = 2
        EndPoint = 3

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._curve: OdgCurve = OdgCurve()
        self._curvePath: QPainterPath = QPainterPath()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'OdgCurveItem':
        copiedItem = OdgCurveItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setCurve(self.curve())
        return copiedItem

    # ==================================================================================================================

    def setCurve(self, curve: OdgCurve) -> None:
        self._curve = OdgCurve.copy(curve)

        # Put the item's position at the center of the curve
        offset = self._curve.center()
        self.setPosition(self.mapToScene(offset))
        self._curve.translate(-offset)

        # Update curve path
        self._curvePath.clear()
        self._curvePath.moveTo(self._curve.p1())
        self._curvePath.cubicTo(self._curve.cp1(), self._curve.cp2(), self._curve.p2())

        # Set point positions to match self._curve
        self._points[OdgCurveItem.PointIndex.StartPoint].setPosition(self._curve.p1())
        self._points[OdgCurveItem.PointIndex.StartControlPoint].setPosition(self._curve.cp1())
        self._points[OdgCurveItem.PointIndex.EndControlPoint].setPosition(self._curve.cp2())
        self._points[OdgCurveItem.PointIndex.EndPoint].setPosition(self._curve.p2())

    def curve(self) -> OdgCurve:
        return self._curve

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
        if (name == 'curve'):
            return self.curve()
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
        rect = self._curvePath.boundingRect()

        # Adjust for pen width
        halfPenWidth = self.style().lookupPenWidth() / 2
        rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()

        # Calculate curve shape
        pen = self.style().lookupPen()

        shape = self._strokePath(self._curvePath, pen)

        # Add shape for each marker, if necessary
        startMarker = self.style().lookupStartMarker()
        if (self._shouldShowStartMarker(startMarker.size())):
            shape.addPath(startMarker.shape(pen, self._curve.p1(), self._startMarkerAngle()))

        endMarker = self.style().lookupEndMarker()
        if (self._shouldShowEndMarker(endMarker.size())):
            shape.addPath(endMarker.shape(pen, self._curve.p2(), self._endMarkerAngle()))

        return shape

    def isValid(self) -> bool:
        rect = self._curvePath.boundingRect()
        return (rect.width() != 0 or rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw line
        pen = self.style().lookupPen()

        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(pen)
        painter.drawPath(self._curvePath)

        # Draw markers if necessary
        startMarker = self.style().lookupStartMarker()
        if (self._shouldShowStartMarker(startMarker.size())):
            startMarker.paint(painter, pen, self._curve.p1(), self._startMarkerAngle())

        endMarker = self.style().lookupEndMarker()
        if (self._shouldShowEndMarker(endMarker.size())):
            endMarker.paint(painter, pen, self._curve.p2(), self._endMarkerAngle())

        # Draw control lines, if necessary
        if (self.isSelected()):
            controlPen = QPen(pen)
            controlPen.setStyle(Qt.PenStyle.DotLine)
            controlPen.setWidthF(pen.width() * 0.75)

            painter.setPen(controlPen)
            painter.drawLine(self._curve.p1(), self._curve.cp1())
            painter.drawLine(self._curve.p2(), self._curve.cp2())

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            originalStartControlOffset = self._curve.cp1() - self._curve.p1()
            originalEndControlOffset = self._curve.cp2() - self._curve.p2()

            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            curve = OdgCurve.copy(self._curve)
            match (pointIndex):
                case OdgCurveItem.PointIndex.StartPoint:
                    curve.setP1(position)
                    curve.setCP1(position + originalStartControlOffset)
                case OdgCurveItem.PointIndex.StartControlPoint:
                    curve.setCP1(position)
                case OdgCurveItem.PointIndex.EndControlPoint:
                    curve.setCP2(position)
                case OdgCurveItem.PointIndex.EndPoint:
                    curve.setP2(position)
                    curve.setCP2(position + originalEndControlOffset)

            self.setCurve(curve)

    def scale(self, scale: float) -> None:
        super().scale(scale)

        scaledCurve = OdgCurve.copy(self._curve)
        scaledCurve.scale(scale)
        self.setCurve(scaledCurve)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = 4 * grid
        if (size <= 0):
            size = sceneRect.width() / 40

        curve = OdgCurve()
        curve.setP1(QPointF(-size, -size))
        curve.setCP1(QPointF(0, -size))
        curve.setCP2(QPointF(0, size))
        curve.setP2(QPointF(size, size))
        self.setCurve(curve)

    # ==================================================================================================================

    def _shouldShowStartMarker(self, markerSize: float) -> bool:
        return (self._curve.length() >= markerSize)

    def _shouldShowEndMarker(self, markerSize: float) -> bool:
        return (self._curve.length() >= markerSize)

    def _startMarkerAngle(self) -> float:
        return self._curve.startAngle()

    def _endMarkerAngle(self) -> float:
        return self._curve.endAngle()
