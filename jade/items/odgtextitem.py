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
from PySide6.QtGui import QBrush, QColor, QFont, QPainter
from .odgfontstyle import OdgFontStyle
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint


class OdgTextItem(OdgItem):
    def __init__(self) -> None:
        super().__init__()

        self._caption: str = ''

        self._font: QFont = QFont()
        self._alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
        self._padding: QSizeF = QSizeF(0, 0)
        self._brush: QBrush = QBrush()

        self._textRect: QRectF = QRectF()

        self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.NoType))

    def __copy__(self) -> 'OdgTextItem':
        copiedItem = OdgTextItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setCaption(self.caption())
        copiedItem.setFont(self.font())
        copiedItem.setAlignment(self.alignment())
        copiedItem.setPadding(self.padding())
        copiedItem.setBrush(self.brush())
        return copiedItem

    # ==================================================================================================================

    def setCaption(self, caption: str) -> None:
        self._caption = str(caption)

    def caption(self) -> str:
        return self._caption

    # ==================================================================================================================

    def setFont(self, font: QFont) -> None:
        self._font = QFont(font)

    def setAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._alignment = alignment

    def setPadding(self, padding: QSizeF) -> None:
        self._padding = QSizeF(padding)

    def setBrush(self, brush: QBrush) -> None:
        self._brush = QBrush(brush)

    def font(self) -> QFont:
        return self._font

    def alignment(self) -> Qt.AlignmentFlag:
        return self._alignment

    def padding(self) -> QSizeF:
        return self._padding

    def brush(self) -> QBrush:
        return self._brush

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'caption' and isinstance(value, str)):
            self.setCaption(value)
        elif (name == 'font' and isinstance(value, QFont)):
            self.setFont(value)
        elif (name == 'fontFamily' and isinstance(value, str)):
            font = self.font()
            font.setFamily(value)
            self.setFont(font)
        elif (name == 'fontSize' and isinstance(value, float)):
            font = self.font()
            font.setPointSizeF(value)
            self.setFont(font)
        elif (name == 'fontStyle' and isinstance(value, OdgFontStyle)):
            font = self.font()
            font.setBold(value.bold())
            font.setItalic(value.italic())
            font.setUnderline(value.underline())
            font.setStrikeOut(value.strikeOut())
            self.setFont(font)
        elif (name == 'textAlignment' and isinstance(value, Qt.AlignmentFlag)):
            self.setAlignment(value)
        elif (name == 'textPadding' and isinstance(value, QSizeF)):
            self.setPadding(value)
        elif (name == 'textBrush' and isinstance(value, QBrush)):
            self.setBrush(value)
        elif (name == 'textColor' and isinstance(value, QColor)):
            self.setBrush(QBrush(QColor(value)))

    def property(self, name: str) -> Any:
        if (name == 'position'):
            return self.position()
        if (name == 'caption'):
            return self.caption()
        if (name == 'font'):
            return self.font()
        if (name == 'fontFamily'):
            return self.font().family()
        if (name == 'fontSize'):
            return self.font().pointSizeF()
        if (name == 'fontStyle'):
            style = OdgFontStyle()
            style.setBold(self.font().bold())
            style.setItalic(self.font().italic())
            style.setUnderline(self.font().underline())
            style.setStrikeOut(self.font().strikeOut())
            return style
        if (name == 'textAlignment'):
            return self.alignment()
        if (name == 'textPadding'):
            return self.padding()
        if (name == 'textBrush'):
            return self.brush()
        if (name == 'textColor'):
            return self.brush().color()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        if (self._textRect.isNull()):
            (self._textRect, _, _) = self._calculateTextRect(QPointF(0, 0), self._font, self._alignment, self._padding,
                                                             self._caption)
        return QRectF(self._textRect)

    def isValid(self) -> bool:
        return (self._caption != '')

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        self._textRect = self._drawText(painter, QPointF(0, 0), self._font, self._alignment, self._padding,
                                        self._brush, self._caption)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self._font.setPointSizeF(self._font.pointSizeF() * scale)
        self._padding.setWidth(self._padding.width() * scale)
        self._padding.setHeight(self._padding.height() * scale)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setCaption('Label')
