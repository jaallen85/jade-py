# odgreader.py
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
import re
from zipfile import ZipFile
from PySide6.QtCore import Qt, QLineF, QMarginsF, QPointF, QRectF, QSizeF, QXmlStreamReader
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPolygonF, QTransform
from PySide6.QtWidgets import QApplication
from ..items.odgcurveitem import OdgCurve, OdgCurveItem
from ..items.odgellipseitem import OdgEllipseItem
from ..items.odgfontstyle import OdgFontStyle
from ..items.odggroupitem import OdgGroupItem
from ..items.odgitem import OdgItem
from ..items.odglineitem import OdgLineItem
from ..items.odgmarker import OdgMarker
from ..items.odgpolygonitem import OdgPolygonItem
from ..items.odgpolylineitem import OdgPolylineItem
from ..items.odgrectitem import OdgRectItem
from ..items.odgtextitem import OdgTextItem
from ..items.odgtextellipseitem import OdgTextEllipseItem
from ..items.odgtextrectitem import OdgTextRectItem
from .odgpage import OdgPage
from .odgunits import OdgUnits


class OdgReaderStyle:
    def __init__(self, name: str) -> None:
        self._name: str = name

        self._parent: OdgReaderStyle | None = None

        self._penStyle: Qt.PenStyle | None = None
        self._penWidth: float | None = None
        self._penColor: QColor | None = None
        self._penCapStyle: Qt.PenCapStyle | None = None
        self._penJoinStyle: Qt.PenJoinStyle | None = None
        self._brushColor: QColor | None = None

        self._startMarkerStyle: OdgMarker.Style | None = None
        self._startMarkerSize: float | None = None
        self._endMarkerStyle: OdgMarker.Style | None = None
        self._endMarkerSize: float | None = None

        self._fontFamily: str | None = None
        self._fontSize: float | None = None
        self._fontStyle: OdgFontStyle | None = None
        self._textAlignment: Qt.AlignmentFlag | None = None
        self._textPadding: QSizeF | None = None
        self._textColor: QColor | None = None

    # ==================================================================================================================

    def setName(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        return self._name

    # ==================================================================================================================

    def setParent(self, parent: 'OdgReaderStyle | None') -> None:
        self._parent = parent

    def parent(self) -> 'OdgReaderStyle | None':
        return self._parent

    # ==================================================================================================================

    def setPenStyle(self, style: Qt.PenStyle | None) -> None:
        self._penStyle = style

    def setPenWidth(self, width: float | None) -> None:
        self._penWidth = width

    def setPenColor(self, color: QColor | None) -> None:
        if (isinstance(color, QColor)):
            self._penColor = QColor(color)
        else:
            self._penColor = None

    def setPenCapStyle(self, style: Qt.PenCapStyle | None) -> None:
        self._penCapStyle = style

    def setPenJoinStyle(self, style: Qt.PenJoinStyle | None) -> None:
        self._penJoinStyle = style

    def setBrushColor(self, color: QColor | None) -> None:
        if (isinstance(color, QColor)):
            self._brushColor = QColor(color)
        else:
            self._brushColor = None

    def penStyle(self) -> Qt.PenStyle | None:
        return self._penStyle

    def penWidth(self) -> float | None:
        return self._penWidth

    def penColor(self) -> QColor | None:
        return self._penColor

    def penCapStyle(self) -> Qt.PenCapStyle | None:
        return self._penCapStyle

    def penJoinStyle(self) -> Qt.PenJoinStyle | None:
        return self._penJoinStyle

    def brushColor(self) -> QColor | None:
        return self._brushColor

    # ==================================================================================================================

    def setStartMarkerStyle(self, style: OdgMarker.Style | None) -> None:
        self._startMarkerStyle = style

    def setStartMarkerSize(self, size: float | None) -> None:
        self._startMarkerSize = size

    def setEndMarkerStyle(self, style: OdgMarker.Style | None) -> None:
        self._endMarkerStyle = style

    def setEndMarkerSize(self, size: float | None) -> None:
        self._endMarkerSize = size

    def startMarkerStyle(self) -> OdgMarker.Style | None:
        return self._startMarkerStyle

    def startMarkerSize(self) -> float | None:
        return self._startMarkerSize

    def endMarkerStyle(self) -> OdgMarker.Style | None:
        return self._endMarkerStyle

    def endMarkerSize(self) -> float | None:
        return self._endMarkerSize

    # ==================================================================================================================

    def setFontFamily(self, family: str | None) -> None:
        self._fontFamily = family

    def setFontSize(self, size: float | None) -> None:
        self._fontSize = size

    def setFontStyle(self, style: OdgFontStyle | None) -> None:
        if (isinstance(style, OdgFontStyle)):
            self._fontStyle = OdgFontStyle.copy(style)
        else:
            self._fontStyle = None

    def setTextAlignment(self, alignment: Qt.AlignmentFlag | None) -> None:
        self._textAlignment = alignment

    def setTextPadding(self, padding: QSizeF | None) -> None:
        if (isinstance(padding, QSizeF)):
            self._textPadding = QSizeF(padding)
        else:
            self._textPadding = None

    def setTextColor(self, color: QColor | None) -> None:
        if (isinstance(color, QColor)):
            self._textColor = QColor(color)
        else:
            self._textColor = None

    def fontFamily(self) -> str | None:
        return self._fontFamily

    def fontSize(self) -> float | None:
        return self._fontSize

    def fontStyle(self) -> OdgFontStyle | None:
        return self._fontStyle

    def textAlignment(self) -> Qt.AlignmentFlag | None:
        return self._textAlignment

    def textPadding(self) -> QSizeF | None:
        return self._textPadding

    def textColor(self) -> QColor | None:
        return self._textColor

    # ==================================================================================================================

    def lookupPen(self) -> QPen:
        return QPen(QBrush(self.lookupPenColor()), self.lookupPenWidth(), self.lookupPenStyle(),
                    self.lookupPenCapStyle(), self.lookupPenJoinStyle())

    def lookupPenStyle(self) -> Qt.PenStyle:
        if (isinstance(self._penStyle, Qt.PenStyle)):
            return self._penStyle
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupPenStyle()
        return Qt.PenStyle.NoPen

    def lookupPenColor(self) -> QColor:
        if (isinstance(self._penColor, QColor)):
            return self._penColor
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupPenColor()
        return QColor(0, 0, 0)

    def lookupPenWidth(self) -> float:
        if (isinstance(self._penWidth, float)):
            return self._penWidth
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupPenWidth()
        return 1.0

    def lookupPenCapStyle(self) -> Qt.PenCapStyle:
        if (isinstance(self._penCapStyle, Qt.PenCapStyle)):
            return self._penCapStyle
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupPenCapStyle()
        return Qt.PenCapStyle.RoundCap

    def lookupPenJoinStyle(self) -> Qt.PenJoinStyle:
        if (isinstance(self._penJoinStyle, Qt.PenJoinStyle)):
            return self._penJoinStyle
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupPenJoinStyle()
        return Qt.PenJoinStyle.RoundJoin

    # ==================================================================================================================

    def lookupBrush(self) -> QBrush:
        return QBrush(self.lookupBrushColor())

    def lookupBrushColor(self) -> QColor:
        if (isinstance(self._brushColor, QColor)):
            return self._brushColor
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupBrushColor()
        return QColor(255, 255, 255)

    # ==================================================================================================================

    def lookupStartMarker(self) -> OdgMarker:
        return OdgMarker(self.lookupStartMarkerStyle(), self.lookupStartMarkerSize())

    def lookupEndMarker(self) -> OdgMarker:
        return OdgMarker(self.lookupEndMarkerStyle(), self.lookupEndMarkerSize())

    def lookupStartMarkerStyle(self) -> OdgMarker.Style:
        if (isinstance(self._startMarkerStyle, OdgMarker.Style)):
            return self._startMarkerStyle
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupStartMarkerStyle()
        return OdgMarker.Style.NoMarker

    def lookupStartMarkerSize(self) -> float:
        if (isinstance(self._startMarkerSize, float)):
            return self._startMarkerSize
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupStartMarkerSize()
        return 0.0

    def lookupEndMarkerStyle(self) -> OdgMarker.Style:
        if (isinstance(self._endMarkerStyle, OdgMarker.Style)):
            return self._endMarkerStyle
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupEndMarkerStyle()
        return OdgMarker.Style.NoMarker

    def lookupEndMarkerSize(self) -> float:
        if (isinstance(self._endMarkerSize, float)):
            return self._endMarkerSize
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupEndMarkerSize()
        return 0.0

    # ==================================================================================================================

    def lookupFont(self) -> QFont:
        font = QFont(self.lookupFontFamily())
        font.setPointSizeF(self.lookupFontSize())

        style = self.lookupFontStyle()
        font.setBold(style.bold())
        font.setItalic(style.italic())
        font.setUnderline(style.underline())
        font.setStrikeOut(style.strikeOut())

        return font

    def lookupFontFamily(self) -> str:
        if (isinstance(self._fontFamily, str)):
            return self._fontFamily
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupFontFamily()
        return ''

    def lookupFontSize(self) -> float:
        if (isinstance(self._fontSize, float)):
            return self._fontSize
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupFontSize()
        return 0.0

    def lookupFontStyle(self) -> 'OdgFontStyle':
        if (isinstance(self._fontStyle, OdgFontStyle)):
            return self._fontStyle
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupFontStyle()
        return OdgFontStyle()

    def lookupTextAlignment(self) -> Qt.AlignmentFlag:
        if (isinstance(self._textAlignment, Qt.AlignmentFlag)):
            return self._textAlignment
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupTextAlignment()
        return (Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

    def lookupTextPadding(self) -> QSizeF:
        if (isinstance(self._textPadding, QSizeF)):
            return self._textPadding
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupTextPadding()
        return QSizeF(0, 0)

    def lookupTextBrush(self) -> QBrush:
        return QBrush(self.lookupTextColor())

    def lookupTextColor(self) -> QColor:
        if (isinstance(self._textColor, QColor)):
            return self._textColor
        if (isinstance(self._parent, OdgReaderStyle)):
            return self._parent.lookupTextColor()
        return QColor(0, 0, 0)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgReader:
    def __init__(self) -> None:
        self._units: OdgUnits = OdgUnits.Inches
        self._pageSize: QSizeF = QSizeF(8.2, 6.2)
        self._pageMargins: QMarginsF = QMarginsF(0.1, 0.1, 0.1, 0.1)
        self._backgroundColor: QColor = QColor(255, 255, 255)

        self._grid: float = 0.05
        self._gridVisible: bool = True
        self._gridColor: QColor = QColor(0, 128, 128)
        self._gridSpacingMajor: int = 8
        self._gridSpacingMinor: int = 2

        self._pages: list[OdgPage] = []

        self._defaultItemStyle: OdgReaderStyle = OdgReaderStyle('standard')
        self._itemStyles: list[OdgReaderStyle] = []
        self._automaticItemStyles: list[OdgReaderStyle] = []

    def __del__(self) -> None:
        del self._pages[:]
        del self._defaultItemStyle
        del self._itemStyles[:]
        del self._automaticItemStyles[:]

    # ==================================================================================================================

    def units(self) -> OdgUnits:
        return self._units

    def pageSize(self) -> QSizeF:
        return self._pageSize

    def pageMargins(self) -> QMarginsF:
        return self._pageMargins

    def backgroundColor(self) -> QColor:
        return self._backgroundColor

    # ==================================================================================================================

    def grid(self) -> float:
        return self._grid

    def isGridVisible(self) -> bool:
        return self._gridVisible

    def gridColor(self) -> QColor:
        return self._gridColor

    def gridSpacingMajor(self) -> int:
        return self._gridSpacingMajor

    def gridSpacingMinor(self) -> int:
        return self._gridSpacingMinor

    # ==================================================================================================================

    def defaultItemBrush(self) -> QBrush:
        return self._defaultItemStyle.lookupBrush()

    def defaultItemPen(self) -> QPen:
        return self._defaultItemStyle.lookupPen()

    def defaultItemStartMarker(self) -> OdgMarker:
        return self._defaultItemStyle.lookupStartMarker()

    def defaultItemEndMarker(self) -> OdgMarker:
        return self._defaultItemStyle.lookupEndMarker()

    def defaultItemFont(self) -> QFont:
        return self._defaultItemStyle.lookupFont()

    def defaultItemTextAlignment(self) -> Qt.AlignmentFlag:
        return self._defaultItemStyle.lookupTextAlignment()

    def defaultItemTextPadding(self) -> QSizeF:
        return self._defaultItemStyle.lookupTextPadding()

    def defaultItemTextBrush(self) -> QBrush:
        return self._defaultItemStyle.lookupTextBrush()

    # ==================================================================================================================

    def pages(self) -> list[OdgPage]:
        return self._pages

    def takePages(self) -> list[OdgPage]:
        pages = self._pages.copy()
        self._pages = []
        return pages

    # ==================================================================================================================

    def readFromFile(self, path: str) -> None:
        with ZipFile(path, 'r') as odgFile:
            with odgFile.open('settings.xml', 'r') as settingsFile:
                self._readSettings(settingsFile.read().decode('utf-8'))
            with odgFile.open('styles.xml', 'r') as stylesFile:
                self._readStyles(stylesFile.read().decode('utf-8'))
            with odgFile.open('content.xml', 'r') as contentFile:
                self._readContent(contentFile.read().decode('utf-8'))

    def readFromClipboard(self) -> list[OdgItem]:
        items: list[OdgItem] = []

        xml = QXmlStreamReader(QApplication.clipboard().text())
        if (xml.readNextStartElement() and xml.qualifiedName() == 'jade-items'):
            attributes = xml.attributes()
            for index in range(attributes.count()):
                attr = attributes.at(index)
                match (attr.name()):
                    case 'units':
                        self._units = OdgUnits.fromStr(attr.value())
                    case 'page-width':
                        self._pageSize.setWidth(self._lengthFromString(attr.value()))
                    case 'page-height':
                        self._pageSize.setHeight(self._lengthFromString(attr.value()))
                    case 'margin-left':
                        self._pageMargins.setLeft(self._lengthFromString(attr.value()))
                    case 'margin-top':
                        self._pageMargins.setTop(self._lengthFromString(attr.value()))
                    case 'margin-right':
                        self._pageMargins.setRight(self._lengthFromString(attr.value()))
                    case 'margin-bottom':
                        self._pageMargins.setBottom(self._lengthFromString(attr.value()))

            while (xml.readNextStartElement()):
                if (xml.qualifiedName() == 'styles'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() in ('style:default-style', 'style:style')):
                            self._readStyle(xml, automatic=False)
                        else:
                            xml.skipCurrentElement()
                elif (xml.qualifiedName() == 'automatic-styles'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() == 'style:style'):
                            self._readStyle(xml, automatic=True)
                        else:
                            xml.skipCurrentElement()
                elif (xml.qualifiedName() == 'items'):
                    items.extend(self._readItems(xml))
                else:
                    xml.skipCurrentElement()

        return items

    # ==================================================================================================================

    def _readSettings(self, settings: str) -> None:
        xml = QXmlStreamReader(settings)

        if (xml.readNextStartElement() and xml.qualifiedName() == 'office:document-settings'):
            while (xml.readNextStartElement()):
                if (xml.qualifiedName() == 'office:settings'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() == 'config:config-item-set'):
                            attr = xml.attributes()
                            if (attr.hasAttribute('config:name') and attr.value('config:name') == 'jade:settings'):
                                while (xml.readNextStartElement()):
                                    if (xml.qualifiedName() == 'config:config-item'):
                                        self._readConfigItem(xml)
                                    else:
                                        xml.skipCurrentElement()
                        else:
                            xml.skipCurrentElement()
                else:
                    xml.skipCurrentElement()
        else:
            xml.skipCurrentElement()

    def _readStyles(self, styles: str) -> None:
        xml = QXmlStreamReader(styles)

        if (xml.readNextStartElement() and xml.qualifiedName() == 'office:document-styles'):
            while (xml.readNextStartElement()):
                if (xml.qualifiedName() == 'office:styles'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() in ('style:default-style', 'style:style')):
                            self._readStyle(xml, automatic=False)
                        else:
                            xml.skipCurrentElement()
                elif (xml.qualifiedName() == 'office:automatic-styles'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() == 'style:page-layout'):
                            self._readPageLayout(xml)
                        elif (xml.qualifiedName() == 'style:style'):
                            self._readPageStyle(xml)
                        else:
                            xml.skipCurrentElement()
                else:
                    xml.skipCurrentElement()
        else:
            xml.skipCurrentElement()

    def _readContent(self, content: str) -> None:
        xml = QXmlStreamReader(content)

        if (xml.readNextStartElement() and xml.qualifiedName() == 'office:document-content'):
            while (xml.readNextStartElement()):
                if (xml.qualifiedName() == 'office:automatic-styles'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() == 'style:style'):
                            self._readStyle(xml, automatic=True)
                        else:
                            xml.skipCurrentElement()
                elif (xml.qualifiedName() == 'office:body'):
                    while (xml.readNextStartElement()):
                        if (xml.qualifiedName() == 'office:drawing'):
                            while (xml.readNextStartElement()):
                                if (xml.qualifiedName() == 'draw:page'):
                                    self._readPage(xml)
                                else:
                                    xml.skipCurrentElement()
                        else:
                            xml.skipCurrentElement()
                else:
                    xml.skipCurrentElement()
        else:
            xml.skipCurrentElement()

    # ==================================================================================================================

    def _readConfigItem(self, xml: QXmlStreamReader) -> None:
        attributes = xml.attributes()
        text = xml.readElementText()
        if (attributes.hasAttribute('config:name') and attributes.hasAttribute('config:type')):
            name = attributes.value('config:name')
            typeStr = attributes.value('config:type')
            if (name == 'units' and typeStr == 'string'):
                self._units = OdgUnits.fromStr(text)
            elif (name == 'grid' and typeStr == 'double'):
                self._grid = float(text)
            elif (name == 'gridVisible' and typeStr == 'boolean'):
                self._gridVisible = (text.strip().lower() == 'true')
            elif (name == 'gridColor' and typeStr == 'string'):
                self._gridColor = self._colorFromString(text)
            elif (name == 'gridSpacingMajor' and typeStr == 'int'):
                self._gridSpacingMajor = int(text)
            elif (name == 'gridSpacingMinor' and typeStr == 'int'):
                self._gridSpacingMinor = int(text)

    def _readPageLayout(self, xml: QXmlStreamReader) -> None:
        # ASSUMPTION: Each ODG document contains one and only one style:page-layout element.
        while (xml.readNextStartElement()):
            if (xml.qualifiedName() == 'style:page-layout-properties'):
                attributes = xml.attributes()
                for index in range(attributes.count()):
                    attr = attributes.at(index)
                    match (attr.qualifiedName()):
                        case 'fo:page-width':
                            self._pageSize.setWidth(self._lengthFromString(attr.value()))
                        case 'fo:page-height':
                            self._pageSize.setHeight(self._lengthFromString(attr.value()))
                        case 'fo:margin-left':
                            self._pageMargins.setLeft(self._lengthFromString(attr.value()))
                        case 'fo:margin-top':
                            self._pageMargins.setTop(self._lengthFromString(attr.value()))
                        case 'fo:margin-right':
                            self._pageMargins.setRight(self._lengthFromString(attr.value()))
                        case 'fo:margin-bottom':
                            self._pageMargins.setBottom(self._lengthFromString(attr.value()))
            xml.skipCurrentElement()

    def _readPageStyle(self, xml: QXmlStreamReader) -> None:
        # ASSUMPTION: Each ODG document contains one and only one style:style element with style:family attribute set
        # to 'drawing-page'.
        while (xml.readNextStartElement()):
            if (xml.qualifiedName() == 'style:drawing-page-properties'):
                attributes = xml.attributes()
                for index in range(attributes.count()):
                    attr = attributes.at(index)
                    match (attr.qualifiedName()):
                        case 'draw:fill':
                            if (attr.value() == 'none'):
                                self._backgroundColor.setAlpha(0)
                        case 'draw:fill-color':
                            color = self._colorFromString(attr.value())
                            self._backgroundColor.setRed(color.red())
                            self._backgroundColor.setGreen(color.green())
                            self._backgroundColor.setBlue(color.blue())
                        case 'draw:opacity':
                            self._backgroundColor.setAlphaF(self._percentFromString(attr.value()))
            xml.skipCurrentElement()

    def _readStyle(self, xml: QXmlStreamReader, automatic: bool) -> None:
        if (xml.qualifiedName() == 'style:default-style'):
            self._defaultItemStyle = self._readItemStyle(xml, self._defaultItemStyle)
        elif (xml.qualifiedName() == 'style:style'):
            attributes = xml.attributes()
            if (attributes.hasAttribute('style:name') and attributes.value('style:name') == 'standard'):
                self._defaultItemStyle = self._readItemStyle(xml, self._defaultItemStyle)
            else:
                newStyle = self._readItemStyle(xml, OdgReaderStyle(attributes.value('style:name')))
                if (automatic):
                    self._automaticItemStyles.append(newStyle)
                else:
                    self._itemStyles.append(newStyle)
        else:
            xml.skipCurrentElement()

    def _readPage(self, xml: QXmlStreamReader) -> None:
        page = OdgPage(f'Page {len(self._pages) + 1}')

        attributes = xml.attributes()
        if (attributes.hasAttribute('draw:name')):
            page.setName(attributes.value('draw:name'))

        for item in self._readItems(xml):
            page.addItem(item)

        self._pages.append(page)

    # ==================================================================================================================

    def _readItemStyle(self, xml: QXmlStreamReader, newStyle: OdgReaderStyle) -> OdgReaderStyle:
        if (newStyle != self._defaultItemStyle):
            newStyle.setParent(self._defaultItemStyle)

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'style:name':
                    newStyle.setName(attr.value())
                case 'style:parent-name':
                    parentStyleName = attr.value()
                    for style in self._itemStyles:
                        if (style.name() == parentStyleName):
                            newStyle.setParent(style)
                            break

        while (xml.readNextStartElement()):
            if (xml.qualifiedName() == 'style:graphic-properties'):
                attributes = xml.attributes()
                for i in range(attributes.count()):
                    attr = attributes.at(i)
                    match (attr.qualifiedName()):
                        # Pen style
                        case 'draw:stroke':
                            match (attr.value()):
                                case 'solid':
                                    newStyle.setPenStyle(Qt.PenStyle.SolidLine)
                                case 'none':
                                    newStyle.setPenStyle(Qt.PenStyle.NoPen)
                        case 'draw:stroke-dash':
                            match (attr.value()):
                                case 'Dash_20__28_Rounded_29_':
                                    newStyle.setPenStyle(Qt.PenStyle.DashLine)
                                case 'Dot_20__28_Rounded_29_':
                                    newStyle.setPenStyle(Qt.PenStyle.DotLine)
                                case 'Dash_20_Dot_20__28_Rounded_29_':
                                    newStyle.setPenStyle(Qt.PenStyle.DashDotLine)
                                case 'Dash_20_Dot_20_Dot_20__28_Rounded_29_':
                                    newStyle.setPenStyle(Qt.PenStyle.DashDotDotLine)

                        # Pen width
                        case 'svg:stroke-width':
                            newStyle.setPenWidth(self._lengthFromString(attr.value()))

                        # Pen color
                        case 'svg:stroke-color':
                            newStyle.setPenColor(QColor(attr.value()))
                        case 'svg:stroke-opacity':
                            penColor = newStyle.penColor()
                            if (isinstance(penColor, QColor)):
                                penColor.setAlphaF(self._percentFromString(attr.value()))
                                newStyle.setPenColor(penColor)

                        # Pen cap style
                        case 'svg:stroke-linecap':
                            match (attr.value()):
                                case 'butt':
                                    newStyle.setPenCapStyle(Qt.PenCapStyle.FlatCap)
                                case 'square':
                                    newStyle.setPenCapStyle(Qt.PenCapStyle.SquareCap)
                                case 'round':
                                    newStyle.setPenCapStyle(Qt.PenCapStyle.RoundCap)

                        # Pen join style
                        case 'draw:stroke-linejoin':
                            match (attr.value()):
                                case 'miter':
                                    newStyle.setPenJoinStyle(Qt.PenJoinStyle.MiterJoin)
                                case 'bevel':
                                    newStyle.setPenJoinStyle(Qt.PenJoinStyle.BevelJoin)
                                case 'round':
                                    newStyle.setPenJoinStyle(Qt.PenJoinStyle.RoundJoin)

                        # Brush color
                        case 'draw:fill':
                            match (attr.value()):
                                case 'solid':
                                    newStyle.setBrushColor(QColor(0, 0, 0))
                                case 'none':
                                    newStyle.setBrushColor(QColor(0, 0, 0, 0))
                        case 'draw:fill-color':
                            newStyle.setBrushColor(QColor(attr.value()))
                        case 'draw:opacity':
                            brushColor = newStyle.brushColor()
                            if (isinstance(brushColor, QColor)):
                                brushColor.setAlphaF(self._percentFromString(attr.value()))
                                newStyle.setBrushColor(brushColor)

                        # Start marker style
                        case 'draw:marker-start':
                            match (attr.value()):
                                case 'Triangle':
                                    newStyle.setStartMarkerStyle(OdgMarker.Style.Triangle)
                                case 'Circle':
                                    newStyle.setStartMarkerStyle(OdgMarker.Style.Circle)

                        # Start marker size
                        case 'draw:marker-start-width':
                            newStyle.setStartMarkerSize(self._lengthFromString(attr.value()))

                        # End marker style
                        case 'draw:marker-end':
                            match (attr.value()):
                                case 'Triangle':
                                    newStyle.setEndMarkerStyle(OdgMarker.Style.Triangle)
                                case 'Circle':
                                    newStyle.setEndMarkerStyle(OdgMarker.Style.Circle)

                        # End marker size
                        case 'draw:marker-end-width':
                            newStyle.setEndMarkerSize(self._lengthFromString(attr.value()))

                        # Text alignment
                        case 'draw:textarea-horizontal-align':
                            alignment = newStyle.textAlignment()
                            if (isinstance(alignment, Qt.AlignmentFlag)):
                                alignment = (alignment & (~Qt.AlignmentFlag.AlignHorizontal_Mask))
                            else:
                                alignment = Qt.AlignmentFlag(0)
                            match (attr.value()):
                                case 'left':
                                    alignment = (alignment | Qt.AlignmentFlag.AlignLeft)
                                case 'right':
                                    alignment = (alignment | Qt.AlignmentFlag.AlignRight)
                                case _:
                                    alignment = (alignment | Qt.AlignmentFlag.AlignHCenter)
                            newStyle.setTextAlignment(alignment)

                        case 'draw:textarea-vertical-align':
                            alignment = newStyle.textAlignment()
                            if (isinstance(alignment, Qt.AlignmentFlag)):
                                alignment = (alignment & (~Qt.AlignmentFlag.AlignVertical_Mask))
                            else:
                                alignment = Qt.AlignmentFlag(0)
                            match (attr.value()):
                                case 'top':
                                    alignment = (alignment | Qt.AlignmentFlag.AlignTop)
                                case 'bottom':
                                    alignment = (alignment | Qt.AlignmentFlag.AlignBottom)
                                case _:
                                    alignment = (alignment | Qt.AlignmentFlag.AlignVCenter)
                            newStyle.setTextAlignment(alignment)

                        # Text padding
                        case 'fo:padding-left':
                            padding = newStyle.textPadding()
                            if (isinstance(padding, QSizeF)):
                                padding.setWidth(0)
                            else:
                                padding = QSizeF()
                            padding.setWidth(self._lengthFromString(attr.value()))
                            newStyle.setTextPadding(padding)

                        case 'fo:padding-top':
                            padding = newStyle.textPadding()
                            if (isinstance(padding, QSizeF)):
                                padding.setHeight(0)
                            else:
                                padding = QSizeF()
                            padding.setHeight(self._lengthFromString(attr.value()))
                            newStyle.setTextPadding(padding)

            elif (xml.qualifiedName() == 'style:text-properties'):
                attributes = xml.attributes()
                for i in range(attributes.count()):
                    attr = attributes.at(i)
                    match (attr.qualifiedName()):
                        # Font family
                        case 'style:font-name':
                            newStyle.setFontFamily(attr.value())

                        # Font size
                        case 'fo:font-size':
                            newStyle.setFontSize(self._lengthFromString(attr.value()))

                        # Font style
                        case 'fo:font-weight':
                            fontStyle = newStyle.fontStyle()
                            if (isinstance(fontStyle, OdgFontStyle)):
                                fontStyle.setBold(attr.value() == 'bold')
                            else:
                                fontStyle = OdgFontStyle(attr.value() == 'bold', False, False, False)
                            newStyle.setFontStyle(fontStyle)

                        case 'fo:font-style':
                            fontStyle = newStyle.fontStyle()
                            if (isinstance(fontStyle, OdgFontStyle)):
                                fontStyle.setItalic(attr.value() == 'italic')
                            else:
                                fontStyle = OdgFontStyle(False, attr.value() == 'italic', False, False)
                            newStyle.setFontStyle(fontStyle)

                        case 'style:text-underline-style':
                            fontStyle = newStyle.fontStyle()
                            if (isinstance(fontStyle, OdgFontStyle)):
                                fontStyle.setUnderline(attr.value() == 'solid')
                            else:
                                fontStyle = OdgFontStyle(False, False, attr.value() == 'solid', False)
                            newStyle.setFontStyle(fontStyle)

                        case 'style:text-line-through-style':
                            fontStyle = newStyle.fontStyle()
                            if (isinstance(fontStyle, OdgFontStyle)):
                                fontStyle.setStrikeOut(attr.value() == 'solid')
                            else:
                                fontStyle = OdgFontStyle(False, False, False, attr.value() == 'solid')
                            newStyle.setFontStyle(fontStyle)

                        # Text color
                        case 'fo:color':
                            newStyle.setTextColor(QColor(attr.value()))
                        case 'loext:opacity':
                            textColor = newStyle.textColor()
                            if (isinstance(textColor, QColor)):
                                textColor.setAlphaF(self._percentFromString(attr.value()))
                                newStyle.setTextColor(textColor)

            xml.skipCurrentElement()

        return newStyle

    # ==================================================================================================================

    def _readItems(self, xml: QXmlStreamReader) -> list[OdgItem]:
        items: list[OdgItem] = []

        while (xml.readNextStartElement()):
            item = None
            if (xml.qualifiedName() == 'draw:line'):
                item = self._readLineItem(xml)
            elif (xml.qualifiedName() == 'draw:rect'):
                item = self._readRectItem(xml)
            elif (xml.qualifiedName() == 'draw:ellipse'):
                item = self._readEllipseItem(xml)
            elif (xml.qualifiedName() == 'draw:polyline'):
                item = self._readPolylineItem(xml)
            elif (xml.qualifiedName() == 'draw:polygon'):
                item = self._readPolygonItem(xml)
            elif (xml.qualifiedName() == 'draw:path'):
                item = self._readPathItem(xml)
            elif (xml.qualifiedName() == 'draw:g'):
                item = self._readGroupItem(xml)
            else:
                xml.skipCurrentElement()

            if (isinstance(item, OdgItem)):
                items.append(item)

        return items

    def _readLineItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read line attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        x1, y1, x2, y2 = (0.0, 0.0, 0.0, 0.0)

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:style-name':
                    styleName = attr.value()
                case 'draw:transform':
                    position, rotation, flipped = self._transformFromString(attr.value())
                case 'svg:x1':
                    x1 = self._lengthFromString(attr.value())
                case 'svg:y1':
                    y1 = self._lengthFromString(attr.value())
                case 'svg:x2':
                    x2 = self._lengthFromString(attr.value())
                case 'svg:y2':
                    y2 = self._lengthFromString(attr.value())

        xml.skipCurrentElement()

        # Create line item and return it if valid
        lineItem = OdgLineItem()
        lineItem.setPosition(position)
        lineItem.setRotation(rotation)
        lineItem.setFlipped(flipped)
        lineItem.setLine(QLineF(x1, y1, x2, y2))

        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgReaderStyle)):
            lineItem.setPen(style.lookupPen())
            lineItem.setStartMarker(style.lookupStartMarker())
            lineItem.setEndMarker(style.lookupEndMarker())

        if (lineItem.isValid()):
            return lineItem
        del lineItem
        return None

    def _readRectItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read rect attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        left, top, width, height = (0.0, 0.0, 0.0, 0.0)
        cornerRadius = 0.0
        isText = False
        isTextRect = False

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:style-name':
                    styleName = attr.value()
                case 'draw:transform':
                    position, rotation, flipped = self._transformFromString(attr.value())
                case 'svg:x':
                    left = self._lengthFromString(attr.value())
                case 'svg:y':
                    top = self._lengthFromString(attr.value())
                case 'svg:width':
                    width = self._lengthFromString(attr.value())
                case 'svg:height':
                    height = self._lengthFromString(attr.value())
                case 'draw:corner-radius':
                    cornerRadius = self._lengthFromString(attr.value())
                case 'jade:text-item-hint':
                    isText = (attr.value() == 'text')
                    isTextRect = (attr.value() == 'text-rect')

        caption = ''
        while (xml.readNextStartElement()):
            if (xml.qualifiedName() == 'text:p'):
                while (xml.readNextStartElement()):
                    if (xml.qualifiedName() == 'text:span'):
                        if (caption == ''):
                            caption = f'{xml.readElementText()}'
                        else:
                            caption = f'{caption}\n{xml.readElementText()}'
        isTextRect = (isTextRect or caption != '')

        if (isText):
            # Create text item and return it if valid
            textItem = OdgTextItem()
            textItem.setPosition(position)
            textItem.setRotation(rotation)
            textItem.setFlipped(flipped)
            textItem.setCaption(caption)

            style = self._findAutomaticStyle(styleName)
            if (isinstance(style, OdgReaderStyle)):
                textItem.setFont(style.lookupFont())
                textItem.setAlignment(style.lookupTextAlignment())
                textItem.setPadding(style.lookupTextPadding())
                textItem.setBrush(style.lookupTextBrush())

            if (textItem.isValid()):
                return textItem
            del textItem
            return None

        if (isTextRect):
            # Create text rect item and return it if valid
            textRectItem = OdgTextRectItem()
            textRectItem.setPosition(position)
            textRectItem.setRotation(rotation)
            textRectItem.setFlipped(flipped)
            textRectItem.setRect(QRectF(left, top, width, height))
            textRectItem.setCornerRadius(cornerRadius)
            textRectItem.setCaption(caption)

            style = self._findAutomaticStyle(styleName)
            if (isinstance(style, OdgReaderStyle)):
                textRectItem.setBrush(style.lookupBrush())
                textRectItem.setPen(style.lookupPen())
                textRectItem.setFont(style.lookupFont())
                textRectItem.setTextAlignment(style.lookupTextAlignment())
                textRectItem.setTextPadding(style.lookupTextPadding())
                textRectItem.setTextBrush(style.lookupTextBrush())

            if (textRectItem.isValid()):
                return textRectItem
            del textRectItem
            return None

        # Create rect item and return it if valid
        rectItem = OdgRectItem()
        rectItem.setPosition(position)
        rectItem.setRotation(rotation)
        rectItem.setFlipped(flipped)
        rectItem.setRect(QRectF(left, top, width, height))
        rectItem.setCornerRadius(cornerRadius)

        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgReaderStyle)):
            rectItem.setBrush(style.lookupBrush())
            rectItem.setPen(style.lookupPen())

        if (rectItem.isValid()):
            return rectItem
        del rectItem
        return None

    def _readEllipseItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read ellipse attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        left, top, width, height = (0.0, 0.0, 0.0, 0.0)
        isTextEllipse = False

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:style-name':
                    styleName = attr.value()
                case 'draw:transform':
                    position, rotation, flipped = self._transformFromString(attr.value())
                case 'svg:x':
                    left = self._lengthFromString(attr.value())
                case 'svg:y':
                    top = self._lengthFromString(attr.value())
                case 'svg:width':
                    width = self._lengthFromString(attr.value())
                case 'svg:height':
                    height = self._lengthFromString(attr.value())
                case 'jade:text-item-hint':
                    isTextEllipse = (attr.value() == 'text-ellipse')

        caption = ''
        while (xml.readNextStartElement()):
            if (xml.qualifiedName() == 'text:p'):
                while (xml.readNextStartElement()):
                    if (xml.qualifiedName() == 'text:span'):
                        if (caption == ''):
                            caption = f'{xml.readElementText()}'
                        else:
                            caption = f'{caption}\n{xml.readElementText()}'
        isTextEllipse = (isTextEllipse or caption != '')

        if (isTextEllipse):
            # Create text ellipse item and return it if valid
            textEllipseItem = OdgTextEllipseItem()
            textEllipseItem.setPosition(position)
            textEllipseItem.setRotation(rotation)
            textEllipseItem.setFlipped(flipped)
            textEllipseItem.setRect(QRectF(left, top, width, height))
            textEllipseItem.setCaption(caption)

            style = self._findAutomaticStyle(styleName)
            if (isinstance(style, OdgReaderStyle)):
                textEllipseItem.setBrush(style.lookupBrush())
                textEllipseItem.setPen(style.lookupPen())
                textEllipseItem.setFont(style.lookupFont())
                textEllipseItem.setTextAlignment(style.lookupTextAlignment())
                textEllipseItem.setTextPadding(style.lookupTextPadding())
                textEllipseItem.setTextBrush(style.lookupTextBrush())

            if (textEllipseItem.isValid()):
                return textEllipseItem
            del textEllipseItem
            return None

        # Create ellipse item and return it if valid
        ellipseItem = OdgEllipseItem()
        ellipseItem.setPosition(position)
        ellipseItem.setRotation(rotation)
        ellipseItem.setFlipped(flipped)
        ellipseItem.setRect(QRectF(left, top, width, height))

        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgReaderStyle)):
            ellipseItem.setBrush(style.lookupBrush())
            ellipseItem.setPen(style.lookupPen())

        if (ellipseItem.isValid()):
            return ellipseItem
        del ellipseItem
        return None

    def _readPolylineItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read polyline attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        points = QPolygonF()

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:style-name':
                    styleName = attr.value()
                case 'draw:transform':
                    position, rotation, flipped = self._transformFromString(attr.value())
                case 'draw:points':
                    points = self._pointsFromString(attr.value())

        xml.skipCurrentElement()

        # Create polyline item and return it if valid
        polylineItem = OdgPolylineItem()
        polylineItem.setPosition(position)
        polylineItem.setRotation(rotation)
        polylineItem.setFlipped(flipped)
        polylineItem.setPolyline(points)

        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgReaderStyle)):
            polylineItem.setPen(style.lookupPen())
            polylineItem.setStartMarker(style.lookupStartMarker())
            polylineItem.setEndMarker(style.lookupEndMarker())

        if (polylineItem.isValid()):
            return polylineItem
        del polylineItem
        return None

    def _readPolygonItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read polygon attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        points = QPolygonF()

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:style-name':
                    styleName = attr.value()
                case 'draw:transform':
                    position, rotation, flipped = self._transformFromString(attr.value())
                case 'draw:points':
                    points = self._pointsFromString(attr.value())

        xml.skipCurrentElement()

        # Create polygon item and return it if valid
        polygonItem = OdgPolygonItem()
        polygonItem.setPosition(position)
        polygonItem.setRotation(rotation)
        polygonItem.setFlipped(flipped)
        polygonItem.setPolygon(points)

        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgReaderStyle)):
            polygonItem.setBrush(style.lookupBrush())
            polygonItem.setPen(style.lookupPen())

        if (polygonItem.isValid()):
            return polygonItem
        del polygonItem
        return None

    def _readPathItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read path attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        path = QPainterPath()
        left, top, width, height = (0.0, 0.0, 0.0, 0.0)
        viewBox = QRectF()

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:style-name':
                    styleName = attr.value()
                case 'draw:transform':
                    position, rotation, flipped = self._transformFromString(attr.value())
                case 'svg:d':
                    path = self._pathFromString(attr.value())
                case 'svg:x':
                    left = self._lengthFromString(attr.value())
                case 'svg:y':
                    top = self._lengthFromString(attr.value())
                case 'svg:width':
                    width = self._lengthFromString(attr.value())
                case 'svg:height':
                    height = self._lengthFromString(attr.value())
                case 'svg:viewBox':
                    viewBox = self._viewBoxFromString(attr.value())

        xml.skipCurrentElement()

        # Map the path from view box coordinates to item coordinates
        if (viewBox.width() != 0 and viewBox.height() != 0):
            transform = QTransform()
            transform.translate(-viewBox.left(), -viewBox.top())
            transform.scale(width / viewBox.width(), height / viewBox.height())
            transform.translate(left, top)
            path = transform.map(path)

        if (path.elementCount() == 4 and path.elementAt(0).isMoveTo() and path.elementAt(1).isCurveTo()):
            # Create path item and return it if valid
            curve = OdgCurve()
            curve.setP1(QPointF(path.elementAt(0).x, path.elementAt(0).y))      # type:ignore
            curve.setCP1(QPointF(path.elementAt(1).x, path.elementAt(1).y))     # type:ignore
            curve.setCP2(QPointF(path.elementAt(2).x, path.elementAt(2).y))     # type:ignore
            curve.setP2(QPointF(path.elementAt(3).x, path.elementAt(3).y))      # type:ignore

            curveItem = OdgCurveItem()
            curveItem.setPosition(position)
            curveItem.setRotation(rotation)
            curveItem.setFlipped(flipped)
            curveItem.setCurve(curve)

            style = self._findAutomaticStyle(styleName)
            if (isinstance(style, OdgReaderStyle)):
                curveItem.setPen(style.lookupPen())
                curveItem.setStartMarker(style.lookupStartMarker())
                curveItem.setEndMarker(style.lookupEndMarker())

            if (curveItem.isValid()):
                return curveItem
            del curveItem
            return None

        return None

    def _readGroupItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read group items from XML
        items = self._readItems(xml)

        # Create group item and return it if valid
        groupItem = OdgGroupItem()

        if (len(items) > 0):
            # Put the group position equal to the position of the last item and adjust each item's position
            # accordingly
            groupItem.setPosition(items[-1].position())
            for item in items:
                item.setPosition(groupItem.mapFromScene(item.position()))

        groupItem.setItems(items)

        if (groupItem.isValid()):
            return groupItem

        del groupItem
        return None

    def _findAutomaticStyle(self, name: str) -> OdgReaderStyle | None:
        for style in self._automaticItemStyles:
            if (style.name() == name):
                return style
        return None

    # ==================================================================================================================

    def _lengthFromString(self, text: str) -> float:
        text = text.strip()
        pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
        match = re.match(pattern, text, re.VERBOSE)
        if (match is not None):
            try:
                length = float(match.group(0))
                unitsStr = text[match.end():].strip()
                if (unitsStr == ''):
                    # Assume the value provided is in the same units as self._units
                    return length
                # Try to convert the provided value to the same units as self._units; fail if unrecognized units
                # are provided
                units = OdgUnits.fromStr(unitsStr)
                return OdgUnits.convert(length, units, self._units)
            except ValueError:
                pass
        return 0

    def _xCoordinateFromString(self, text: str) -> float:
        return self._lengthFromString(text) - self._pageMargins.left()

    def _yCoordinateFromString(self, text: str) -> float:
        return self._lengthFromString(text) - self._pageMargins.top()

    def _percentFromString(self, text: str) -> float:
        text = text.strip()
        try:
            if (text.endswith('%')):
                return float(text[:-1]) / 100.0
            return float(text)
        except ValueError:
            pass
        return 0

    def _transformFromString(self, text: str) -> tuple[QPointF, int, bool]:
        position = QPointF(0, 0)
        rotation = 0
        flipped = False
        try:
            for token in text.split(')'):
                strippedToken = token.strip()
                if (strippedToken.startswith('translate(')):
                    coords = strippedToken[10:].split(',')
                    position.setX(position.x() + self._xCoordinateFromString(coords[0]))
                    position.setY(position.y() + self._yCoordinateFromString(coords[1]))
                elif (strippedToken.startswith('scale(')):
                    flipped = (not flipped)
                elif (strippedToken.startswith('rotate(')):
                    rotation = rotation + int(float(strippedToken[7:]) / (-math.pi / 2))
        except (KeyError, ValueError):
            pass
        return (position, rotation, flipped)

    def _pointsFromString(self, text: str) -> QPolygonF:
        polygon = QPolygonF()
        try:
            for token in text.split(' '):
                coordTokens = token.split(',')
                polygon.append(QPointF(float(coordTokens[0]), float(coordTokens[1])))
        except (KeyError, ValueError):
            pass
        return polygon

    def _pathFromString(self, text: str) -> QPainterPath:
        try:
            path = QPainterPath()

            tokenList = text.split(' ')
            for index, token in enumerate(tokenList):
                if (token == 'M'):
                    path.moveTo(float(tokenList[index + 1]), float(tokenList[index + 2]))
                elif (token == 'L'):
                    path.lineTo(float(tokenList[index + 1]), float(tokenList[index + 2]))
                elif (token == 'C'):
                    path.cubicTo(float(tokenList[index + 1]), float(tokenList[index + 2]),
                                 float(tokenList[index + 3]), float(tokenList[index + 4]),
                                 float(tokenList[index + 5]), float(tokenList[index + 6]))

            return path
        except (ValueError, IndexError):
            pass
        return QPainterPath()

    def _viewBoxFromString(self, text: str) -> QRectF:
        rect = QRectF()
        try:
            tokens = text.split(' ')
            rect = QRectF(float(tokens[0]), float(tokens[1]), float(tokens[2]), float(tokens[3]))
        except (KeyError, ValueError):
            pass
        return rect

    def _colorFromString(self, text: str) -> QColor:
        return QColor.fromString(text)
