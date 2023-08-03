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
from PySide6.QtGui import QColor, QPainter, QPainterPath
from .odgitem import OdgRectItemBase
from .odgitempoint import OdgItemPoint


class OdgRectItem(OdgRectItemBase):
    def __init__(self) -> None:
        super().__init__()

        self._cornerRadius: float = 0.0

        # All points are control and connection points
        for point in self._points:
            point.setType(OdgItemPoint.Type.ControlAndConnection)

    def __copy__(self) -> 'OdgRectItem':
        copiedItem = OdgRectItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setRect(self.rect())
        copiedItem.setCornerRadius(self.cornerRadius())
        return copiedItem

    # ==================================================================================================================

    def setCornerRadius(self, radius: float) -> None:
        self._cornerRadius = radius

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

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self.style().lookupBrush())
        painter.setPen(self.style().lookupPen())
        painter.drawRoundedRect(self._rect.normalized(), self._cornerRadius, self._cornerRadius)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self.setCornerRadius(self._cornerRadius * scale)
