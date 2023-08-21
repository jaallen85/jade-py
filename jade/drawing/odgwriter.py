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
from zipfile import ZipFile
from PySide6.QtCore import Qt, QByteArray, QMarginsF, QPointF, QRectF, QSizeF, QXmlStreamWriter
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QApplication
from ..items.odgcurveitem import OdgCurveItem
from ..items.odgellipseitem import OdgEllipseItem
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


class OdgWriter:
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

        self._defaultItemBrush: QBrush = QBrush(QColor(255, 255, 255))
        self._defaultItemPen: QPen = QPen(QBrush(QColor(0, 0, 0)), 0.01, Qt.PenStyle.SolidLine,
                                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self._defaultItemStartMarker: OdgMarker = OdgMarker(OdgMarker.Style.NoMarker, 0.06)
        self._defaultItemEndMarker: OdgMarker = OdgMarker(OdgMarker.Style.NoMarker, 0.06)
        self._defaultItemFont: QFont = QFont('Arial')
        self._defaultItemFont.setPointSizeF(0.1)
        self._defaultItemTextAlignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
        self._defaultItemTextPadding: QSizeF = QSizeF(0, 0)
        self._defaultItemTextBrush: QBrush = QBrush(QColor(0, 0, 0))

        self._pages: list[OdgPage] = []

        self._styleFontFaces: list[str] = []
        self._contentFontFaces: list[str] = []
        self._contentStyleIndex: int = 0

    # ==================================================================================================================

    def setUnits(self, units: OdgUnits) -> None:
        self._units = units

    def setPageSize(self, size: QSizeF) -> None:
        self._pageSize = QSizeF(size)

    def setPageMargins(self, margins: QMarginsF) -> None:
        self._pageMargins = QMarginsF(margins)

    def setBackgroundColor(self, color: QColor) -> None:
        self._backgroundColor = QColor(color)

    # ==================================================================================================================

    def setGrid(self, grid: float) -> None:
        self._grid = grid

    def setGridVisible(self, visible: bool) -> None:
        self._gridVisible = visible

    def setGridColor(self, color: QColor) -> None:
        self._gridColor = QColor(color)

    def setGridSpacingMajor(self, spacing: int) -> None:
        self._gridSpacingMajor = spacing

    def setGridSpacingMinor(self, spacing: int) -> None:
        self._gridSpacingMinor = spacing

    # ==================================================================================================================

    def setDefaultItemBrush(self, brush: QBrush) -> None:
        self._defaultItemBrush = QBrush(brush)

    def setDefaultItemPen(self, pen: QPen) -> None:
        self._defaultItemPen = QPen(pen)

    def setDefaultItemStartMarker(self, marker: OdgMarker) -> None:
        self._defaultItemStartMarker = OdgMarker(marker.style(), marker.size())

    def setDefaultItemEndMarker(self, marker: OdgMarker) -> None:
        self._defaultItemEndMarker = OdgMarker(marker.style(), marker.size())

    def setDefaultItemFont(self, font: QFont) -> None:
        self._defaultItemFont = QFont(font)

    def setDefaultItemTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._defaultItemTextAlignment = alignment

    def setDefaultItemTextPadding(self, padding: QSizeF) -> None:
        self._defaultItemTextPadding = QSizeF(padding)

    def setDefaultItemTextBrush(self, brush: QBrush) -> None:
        self._defaultItemTextBrush = QBrush(brush)

    # ==================================================================================================================

    def setPages(self, pages: list[OdgPage]) -> None:
        self._pages = pages

    # ==================================================================================================================

    def writeToFile(self, path: str) -> None:
        with ZipFile(path, 'w') as odgFile:
            with odgFile.open('mimetype', 'w') as mimetypeFile:
                mimetypeFile.write(b'application/vnd.oasis.opendocument.graphics')
            with odgFile.open('META-INF/manifest.xml', 'w') as manifestFile:
                manifestFile.write(self._writeManifest())
            with odgFile.open('meta.xml', 'w') as metaFile:
                metaFile.write(self._writeMeta())
            with odgFile.open('settings.xml', 'w') as settingsFile:
                settingsFile.write(self._writeSettings())
            with odgFile.open('styles.xml', 'w') as stylesFile:
                stylesFile.write(self._writeStyles())
            with odgFile.open('content.xml', 'w') as contentFile:
                contentFile.write(self._writeContent())

    def writeToClipboard(self, items: list[OdgItem]) -> None:
        clipboard = QByteArray()

        xml = QXmlStreamWriter(clipboard)
        xml.setAutoFormatting(True)
        xml.setAutoFormattingIndent(2)

        xml.writeStartDocument()
        xml.writeStartElement('jade-items')
        xml.writeAttribute('units', str(self._units))
        xml.writeAttribute('page-width', self._lengthToString(self._pageSize.width()))
        xml.writeAttribute('page-height', self._lengthToString(self._pageSize.height()))
        xml.writeAttribute('margin-left', self._lengthToString(self._pageMargins.left()))
        xml.writeAttribute('margin-top', self._lengthToString(self._pageMargins.top()))
        xml.writeAttribute('margin-right', self._lengthToString(self._pageMargins.right()))
        xml.writeAttribute('margin-bottom', self._lengthToString(self._pageMargins.bottom()))
        xml.writeAttribute('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        xml.writeAttribute('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        xml.writeAttribute('xmlns:loext', 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0')
        xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        xml.writeAttribute('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        xml.writeAttribute('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        xml.writeAttribute('xmlns:text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')
        xml.writeAttribute('xmlns:jade', 'https://github.com/jaallen85/jade')

        # Default item style
        xml.writeStartElement('styles')
        self._writeStyle(xml, 'standard', True, self._defaultItemBrush, self._defaultItemPen,
                         self._defaultItemStartMarker, self._defaultItemEndMarker,
                         self._defaultItemFont, self._defaultItemTextAlignment, self._defaultItemTextPadding,
                         self._defaultItemTextBrush)
        xml.writeEndElement()

        # Automatic item styles
        self._contentStyleIndex = 0

        xml.writeStartElement('automatic-styles')
        self._writeItemStyles(xml, items)
        xml.writeEndElement()

        # Items
        self._contentStyleIndex = 0

        xml.writeStartElement('items')
        self._writeItems(xml, items)
        xml.writeEndElement()

        xml.writeEndElement()
        xml.writeEndDocument()

        QApplication.clipboard().setText(clipboard.data().decode('utf-8'))

    # ==================================================================================================================

    def _writeManifest(self) -> bytes:
        manifest = QByteArray()

        xml = QXmlStreamWriter(manifest)
        # xml.setAutoFormatting(True)
        # xml.setAutoFormattingIndent(2)

        xml.writeStartDocument()
        xml.writeStartElement('manifest:manifest')
        xml.writeAttribute('xmlns:manifest', 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0')
        xml.writeAttribute('manifest:version', '1.3')

        xml.writeStartElement('manifest:file-entry')
        xml.writeAttribute('manifest:full-path', '/')
        xml.writeAttribute('manifest:version', '1.3')
        xml.writeAttribute('manifest:media-type', 'application/vnd.oasis.opendocument.graphics')
        xml.writeEndElement()

        xml.writeStartElement('manifest:file-entry')
        xml.writeAttribute('manifest:full-path', 'content.xml')
        xml.writeAttribute('manifest:media-type', 'text/xml')
        xml.writeEndElement()

        xml.writeStartElement('manifest:file-entry')
        xml.writeAttribute('manifest:full-path', 'meta.xml')
        xml.writeAttribute('manifest:media-type', 'text/xml')
        xml.writeEndElement()

        xml.writeStartElement('manifest:file-entry')
        xml.writeAttribute('manifest:full-path', 'settings.xml')
        xml.writeAttribute('manifest:media-type', 'text/xml')
        xml.writeEndElement()

        xml.writeStartElement('manifest:file-entry')
        xml.writeAttribute('manifest:full-path', 'styles.xml')
        xml.writeAttribute('manifest:media-type', 'text/xml')
        xml.writeEndElement()

        xml.writeEndElement()
        xml.writeEndDocument()

        return manifest.data()

    def _writeMeta(self) -> bytes:
        meta = QByteArray()

        xml = QXmlStreamWriter(meta)
        # xml.setAutoFormatting(True)
        # xml.setAutoFormattingIndent(2)

        xml.writeStartDocument()
        xml.writeStartElement('office:document-meta')
        xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        xml.writeAttribute('office:version', '1.3')

        xml.writeEndElement()
        xml.writeEndDocument()

        return meta.data()

    def _writeSettings(self) -> bytes:
        settings = QByteArray()

        xml = QXmlStreamWriter(settings)
        # xml.setAutoFormatting(True)
        # xml.setAutoFormattingIndent(2)

        xml.writeStartDocument()
        xml.writeStartElement('office:document-settings')
        xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        xml.writeAttribute('xmlns:config', 'urn:oasis:names:tc:opendocument:xmlns:config:1.0')
        xml.writeAttribute('office:version', '1.3')

        xml.writeStartElement('office:settings')

        xml.writeStartElement('config:config-item-set')
        xml.writeAttribute('config:name', 'jade:settings')

        self._writeConfigItems(xml)

        xml.writeEndElement()   # config:config-item-set

        xml.writeEndElement()   # office:settings

        xml.writeEndElement()   # office:document-settings
        xml.writeEndDocument()

        return settings.data()

    def _writeStyles(self) -> bytes:
        styles = QByteArray()

        xml = QXmlStreamWriter(styles)
        # xml.setAutoFormatting(True)
        # xml.setAutoFormattingIndent(2)

        xml.writeStartDocument()
        xml.writeStartElement('office:document-styles')
        xml.writeAttribute('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        xml.writeAttribute('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        xml.writeAttribute('xmlns:loext', 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0')
        xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        xml.writeAttribute('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        xml.writeAttribute('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')

        # Font face declarations
        xml.writeStartElement('office:font-face-decls')
        self._writeFontFace(xml, self._defaultItemFont, defaultStyle=True)
        xml.writeEndElement()

        # Item styles
        xml.writeStartElement('office:styles')
        self._writeDashStyles(xml)
        self._writeMarkerStyles(xml)
        self._writeStyle(xml, 'standard', True, self._defaultItemBrush, self._defaultItemPen,
                         self._defaultItemStartMarker, self._defaultItemEndMarker,
                         self._defaultItemFont, self._defaultItemTextAlignment, self._defaultItemTextPadding,
                         self._defaultItemTextBrush)
        xml.writeEndElement()

        # Page layout and style
        xml.writeStartElement('office:automatic-styles')
        self._writePageLayout(xml)
        self._writePageStyle(xml)
        xml.writeEndElement()

        # Master page
        xml.writeStartElement('office:master-styles')

        xml.writeStartElement('style:master-page')
        xml.writeAttribute('style:name', 'Default')
        xml.writeAttribute('style:page-layout-name', 'DefaultPageLayout')
        xml.writeAttribute('draw:style-name', 'DefaultPageStyle')
        xml.writeEndElement()

        xml.writeEndElement()   # office:master-styles

        xml.writeEndElement()   # office:styles

        xml.writeEndElement()   # office:document-styles
        xml.writeEndDocument()

        return styles.data()

    def _writeContent(self) -> bytes:
        content = QByteArray()

        xml = QXmlStreamWriter(content)
        # xml.setAutoFormatting(True)
        # xml.setAutoFormattingIndent(2)

        xml.writeStartDocument()
        xml.writeStartElement('office:document-content')
        xml.writeAttribute('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        xml.writeAttribute('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        xml.writeAttribute('xmlns:loext', 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0')
        xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        xml.writeAttribute('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        xml.writeAttribute('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        xml.writeAttribute('xmlns:text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')
        xml.writeAttribute('xmlns:jade', 'https://github.com/jaallen85/jade')
        xml.writeAttribute('office:version', '1.3')

        # Font face declarations
        xml.writeStartElement('office:font-face-decls')
        for page in self._pages:
            self._writeItemFontFaces(xml, page.items())
        xml.writeEndElement()

        # Automatic item styles
        self._contentStyleIndex = 0

        xml.writeStartElement('office:automatic-styles')
        for page in self._pages:
            self._writeItemStyles(xml, page.items())
        xml.writeEndElement()   # office:automatic-styles

        # Pages
        self._contentStyleIndex = 0

        xml.writeStartElement('office:body')
        xml.writeStartElement('office:drawing')

        for page in self._pages:
            xml.writeStartElement('draw:page')
            if (page.name() != ''):
                xml.writeAttribute('draw:name', page.name())
            xml.writeAttribute('draw:master-page-name', 'Default')
            self._writeItems(xml, page.items())
            xml.writeEndElement()   # draw:page

        xml.writeEndElement()   # office:drawing
        xml.writeEndElement()   # office:body

        xml.writeEndElement()
        xml.writeEndDocument()

        return content.data()

    # ==================================================================================================================

    def _writeConfigItems(self, xml: QXmlStreamWriter) -> None:
        xml.writeStartElement('config:config-item')
        xml.writeAttribute('config:name', 'units')
        xml.writeAttribute('config:type', 'string')
        xml.writeCharacters(str(self._units))
        xml.writeEndElement()

        xml.writeStartElement('config:config-item')
        xml.writeAttribute('config:name', 'grid')
        xml.writeAttribute('config:type', 'double')
        xml.writeCharacters(str(self._grid))
        xml.writeEndElement()

        xml.writeStartElement('config:config-item')
        xml.writeAttribute('config:name', 'gridVisible')
        xml.writeAttribute('config:type', 'boolean')
        xml.writeCharacters('true' if self._gridVisible else 'false')
        xml.writeEndElement()

        xml.writeStartElement('config:config-item')
        xml.writeAttribute('config:name', 'gridColor')
        xml.writeAttribute('config:type', 'string')
        xml.writeCharacters(self._colorToString(self._gridColor))
        xml.writeEndElement()

        xml.writeStartElement('config:config-item')
        xml.writeAttribute('config:name', 'gridSpacingMajor')
        xml.writeAttribute('config:type', 'int')
        xml.writeCharacters(str(self._gridSpacingMajor))
        xml.writeEndElement()

        xml.writeStartElement('config:config-item')
        xml.writeAttribute('config:name', 'gridSpacingMinor')
        xml.writeAttribute('config:type', 'int')
        xml.writeCharacters(str(self._gridSpacingMinor))
        xml.writeEndElement()

    # ==================================================================================================================

    def _writeFontFace(self, xml: QXmlStreamWriter, font: QFont, defaultStyle: bool) -> None:
        family = font.family()

        writeXmlElement = False
        if (defaultStyle):
            writeXmlElement = True
        elif (family not in self._contentFontFaces):
            self._contentFontFaces.append(family)
            writeXmlElement = True

        if (writeXmlElement):
            xml.writeStartElement('style:font-face')
            xml.writeAttribute('style:name', family)
            xml.writeAttribute('svg:font-family', family)
            xml.writeEndElement()

    def _writeDashStyles(self, xml: QXmlStreamWriter) -> None:
        # OpenOffice built-in dash styles
        xml.writeStartElement('draw:stroke-dash')
        xml.writeAttribute('draw:name', 'Dash_20__28_Rounded_29_')
        xml.writeAttribute('draw:display-name', 'Dash (Rounded)')
        xml.writeAttribute('draw:style', 'round')
        xml.writeAttribute('draw:dots1', '1')
        xml.writeAttribute('draw:dots1-length', '201%')
        xml.writeAttribute('draw:distance', '199%')
        xml.writeEndElement()

        xml.writeStartElement('draw:stroke-dash')
        xml.writeAttribute('draw:name', 'Dot_20__28_Rounded_29_')
        xml.writeAttribute('draw:display-name', 'Dot (Rounded)')
        xml.writeAttribute('draw:style', 'round')
        xml.writeAttribute('draw:dots1', '1')
        xml.writeAttribute('draw:dots1-length', '1%')
        xml.writeAttribute('draw:distance', '199%')
        xml.writeEndElement()

        xml.writeStartElement('draw:stroke-dash')
        xml.writeAttribute('draw:name', 'Dash_20_Dot_20__28_Rounded_29_')
        xml.writeAttribute('draw:display-name', 'Dash Dot (Rounded)')
        xml.writeAttribute('draw:style', 'round')
        xml.writeAttribute('draw:dots1', '1')
        xml.writeAttribute('draw:dots1-length', '201%')
        xml.writeAttribute('draw:dots2', '1')
        xml.writeAttribute('draw:dots2-length', '1%')
        xml.writeAttribute('draw:distance', '199%')
        xml.writeEndElement()

        xml.writeStartElement('draw:stroke-dash')
        xml.writeAttribute('draw:name', 'Dash_20_Dot_20_Dot_20__28_Rounded_29_')
        xml.writeAttribute('draw:display-name', 'Dash Dot Dot (Rounded)')
        xml.writeAttribute('draw:style', 'round')
        xml.writeAttribute('draw:dots1', '1')
        xml.writeAttribute('draw:dots1-length', '201%')
        xml.writeAttribute('draw:dots2', '2')
        xml.writeAttribute('draw:dots2-length', '1%')
        xml.writeAttribute('draw:distance', '199%')
        xml.writeEndElement()

    def _writeMarkerStyles(self, xml: QXmlStreamWriter) -> None:
        xml.writeStartElement('draw:marker')
        xml.writeAttribute('draw:name', 'Triangle')
        xml.writeAttribute('svg:viewBox', '0 0 1013 1130')
        xml.writeAttribute('svg:d', ('M1009 1050l-449-1008-22-30-29-12-34 12-21 26-449 1012-5 13v8l5 21 12 21 17 '
                                     '13 21 4h903l21-4 21-13 9-21 4-21v-8z'))
        xml.writeEndElement()

        xml.writeStartElement('draw:marker')
        xml.writeAttribute('draw:name', 'Circle')
        xml.writeAttribute('svg:viewBox', '0 0 1131 1131')
        xml.writeAttribute('svg:d', ('M462 1118l-102-29-102-51-93-72-72-93-51-102-29-102-13-105 13-102 29-106 '
                                     '51-102 72-89 93-72 102-50 102-34 106-9 101 9 106 34 98 50 93 72 72 89 51 102 '
                                     '29 106 13 102-13 105-29 102-51 102-72 93-93 72-98 51-106 29-101 13z'))
        xml.writeEndElement()

    def _writeStyle(self, xml: QXmlStreamWriter, name: str, default: bool,
                    brush: QBrush | None = None, pen: QPen | None = None,
                    startMarker: OdgMarker | None = None, endMarker: OdgMarker | None = None,
                    font: QFont | None = None, textAlignment: Qt.AlignmentFlag | None = None,
                    textPadding: QSizeF | None = None, textBrush: QBrush | None = None) -> None:
        xml.writeStartElement('style:style')

        # Identifying information
        xml.writeAttribute('style:name', name)
        xml.writeAttribute('style:family', 'graphic')
        if (not default):
            xml.writeAttribute('style:parent-style-name', 'standard')

        # Graphic properties
        hasUniqueGraphicProperty = (self._hasUniqueBrushStyle(brush, default) or
                                    self._hasUniquePenStyle(pen, default) or
                                    self._hasUniqueStartMarkerStyle(startMarker, default) or
                                    self._hasUniqueEndMarkerStyle(endMarker, default) or
                                    self._hasUniqueTextAlignmentStyle(textAlignment, default) or
                                    self._hasUniqueTextPaddingStyle(textPadding, default))
        if (hasUniqueGraphicProperty):
            xml.writeStartElement('style:graphic-properties')
            self._writeBrushStyle(xml, brush, default)
            self._writePenStyle(xml, pen, default)
            self._writeStartMarkerStyle(xml, startMarker, default)
            self._writeEndMarkerStyle(xml, endMarker, default)
            self._writeTextAlignmentStyle(xml, textAlignment, default)
            self._writeTextPaddingStyle(xml, textPadding, default)
            xml.writeEndElement()

        # Paragraph properties
        hasParagraphProperty = self._hasUniqueTextAlignmentStyle(textAlignment, default)
        if (hasParagraphProperty):
            xml.writeStartElement('style:paragraph-properties')
            self._writeTextAlignmentParagraphStyle(xml, textAlignment, default)
            xml.writeEndElement()

        # Text properties
        hasTextProperty = (self._hasUniqueFontStyle(font, default) or self._hasUniqueTextBrushStyle(textBrush, default))
        if (hasTextProperty):
            xml.writeStartElement('style:text-properties')
            self._writeFontStyle(xml, font, default)
            self._writeTextBrushStyle(xml, textBrush, default)
            xml.writeEndElement()

        xml.writeEndElement()   # style:style

    def _writeParagraphStyle(self, xml: QXmlStreamWriter, name: str, textAlignment: Qt.AlignmentFlag) -> None:
        xml.writeStartElement('style:style')

        xml.writeAttribute('style:name', name)
        xml.writeAttribute('style:family', 'paragraph')
        xml.writeAttribute('style:parent-style-name', 'standard')

        # Paragraph properties
        hasParagraphProperty = self._hasUniqueTextAlignmentStyle(textAlignment, False)
        if (hasParagraphProperty):
            xml.writeStartElement('style:paragraph-properties')
            self._writeTextAlignmentParagraphStyle(xml, textAlignment, False)
            xml.writeEndElement()

        xml.writeEndElement()   # style:style

    def _writeTextStyle(self, xml: QXmlStreamWriter, name: str, font: QFont, textBrush: QBrush) -> None:
        xml.writeStartElement('style:style')

        xml.writeAttribute('style:name', name)
        xml.writeAttribute('style:family', 'text')
        xml.writeAttribute('style:parent-style-name', 'standard')

        # Text properties
        hasTextProperty = (self._hasUniqueFontStyle(font, False) or self._hasUniqueTextBrushStyle(textBrush, False))
        if (hasTextProperty):
            xml.writeStartElement('style:text-properties')
            self._writeFontStyle(xml, font, False)
            self._writeTextBrushStyle(xml, textBrush, False)
            xml.writeEndElement()

        xml.writeEndElement()   # style:style

    # ==================================================================================================================

    def _hasUniqueBrushStyle(self, brush: QBrush | None, default: bool) -> bool:
        if (isinstance(brush, QBrush)):
            return (default or brush.color() != self._defaultItemBrush.color())
        return False

    def _hasUniquePenStyle(self, pen: QPen | None, default: bool) -> bool:
        if (isinstance(pen, QPen)):
            return (default or (pen.style() != self._defaultItemPen.style() or
                                pen.widthF() != self._defaultItemPen.widthF() or
                                pen.brush().color() != self._defaultItemPen.brush().color() or
                                pen.capStyle() != self._defaultItemPen.capStyle() or
                                pen.joinStyle() != self._defaultItemPen.joinStyle()))
        return False

    def _hasUniqueStartMarkerStyle(self, marker: OdgMarker | None, default: bool) -> bool:
        if (isinstance(marker, OdgMarker)):
            return (default or (marker.style() != self._defaultItemStartMarker.style() or
                                marker.size() != self._defaultItemStartMarker.size()))
        return False

    def _hasUniqueEndMarkerStyle(self, marker: OdgMarker | None, default: bool) -> bool:
        if (isinstance(marker, OdgMarker)):
            return (default or (marker.style() != self._defaultItemEndMarker.style() or
                                marker.size() != self._defaultItemEndMarker.size()))
        return False

    def _hasUniqueFontStyle(self, font: QFont | None, default: bool) -> bool:
        if (isinstance(font, QFont)):
            return (default or (font.family() != self._defaultItemFont.family() or
                                font.pointSizeF() != self._defaultItemFont.pointSizeF() or
                                font.bold() != self._defaultItemFont.bold() or
                                font.italic() != self._defaultItemFont.italic() or
                                font.underline() != self._defaultItemFont.underline() or
                                font.strikeOut() != self._defaultItemFont.strikeOut()))
        return False

    def _hasUniqueTextAlignmentStyle(self, textAlignment: Qt.AlignmentFlag | None, default: bool) -> bool:
        if (isinstance(textAlignment, Qt.AlignmentFlag)):
            return (default or textAlignment != self._defaultItemTextAlignment)
        return False

    def _hasUniqueTextPaddingStyle(self, textPadding: QSizeF | None, default: bool) -> bool:
        if (isinstance(textPadding, QSizeF)):
            return (default or textPadding != self._defaultItemTextPadding)
        return False

    def _hasUniqueTextBrushStyle(self, textBrush: QBrush | None, default: bool) -> bool:
        if (isinstance(textBrush, QBrush)):
            return (default or textBrush.color() != self._defaultItemTextBrush.color())
        return False

    def _writeBrushStyle(self, xml: QXmlStreamWriter, brush: QBrush | None, default: bool) -> None:
        if (isinstance(brush, QBrush)):
            if (default or brush.color() != self._defaultItemBrush.color()):
                # Brush color
                color = brush.color()
                if (color == QColor(0, 0, 0, 0)):
                    xml.writeAttribute('draw:fill', 'none')
                else:
                    xml.writeAttribute('draw:fill', 'solid')
                    xml.writeAttribute('draw:fill-color', self._colorToString(color))
                    xml.writeAttribute('draw:opacity', f'{color.alphaF() * 100:.4g}%')

    def _writePenStyle(self, xml: QXmlStreamWriter, pen: QPen | None, default: bool) -> None:
        if (isinstance(pen, QPen)):
            # Pen style
            if (default or pen.style() != self._defaultItemPen.style()):
                match (pen.style()):
                    case Qt.PenStyle.SolidLine:
                        xml.writeAttribute('draw:stroke', 'solid')
                    case Qt.PenStyle.DashLine:
                        xml.writeAttribute('draw:stroke', 'dash')
                        xml.writeAttribute('draw:stroke-dash', 'Dash_20__28_Rounded_29_')
                    case Qt.PenStyle.DotLine:
                        xml.writeAttribute('draw:stroke', 'dash')
                        xml.writeAttribute('draw:stroke-dash', 'Dot_20__28_Rounded_29_')
                    case Qt.PenStyle.DashDotLine:
                        xml.writeAttribute('draw:stroke', 'dash')
                        xml.writeAttribute('draw:stroke-dash', 'Dash_20_Dot_20__28_Rounded_29_')
                    case Qt.PenStyle.DashDotDotLine:
                        xml.writeAttribute('draw:stroke', 'dash')
                        xml.writeAttribute('draw:stroke-dash', 'Dash_20_Dot_20_Dot_20__28_Rounded_29_')
                    case _:
                        xml.writeAttribute('draw:stroke', 'none')

            if (pen.style() != Qt.PenStyle.NoPen):
                # Pen width
                if (default or pen.widthF() != self._defaultItemPen.widthF()):
                    xml.writeAttribute('svg:stroke-width', self._lengthToString(pen.widthF()))

                # Pen color
                if (default or pen.brush().color() != self._defaultItemPen.brush().color()):
                    xml.writeAttribute('svg:stroke-color', self._colorToString(pen.brush().color()))
                    xml.writeAttribute('svg:stroke-opacity', f'{pen.brush().color().alphaF() * 100:.4g}%')

                # Pen cap style
                if (default or pen.capStyle() != self._defaultItemPen.capStyle()):
                    match (pen.capStyle()):
                        case Qt.PenCapStyle.FlatCap:
                            xml.writeAttribute('svg:stroke-linecap', 'butt')
                        case Qt.PenCapStyle.SquareCap:
                            xml.writeAttribute('svg:stroke-linecap', 'square')
                        case _:
                            xml.writeAttribute('svg:stroke-linecap', 'round')

                # Pen join style
                if (default or pen.joinStyle() != self._defaultItemPen.joinStyle()):
                    match (pen.joinStyle()):
                        case (Qt.PenJoinStyle.MiterJoin | Qt.PenJoinStyle.SvgMiterJoin):
                            xml.writeAttribute('draw:stroke-linejoin', 'miter')
                        case Qt.PenJoinStyle.BevelJoin:
                            xml.writeAttribute('draw:stroke-linejoin', 'bevel')
                        case _:
                            xml.writeAttribute('draw:stroke-linejoin', 'round')

    def _writeStartMarkerStyle(self, xml: QXmlStreamWriter, marker: OdgMarker | None, default: bool) -> None:
        if (isinstance(marker, OdgMarker)):
            # Start marker style
            if (default or marker.style() != self._defaultItemStartMarker.style()):
                match (marker.style()):
                    case OdgMarker.Style.Triangle:
                        xml.writeAttribute('draw:marker-start', 'Triangle')
                        xml.writeAttribute('draw:marker-start-center', 'false')
                    case OdgMarker.Style.Circle:
                        xml.writeAttribute('draw:marker-start', 'Circle')
                        xml.writeAttribute('draw:marker-start-center', 'true')
                    case _:
                        xml.writeAttribute('draw:marker-start', 'None')

            # Start marker size
            if (default or marker.size() != self._defaultItemStartMarker.size()):
                xml.writeAttribute('draw:marker-start-width', self._lengthToString(marker.size()))

    def _writeEndMarkerStyle(self, xml: QXmlStreamWriter, marker: OdgMarker | None, default: bool) -> None:
        if (isinstance(marker, OdgMarker)):
            # End marker style
            if (default or marker.style() != self._defaultItemEndMarker.style()):
                match (marker.style()):
                    case OdgMarker.Style.Triangle:
                        xml.writeAttribute('draw:marker-end', 'Triangle')
                        xml.writeAttribute('draw:marker-end-center', 'false')
                    case OdgMarker.Style.Circle:
                        xml.writeAttribute('draw:marker-end', 'Circle')
                        xml.writeAttribute('draw:marker-end-center', 'true')
                    case _:
                        xml.writeAttribute('draw:marker-end', 'None')

            # End marker size
            if (default or marker.size() != self._defaultItemEndMarker.size()):
                xml.writeAttribute('draw:marker-end-width', self._lengthToString(marker.size()))

    def _writeFontStyle(self, xml: QXmlStreamWriter, font: QFont | None, default: bool) -> None:
        if (isinstance(font, QFont)):
            # Font family
            if (default or font.family() != self._defaultItemFont.family()):
                xml.writeAttribute('style:font-name', font.family())

            # Font size
            if (default or font.pointSizeF() != self._defaultItemFont.pointSizeF()):
                xml.writeAttribute('fo:font-size', self._lengthToString(font.pointSizeF()))

            # Font style
            if (default or font.bold() != self._defaultItemFont.bold()):
                xml.writeAttribute('fo:font-weight', 'bold' if (font.bold()) else 'normal')
            if (default or font.italic() != self._defaultItemFont.italic()):
                xml.writeAttribute('fo:font-style', 'italic' if (font.italic()) else 'normal')
            if (default or font.underline() != self._defaultItemFont.underline()):
                if (font.underline()):
                    xml.writeAttribute('style:text-underline-style', 'solid')
                    xml.writeAttribute('style:text-underline-width', 'single')
                    xml.writeAttribute('style:text-underline-color', 'font-color')
                else:
                    xml.writeAttribute('style:text-underline-style', 'none')
            if (default or font.strikeOut() != self._defaultItemFont.strikeOut()):
                if (font.strikeOut()):
                    xml.writeAttribute('style:text-line-through-style', 'solid')
                    xml.writeAttribute('style:text-line-through-type', 'single')
                else:
                    xml.writeAttribute('style:text-line-through-style', 'none')

    def _writeTextAlignmentStyle(self, xml: QXmlStreamWriter, textAlignment: Qt.AlignmentFlag | None,
                                 default: bool) -> None:
        if (isinstance(textAlignment, Qt.AlignmentFlag)):
            if (default or textAlignment != self._defaultItemTextAlignment):
                if (textAlignment & Qt.AlignmentFlag.AlignLeft):
                    xml.writeAttribute('draw:textarea-horizontal-align', 'left')
                elif (textAlignment & Qt.AlignmentFlag.AlignRight):
                    xml.writeAttribute('draw:textarea-horizontal-align', 'right')
                else:
                    xml.writeAttribute('draw:textarea-horizontal-align', 'center')

                if (textAlignment & Qt.AlignmentFlag.AlignTop):
                    xml.writeAttribute('draw:textarea-vertical-align', 'top')
                elif (textAlignment & Qt.AlignmentFlag.AlignBottom):
                    xml.writeAttribute('draw:textarea-vertical-align', 'bottom')
                else:
                    xml.writeAttribute('draw:textarea-vertical-align', 'middle')

    def _writeTextAlignmentParagraphStyle(self, xml: QXmlStreamWriter, textAlignment: Qt.AlignmentFlag | None,
                                          default: bool) -> None:
        if (isinstance(textAlignment, Qt.AlignmentFlag)):
            if (default or textAlignment != self._defaultItemTextAlignment):
                if (textAlignment & Qt.AlignmentFlag.AlignLeft):
                    xml.writeAttribute('fo:text-align', 'start')
                elif (textAlignment & Qt.AlignmentFlag.AlignRight):
                    xml.writeAttribute('fo:text-align', 'end')
                else:
                    xml.writeAttribute('fo:text-align', 'center')

    def _writeTextPaddingStyle(self, xml: QXmlStreamWriter, textPadding: QSizeF | None, default: bool) -> None:
        if (isinstance(textPadding, QSizeF)):
            if (default or textPadding != self._defaultItemTextPadding):
                xml.writeAttribute('fo:padding-left', self._lengthToString(textPadding.width()))
                xml.writeAttribute('fo:padding-top', self._lengthToString(textPadding.height()))
                xml.writeAttribute('fo:padding-right', self._lengthToString(textPadding.width()))
                xml.writeAttribute('fo:padding-bottom', self._lengthToString(textPadding.height()))

    def _writeTextBrushStyle(self, xml: QXmlStreamWriter, textBrush: QBrush | None, default: bool) -> None:
        if (isinstance(textBrush, QBrush)):
            if (default or textBrush.color() != self._defaultItemTextBrush.color()):
                xml.writeAttribute('fo:color', self._colorToString(textBrush.color()))
                xml.writeAttribute('loext:opacity', f'{textBrush.color().alphaF() * 100:.4g}%')

    # ==================================================================================================================

    def _writePageLayout(self, xml: QXmlStreamWriter) -> None:
        xml.writeStartElement('style:page-layout')
        xml.writeAttribute('style:name', 'DefaultPageLayout')

        xml.writeStartElement('style:page-layout-properties')
        xml.writeAttribute('fo:page-width', self._lengthToString(self._pageSize.width()))
        xml.writeAttribute('fo:page-height', self._lengthToString(self._pageSize.height()))
        xml.writeAttribute('fo:margin-left', self._lengthToString(self._pageMargins.left()))
        xml.writeAttribute('fo:margin-top', self._lengthToString(self._pageMargins.top()))
        xml.writeAttribute('fo:margin-right', self._lengthToString(self._pageMargins.right()))
        xml.writeAttribute('fo:margin-bottom', self._lengthToString(self._pageMargins.bottom()))
        xml.writeEndElement()

        xml.writeEndElement()    # style:page-layout

    def _writePageStyle(self, xml: QXmlStreamWriter) -> None:
        xml.writeStartElement('style:style')
        xml.writeAttribute('style:name', 'DefaultPageStyle')
        xml.writeAttribute('style:family', 'drawing-page')

        xml.writeStartElement('style:drawing-page-properties')
        if (self._backgroundColor == QColor(0, 0, 0, 0)):
            xml.writeAttribute('draw:fill', 'none')
        else:
            xml.writeAttribute('draw:fill', 'solid')
            xml.writeAttribute('draw:fill-color', self._colorToString(self._backgroundColor))
            if (self._backgroundColor.alpha() != 255):
                xml.writeAttribute('draw:opacity', f'{self._backgroundColor.alphaF() * 100:.4g}%')
        xml.writeAttribute('draw:background-size', 'border')
        xml.writeEndElement()

        xml.writeEndElement()   # style:style

    # ==================================================================================================================

    def _writeItemFontFaces(self, xml: QXmlStreamWriter, items: list[OdgItem]) -> None:
        for item in items:
            if (isinstance(item, OdgGroupItem)):
                self._writeItemFontFaces(xml, item.items())
            elif (isinstance(item, (OdgTextItem, OdgTextEllipseItem, OdgTextRectItem))):
                self._writeFontFace(xml, item.font(), defaultStyle=False)

    def _writeItemStyles(self, xml: QXmlStreamWriter, items: list[OdgItem]) -> None:
        for item in items:
            self._contentStyleIndex = self._contentStyleIndex + 1
            styleName = f'Style_{self._contentStyleIndex:04d}'

            if (isinstance(item, (OdgLineItem, OdgCurveItem, OdgPolylineItem))):
                self._writeStyle(xml, styleName, default=False,
                                 pen=item.pen(), startMarker=item.startMarker(), endMarker=item.endMarker())
            elif (isinstance(item, (OdgRectItem, OdgEllipseItem, OdgPolygonItem))):
                self._writeStyle(xml, styleName, default=False,
                                 brush=item.brush(), pen=item.pen())
            elif (isinstance(item, OdgTextItem)):
                self._writeStyle(xml, styleName, default=False,
                                 brush=QBrush(QColor(0, 0, 0, 0)), pen=QPen(Qt.PenStyle.NoPen),
                                 font=item.font(), textAlignment=item.alignment(),
                                 textPadding=item.padding(), textBrush=item.brush())
                self._writeParagraphStyle(xml, styleName + '_P', textAlignment=item.alignment())
                self._writeTextStyle(xml, styleName + '_T', font=item.font(), textBrush=item.brush())
            elif (isinstance(item, (OdgTextRectItem, OdgTextEllipseItem))):
                self._writeStyle(xml, styleName, default=False,
                                 brush=item.brush(), pen=item.pen(),
                                 font=item.font(), textAlignment=item.textAlignment(), textPadding=item.textPadding(),
                                 textBrush=item.textBrush())
                self._writeParagraphStyle(xml, styleName + '_P', textAlignment=item.textAlignment())
                self._writeTextStyle(xml, styleName + '_T', font=item.font(), textBrush=item.textBrush())
            elif (isinstance(item, OdgGroupItem)):
                self._writeItemStyles(xml, item.items())

    def _writeItems(self, xml: QXmlStreamWriter, items: list[OdgItem]) -> None:
        for item in items:
            self._contentStyleIndex = self._contentStyleIndex + 1
            styleName = f'Style_{self._contentStyleIndex:04d}'

            if (isinstance(item, OdgLineItem)):
                self._writeLineItem(xml, item, styleName)
            elif (isinstance(item, OdgRectItem)):
                self._writeRectItem(xml, item, styleName)
            elif (isinstance(item, OdgEllipseItem)):
                self._writeEllipseItem(xml, item, styleName)
            elif (isinstance(item, OdgPolylineItem)):
                self._writePolylineItem(xml, item, styleName)
            elif (isinstance(item, OdgPolygonItem)):
                self._writePolygonItem(xml, item, styleName)
            elif (isinstance(item, OdgCurveItem)):
                self._writeCurveItem(xml, item, styleName)
            elif (isinstance(item, OdgTextItem)):
                self._writeTextItem(xml, item, styleName)
            elif (isinstance(item, OdgTextRectItem)):
                self._writeTextRectItem(xml, item, styleName)
            elif (isinstance(item, OdgTextEllipseItem)):
                self._writeTextEllipseItem(xml, item, styleName)
            elif (isinstance(item, OdgGroupItem)):
                self._writeGroupItem(xml, item)

    # ==================================================================================================================

    def _writeLineItem(self, xml: QXmlStreamWriter, item: OdgLineItem, styleName: str) -> None:
        xml.writeStartElement('draw:line')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Line-specific attributes
        line = item.line()
        xml.writeAttribute('svg:x1', self._lengthToString(line.x1()))
        xml.writeAttribute('svg:y1', self._lengthToString(line.y1()))
        xml.writeAttribute('svg:x2', self._lengthToString(line.x2()))
        xml.writeAttribute('svg:y2', self._lengthToString(line.y2()))

        xml.writeEndElement()

    def _writeRectItem(self, xml: QXmlStreamWriter, item: OdgRectItem, styleName: str) -> None:
        xml.writeStartElement('draw:rect')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Rect-specific attributes
        rect = item.rect()
        xml.writeAttribute('svg:x', self._lengthToString(rect.left()))
        xml.writeAttribute('svg:y', self._lengthToString(rect.top()))
        xml.writeAttribute('svg:width', self._lengthToString(rect.width()))
        xml.writeAttribute('svg:height', self._lengthToString(rect.height()))
        if (item.cornerRadius() != 0):
            xml.writeAttribute('draw:corner-radius', self._lengthToString(item.cornerRadius()))

        xml.writeEndElement()

    def _writeEllipseItem(self, xml: QXmlStreamWriter, item: OdgEllipseItem, styleName: str) -> None:
        xml.writeStartElement('draw:ellipse')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Ellipse-specific attributes
        ellipse = item.ellipse()
        xml.writeAttribute('svg:x', self._lengthToString(ellipse.left()))
        xml.writeAttribute('svg:y', self._lengthToString(ellipse.top()))
        xml.writeAttribute('svg:width', self._lengthToString(ellipse.width()))
        xml.writeAttribute('svg:height', self._lengthToString(ellipse.height()))

        xml.writeEndElement()

    def _writePolylineItem(self, xml: QXmlStreamWriter, item: OdgPolylineItem, styleName: str) -> None:
        xml.writeStartElement('draw:polyline')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Polyline-specific attributes
        polyline = item.polyline()
        polylineBoundingRect = polyline.boundingRect()

        xml.writeAttribute('svg:x', self._lengthToString(polylineBoundingRect.left()))
        xml.writeAttribute('svg:y', self._lengthToString(polylineBoundingRect.top()))
        xml.writeAttribute('svg:width', self._lengthToString(polylineBoundingRect.width()))
        xml.writeAttribute('svg:height', self._lengthToString(polylineBoundingRect.height()))
        xml.writeAttribute('svg:viewBox', self._viewBoxToString(polylineBoundingRect))
        xml.writeAttribute('draw:points', self._pointsToString(polyline))

        xml.writeEndElement()

    def _writePolygonItem(self, xml: QXmlStreamWriter, item: OdgPolygonItem, styleName: str) -> None:
        xml.writeStartElement('draw:polygon')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Polygon-specific attributes
        polygon = item.polygon()
        polygonBoundingRect = polygon.boundingRect()

        xml.writeAttribute('svg:x', self._lengthToString(polygonBoundingRect.left()))
        xml.writeAttribute('svg:y', self._lengthToString(polygonBoundingRect.top()))
        xml.writeAttribute('svg:width', self._lengthToString(polygonBoundingRect.width()))
        xml.writeAttribute('svg:height', self._lengthToString(polygonBoundingRect.height()))
        xml.writeAttribute('svg:viewBox', self._viewBoxToString(polygonBoundingRect))
        xml.writeAttribute('draw:points', self._pointsToString(polygon))

        xml.writeEndElement()

    def _writeCurveItem(self, xml: QXmlStreamWriter, item: OdgCurveItem, styleName: str) -> None:
        xml.writeStartElement('draw:path')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Curve-specific attributes
        curve = item.curve()
        curvePath = QPainterPath()
        curvePath.moveTo(curve.p1())
        curvePath.cubicTo(curve.cp1(), curve.cp2(), curve.p2())
        curvePathBoundingRect = curvePath.boundingRect()

        xml.writeAttribute('svg:x', self._lengthToString(curvePathBoundingRect.left()))
        xml.writeAttribute('svg:y', self._lengthToString(curvePathBoundingRect.top()))
        xml.writeAttribute('svg:width', self._lengthToString(curvePathBoundingRect.width()))
        xml.writeAttribute('svg:height', self._lengthToString(curvePathBoundingRect.height()))
        xml.writeAttribute('svg:viewBox', self._viewBoxToString(curvePathBoundingRect))
        xml.writeAttribute('svg:d', self._pathToString(curvePath))

        xml.writeEndElement()

    def _writeTextItem(self, xml: QXmlStreamWriter, item: OdgTextItem, styleName: str) -> None:
        xml.writeStartElement('draw:rect')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)
        xml.writeAttribute('draw:text-style-name', styleName + '_P')

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Text-specific attributes
        rect = item.boundingRect()

        if (self._grid > 0):
            # Snap the edges of the rect to the grid
            left = self._grid * math.floor(rect.left() / self._grid)
            top = self._grid * math.floor(rect.top() / self._grid)
            right = self._grid * math.ceil(rect.right() / self._grid)
            bottom = self._grid * math.ceil(rect.bottom() / self._grid)
            rect = QRectF(left, top, right - left, bottom - top)

        xml.writeAttribute('svg:x', self._lengthToString(rect.left()))
        xml.writeAttribute('svg:y', self._lengthToString(rect.top()))
        xml.writeAttribute('svg:width', self._lengthToString(rect.width()))
        xml.writeAttribute('svg:height', self._lengthToString(rect.height()))
        xml.writeAttribute('jade:text-item-hint', 'text')

        for line in item.caption().split('\n'):
            xml.writeStartElement('text:p')
            xml.writeAttribute('text:style-name', styleName + '_P')
            xml.writeStartElement('text:span')
            xml.writeAttribute('text:style-name', styleName + '_T')
            xml.writeCharacters(line)
            xml.writeEndElement()
            xml.writeEndElement()

        xml.writeEndElement()

    def _writeTextRectItem(self, xml: QXmlStreamWriter, item: OdgTextRectItem, styleName: str) -> None:
        xml.writeStartElement('draw:rect')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)
        xml.writeAttribute('draw:text-style-name', styleName + '_P')

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Rect-specific attributes
        rect = item.rect()
        xml.writeAttribute('svg:x', self._lengthToString(rect.left()))
        xml.writeAttribute('svg:y', self._lengthToString(rect.top()))
        xml.writeAttribute('svg:width', self._lengthToString(rect.width()))
        xml.writeAttribute('svg:height', self._lengthToString(rect.height()))
        if (item.cornerRadius() != 0):
            xml.writeAttribute('draw:corner-radius', self._lengthToString(item.cornerRadius()))
        xml.writeAttribute('jade:text-item-hint', 'text-rect')

        # Text
        for line in item.caption().split('\n'):
            xml.writeStartElement('text:p')
            xml.writeAttribute('text:style-name', styleName + '_P')
            xml.writeStartElement('text:span')
            xml.writeAttribute('text:style-name', styleName + '_T')
            xml.writeCharacters(line)
            xml.writeEndElement()
            xml.writeEndElement()

        xml.writeEndElement()

    def _writeTextEllipseItem(self, xml: QXmlStreamWriter, item: OdgTextEllipseItem, styleName: str) -> None:
        xml.writeStartElement('draw:ellipse')

        # Common item attributes
        xml.writeAttribute('draw:style-name', styleName)
        xml.writeAttribute('draw:text-style-name', styleName + '_P')

        transform = self._transformToString(item.position(), item.rotation(), item.isFlipped())
        if (transform != ''):
            xml.writeAttribute('draw:transform', transform)

        # Ellipse-specific attributes
        ellipse = item.ellipse()
        xml.writeAttribute('svg:x', self._lengthToString(ellipse.left()))
        xml.writeAttribute('svg:y', self._lengthToString(ellipse.top()))
        xml.writeAttribute('svg:width', self._lengthToString(ellipse.width()))
        xml.writeAttribute('svg:height', self._lengthToString(ellipse.height()))
        xml.writeAttribute('jade:text-item-hint', 'text-ellipse')

        # Text
        for line in item.caption().split('\n'):
            xml.writeStartElement('text:p')
            xml.writeAttribute('text:style-name', styleName + '_P')
            xml.writeStartElement('text:span')
            xml.writeAttribute('text:style-name', styleName + '_T')
            xml.writeCharacters(line)
            xml.writeEndElement()
            xml.writeEndElement()

        xml.writeEndElement()

    def _writeGroupItem(self, xml: QXmlStreamWriter, item: OdgGroupItem) -> None:
        xml.writeStartElement('draw:g')

        # NOTE: The elaborate code in this function is necessary because the draw:g element does not support the
        # draw:transform attribute.

        # Save group and child item's original position/transform to be restored later
        originalPosition = QPointF(item.position())
        originalRotation = item.rotation()
        originalFlipped = item.isFlipped()

        originalChildPosition = {}
        originalChildRotation = {}
        originalChildFlipped = {}
        for child in item.items():
            originalChildPosition[child] = child.position()
            originalChildRotation[child] = child.rotation()
            originalChildFlipped[child] = child.isFlipped()

        # Apply the group's position/transform to each item
        for child in item.items():
            child.setPosition(item.mapToScene(child.position()))
            child.setRotation(child.rotation() + item.rotation())
            if (item.isFlipped()):
                child.setFlipped(not child.isFlipped())

        # Clear group's position/transform
        item.setPosition(QPointF(0, 0))
        item.setRotation(0)
        item.setFlipped(False)

        # Write group to XML
        self._writeItems(xml, item.items())

        # Restore group and child items' original position/transform
        for child in item.items():
            child.setPosition(originalChildPosition[child])
            child.setRotation(originalChildRotation[child])
            child.setFlipped(originalChildFlipped[child])

        item.setPosition(originalPosition)
        item.setRotation(originalRotation)
        item.setFlipped(originalFlipped)

        xml.writeEndElement()

    # ==================================================================================================================

    def _lengthToString(self, value: float) -> str:
        return f'{value:.8g}{str(self._units)}'

    def _xCoordinateToString(self, x: float) -> str:
        return f'{x + self._pageMargins.left():.8g}{str(self._units)}'

    def _yCoordinateToString(self, y: float) -> str:
        return f'{y + self._pageMargins.top():.8g}{str(self._units)}'

    def _transformToString(self, position: QPointF, rotation: int, flipped: bool) -> str:
        transformStr = ''

        if (rotation != 0):
            transformStr = f'{transformStr} rotate({rotation * (-math.pi / 2)})'
        if (flipped):
            transformStr = f'{transformStr} scale(-1, 1)'
        if (position.x() != 0 or position.y() != 0):
            xStr = self._xCoordinateToString(position.x())
            yStr = self._yCoordinateToString(position.y())
            transformStr = f'{transformStr} translate({xStr}, {yStr})'

        return transformStr.strip()

    def _pointsToString(self, points: QPolygonF) -> str:
        pointsStr = ''

        for index in range(points.count()):
            point = points.at(index)
            pointsStr = f'{pointsStr} {point.x():.8g},{point.y():.8g}'

        return pointsStr.strip()

    def _pathToString(self, path: QPainterPath) -> str:
        pathStr = ''

        for index in range(path.elementCount()):
            pathElement = path.elementAt(index)
            match (pathElement.type):                                                   # type: ignore
                case QPainterPath.ElementType.MoveToElement:
                    pathStr = f'{pathStr} M {pathElement.x:.8g} {pathElement.y:.8g}'    # type: ignore
                case QPainterPath.ElementType.LineToElement:
                    pathStr = f'{pathStr} L {pathElement.x:.8g} {pathElement.y:.8g}'    # type: ignore
                case QPainterPath.ElementType.CurveToElement:
                    pathStr = f'{pathStr} C {pathElement.x:.8g} {pathElement.y:.8g}'    # type: ignore
                case QPainterPath.ElementType.CurveToDataElement:
                    pathStr = f'{pathStr} {pathElement.x:.8g} {pathElement.y:.8g}'      # type: ignore

        return pathStr.strip()

    def _viewBoxToString(self, viewBox: QRectF) -> str:
        return f'{viewBox.left():.8g} {viewBox.top():.8g} {viewBox.width():.8g} {viewBox.height():.8g}'

    def _colorToString(self, color: QColor) -> str:
        return color.name(QColor.NameFormat.HexRgb)
