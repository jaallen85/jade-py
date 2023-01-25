# drawingtextellipseitem.py
# Copyright (C) 2022  Jason Allen
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

import typing
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen
from .drawingellipseitem import DrawingEllipseItem


class DrawingTextEllipseItem(DrawingEllipseItem):
    def __init__(self) -> None:
        super().__init__()

        self._caption: str = ''
        self._font: QFont = QFont()
        self._textPen: QPen = QPen()

        self._textRect: QRectF = QRectF()

    def __copy__(self) -> 'DrawingTextEllipseItem':
        copiedItem = DrawingTextEllipseItem()
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.setEllipse(self.ellipse())
        copiedItem.setBrush(self.brush())
        copiedItem.setPen(self.pen())
        copiedItem.setCaption(self.caption())
        copiedItem.setFont(self.font())
        copiedItem.setTextBrush(self.textBrush())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'textEllipse'

    def prettyName(self) -> str:
        return 'Text Ellipse'

    # ==================================================================================================================

    def setCaption(self, caption: str) -> None:
        self._caption = str(caption)

    def caption(self) -> str:
        return self._caption

    # ==================================================================================================================

    def setFont(self, font: QFont) -> None:
        self._font = QFont(font)

    def setTextBrush(self, brush: QBrush) -> None:
        self._textPen.setBrush(brush)

    def font(self) -> QFont:
        return self._font

    def textBrush(self) -> QBrush:
        return self._textPen.brush()

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
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
        elif (name == 'fontBold' and isinstance(value, bool)):
            font = self.font()
            font.setBold(value)
            self.setFont(font)
        elif (name == 'fontItalic' and isinstance(value, bool)):
            font = self.font()
            font.setItalic(value)
            self.setFont(font)
        elif (name == 'fontUnderline' and isinstance(value, bool)):
            font = self.font()
            font.setUnderline(value)
            self.setFont(font)
        elif (name == 'fontStrikeOut' and isinstance(value, bool)):
            font = self.font()
            font.setStrikeOut(value)
            self.setFont(font)
        elif (name == 'fontStyle' and isinstance(value, list) and len(value) == 4):
            font = self.font()
            font.setBold(value[0])
            font.setItalic(value[1])
            font.setUnderline(value[2])
            font.setStrikeOut(value[3])
            self.setFont(font)
        elif (name == 'textBrush' and isinstance(value, QBrush)):
            self.setTextBrush(value)
        elif (name == 'textColor' and isinstance(value, QColor)):
            self.setTextBrush(QBrush(QColor(value)))

    def property(self, name: str) -> typing.Any:
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
        if (name == 'fontBold'):
            return self.font().bold()
        if (name == 'fontItalic'):
            return self.font().italic()
        if (name == 'fontUnderline'):
            return self.font().underline()
        if (name == 'fontStrikeOut'):
            return self.font().strikeOut()
        if (name == 'fontStyle'):
            styles = []
            styles.append(self.font().bold())
            styles.append(self.font().italic())
            styles.append(self.font().underline())
            styles.append(self.font().strikeOut())
            return styles
        if (name == 'textBrush'):
            return self.textBrush()
        if (name == 'textColor'):
            return self.textBrush().color()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        if (self._textRect.isNull()):
            self._textRect = self._calculateTextRect(self._font)
        return super().boundingRect().united(self._textRect)

    def shape(self) -> QPainterPath:
        shape = super().shape()

        textPath = QPainterPath()
        if (self._textRect.isNull()):
            self._textRect = self._calculateTextRect(self._font)
        textPath.addRect(self._textRect)
        shape = shape.united(textPath)

        return shape

    def isValid(self) -> bool:
        return (super().isValid() and self._caption != '')

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        # Draw ellipse
        super().paint(painter)

        # Draw text
        font = QFont(self._font)
        font.setPointSizeF(font.pointSizeF() * 96.0 / painter.paintEngine().paintDevice().logicalDpiX())

        self._textRect = self._calculateTextRect(font)

        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._textPen)
        painter.setFont(font)
        painter.drawText(self._textRect, Qt.AlignmentFlag.AlignCenter, self._caption)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        super().placeCreateEvent(sceneRect, grid)
        self.setCaption('Label')

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        self._writeFont(element, 'font', self._font)
        self._writeBrush(element, 'text', self._textPen.brush())

        element.text = self._caption

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        self.setFont(self._readFont(element, 'font'))
        self.setTextBrush(self._readBrush(element, 'text'))

        if (isinstance(element.text, str)):
            self.setCaption(element.text)

    # ==================================================================================================================

    def _calculateTextRect(self, font: QFont) -> QRectF:
        if (self.isValid()):
            # Determine text width and height
            fontMetrics = QFontMetricsF(font)
            (textWidth, textHeight) = (0.0, 0.0)
            for line in self._caption.split('\n'):
                textWidth = max(textWidth, fontMetrics.boundingRect(line).width())
                textHeight += fontMetrics.lineSpacing()
            textHeight -= fontMetrics.leading()

            return QRectF(-textWidth / 2, -textHeight / 2, textWidth, textHeight).translated(self._ellipse.center())
        return QRectF()
