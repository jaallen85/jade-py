# odgellipseitem.py
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
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath
from .odgitem import OdgRectItemBase
from .odgitempoint import OdgItemPoint


class OdgEllipseItem(OdgRectItemBase):
    def __init__(self) -> None:
        super().__init__()

        # Corner points are control but not connection points; edge points are control and connection points
        for index, point in enumerate(self._points):
            if ((index % 2) == 0):
                point.setType(OdgItemPoint.Type.Control)
            else:
                point.setType(OdgItemPoint.Type.ControlAndConnection)

    def __copy__(self) -> 'OdgEllipseItem':
        copiedItem = OdgEllipseItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setEllipse(self.ellipse())
        return copiedItem

    # ==================================================================================================================

    def setEllipse(self, ellipse: QRectF) -> None:
        self.setRect(ellipse)

    def ellipse(self) -> QRectF:
        return self.rect()

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'penStyle' and isinstance(value, Qt.PenStyle)):
            self._style.setPenStyleIfUnique(Qt.PenStyle(value))
        elif (name == 'penWidth' and isinstance(value, float)):
            self._style.setPenWidthIfUnique(value)
        elif (name == 'penColor' and isinstance(value, QColor)):
            self._style.setPenColorIfUnique(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self._style.setBrushColorIfUnique(value)

    def property(self, name: str) -> Any:
        if (name == 'ellipse'):
            return self.ellipse()
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
            ellipsePath = QPainterPath()
            ellipsePath.addEllipse(normalizedRect)

            shape = self._strokePath(ellipsePath, pen)
            if (brush.color().alpha() > 0):
                shape = shape.united(ellipsePath)
        else:
            shape.addEllipse(normalizedRect)

        return shape

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(self.style().lookupBrush())
        painter.setPen(self.style().lookupPen())
        painter.drawEllipse(self._rect.normalized())
