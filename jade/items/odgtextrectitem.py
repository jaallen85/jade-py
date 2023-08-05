# odgtextrectitem.py
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
from PySide6.QtGui import QColor, QPainter, QPainterPath
from .odgitem import OdgRectItemBase
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgFontStyle


class OdgTextRectItem(OdgRectItemBase):
    def __init__(self) -> None:
        super().__init__()

        self._cornerRadius: float = 0.0

        self._caption: str = ''

        self._textRect: QRectF = QRectF()

        # All points are control and connection points
        for point in self._points:
            point.setType(OdgItemPoint.Type.ControlAndConnection)

    def __copy__(self) -> 'OdgTextRectItem':
        copiedItem = OdgTextRectItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setRect(self.rect())
        copiedItem.setCornerRadius(self.cornerRadius())
        copiedItem.setCaption(self.caption())
        return copiedItem

    # ==================================================================================================================

    def setCornerRadius(self, radius: float) -> None:
        self._cornerRadius = radius

    def cornerRadius(self) -> float:
        return self._cornerRadius

    # ==================================================================================================================

    def setCaption(self, caption: str) -> None:
        self._caption = str(caption)

    def caption(self) -> str:
        return self._caption

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        if (name == 'cornerRadius' and isinstance(value, float)):
            self.setCornerRadius(value)
        elif (name == 'caption' and isinstance(value, str)):
            self.setCaption(value)
        elif (name == 'penStyle' and isinstance(value, Qt.PenStyle)):
            self._style.setPenStyleIfUnique(Qt.PenStyle(value))
        elif (name == 'penWidth' and isinstance(value, float)):
            self._style.setPenWidthIfUnique(value)
        elif (name == 'penColor' and isinstance(value, QColor)):
            self._style.setPenColorIfUnique(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self._style.setBrushColorIfUnique(value)
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
        if (name == 'rect'):
            return self.rect()
        if (name == 'cornerRadius'):
            return self.cornerRadius()
        if (name == 'caption'):
            return self.caption()
        if (name == 'penStyle'):
            return self._style.lookupPenStyle()
        if (name == 'penWidth'):
            return self._style.lookupPenWidth()
        if (name == 'penColor'):
            return self._style.lookupPenColor()
        if (name == 'brushColor'):
            return self._style.lookupBrushColor()
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
            (self._textRect, _, _) = self._calculateTextRect(self._calculateAnchorPoint(textAlignment), font,
                                                             textAlignment, textPadding, self._caption)
        return super().boundingRect().united(self._textRect)

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

        if (self._textRect.isNull()):
            font = self._style.lookupFont()
            textAlignment = self._style.lookupTextAlignment()
            textPadding = self._style.lookupTextPadding()
            (self._textRect, _, _) = self._calculateTextRect(self._calculateAnchorPoint(textAlignment), font,
                                                             textAlignment, textPadding, self._caption)
        textPath = QPainterPath()
        textPath.addRect(self._textRect)
        shape = shape.united(textPath)

        return shape

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw rect
        painter.setBrush(self.style().lookupBrush())
        painter.setPen(self.style().lookupPen())
        painter.drawRoundedRect(self._rect.normalized(), self._cornerRadius, self._cornerRadius)

        # Draw text
        font = self._style.lookupFont()
        textAlignment = self._style.lookupTextAlignment()
        textPadding = self._style.lookupTextPadding()
        textColor = self._style.lookupTextColor()
        self._textRect = self._drawText(painter, self._calculateAnchorPoint(textAlignment), font, textAlignment,
                                        textPadding, textColor, self._caption)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self.setCornerRadius(self._cornerRadius * scale)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        super().placeCreateEvent(sceneRect, grid)
        self.setCaption('Label')

    # ==================================================================================================================

    def _calculateAnchorPoint(self, alignment: Qt.AlignmentFlag) -> QPointF:
        center = self._rect.center()

        if (alignment & Qt.AlignmentFlag.AlignLeft):
            anchorX = self._rect.left()
        elif (alignment & Qt.AlignmentFlag.AlignRight):
            anchorX = self._rect.right()
        else:
            anchorX = center.x()

        if (alignment & Qt.AlignmentFlag.AlignTop):
            anchorY = self._rect.top()
        elif (alignment & Qt.AlignmentFlag.AlignBottom):
            anchorY = self._rect.bottom()
        else:
            anchorY = center.y()

        return QPointF(anchorX, anchorY)
