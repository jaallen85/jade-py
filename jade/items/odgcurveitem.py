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

from enum import IntEnum
from typing import Any
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from .odgcurve import OdgCurve
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgmarker import OdgMarker


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

        self._pen: QPen = QPen()
        self._startMarker: OdgMarker = OdgMarker()
        self._endMarker: OdgMarker = OdgMarker()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'OdgCurveItem':
        copiedItem = OdgCurveItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setCurve(self.curve())
        copiedItem.setPen(self.pen())
        copiedItem.setStartMarker(self.startMarker())
        copiedItem.setEndMarker(self.endMarker())
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
        if (name == 'curve'):
            return self.curve()
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
        rect = self._curvePath.boundingRect()

        # Adjust for pen width
        halfPenWidth = self._pen.widthF() / 2
        rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()

        # Calculate curve shape
        shape = self._strokePath(self._curvePath, self._pen)

        # Add shape for each marker, if necessary
        if (self._shouldShowStartMarker(self._startMarker.size())):
            shape.addPath(self._startMarker.shape(self._pen, self._curve.p1(), self._startMarkerAngle()))

        if (self._shouldShowEndMarker(self._endMarker.size())):
            shape.addPath(self._endMarker.shape(self._pen, self._curve.p2(), self._endMarkerAngle()))

        return shape

    def isValid(self) -> bool:
        rect = self._curvePath.boundingRect()
        return (rect.width() != 0 or rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw line
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.drawPath(self._curvePath)

        # Draw markers if necessary
        if (self._shouldShowStartMarker(self._startMarker.size())):
            self._startMarker.paint(painter, self._pen, self._curve.p1(), self._startMarkerAngle())

        if (self._shouldShowEndMarker(self._endMarker.size())):
            self._endMarker.paint(painter, self._pen, self._curve.p2(), self._endMarkerAngle())

        # Draw control lines if necessary
        if (self.isSelected()):
            controlPen = QPen(self._pen)
            controlPen.setStyle(Qt.PenStyle.DotLine)
            controlPen.setWidthF(self._pen.width() * 0.75)

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

        self._pen.setWidthF(self._pen.widthF() * scale)
        self._startMarker.setSize(self._startMarker.size() * scale)
        self._endMarker.setSize(self._endMarker.size() * scale)

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
