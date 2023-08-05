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

from typing import Any
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF
from PySide6.QtGui import QColor, QPainter
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgFontStyle


class OdgTextItem(OdgItem):
    def __init__(self) -> None:
        super().__init__()

        self._caption: str = ''

        self._textRect: QRectF = QRectF()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.NoType))

        self.style().setPenStyle(Qt.PenStyle.NoPen)
        self.style().setBrushColor(QColor(0, 0, 0, 0))

    def __copy__(self) -> 'OdgTextItem':
        copiedItem = OdgTextItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setCaption(self.caption())
        return copiedItem

    # ==================================================================================================================

    def setCaption(self, caption: str) -> None:
        self._caption = str(caption)

    def caption(self) -> str:
        return self._caption

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'caption' and isinstance(value, str)):
            self.setCaption(value)
        elif (name == 'fontFamily' and isinstance(value, str)):
            self._style.setFontFamilyIfUnique(value)
        elif (name == 'fontSize' and isinstance(value, float)):
            self._style.setFontSizeIfUnique(value)
        elif (name == 'fontStyle' and isinstance(value, OdgFontStyle)):
            self._style.setFontStyleIfUnique(value)
        elif (name == 'textAlignment' and isinstance(value, Qt.AlignmentFlag)):
            self._style.setTextAlignmentIfUnique(value)
        elif (name == 'textPadding' and isinstance(value, QSizeF)):
            self._style.setTextPaddingIfUnique(value)
        elif (name == 'textColor' and isinstance(value, QColor)):
            self._style.setTextColorIfUnique(value)

    def property(self, name: str) -> Any:
        if (name == 'position'):
            return self.position()
        if (name == 'caption'):
            return self.caption()
        if (name == 'fontFamily'):
            return self._style.lookupFontFamily()
        if (name == 'fontSize'):
            return self._style.lookupFontSize()
        if (name == 'fontStyle'):
            return self._style.lookupFontStyle()
        if (name == 'textAlignment'):
            return self._style.lookupTextAlignment()
        if (name == 'textPadding'):
            return self._style.lookupTextPadding()
        if (name == 'textColor'):
            return self._style.lookupTextColor()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        if (self._textRect.isNull()):
            font = self._style.lookupFont()
            textAlignment = self._style.lookupTextAlignment()
            textPadding = self._style.lookupTextPadding()
            (self._textRect, _, _) = self._calculateTextRect(QPointF(0, 0), font, textAlignment, textPadding,
                                                             self._caption)
        return QRectF(self._textRect)

    def isValid(self) -> bool:
        return (self._caption != '')

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        font = self._style.lookupFont()
        textAlignment = self._style.lookupTextAlignment()
        textPadding = self._style.lookupTextPadding()
        textColor = self._style.lookupTextColor()
        self._textRect = self._drawText(painter, QPointF(0, 0), font, textAlignment, textPadding, textColor,
                                        self._caption)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setCaption('Label')
