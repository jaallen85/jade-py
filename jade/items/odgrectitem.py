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

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from .odgitem import OdgRectItemBase
from .odgitempoint import OdgItemPoint


class OdgRectItem(OdgRectItemBase):
    def __init__(self) -> None:
        super().__init__()

        self._cornerRadius: float = 0.0

        self._brush: QBrush = QBrush()
        self._pen: QPen = QPen()

        # All points are control and connection points
        for point in self._points:
            point.setType(OdgItemPoint.Type.ControlAndConnection)

    def __copy__(self) -> 'OdgRectItem':
        copiedItem = OdgRectItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setRect(self.rect())
        copiedItem.setCornerRadius(self.cornerRadius())
        copiedItem.setBrush(self.brush())
        copiedItem.setPen(self.pen())
        return copiedItem

    # ==================================================================================================================

    def setCornerRadius(self, radius: float) -> None:
        self._cornerRadius = radius

    def cornerRadius(self) -> float:
        return self._cornerRadius

    # ==================================================================================================================

    def setBrush(self, brush: QBrush) -> None:
        self._brush = QBrush(brush)

    def setPen(self, pen: QPen) -> None:
        self._pen = QPen(pen)

    def brush(self) -> QBrush:
        return self._brush

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'cornerRadius' and isinstance(value, float)):
            self.setCornerRadius(value)
        elif (name == 'pen' and isinstance(value, QPen)):
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
        elif (name == 'brush' and isinstance(value, QBrush)):
            self.setBrush(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self.setBrush(QBrush(QColor(value)))

    def property(self, name: str) -> Any:
        if (name == 'rect'):
            return self.rect()
        if (name == 'cornerRadius'):
            return self.cornerRadius()
        if (name == 'pen'):
            return self.pen()
        if (name == 'penStyle'):
            return self.pen().style().value
        if (name == 'penWidth'):
            return self.pen().widthF()
        if (name == 'penColor'):
            return self.pen().brush().color()
        if (name == 'brush'):
            return self.brush()
        if (name == 'brushColor'):
            return self.brush().color()
        return None

    # ==================================================================================================================

    def shape(self) -> QPainterPath:
        normalizedRect = self._rect.normalized()

        shape = QPainterPath()
        if (self._pen.style() != Qt.PenStyle.NoPen):
            rectPath = QPainterPath()
            rectPath.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)

            shape = self._strokePath(rectPath, self._pen)
            if (self._brush.color().alpha() > 0):
                shape = shape.united(rectPath)
        else:
            shape.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)

        return shape

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawRoundedRect(self._rect.normalized(), self._cornerRadius, self._cornerRadius)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self._cornerRadius = self._cornerRadius * scale
        self._pen.setWidthF(self._pen.widthF() * scale)
