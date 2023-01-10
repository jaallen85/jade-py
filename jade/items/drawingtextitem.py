# drawingtextitem.py
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
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingTextItem(DrawingItem):
    def __init__(self) -> None:
        super().__init__()

        self._caption: str = ''
        self._font: QFont = QFont()
        self._alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
        self._pen: QPen = QPen()

        self._textRect: QRectF = QRectF()

        self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.NoType))

    def __copy__(self) -> 'DrawingTextItem':
        copiedItem = DrawingTextItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setCaption(self.caption())
        copiedItem.setFont(self.font())
        copiedItem.setAlignment(self.alignment())
        copiedItem.setBrush(self.brush())
        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'text'

    def prettyName(self) -> str:
        return 'Text'

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

    def setBrush(self, brush: QBrush) -> None:
        self._pen.setBrush(brush)

    def font(self) -> QFont:
        return self._font

    def alignment(self) -> Qt.AlignmentFlag:
        return self._alignment

    def brush(self) -> QBrush:
        return self._pen.brush()

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
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
        elif (name == 'textAlignment' and isinstance(value, Qt.AlignmentFlag)):
            self.setAlignment(value)
        elif (name == 'textBrush' and isinstance(value, QBrush)):
            self.setBrush(value)
        elif (name == 'textColor' and isinstance(value, QColor)):
            self.setBrush(QBrush(QColor(value)))

    def property(self, name: str) -> typing.Any:
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
        if (name == 'textAlignment'):
            return self.alignment()
        if (name == 'textBrush'):
            return self.brush()
        if (name == 'textColor'):
            return self.brush().color()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        if (self._textRect.isNull()):
            self._textRect = self._calculateTextRect(self._font)
        return QRectF(self._textRect)

    def shape(self) -> QPainterPath:
        shape = QPainterPath()
        if (self._textRect.isNull()):
            self._textRect = self._calculateTextRect(self._font)
        shape.addRect(self._textRect)
        return shape

    def centerPosition(self) -> QPointF:
        return QPointF(0, 0)

    def isValid(self) -> bool:
        return (self._caption != '')

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        font = QFont(self._font)
        font.setPointSizeF(font.pointSizeF() * 96.0 / painter.paintEngine().paintDevice().logicalDpiX())

        self._textRect = self._calculateTextRect(font)

        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.setFont(font)
        painter.drawText(self._textRect, self._alignment, self._caption)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        self.setCaption('Label')

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        self._writeFont(element, 'font', self._font)
        self._writeAlignment(element, 'textAlignment', self._alignment)
        self._writeBrush(element, 'text', self._pen.brush())

        element.text = self._caption

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        self.setFont(self._readFont(element, 'font'))
        self.setAlignment(self._readAlignment(element, 'textAlignment'))
        self.setBrush(self._readBrush(element, 'text'))

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

            # Determine text left and top
            (textLeft, textTop) = (0.0, 0.0)
            if (self._alignment & Qt.AlignmentFlag.AlignHCenter):
                textLeft = -textWidth / 2
            elif (self._alignment & Qt.AlignmentFlag.AlignRight):
                textLeft = -textWidth
            if (self._alignment & Qt.AlignmentFlag.AlignVCenter):
                textTop = -textHeight / 2
            elif (self._alignment & Qt.AlignmentFlag.AlignBottom):
                textTop = -textHeight

            return QRectF(textLeft, textTop, textWidth, textHeight)
        return QRectF()
