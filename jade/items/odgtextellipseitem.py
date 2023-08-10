# odgtextellipseitem.py
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
from typing import Any
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from .odgfontstyle import OdgFontStyle
from .odgitem import OdgRectItemBase
from .odgitempoint import OdgItemPoint


class OdgTextEllipseItem(OdgRectItemBase):
    def __init__(self) -> None:
        super().__init__()

        self._brush: QBrush = QBrush()
        self._pen: QPen = QPen()

        self._caption: str = ''

        self._font: QFont = QFont()
        self._textAlignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
        self._textPadding: QSizeF = QSizeF(0, 0)
        self._textBrush: QBrush = QBrush()

        self._textRect: QRectF = QRectF()

        # Corner points are control but not connection points; edge points are control and connection points
        for index, point in enumerate(self._points):
            if ((index % 2) == 0):
                point.setType(OdgItemPoint.Type.Control)
            else:
                point.setType(OdgItemPoint.Type.ControlAndConnection)

    def __copy__(self) -> 'OdgTextEllipseItem':
        copiedItem = OdgTextEllipseItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setEllipse(self.ellipse())
        copiedItem.setBrush(self.brush())
        copiedItem.setPen(self.pen())
        copiedItem.setCaption(self.caption())
        copiedItem.setFont(self.font())
        copiedItem.setTextAlignment(self.textAlignment())
        copiedItem.setTextPadding(self.textPadding())
        copiedItem.setTextBrush(self.textBrush())
        return copiedItem

    # ==================================================================================================================

    def setEllipse(self, ellipse: QRectF) -> None:
        self.setRect(ellipse)

    def ellipse(self) -> QRectF:
        return self.rect()

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

    def setCaption(self, caption: str) -> None:
        self._caption = str(caption)

    def caption(self) -> str:
        return self._caption

    # ==================================================================================================================

    def setFont(self, font: QFont) -> None:
        self._font = QFont(font)

    def setTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._textAlignment = alignment

    def setTextPadding(self, padding: QSizeF) -> None:
        self._textPadding = QSizeF(padding)

    def setTextBrush(self, brush: QBrush) -> None:
        self._textBrush = QBrush(brush)

    def font(self) -> QFont:
        return self._font

    def textAlignment(self) -> Qt.AlignmentFlag:
        return self._textAlignment

    def textPadding(self) -> QSizeF:
        return self._textPadding

    def textBrush(self) -> QBrush:
        return self._textBrush

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
        elif (name == 'brush' and isinstance(value, QBrush)):
            self.setBrush(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self.setBrush(QBrush(QColor(value)))
        elif (name == 'caption' and isinstance(value, str)):
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
            self.setTextAlignment(value)
        elif (name == 'textPadding' and isinstance(value, QSizeF)):
            self.setTextPadding(value)
        elif (name == 'textBrush' and isinstance(value, QBrush)):
            self.setTextBrush(value)
        elif (name == 'textColor' and isinstance(value, QColor)):
            self.setTextBrush(QBrush(QColor(value)))

    def property(self, name: str) -> Any:
        if (name == 'ellipse'):
            return self.ellipse()
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
            return self.textAlignment()
        if (name == 'textPadding'):
            return self.textPadding()
        if (name == 'textBrush'):
            return self.textBrush()
        if (name == 'textColor'):
            return self.textBrush().color()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        if (self._textRect.isNull()):
            (self._textRect, _, _) = self._calculateTextRect(self._calculateAnchorPoint(self._textAlignment),
                                                             self._font, self._textAlignment, self._textPadding,
                                                             self._caption)
        return super().boundingRect().united(self._textRect)

    def shape(self) -> QPainterPath:
        normalizedRect = self._rect.normalized()

        shape = QPainterPath()
        if (self._pen.style() != Qt.PenStyle.NoPen):
            ellipsePath = QPainterPath()
            ellipsePath.addEllipse(normalizedRect)

            shape = self._strokePath(ellipsePath, self._pen)
            if (self._brush.color().alpha() > 0):
                shape = shape.united(ellipsePath)
        else:
            shape.addEllipse(normalizedRect)

        if (self._textRect.isNull()):
            (self._textRect, _, _) = self._calculateTextRect(self._calculateAnchorPoint(self._textAlignment),
                                                             self._font, self._textAlignment, self._textPadding,
                                                             self._caption)
        textPath = QPainterPath()
        textPath.addRect(self._textRect)
        shape = shape.united(textPath)

        return shape

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw rect
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(self._rect.normalized())

        # Draw text
        self._textRect = self._drawText(painter, self._calculateAnchorPoint(self._textAlignment), self._font,
                                        self._textAlignment, self._textPadding, self._textBrush, self._caption)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self._pen.setWidthF(self._pen.widthF() * scale)
        self._font.setPointSizeF(self._font.pointSizeF() * scale)
        self._textPadding.setWidth(self._textPadding.width() * scale)
        self._textPadding.setHeight(self._textPadding.height() * scale)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        super().placeCreateEvent(sceneRect, grid)
        self.setCaption('Label')

    # ==================================================================================================================

    def _calculateAnchorPoint(self, alignment: Qt.AlignmentFlag) -> QPointF:
        if ((alignment & Qt.AlignmentFlag.AlignLeft) and (alignment & Qt.AlignmentFlag.AlignTop)):
            angle = math.radians(-135)
            return QPointF(self._rect.width() / 2 * math.cos(angle), self._rect.height() / 2 * math.sin(angle))
        if ((alignment & Qt.AlignmentFlag.AlignHCenter) and (alignment & Qt.AlignmentFlag.AlignTop)):
            return QPointF(self._rect.center().x(), self._rect.top())
        if ((alignment & Qt.AlignmentFlag.AlignRight) and (alignment & Qt.AlignmentFlag.AlignTop)):
            angle = math.radians(-45)
            return QPointF(self._rect.width() / 2 * math.cos(angle), self._rect.height() / 2 * math.sin(angle))
        if ((alignment & Qt.AlignmentFlag.AlignRight) and (alignment & Qt.AlignmentFlag.AlignVCenter)):
            return QPointF(self._rect.right(), self._rect.center().y())
        if ((alignment & Qt.AlignmentFlag.AlignRight) and (alignment & Qt.AlignmentFlag.AlignBottom)):
            angle = math.radians(45)
            return QPointF(self._rect.width() / 2 * math.cos(angle), self._rect.height() / 2 * math.sin(angle))
        if ((alignment & Qt.AlignmentFlag.AlignHCenter) and (alignment & Qt.AlignmentFlag.AlignBottom)):
            return QPointF(self._rect.center().x(), self._rect.bottom())
        if ((alignment & Qt.AlignmentFlag.AlignLeft) and (alignment & Qt.AlignmentFlag.AlignBottom)):
            angle = math.radians(135)
            return QPointF(self._rect.width() / 2 * math.cos(angle), self._rect.height() / 2 * math.sin(angle))
        if ((alignment & Qt.AlignmentFlag.AlignLeft) and (alignment & Qt.AlignmentFlag.AlignVCenter)):
            return QPointF(self._rect.left(), self._rect.center().y())
        return self._rect.center()
