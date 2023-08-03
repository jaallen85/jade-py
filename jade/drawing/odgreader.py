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
from PySide6.QtGui import QColor, QPainterPath, QPolygonF, QTransform
from ..items.odgcurveitem import OdgCurveItem
from ..items.odgellipseitem import OdgEllipseItem
from ..items.odggroupitem import OdgGroupItem
from ..items.odgitem import OdgItem
from ..items.odgitemstyle import OdgItemStyle
from ..items.odglineitem import OdgLineItem
from ..items.odgmarker import OdgMarker
from ..items.odgpolygonitem import OdgPolygonItem
from ..items.odgpolylineitem import OdgPolylineItem
from ..items.odgrectitem import OdgRectItem
from .odgpage import OdgPage
from .odgunits import OdgUnits


class OdgReader:
    def __init__(self, path: str) -> None:
        self._path: str = path

        self._units: OdgUnits = OdgUnits.Inches
        self._pageSize: QSizeF = QSizeF(8.2, 6.2)
        self._pageMargins: QMarginsF = QMarginsF(0.1, 0.1, 0.1, 0.1)
        self._backgroundColor: QColor = QColor(255, 255, 255)

        self._grid: float = 0.05
        self._gridVisible: bool = True
        self._gridColor: QColor = QColor(0, 128, 128)
        self._gridSpacingMajor: int = 8
        self._gridSpacingMinor: int = 2

        self._defaultItemStyle: OdgItemStyle = OdgItemStyle('standard')
        self._itemStyles: list[OdgItemStyle] = []
        self._automaticItemStyles: list[OdgItemStyle] = []

        self._pages: list[OdgPage] = []

        with ZipFile(self._path, 'r') as odgFile:
            with odgFile.open('settings.xml', 'r') as settingsFile:
                self._readSettings(settingsFile.read().decode('utf-8'))
            with odgFile.open('styles.xml', 'r') as stylesFile:
                self._readStyles(stylesFile.read().decode('utf-8'))
            with odgFile.open('content.xml', 'r') as contentFile:
                self._readContent(contentFile.read().decode('utf-8'))

    def __del__(self) -> None:
        del self._defaultItemStyle
        del self._itemStyles[:]
        del self._automaticItemStyles[:]
        del self._pages[:]

    # ==================================================================================================================

    def path(self) -> str:
        return self._path

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

    def defaultItemStyle(self) -> OdgItemStyle:
        return self._defaultItemStyle

    def itemStyles(self) -> list[OdgItemStyle]:
        return self._itemStyles

    def takeItemStyles(self) -> list[OdgItemStyle]:
        styles = self._itemStyles.copy()
        self._itemStyles = []
        return styles

    # ==================================================================================================================

    def pages(self) -> list[OdgPage]:
        return self._pages

    def takePages(self) -> list[OdgPage]:
        pages = self._pages.copy()
        self._pages = []
        return pages

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
            newStyle = self._readItemStyle(xml)
            newStyle.setParent(None)
            self._defaultItemStyle.copyFromStyle(newStyle)
        elif (xml.qualifiedName() == 'style:style'):
            attributes = xml.attributes()
            if (attributes.hasAttribute('style:name') and attributes.value('style:name') == 'standard'):
                newStyle = self._readItemStyle(xml)
                newStyle.setParent(None)
                self._defaultItemStyle.copyFromStyle(newStyle)
            else:
                newStyle = self._readItemStyle(xml)
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

    def _readItemStyle(self, xml: QXmlStreamReader) -> OdgItemStyle:
        newStyle = OdgItemStyle('')
        newStyle.setParent(self._defaultItemStyle)

        attributes = xml.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'style:name':
                    newStyle.setName(attr.value())
                case 'style:parent-style-name':
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
        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgItemStyle)):
            lineItem.style().copyFromStyle(style)
        lineItem.setLine(QLineF(x1, y1, x2, y2))

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

        xml.skipCurrentElement()

        # Create rect item and return it if valid
        rectItem = OdgRectItem()
        rectItem.setPosition(position)
        rectItem.setRotation(rotation)
        rectItem.setFlipped(flipped)
        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgItemStyle)):
            rectItem.style().copyFromStyle(style)
        rectItem.setRect(QRectF(left, top, width, height))
        rectItem.setCornerRadius(cornerRadius)

        if (rectItem.isValid()):
            return rectItem

        del rectItem
        return None

    def _readEllipseItem(self, xml: QXmlStreamReader) -> OdgItem | None:
        # Read ellipse attributes from XML
        styleName = ''
        position, rotation, flipped = (QPointF(0, 0), 0, False)
        left, top, width, height = (0.0, 0.0, 0.0, 0.0)

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

        xml.skipCurrentElement()

        # Create ellipse item and return it if valid
        ellipseItem = OdgEllipseItem()
        ellipseItem.setPosition(position)
        ellipseItem.setRotation(rotation)
        ellipseItem.setFlipped(flipped)
        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgItemStyle)):
            ellipseItem.style().copyFromStyle(style)
        ellipseItem.setRect(QRectF(left, top, width, height))

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
        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgItemStyle)):
            polylineItem.style().copyFromStyle(style)
        polylineItem.setPolyline(points)

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
        style = self._findAutomaticStyle(styleName)
        if (isinstance(style, OdgItemStyle)):
            polygonItem.style().copyFromStyle(style)
        polygonItem.setPolygon(points)

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
            curve = QPolygonF()
            for elementIndex in range(path.elementCount()):
                element = path.elementAt(elementIndex)
                curve.append(QPointF(element.x, element.y))     # type:ignore

            curveItem = OdgCurveItem()
            curveItem.setPosition(position)
            curveItem.setRotation(rotation)
            curveItem.setFlipped(flipped)
            style = self._findAutomaticStyle(styleName)
            if (isinstance(style, OdgItemStyle)):
                curveItem.style().copyFromStyle(style)
            curveItem.setCurve(curve)

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

    def _findAutomaticStyle(self, name: str) -> OdgItemStyle | None:
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
