# odgwriter.py
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

from xml.etree import ElementTree
from zipfile import ZipFile
from PySide6.QtCore import Qt, QSizeF
from PySide6.QtGui import QBrush, QColor, QPen
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitemgroup import DrawingItemGroup
from ..drawing.drawingpagewidget import DrawingPageWidget
from ..items.drawingcurveitem import DrawingCurveItem
from ..items.drawingellipseitem import DrawingEllipseItem
from ..items.drawinglineitem import DrawingLineItem
from ..items.drawingpathitem import DrawingPathItem
from ..items.drawingpolygonitem import DrawingPolygonItem
from ..items.drawingpolylineitem import DrawingPolylineItem
from ..items.drawingrectitem import DrawingRectItem
from ..items.drawingtextellipseitem import DrawingTextEllipseItem
from ..items.drawingtextitem import DrawingTextItem
from ..items.drawingtextrectitem import DrawingTextRectItem
from ..diagramwidget import DiagramWidget


class OdgWriter:
    def __init__(self, drawing: DiagramWidget, exportEntireDocument: bool, scale: float, units: str) -> None:
        super().__init__()

        self._drawing: DiagramWidget = drawing
        self._exportEntireDocument: bool = exportEntireDocument
        self._scale: float = scale
        self._units: str = str(units)

        # Get master page attributes
        self._pagesToExport: list[DrawingPageWidget] = []
        self._pageSize: QSizeF = QSizeF()
        self._pageMargin: float = 0.0
        self._backgroundColor: QColor = QColor(255, 255, 255)

        currentPage = self._drawing.currentPage()
        if (self._exportEntireDocument):
            self._pagesToExport = self._drawing.pages()

            # LibreOffice only supports one master page (despite the Open Document spec supporting multiple).
            # So all pages in the document must be the same (same size, margin, and background color).
            # Choose a page size and margin that is large enough to fit all the pages in the document.
            # Choose the background color from the first page to use for the entire document.
            for index, page in enumerate(self._drawing.pages()):
                self._pageSize.setWidth(max(self._pageSize.width(), page.pageSize().width()))
                self._pageSize.setHeight(max(self._pageSize.height(), page.pageSize().height()))
                self._pageMargin = max(self._pageMargin, page.pageMargin())
                if (index == 0):
                    self._backgroundColor = page.backgroundBrush().color()

        elif (currentPage is not None):
            self._pagesToExport = [currentPage]
            self._pageSize = currentPage.pageSize()
            self._pageMargin = currentPage.pageMargin()
            self._backgroundColor = currentPage.backgroundBrush().color()

    # ==================================================================================================================

    def write(self, path: str) -> None:
        with ZipFile(path, mode='w') as odgArchive:
            odgArchive.writestr('mimetype', 'application/vnd.oasis.opendocument.graphics')
            odgArchive.writestr('META-INF/manifest.xml', self._writeManifest())
            odgArchive.writestr('meta.xml', self._writeMeta())
            odgArchive.writestr('settings.xml', self._writeSettings())
            odgArchive.writestr('styles.xml', self._writeStyles())
            odgArchive.writestr('content.xml', self._writeContent())

    def _writeManifest(self) -> str:
        manifestElement = ElementTree.Element('manifest:manifest')
        manifestElement.set('xmlns:manifest', 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0')
        manifestElement.set('manifest:version', '1.3')

        fileElement = ElementTree.SubElement(manifestElement, 'manifest:file-entry')
        fileElement.set('manifest:full-path', '/')
        fileElement.set('manifest:version', '1.3')
        fileElement.set('manifest:media-type', 'application/vnd.oasis.opendocument.graphics')

        for path in ('content.xml', 'meta.xml', 'settings.xml', 'styles.xml'):
            fileElement = ElementTree.SubElement(manifestElement, 'manifest:file-entry')
            fileElement.set('manifest:full-path', path)
            fileElement.set('manifest:media-type', 'text/xml')

        ElementTree.indent(manifestElement, space='  ')
        return f'{ElementTree.tostring(manifestElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeMeta(self) -> str:
        metaElement = ElementTree.Element('office:document-meta')
        metaElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        metaElement.set('manifest:version', '1.3')

        ElementTree.SubElement(metaElement, 'office:meta')

        ElementTree.indent(metaElement, space='  ')
        return f'{ElementTree.tostring(metaElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeSettings(self) -> str:
        settingsElement = ElementTree.Element('office:document-settings')
        settingsElement.set('xmlns:config', 'urn:oasis:names:tc:opendocument:xmlns:config:1.0')
        settingsElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        settingsElement.set('manifest:version', '1.3')

        ElementTree.SubElement(settingsElement, 'office:settings')

        ElementTree.indent(settingsElement, space='  ')
        return f'{ElementTree.tostring(settingsElement, encoding="unicode", xml_declaration=True)}\n'

    # ==================================================================================================================

    def _writeStyles(self) -> str:
        printOrientation = 'portrait' if (self._pageSize.width() > self._pageSize.height()) else 'landscape'

        stylesElement = ElementTree.Element('office:document-styles')
        stylesElement.set('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        stylesElement.set('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        stylesElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        stylesElement.set('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        stylesElement.set('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        stylesElement.set('manifest:version', '1.3')

        ElementTree.SubElement(stylesElement, 'office:font-face-decls')

        # Styles
        officeStylesElement = ElementTree.SubElement(stylesElement, 'office:styles')
        self._writeMarkerStyles(officeStylesElement)
        self._writeStrokeDashStyles(officeStylesElement)

        # Automatic styles
        automaticStylesElement = ElementTree.SubElement(stylesElement, 'office:automatic-styles')

        pageLayoutElement = ElementTree.SubElement(automaticStylesElement, 'style:page-layout')
        pageLayoutElement.set('style:name', 'PM0')

        pageLayoutPropertiesElement = ElementTree.SubElement(pageLayoutElement, 'style:page-layout-properties')
        pageLayoutPropertiesElement.set('fo:margin-top', f'{self._sizeToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:margin-bottom', f'{self._sizeToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:margin-left', f'{self._sizeToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:margin-right', f'{self._sizeToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:page-width', f'{self._sizeToString(self._pageSize.width())}')
        pageLayoutPropertiesElement.set('fo:page-height', f'{self._sizeToString(self._pageSize.height())}')
        pageLayoutPropertiesElement.set('style:print-orientation', printOrientation)

        styleElement = ElementTree.SubElement(automaticStylesElement, 'style:style')
        styleElement.set('style:name', 'Mdp1')
        styleElement.set('style:family', 'drawing-page')

        drawingPagePropertiesElement = ElementTree.SubElement(styleElement, 'style:drawing-page-properties')
        drawingPagePropertiesElement.set('draw:background-size', 'full')
        drawingPagePropertiesElement.set('draw:fill', 'solid')
        drawingPagePropertiesElement.set('draw:fill-color', self._backgroundColor.name(QColor.NameFormat.HexRgb))

        # Master styles
        masterStylesElement = ElementTree.SubElement(stylesElement, 'office:master-styles')

        masterPageElement = ElementTree.SubElement(masterStylesElement, 'style:master-page')
        masterPageElement.set('style:name', 'Default')
        masterPageElement.set('style:page-layout-name', 'PM0')
        masterPageElement.set('draw:style-name', 'Mdp1')

        ElementTree.indent(stylesElement, space='  ')
        return f'{ElementTree.tostring(stylesElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeMarkerStyles(self, element: ElementTree.Element) -> None:
        markerElement = ElementTree.SubElement(element, 'draw:marker')
        markerElement.set('draw:name', 'Circle')
        markerElement.set('svg:viewBox', '0 0 1131 1131')
        markerElement.set('svg:d', 'M462 1118l-102-29-102-51-93-72-72-93-51-102-29-102-13-105 13-102 29-106 51-102 '
                                   '72-89 93-72 102-50 102-34 106-9 101 9 106 34 98 50 93 72 72 89 51 102 29 106 13 '
                                   '102-13 105-29 102-51 102-72 93-93 72-98 51-106 29-101 13z')

        markerElement = ElementTree.SubElement(element, 'draw:marker')
        markerElement.set('draw:name', 'Arrowheads_20_2')
        markerElement.set('draw:display-name', 'Arrowheads 2')
        markerElement.set('svg:viewBox', '0 0 20 20')
        markerElement.set('svg:d', 'M0 20l10-20 10 20z')

    def _writeStrokeDashStyles(self, element: ElementTree.Element) -> None:
        strokeDashElement = ElementTree.SubElement(element, 'draw:stroke-dash')
        strokeDashElement.set('draw:name', 'Dash_20__28_Rounded_29_')
        strokeDashElement.set('draw:display-name', 'Dash (Rounded)')
        strokeDashElement.set('draw:style', 'round')
        strokeDashElement.set('draw:dots1', '1')
        strokeDashElement.set('draw:dots1-length', '201%')
        strokeDashElement.set('draw:distance', '199%')

        strokeDashElement = ElementTree.SubElement(element, 'draw:stroke-dash')
        strokeDashElement.set('draw:name', 'Dot_20__28_Rounded_29_')
        strokeDashElement.set('draw:display-name', 'Dot (Rounded)')
        strokeDashElement.set('draw:style', 'round')
        strokeDashElement.set('draw:dots1', '1')
        strokeDashElement.set('draw:dots1-length', '1%')
        strokeDashElement.set('draw:distance', '199%')

        strokeDashElement = ElementTree.SubElement(element, 'draw:stroke-dash')
        strokeDashElement.set('draw:name', 'Dash_20_Dot_20__28_Rounded_29_')
        strokeDashElement.set('draw:display-name', 'Dash Dot (Rounded)')
        strokeDashElement.set('draw:style', 'round')
        strokeDashElement.set('draw:dots1', '1')
        strokeDashElement.set('draw:dots1-length', '201%')
        strokeDashElement.set('draw:dots2', '1')
        strokeDashElement.set('draw:dots2-length', '1%')
        strokeDashElement.set('draw:distance', '199%')

        strokeDashElement = ElementTree.SubElement(element, 'draw:stroke-dash')
        strokeDashElement.set('draw:name', 'Dash_20_Dot_20_Dot_20__28_Rounded_29_')
        strokeDashElement.set('draw:display-name', 'Dash Dot Dot (Rounded)')
        strokeDashElement.set('draw:style', 'round')
        strokeDashElement.set('draw:dots1', '1')
        strokeDashElement.set('draw:dots1-length', '201%')
        strokeDashElement.set('draw:dots2', '2')
        strokeDashElement.set('draw:dots2-length', '1%')
        strokeDashElement.set('draw:distance', '199%')

    # ==================================================================================================================

    def _writeContent(self) -> str:
        contentElement = ElementTree.Element('office:document-content')
        contentElement.set('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        contentElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        contentElement.set('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        contentElement.set('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        contentElement.set('manifest:version', '1.3')

        ElementTree.SubElement(contentElement, 'office:scripts')
        ElementTree.SubElement(contentElement, 'office:font-face-decls')

        # Automatic styles
        automaticStylesElement = ElementTree.SubElement(contentElement, 'office:automatic-styles')

        styleElement = ElementTree.SubElement(automaticStylesElement, 'style:style')
        styleElement.set('style:name', 'dp')
        styleElement.set('style:family', 'drawing-page')

        for page in self._pagesToExport:
            self._writeItemStyles(automaticStylesElement, page.items(), 0)

        # Document body
        bodyElement = ElementTree.SubElement(contentElement, 'office:body')
        drawingElement = ElementTree.SubElement(bodyElement, 'office:drawing')
        for page in self._pagesToExport:
            pageElement = ElementTree.SubElement(drawingElement, 'draw:page')
            pageElement.set('draw:name', page.name())
            pageElement.set('draw:style-name', 'dp')
            pageElement.set('draw:master-page-name', 'Default')
            self._writeItemContent(pageElement, page.items(), 0)

        ElementTree.indent(contentElement, space='  ')
        return f'{ElementTree.tostring(contentElement, encoding="unicode", xml_declaration=True)}\n'

    # ==================================================================================================================

    def _writeItemStyles(self, element: ElementTree.Element, items: list[DrawingItem], index: int) -> int:
        for item in items:
            if (isinstance(item, DrawingLineItem)):
                index = self._writeLineItemStyle(element, item, index)
            elif (isinstance(item, DrawingCurveItem)):
                index = self._writeCurveItemStyle(element, item, index)
            elif (isinstance(item, DrawingPolylineItem)):
                index = self._writePolylineItemStyle(element, item, index)
            elif (isinstance(item, DrawingTextRectItem)):
                index = self._writeTextRectItemStyle(element, item, index)
            elif (isinstance(item, DrawingRectItem)):
                index = self._writeRectItemStyle(element, item, index)
            elif (isinstance(item, DrawingTextEllipseItem)):
                index = self._writeTextEllipseItemStyle(element, item, index)
            elif (isinstance(item, DrawingEllipseItem)):
                index = self._writeEllipseItemStyle(element, item, index)
            elif (isinstance(item, DrawingPolygonItem)):
                index = self._writePolygonItemStyle(element, item, index)
            elif (isinstance(item, DrawingTextItem)):
                index = self._writeTextItemStyle(element, item, index)
            elif (isinstance(item, DrawingPathItem)):
                index = self._writePathItemStyle(element, item, index)
            elif (isinstance(item, DrawingItemGroup)):
                index = self._writeGroupItemStyle(element, item, index)
        return index

    def _writeLineItemStyle(self, element: ElementTree.Element, item: DrawingLineItem, index: int) -> int:
        styleElement = ElementTree.SubElement(element, 'style:style')
        styleElement.set('style:name', f'item{index}Style')
        styleElement.set('style:family', 'graphic')

        graphicPropertiesElement = ElementTree.SubElement(styleElement, 'style:graphic-properties')

        self._writePenAndBrush(graphicPropertiesElement, QBrush(Qt.GlobalColor.transparent), item.pen())
        self._writeArrows(graphicPropertiesElement, item.startArrow(), item.endArrow())

        return index + 1

    def _writeCurveItemStyle(self, element: ElementTree.Element, item: DrawingCurveItem, index: int) -> int:
        return index + 1

    def _writePolylineItemStyle(self, element: ElementTree.Element, item: DrawingPolylineItem, index: int) -> int:
        return index + 1

    def _writeRectItemStyle(self, element: ElementTree.Element, item: DrawingRectItem, index: int) -> int:
        styleElement = ElementTree.SubElement(element, 'style:style')
        styleElement.set('style:name', f'item{index}Style')
        styleElement.set('style:family', 'graphic')

        graphicPropertiesElement = ElementTree.SubElement(styleElement, 'style:graphic-properties')

        self._writePenAndBrush(graphicPropertiesElement, item.brush(), item.pen())

        return index + 1

    def _writeEllipseItemStyle(self, element: ElementTree.Element, item: DrawingEllipseItem, index: int) -> int:
        return index + 1

    def _writePolygonItemStyle(self, element: ElementTree.Element, item: DrawingPolygonItem, index: int) -> int:
        return index + 1

    def _writeTextItemStyle(self, element: ElementTree.Element, item: DrawingTextItem, index: int) -> int:
        return index + 1

    def _writeTextRectItemStyle(self, element: ElementTree.Element, item: DrawingTextRectItem, index: int) -> int:
        return index + 1

    def _writeTextEllipseItemStyle(self, element: ElementTree.Element, item: DrawingTextEllipseItem, index: int) -> int:
        return index + 1

    def _writePathItemStyle(self, element: ElementTree.Element, item: DrawingPathItem, index: int) -> int:
        return index + 1

    def _writeGroupItemStyle(self, element: ElementTree.Element, item: DrawingItemGroup, index: int) -> int:
        return index + 1

    def _writePenAndBrush(self, element: ElementTree.Element, brush: QBrush, pen: QPen) -> None:
        # Brush
        alpha = brush.color().alpha()
        if (alpha != 0):
            element.set('draw:fill', 'solid')
            color = QColor(brush.color())
            color.setAlpha(255)
            element.set('draw:fill-color', color.name(QColor.NameFormat.HexRgb))
            if (alpha != 255):
                element.set('draw:opacity', f'{alpha / 255 * 100:.1f}%')
        else:
            element.set('draw:fill', 'none')

        # Pen
        alpha = pen.brush().color().alpha()
        if (alpha != 0 and pen.style() != Qt.PenStyle.NoPen):
            element.set('draw:stroke', 'solid' if (pen.style() == Qt.PenStyle.SolidLine) else 'dash')

            color = QColor(pen.brush().color())
            color.setAlpha(255)
            element.set('svg:stroke-color', color.name(QColor.NameFormat.HexRgb))
            if (alpha != 255):
                element.set('svg:stroke-opacity', f'{alpha / 255 * 100:.1f}%')

            element.set('svg:stroke-width', f'{self._penWidthToString(pen.widthF())}')

            match (pen.style()):
                case Qt.PenStyle.DashLine:
                    element.set('draw:stroke-dash', 'Dash_20__28_Rounded_29_')
                case Qt.PenStyle.DotLine:
                    element.set('draw:stroke-dash', 'Dot_20__28_Rounded_29_')
                case Qt.PenStyle.DashDotLine:
                    element.set('draw:stroke-dash', 'Dash_20_Dot_20__28_Rounded_29_')
                case Qt.PenStyle.DashDotDotLine:
                    element.set('draw:stroke-dash', 'Dash_20_Dot_20_Dot_20__28_Rounded_29_')

            match (pen.capStyle()):
                case Qt.PenCapStyle.SquareCap:
                    element.set('svg:stroke-linecap', 'square')
                case Qt.PenCapStyle.RoundCap:
                    element.set('svg:stroke-linecap', 'round')

            match (pen.joinStyle()):
                case Qt.PenJoinStyle.BevelJoin:
                    element.set('draw:stroke-linejoin', 'bevel')
                case Qt.PenJoinStyle.RoundJoin:
                    element.set('draw:stroke-linejoin', 'round')
        else:
            element.set('draw:stroke', 'none')

    def _writeArrows(self, element: ElementTree.Element, startArrow: DrawingArrow, endArrow: DrawingArrow) -> None:
        if (startArrow.style() != DrawingArrow.Style.NoStyle):
            if (startArrow.style() in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
                element.set('draw:marker-start', 'Circle')
                element.set('draw:marker-start-width', self._sizeToString(startArrow.size()))
                element.set('draw:marker-start-center', 'true')
            else:
                element.set('draw:marker-start', 'Arrowheads_20_2')
                element.set('draw:marker-start-width', self._sizeToString(startArrow.size() / 2 * 1.5))
                element.set('draw:marker-start-center', 'false')

        if (endArrow.style() != DrawingArrow.Style.NoStyle):
            if (endArrow.style() in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
                element.set('draw:marker-end', 'Circle')
                element.set('draw:marker-end-width', self._sizeToString(endArrow.size()))
                element.set('draw:marker-end-center', 'true')
            else:
                element.set('draw:marker-end', 'Arrowheads_20_2')
                element.set('draw:marker-end-width', self._sizeToString(endArrow.size() / 2 * 1.5))
                element.set('draw:marker-end-center', 'false')

    # ==================================================================================================================

    def _writeItemContent(self, element: ElementTree.Element, items: list[DrawingItem], index: int) -> int:
        for item in items:
            if (isinstance(item, DrawingLineItem)):
                index = self._writeLineItemContent(element, item, index)
            elif (isinstance(item, DrawingCurveItem)):
                index = self._writeCurveItemContent(element, item, index)
            elif (isinstance(item, DrawingPolylineItem)):
                index = self._writePolylineItemContent(element, item, index)
            elif (isinstance(item, DrawingTextRectItem)):
                index = self._writeTextRectItemContent(element, item, index)
            elif (isinstance(item, DrawingRectItem)):
                index = self._writeRectItemContent(element, item, index)
            elif (isinstance(item, DrawingTextEllipseItem)):
                index = self._writeTextEllipseItemContent(element, item, index)
            elif (isinstance(item, DrawingEllipseItem)):
                index = self._writeEllipseItemContent(element, item, index)
            elif (isinstance(item, DrawingPolygonItem)):
                index = self._writePolygonItemContent(element, item, index)
            elif (isinstance(item, DrawingTextItem)):
                index = self._writeTextItemContent(element, item, index)
            elif (isinstance(item, DrawingPathItem)):
                index = self._writePathItemContent(element, item, index)
            elif (isinstance(item, DrawingItemGroup)):
                index = self._writeGroupItemContent(element, item, index)
        return index

    def _writeLineItemContent(self, element: ElementTree.Element, item: DrawingLineItem, index: int) -> int:
        lineElement = ElementTree.SubElement(element, 'draw:line')

        p1 = item.mapToScene(item.line().p1())
        p2 = item.mapToScene(item.line().p2())
        lineElement.set('svg:x1', f'{self._positionToString(p1.x())}')
        lineElement.set('svg:y1', f'{self._positionToString(p1.y())}')
        lineElement.set('svg:x2', f'{self._positionToString(p2.x())}')
        lineElement.set('svg:y2', f'{self._positionToString(p2.y())}')

        lineElement.set('draw:style-name', f'item{index}Style')

        return index + 1

    def _writeCurveItemContent(self, element: ElementTree.Element, item: DrawingCurveItem, index: int) -> int:
        return index + 1

    def _writePolylineItemContent(self, element: ElementTree.Element, item: DrawingPolylineItem, index: int) -> int:
        return index + 1

    def _writeRectItemContent(self, element: ElementTree.Element, item: DrawingRectItem, index: int) -> int:
        rectElement = ElementTree.SubElement(element, 'draw:rect')

        rect = item.mapRectToScene(item.rect())
        rectElement.set('svg:x', f'{self._positionToString(rect.left())}')
        rectElement.set('svg:y', f'{self._positionToString(rect.top())}')
        rectElement.set('svg:width', f'{self._sizeToString(rect.width())}')
        rectElement.set('svg:height', f'{self._sizeToString(rect.height())}')

        if (item.cornerRadius() != 0):
            rectElement.set('svg:rx', f'{self._sizeToString(item.cornerRadius())}')
            rectElement.set('svg:ry', f'{self._sizeToString(item.cornerRadius())}')

        rectElement.set('draw:style-name', f'item{index}Style')

        return index + 1

    def _writeEllipseItemContent(self, element: ElementTree.Element, item: DrawingEllipseItem, index: int) -> int:
        return index + 1

    def _writePolygonItemContent(self, element: ElementTree.Element, item: DrawingPolygonItem, index: int) -> int:
        return index + 1

    def _writeTextItemContent(self, element: ElementTree.Element, item: DrawingTextItem, index: int) -> int:
        return index + 1

    def _writeTextRectItemContent(self, element: ElementTree.Element, item: DrawingTextRectItem, index: int) -> int:
        return index + 1

    def _writeTextEllipseItemContent(self, element: ElementTree.Element, item: DrawingTextEllipseItem,
                                     index: int) -> int:
        return index + 1

    def _writePathItemContent(self, element: ElementTree.Element, item: DrawingPathItem, index: int) -> int:
        return index + 1

    def _writeGroupItemContent(self, element: ElementTree.Element, item: DrawingItemGroup, index: int) -> int:
        return index + 1

    # ==================================================================================================================

    def _positionToString(self, position: float) -> str:
        return f'{(position + self._pageMargin) * self._scale}{self._units}'

    def _sizeToString(self, size: float) -> str:
        return f'{size * self._scale}{self._units}'

    def _penWidthToString(self, size: float) -> str:
        penWidth = size * self._scale
        penWidthIn = penWidth if (self._units == 'in') else penWidth * 25.4
        penWidthPoints = penWidthIn * 72

        # Round the pen width to the nearest default value supported by LibreOffice if it is within 11%
        supportedPenWidthsPoints = [0.5, 0.8, 1.0, 1.5, 2.3, 3.0, 4.5, 6.0]
        for supportedPenWidthPoints in supportedPenWidthsPoints:
            if (abs(1 - penWidthPoints / supportedPenWidthPoints) < 0.11):
                penWidthIn = supportedPenWidthPoints / 72

        return f'{penWidthIn}in' if (self._units == 'in') else f'{penWidthIn * 25.4}mm'
