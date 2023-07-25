# odgrectitem.py
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
from PySide6.QtGui import QColor, QPainter, QPainterPath
from ..odg.odgitem import OdgItem
from ..odg.odgitempoint import OdgItemPoint
from ..odg.odgreader import OdgReader
from ..odg.odgwriter import OdgWriter


class OdgRectItem(OdgItem):
    class PointIndex(IntEnum):
        TopLeft = 0
        TopMiddle = 1
        TopRight = 2
        MiddleRight = 3
        BottomRight = 4
        BottomMiddle = 5
        BottomLeft = 6
        MiddleLeft = 7

    # ==================================================================================================================

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._rect: QRectF = QRectF()
        self._cornerRadius: float = 0.0

        for _ in range(8):
            self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.ControlAndConnection))

    def __copy__(self) -> 'OdgRectItem':
        copiedItem = OdgRectItem(self.name())
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setRect(self.rect())
        copiedItem.setCornerRadius(self.cornerRadius())
        return copiedItem

    # ==================================================================================================================

    def type(self) -> str:
        return 'rect'

    def prettyType(self) -> str:
        return 'Rect'

    def qualifiedType(self) -> str:
        return 'draw:rect'

    # ==================================================================================================================

    def setRect(self, rect: QRectF) -> None:
        if (rect.width() >= 0 and rect.height() >= 0):
            self._rect = QRectF(rect)

            # Put the item's position at the center of the rect
            offset = rect.center()
            self.setPosition(self.mapToScene(offset))
            self._rect.translate(-offset)

            # Set point positions to match self._rect
            if (len(self._points) >= 8):
                center = self._rect.center()
                self._points[OdgRectItem.PointIndex.TopLeft].setPosition(QPointF(self._rect.left(), self._rect.top()))
                self._points[OdgRectItem.PointIndex.TopMiddle].setPosition(QPointF(center.x(), self._rect.top()))
                self._points[OdgRectItem.PointIndex.TopRight].setPosition(QPointF(self._rect.right(), self._rect.top()))
                self._points[OdgRectItem.PointIndex.MiddleRight].setPosition(QPointF(self._rect.right(), center.y()))
                self._points[OdgRectItem.PointIndex.BottomRight].setPosition(QPointF(self._rect.right(), self._rect.bottom()))  # noqa
                self._points[OdgRectItem.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), self._rect.bottom()))
                self._points[OdgRectItem.PointIndex.BottomLeft].setPosition(QPointF(self._rect.left(), self._rect.bottom()))    # noqa
                self._points[OdgRectItem.PointIndex.MiddleLeft].setPosition(QPointF(self._rect.left(), center.y()))

    def setCornerRadius(self, radius: float) -> None:
        self._cornerRadius = radius

    def rect(self) -> QRectF:
        return self._rect

    def cornerRadius(self) -> float:
        return self._cornerRadius

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'cornerRadius' and isinstance(value, float)):
            self.setCornerRadius(value)
        elif (name == 'penStyle' and isinstance(value, Qt.PenStyle)):
            self._style.setPenStyleIfUnique(Qt.PenStyle(value))
        elif (name == 'penWidth' and isinstance(value, float)):
            self._style.setPenWidthIfUnique(value)
        elif (name == 'penColor' and isinstance(value, QColor)):
            self._style.setPenColorIfUnique(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self._style.setBrushColorIfUnique(value)

    def property(self, name: str) -> Any:
        if (name == 'rect'):
            return self.rect()
        if (name == 'cornerRadius'):
            return self.cornerRadius()
        if (name == 'penStyle'):
            return self._style.lookupPenStyle()
        if (name == 'penWidth'):
            return self._style.lookupPenWidth()
        if (name == 'penColor'):
            return self._style.lookupPenColor()
        if (name == 'brushColor'):
            return self._style.lookupBrushColor()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = QRectF(self._rect.normalized())

        # Adjust for pen width
        if (self.style().lookupPenStyle() != Qt.PenStyle.NoPen):
            halfPenWidth = self.style().lookupPenWidth() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        normalizedRect = self._rect.normalized()
        pen = self.style().lookupPen()
        brush = self.style().lookupBrush()

        shape = QPainterPath()
        if (pen.style() != Qt.PenStyle.NoPen):
            rectPath = QPainterPath()
            rectPath.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)

            shape = self._strokePath(rectPath, pen)
            if (brush.color().alpha() > 0):
                shape = shape.united(rectPath)
        else:
            shape.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)

        return shape

    def isValid(self) -> bool:
        return (self._rect.width() != 0 or self._rect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self.style().lookupBrush())
        painter.setPen(self.style().lookupPen())
        painter.drawRoundedRect(self._rect.normalized(), self._cornerRadius, self._cornerRadius)

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            if (snapTo45Degrees and len(self._points) >= 8):
                position = self._snapResizeTo45Degrees(point, position,
                                                       self._points[OdgRectItem.PointIndex.TopLeft],
                                                       self._points[OdgRectItem.PointIndex.BottomRight])
            position = self.mapFromScene(position)

            rect = QRectF(self._rect)
            pointIndex = self._points.index(point)

            # Ensure that rect.width() >= 0
            if (pointIndex in (OdgRectItem.PointIndex.TopLeft, OdgRectItem.PointIndex.MiddleLeft,
                               OdgRectItem.PointIndex.BottomLeft)):
                if (position.x() > rect.right()):
                    rect.setLeft(rect.right())
                else:
                    rect.setLeft(position.x())
            elif (pointIndex in (OdgRectItem.PointIndex.TopRight, OdgRectItem.PointIndex.MiddleRight,
                                 OdgRectItem.PointIndex.BottomRight)):
                if (position.x() < rect.left()):
                    rect.setRight(rect.left())
                else:
                    rect.setRight(position.x())

            # Ensure that rect.height() >= 0
            if (pointIndex in (OdgRectItem.PointIndex.TopLeft, OdgRectItem.PointIndex.TopMiddle,
                               OdgRectItem.PointIndex.TopRight)):
                if (position.y() > rect.bottom()):
                    rect.setTop(rect.bottom())
                else:
                    rect.setTop(position.y())
            elif (pointIndex in (OdgRectItem.PointIndex.BottomLeft, OdgRectItem.PointIndex.BottomMiddle,
                                 OdgRectItem.PointIndex.BottomRight)):
                if (position.y() < rect.top()):
                    rect.setBottom(rect.top())
                else:
                    rect.setBottom(position.y())

            self.setRect(rect)

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self.setRect(QRectF(self._rect.left() * scale, self._rect.top() * scale,
                            self._rect.width() * scale, self._rect.height() * scale))
        self.setCornerRadius(self._cornerRadius * scale)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = 8 * grid
        if (size <= 0):
            size = sceneRect.width() / 40
        self.setRect(QRectF(-size, -size / 2, 2 * size, size))

    def placeResizeStartPoint(self) -> OdgItemPoint | None:
        return self._points[OdgRectItem.PointIndex.TopLeft] if (len(self._points) >= 8) else None

    def placeResizeEndPoint(self) -> OdgItemPoint | None:
        return self._points[OdgRectItem.PointIndex.BottomRight] if (len(self._points) >= 8) else None

    # ==================================================================================================================

    def write(self, writer: OdgWriter) -> None:
        super().write(writer)

        writer.writeLengthAttribute('svg:x', self._rect.left())
        writer.writeLengthAttribute('svg:y', self._rect.top())
        writer.writeLengthAttribute('svg:width', self._rect.width())
        writer.writeLengthAttribute('svg:height', self._rect.height())

        if (self._cornerRadius != 0):
            writer.writeLengthAttribute('draw:corner-radius', self._cornerRadius)

    def read(self, reader: OdgReader) -> None:
        pass
