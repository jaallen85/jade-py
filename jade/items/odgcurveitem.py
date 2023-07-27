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
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from ..odg.odgitem import OdgItem
from ..odg.odgitempoint import OdgItemPoint
from ..odg.odgitemstyle import OdgItemStyle
from ..odg.odgmarker import OdgMarker
from ..odg.odgreader import OdgReader
from ..odg.odgwriter import OdgWriter


class OdgCurveItem(OdgItem):
    class PointIndex(IntEnum):
        StartPoint = 0
        StartControlPoint = 1
        EndControlPoint = 2
        EndPoint = 3

    # ==================================================================================================================

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._curve: QPolygonF = QPolygonF()
        for _ in range(4):
            self._curve.append(QPointF())
        self._curvePath: QPainterPath = QPainterPath()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))
        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.FreeControlAndConnection))

    def __copy__(self) -> 'OdgCurveItem':
        copiedItem = OdgCurveItem(self.name())
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setCurve(self.curve())
        return copiedItem

    # ==================================================================================================================

    def type(self) -> str:
        return 'curve'

    def prettyType(self) -> str:
        return 'Curve'

    def qualifiedType(self) -> str:
        return 'draw:path'

    # ==================================================================================================================

    def setCurve(self, curve: QPolygonF) -> None:
        if (curve.size() == 4):
            self._curve = QPolygonF(curve)

            # Put the item's position at the center of the curve
            offset = QLineF(curve.at(OdgCurveItem.PointIndex.StartPoint),
                            curve.at(OdgCurveItem.PointIndex.EndPoint)).center()
            self.setPosition(self.mapToScene(offset))
            self._curve.translate(-offset)

            # Update curve path
            self._curvePath.clear()
            self._curvePath.moveTo(self._curve.at(OdgCurveItem.PointIndex.StartPoint))
            self._curvePath.cubicTo(self._curve.at(OdgCurveItem.PointIndex.StartControlPoint),
                                    self._curve.at(OdgCurveItem.PointIndex.EndControlPoint),
                                    self._curve.at(OdgCurveItem.PointIndex.EndPoint))

            # Set point positions to match self._curve
            for index, point in enumerate(self._points):
                point.setPosition(self._curve.at(index))

    def curve(self) -> QPolygonF:
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
            shape.addPath(startMarker.shape(pen, self._curve.at(OdgCurveItem.PointIndex.StartPoint),
                                            self._startMarkerAngle()))

        endMarker = self.style().lookupEndMarker()
        if (self._shouldShowEndMarker(endMarker.size())):
            shape.addPath(endMarker.shape(pen, self._curve.at(OdgCurveItem.PointIndex.EndPoint),
                                          self._endMarkerAngle()))

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
            startMarker.paint(painter, pen, self._curve.at(OdgCurveItem.PointIndex.StartPoint),
                              self._startMarkerAngle())

        endMarker = self.style().lookupEndMarker()
        if (self._shouldShowEndMarker(endMarker.size())):
            endMarker.paint(painter, pen, self._curve.at(OdgCurveItem.PointIndex.EndPoint),
                            self._endMarkerAngle())

        # Draw control lines, if necessary
        if (self.isSelected()):
            controlPen = QPen(pen)
            controlPen.setStyle(Qt.PenStyle.DotLine)
            controlPen.setWidthF(pen.width() * 0.75)

            painter.setPen(controlPen)
            painter.drawLine(self._curve.at(OdgCurveItem.PointIndex.StartPoint),
                             self._curve.at(OdgCurveItem.PointIndex.StartControlPoint))
            painter.drawLine(self._curve.at(OdgCurveItem.PointIndex.EndPoint),
                             self._curve.at(OdgCurveItem.PointIndex.EndControlPoint))

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points and self._curve.size() == 4):
            originalStartControlOffset = (self._curve.at(OdgCurveItem.PointIndex.StartControlPoint) -
                                          self._curve.at(OdgCurveItem.PointIndex.StartPoint))
            originalEndControlOffset = (self._curve.at(OdgCurveItem.PointIndex.EndControlPoint) -
                                        self._curve.at(OdgCurveItem.PointIndex.EndPoint))

            pointIndex = self._points.index(point)
            position = self.mapFromScene(position)

            curve = QPolygonF(self._curve)
            if (0 <= pointIndex < curve.size()):
                curve.takeAt(pointIndex)
                curve.insert(pointIndex, position)

            # If the start or end point is resized, also move the corresponding control point
            if (pointIndex == OdgCurveItem.PointIndex.StartPoint):
                curve.takeAt(OdgCurveItem.PointIndex.StartControlPoint)
                curve.insert(OdgCurveItem.PointIndex.StartControlPoint, position + originalStartControlOffset)
            elif (pointIndex == OdgCurveItem.PointIndex.EndPoint):
                curve.takeAt(OdgCurveItem.PointIndex.EndControlPoint)
                curve.insert(OdgCurveItem.PointIndex.EndControlPoint, position + originalEndControlOffset)

            self.setCurve(curve)

    def scale(self, scale: float) -> None:
        super().scale(scale)

        scaledCurve = QPolygonF()
        for index in range(self._curve.count()):
            point = self._curve.at(index)
            scaledCurve.append(QPointF(point.x() * scale, point.y() * scale))
        self.setCurve(scaledCurve)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
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

    def write(self, writer: OdgWriter) -> None:
        super().write(writer)

        viewBox = self._curvePath.boundingRect()
        writer.writeLengthAttribute('svg:x', viewBox.left())
        writer.writeLengthAttribute('svg:y', viewBox.top())
        writer.writeLengthAttribute('svg:width', viewBox.width())
        writer.writeLengthAttribute('svg:height', viewBox.height())
        writer.writeAttribute('svg:viewBox', (f'{writer.lengthToNoUnitsString(viewBox.left())} '
                                              f'{writer.lengthToNoUnitsString(viewBox.top())} '
                                              f'{writer.lengthToNoUnitsString(viewBox.width())} '
                                              f'{writer.lengthToNoUnitsString(viewBox.height())}'))

        p1 = self._curve.at(OdgCurveItem.PointIndex.StartPoint)
        cp1 = self._curve.at(OdgCurveItem.PointIndex.StartControlPoint)
        cp2 = self._curve.at(OdgCurveItem.PointIndex.EndControlPoint)
        p2 = self._curve.at(OdgCurveItem.PointIndex.EndPoint)
        writer.writeAttribute('svg:d', (f'M {writer.lengthToNoUnitsString(p1.x())},{writer.lengthToNoUnitsString(p1.y())} '     # noqa
                                        f'C {writer.lengthToNoUnitsString(cp1.x())},{writer.lengthToNoUnitsString(cp1.y())} '   # noqa
                                        f'{writer.lengthToNoUnitsString(cp2.x())},{writer.lengthToNoUnitsString(cp2.y())} '     # noqa
                                        f'{writer.lengthToNoUnitsString(p2.x())},{writer.lengthToNoUnitsString(p2.y())}'))      # noqa

    def read(self, reader: OdgReader, automaticItemStyles: list[OdgItemStyle]) -> None:
        super().read(reader, automaticItemStyles)

        try:
            attr = reader.attributes()
            if (attr.hasAttribute('svg:d')):
                tokens = attr.value('svg:d').split(' ')
                if (len(tokens) == 6 and tokens[0] == 'M' and tokens[2] == 'C'):
                    curve = QPolygonF()
                    coordTokens = tokens[1].split(',')
                    curve.append(QPointF(float(coordTokens[0]), float(coordTokens[1])))
                    coordTokens = tokens[3].split(',')
                    curve.append(QPointF(float(coordTokens[0]), float(coordTokens[1])))
                    coordTokens = tokens[4].split(',')
                    curve.append(QPointF(float(coordTokens[0]), float(coordTokens[1])))
                    coordTokens = tokens[5].split(',')
                    curve.append(QPointF(float(coordTokens[0]), float(coordTokens[1])))
                    self.setCurve(curve)
        except (ValueError, KeyError):
            pass

        reader.skipCurrentElement()

    # ==================================================================================================================

    def _shouldShowStartMarker(self, markerSize: float) -> bool:
        length = QLineF(self._curve.at(OdgCurveItem.PointIndex.StartPoint),
                        self._curve.at(OdgCurveItem.PointIndex.EndPoint)).length()
        return (length >= markerSize)

    def _shouldShowEndMarker(self, markerSize: float) -> bool:
        length = QLineF(self._curve.at(OdgCurveItem.PointIndex.StartPoint),
                        self._curve.at(OdgCurveItem.PointIndex.EndPoint)).length()
        return (length >= markerSize)

    def _startMarkerAngle(self) -> float:
        p1 = self._curve.at(OdgCurveItem.PointIndex.StartPoint)
        p2 = self._pointFromRatio(0.05)
        return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi

    def _endMarkerAngle(self) -> float:
        p1 = self._curve.at(OdgCurveItem.PointIndex.EndPoint)
        p2 = self._pointFromRatio(0.95)
        return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi

    def _pointFromRatio(self, ratio: float) -> QPointF:
        curveStartPosition = self._curve.at(OdgCurveItem.PointIndex.StartPoint)
        curveStartControlPosition = self._curve.at(OdgCurveItem.PointIndex.StartControlPoint)
        curveEndControlPosition = self._curve.at(OdgCurveItem.PointIndex.EndControlPoint)
        curveEndPosition = self._curve.at(OdgCurveItem.PointIndex.EndPoint)
        x = ((1 - ratio) * (1 - ratio) * (1 - ratio) * curveStartPosition.x() +
             3 * ratio * (1 - ratio) * (1 - ratio) * curveStartControlPosition.x() +
             3 * ratio * ratio * (1 - ratio) * curveEndControlPosition.x() +
             ratio * ratio * ratio * curveEndPosition.x())
        y = ((1 - ratio) * (1 - ratio) * (1 - ratio) * curveStartPosition.y() +
             3 * ratio * (1 - ratio) * (1 - ratio) * curveStartControlPosition.y() +
             3 * ratio * ratio * (1 - ratio) * curveEndControlPosition.y() +
             ratio * ratio * ratio * curveEndPosition.y())
        return QPointF(x, y)
