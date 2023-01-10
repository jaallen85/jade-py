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

import math
from xml.etree import ElementTree
from zipfile import ZipFile
from PySide6.QtCore import Qt, QLineF, QMarginsF, QPointF, QRectF, QSizeF
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPolygonF
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawinggroupitem import DrawingGroupItem
from ..drawing.drawingitem import DrawingItem
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

        self._itemIndex: int = 0

        # Determine master page attributes
        self._pagesToExport: list[DrawingPageWidget] = []
        self._pageSize: QSizeF = QSizeF()
        self._pageMargin: float = 0.0

        currentPage = self._drawing.currentPage()
        if (self._exportEntireDocument):
            self._pagesToExport = self._drawing.pages()

            # LibreOffice only supports one master page (despite the Open Document spec supporting multiple).
            # So all pages in the document must be the same size and have the same margins.
            # Here we choose a page size and margin that is large enough to fit all the pages in the document.
            for page in self._drawing.pages():
                self._pageSize.setWidth(max(self._pageSize.width(), page.pageSize().width()))
                self._pageSize.setHeight(max(self._pageSize.height(), page.pageSize().height()))
                self._pageMargin = max(self._pageMargin, page.pageMargin())

        elif (currentPage is not None):
            self._pagesToExport = [currentPage]

            # Since we're only exporting a single page, use its size and margins for the master page
            self._pageSize = currentPage.pageSize()
            self._pageMargin = currentPage.pageMargin()

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

        return f'{ElementTree.tostring(manifestElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeMeta(self) -> str:
        metaElement = ElementTree.Element('office:document-meta')
        metaElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        metaElement.set('manifest:version', '1.3')

        ElementTree.SubElement(metaElement, 'office:meta')

        return f'{ElementTree.tostring(metaElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeSettings(self) -> str:
        settingsElement = ElementTree.Element('office:document-settings')
        settingsElement.set('xmlns:config', 'urn:oasis:names:tc:opendocument:xmlns:config:1.0')
        settingsElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        settingsElement.set('manifest:version', '1.3')

        ElementTree.SubElement(settingsElement, 'office:settings')

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
        pageLayoutPropertiesElement.set('fo:margin-top', f'{self._lengthToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:margin-bottom', f'{self._lengthToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:margin-left', f'{self._lengthToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:margin-right', f'{self._lengthToString(self._pageMargin)}')
        pageLayoutPropertiesElement.set('fo:page-width', f'{self._lengthToString(self._pageSize.width())}')
        pageLayoutPropertiesElement.set('fo:page-height', f'{self._lengthToString(self._pageSize.height())}')
        pageLayoutPropertiesElement.set('style:print-orientation', printOrientation)

        styleElement = ElementTree.SubElement(automaticStylesElement, 'style:style')
        styleElement.set('style:name', 'Mdp1')
        styleElement.set('style:family', 'drawing-page')

        drawingPagePropertiesElement = ElementTree.SubElement(styleElement, 'style:drawing-page-properties')
        drawingPagePropertiesElement.set('draw:background-size', 'full')
        drawingPagePropertiesElement.set('draw:fill', 'solid')
        drawingPagePropertiesElement.set('draw:fill-color', '#FFFFFF')

        # Master styles
        masterStylesElement = ElementTree.SubElement(stylesElement, 'office:master-styles')

        masterPageElement = ElementTree.SubElement(masterStylesElement, 'style:master-page')
        masterPageElement.set('style:name', 'Default')
        masterPageElement.set('style:page-layout-name', 'PM0')
        masterPageElement.set('draw:style-name', 'Mdp1')

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
        contentElement.set('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        contentElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        contentElement.set('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        contentElement.set('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        contentElement.set('xmlns:text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')
        contentElement.set('manifest:version', '1.3')

        ElementTree.SubElement(contentElement, 'office:scripts')
        ElementTree.SubElement(contentElement, 'office:font-face-decls')

        # Automatic styles
        automaticStylesElement = ElementTree.SubElement(contentElement, 'office:automatic-styles')

        for pageIndex, page in enumerate(self._pagesToExport):
            styleElement = ElementTree.SubElement(automaticStylesElement, 'style:style')
            styleElement.set('style:name', f'dp{pageIndex}')
            styleElement.set('style:family', 'drawing-page')

            drawingPagePropertiesElement = ElementTree.SubElement(styleElement, 'style:drawing-page-properties')
            drawingPagePropertiesElement.set('draw:background-size', 'full')
            drawingPagePropertiesElement.set('draw:fill', 'solid')
            drawingPagePropertiesElement.set('draw:fill-color',
                                             page.backgroundBrush().color().name(QColor.NameFormat.HexRgb))

        # Document body
        bodyElement = ElementTree.SubElement(contentElement, 'office:body')
        drawingElement = ElementTree.SubElement(bodyElement, 'office:drawing')
        for pageIndex, page in enumerate(self._pagesToExport):
            pageElement = ElementTree.SubElement(drawingElement, 'draw:page')
            pageElement.set('draw:name', page.name())
            pageElement.set('draw:style-name', f'dp{pageIndex}')
            pageElement.set('draw:master-page-name', 'Default')
            self._writeItems(pageElement, automaticStylesElement, page.items())

        return f'{ElementTree.tostring(contentElement, encoding="unicode", xml_declaration=True)}\n'

    # ==================================================================================================================

    def _writeItems(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                    items: list[DrawingItem]) -> None:
        for item in items:
            if (isinstance(item, DrawingLineItem)):
                self._writeLineItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingCurveItem)):
                self._writeCurveItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingPolylineItem)):
                self._writePolylineItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingTextRectItem)):
                self._writeTextRectItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingRectItem)):
                self._writeRectItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingTextEllipseItem)):
                self._writeTextEllipseItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingEllipseItem)):
                self._writeEllipseItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingPolygonItem)):
                self._writePolygonItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingTextItem)):
                self._writeTextItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingPathItem)):
                self._writePathItem(pageElement, automaticStylesElement, item)
            elif (isinstance(item, DrawingGroupItem)):
                self._writeGroupItem(pageElement, automaticStylesElement, item)

    def _writeLineItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                       item: DrawingLineItem) -> None:
        # Line
        lineElement = ElementTree.SubElement(pageElement, 'draw:line')

        self._writeTransform(lineElement, QPointF(0, 0), 0, False)

        p1 = item.mapToScene(item.line().p1())
        p2 = item.mapToScene(item.line().p2())
        lineElement.set('svg:x1', f'{self._lengthToString(p1.x())}')
        lineElement.set('svg:y1', f'{self._lengthToString(p1.y())}')
        lineElement.set('svg:x2', f'{self._lengthToString(p2.x())}')
        lineElement.set('svg:y2', f'{self._lengthToString(p2.y())}')

        graphicStyleName, _, _ = self._getUniqueItemStyleNames()
        lineElement.set('draw:style-name', graphicStyleName)

        # Style
        startArrow, endArrow = None, None
        lineLength = QLineF(p1, p2).length()
        if (item.startArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.startArrow().size()):
            startArrow = item.startArrow()
        if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.endArrow().size()):
            endArrow = item.endArrow()

        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=QBrush(Qt.GlobalColor.transparent),
                                pen=item.pen(), startArrow=startArrow, endArrow=endArrow)

    def _writeCurveItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                        item: DrawingCurveItem) -> None:
        curve = item.curve()
        if (curve.size() == 4):
            pathElement = ElementTree.SubElement(pageElement, 'draw:path')

            # Curve
            p1 = curve.at(0)
            cp1 = curve.at(1)
            cp2 = curve.at(2)
            p2 = curve.at(3)

            path = QPainterPath()
            path.moveTo(p1)
            path.cubicTo(cp1, cp2, p2)
            rect = path.boundingRect()

            self._writeTransform(pathElement, item.position(), item.rotation(), item.isFlipped())
            self._writeRect(pathElement, rect)
            self._writePath(pathElement, path, rect)

            graphicStyleName, _, _ = self._getUniqueItemStyleNames()
            pathElement.set('draw:style-name', graphicStyleName)

            # Style
            lineLength = QLineF(curve.at(0), curve.at(curve.size() - 1)).length()
            if (item.startArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.startArrow().size()):
                startArrow = item.startArrow()
            if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.endArrow().size()):
                endArrow = item.endArrow()

            self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=QBrush(Qt.GlobalColor.transparent),
                                    pen=item.pen(), startArrow=startArrow, endArrow=endArrow)

    def _writePolylineItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                           item: DrawingPolylineItem) -> None:
        polylineElement = ElementTree.SubElement(pageElement, 'draw:polyline')

        # Polyline
        polyline = item.polyline()
        sceneBoundingRect = item.mapPolygonToScene(polyline).boundingRect()

        self._writeTransform(polylineElement, QPointF(0, 0), 0, False)
        self._writeRect(polylineElement, sceneBoundingRect)
        self._writePoints(polylineElement, polyline)

        graphicStyleName, _, _ = self._getUniqueItemStyleNames()
        polylineElement.set('draw:style-name', graphicStyleName)

        # Style
        startArrow, endArrow = None, None
        if (polyline.size() >= 2):
            firstLength = QLineF(polyline.at(0), polyline.at(1)).length()
            lastLength = QLineF(polyline.at(polyline.size() - 1), polyline.at(polyline.size() - 2)).length()
            if (item.startArrow().style() != DrawingArrow.Style.NoStyle and firstLength >= item.startArrow().size()):
                startArrow = item.startArrow()
            if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lastLength >= item.endArrow().size()):
                endArrow = item.endArrow()

        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=QBrush(Qt.GlobalColor.transparent),
                                pen=item.pen(), startArrow=startArrow, endArrow=endArrow)

    def _writeRectItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                       item: DrawingRectItem) -> None:
        # Rect
        rectElement = ElementTree.SubElement(pageElement, 'draw:rect')

        self._writeTransform(rectElement, QPointF(0, 0), 0, False)
        self._writeRect(rectElement, item.mapRectToScene(item.rect()))

        if (item.cornerRadius() != 0):
            rectElement.set('svg:rx', f'{self._lengthToString(item.cornerRadius())}')
            rectElement.set('svg:ry', f'{self._lengthToString(item.cornerRadius())}')

        graphicStyleName, _, _ = self._getUniqueItemStyleNames()
        rectElement.set('draw:style-name', graphicStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=item.brush(), pen=item.pen())

    def _writeEllipseItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                          item: DrawingEllipseItem) -> None:
        ellipseElement = ElementTree.SubElement(pageElement, 'draw:ellipse')

        self._writeTransform(ellipseElement, QPointF(0, 0), 0, False)

        ellipse = item.mapRectToScene(item.ellipse())
        center = ellipse.center()
        ellipseElement.set('svg:cx', f'{self._lengthToString(center.x())}')
        ellipseElement.set('svg:cy', f'{self._lengthToString(center.y())}')
        ellipseElement.set('svg:rx', f'{self._lengthToString(ellipse.width() / 2)}')
        ellipseElement.set('svg:ry', f'{self._lengthToString(ellipse.height() / 2)}')

        graphicStyleName, _, _ = self._getUniqueItemStyleNames()
        ellipseElement.set('draw:style-name', graphicStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=item.brush(), pen=item.pen())

    def _writePolygonItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                          item: DrawingPolygonItem) -> None:
        polygonElement = ElementTree.SubElement(pageElement, 'draw:polygon')

        polygon = item.polygon()
        sceneBoundingRect = item.mapPolygonToScene(polygon).boundingRect()

        self._writeTransform(polygonElement, QPointF(0, 0), 0, False)
        self._writeRect(polygonElement, sceneBoundingRect)
        self._writePoints(polygonElement, polygon)

        graphicStyleName, _, _ = self._getUniqueItemStyleNames()
        polygonElement.set('draw:style-name', graphicStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=item.brush(), pen=item.pen())

    def _writeTextItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                       item: DrawingTextItem) -> None:
        # Rect
        rectElement = ElementTree.SubElement(pageElement, 'draw:rect')

        self._writeTransform(rectElement, item.position(), item.rotation(), item.isFlipped())

        rect = item.boundingRect()
        self._writeRect(rectElement, rect)

        graphicStyleName, paragraphStyleName, textStyleName = self._getUniqueItemStyleNames()
        rectElement.set('draw:style-name', graphicStyleName)
        rectElement.set('draw:text-style-name', paragraphStyleName)

        # Text
        self._writeText(rectElement, item.caption(), paragraphStyleName, textStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, QBrush(Qt.GlobalColor.transparent),
                                QPen(Qt.PenStyle.NoPen), item.alignment(), rect.size(), QMarginsF(0, 0, 0, 0))
        self._writeParagraphStyle(automaticStylesElement, paragraphStyleName, item.font(), item.alignment(),
                                  item.brush())
        self._writeTextStyle(automaticStylesElement, textStyleName, item.font(), item.brush())

    def _writeTextRectItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                           item: DrawingTextRectItem) -> None:
        # Rect
        rectElement = ElementTree.SubElement(pageElement, 'draw:rect')

        self._writeTransform(rectElement, item.position(), item.rotation(), item.isFlipped())

        rect = item.rect()
        self._writeRect(rectElement, rect)

        if (item.cornerRadius() != 0):
            rectElement.set('svg:rx', f'{self._lengthToString(item.cornerRadius())}')
            rectElement.set('svg:ry', f'{self._lengthToString(item.cornerRadius())}')

        graphicStyleName, paragraphStyleName, textStyleName = self._getUniqueItemStyleNames()
        rectElement.set('draw:style-name', graphicStyleName)
        rectElement.set('draw:text-style-name', paragraphStyleName)

        # Text
        self._writeText(rectElement, item.caption(), paragraphStyleName, textStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, item.brush(), item.pen(),
                                Qt.AlignmentFlag.AlignCenter, rect.size(), QMarginsF(0, 0, 0, 0))
        self._writeParagraphStyle(automaticStylesElement, paragraphStyleName, item.font(),
                                  Qt.AlignmentFlag.AlignCenter, item.textBrush())
        self._writeTextStyle(automaticStylesElement, textStyleName, item.font(), item.textBrush())

    def _writeTextEllipseItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                              item: DrawingTextEllipseItem) -> None:
        # Ellipse
        ellipseElement = ElementTree.SubElement(pageElement, 'draw:ellipse')

        self._writeTransform(ellipseElement, item.position(), item.rotation(), item.isFlipped())

        ellipse = item.ellipse()
        center = ellipse.center()
        ellipseElement.set('svg:cx', f'{self._lengthToString(center.x())}')
        ellipseElement.set('svg:cy', f'{self._lengthToString(center.y())}')
        ellipseElement.set('svg:rx', f'{self._lengthToString(ellipse.width() / 2)}')
        ellipseElement.set('svg:ry', f'{self._lengthToString(ellipse.height() / 2)}')

        graphicStyleName, paragraphStyleName, textStyleName = self._getUniqueItemStyleNames()
        ellipseElement.set('draw:style-name', graphicStyleName)
        ellipseElement.set('draw:text-style-name', paragraphStyleName)

        # Text
        self._writeText(ellipseElement, item.caption(), paragraphStyleName, textStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, item.brush(), item.pen(),
                                Qt.AlignmentFlag.AlignCenter, ellipse.size(), QMarginsF(0, 0, 0, 0))
        self._writeParagraphStyle(automaticStylesElement, paragraphStyleName, item.font(),
                                  Qt.AlignmentFlag.AlignCenter, item.textBrush())
        self._writeTextStyle(automaticStylesElement, textStyleName, item.font(), item.textBrush())

    def _writePathItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                       item: DrawingPathItem) -> None:
        pathElement = ElementTree.SubElement(pageElement, 'draw:path')

        # Path
        self._writeTransform(pathElement, item.position(), item.rotation(), item.isFlipped())
        self._writeRect(pathElement, item.rect())
        self._writePath(pathElement, item.path(), item.pathRect())

        graphicStyleName, _, _ = self._getUniqueItemStyleNames()
        pathElement.set('draw:style-name', graphicStyleName)

        # Style
        self._writeGraphicStyle(automaticStylesElement, graphicStyleName, brush=QBrush(Qt.GlobalColor.transparent),
                                pen=item.pen())

    def _writeGroupItem(self, pageElement: ElementTree.Element, automaticStylesElement: ElementTree.Element,
                        item: DrawingGroupItem) -> None:
        groupElement = ElementTree.SubElement(pageElement, 'draw:g')

        # draw:g element does not support the draw:transform attribute, so we must apply the group transform to each
        # of its items
        for child in item.items():
            child.setPosition(item.mapToScene(child.position()))
            child.setRotation(child.rotation() + item.rotation())
            if (item.isFlipped()):
                child.setFlipped(not child.isFlipped())

        self._writeItems(groupElement, automaticStylesElement, item.items())

        # Undo the child item transforms to leave things as we found them
        for child in item.items():
            child.setPosition(item.mapFromScene(child.position()))
            child.setRotation(child.rotation() - item.rotation())
            if (item.isFlipped()):
                child.setFlipped(not child.isFlipped())

    # ==================================================================================================================

    def _writeGraphicStyle(self, element: ElementTree.Element, name: str, brush: QBrush | None = None,
                           pen: QPen | None = None, textAlignment: Qt.AlignmentFlag | None = None,
                           textBoxMinimumSize: QSizeF | None = None, textBoxPadding: QMarginsF | None = None,
                           startArrow: DrawingArrow | None = None, endArrow: DrawingArrow | None = None) -> None:
        styleElement = ElementTree.SubElement(element, 'style:style')
        styleElement.set('style:name', name)
        styleElement.set('style:family', 'graphic')

        graphicPropertiesElement = ElementTree.SubElement(styleElement, 'style:graphic-properties')
        if (isinstance(brush, QBrush)):
            self._writeBrush(graphicPropertiesElement, brush)
        if (isinstance(pen, QPen)):
            self._writePen(graphicPropertiesElement, pen)
        if (isinstance(textAlignment, Qt.AlignmentFlag)):
            self._writeTextAlignment(graphicPropertiesElement, textAlignment)
        if (isinstance(textBoxMinimumSize, QSizeF)):
            self._writeTextBoxMinimumSize(graphicPropertiesElement, textBoxMinimumSize)
        if (isinstance(textBoxPadding, QMarginsF)):
            self._writeTextBoxPadding(graphicPropertiesElement, textBoxPadding)
        if (isinstance(startArrow, DrawingArrow)):
            self._writeStartArrow(graphicPropertiesElement, startArrow)
        if (isinstance(endArrow, DrawingArrow)):
            self._writeEndArrow(graphicPropertiesElement, endArrow)

    def _writeBrush(self, element: ElementTree.Element, brush: QBrush) -> None:
        color = QColor(brush.color())
        alpha = color.alpha()
        if (alpha != 0 and brush.style() != Qt.BrushStyle.NoBrush):
            element.set('draw:fill', 'solid')

            color.setAlpha(255)
            element.set('draw:fill-color', color.name(QColor.NameFormat.HexRgb))

            if (alpha != 255):
                element.set('draw:opacity', f'{alpha / 255 * 100:.1f}%')
        else:
            element.set('draw:fill', 'none')

    def _writePen(self, element: ElementTree.Element, pen: QPen) -> None:
        color = QColor(pen.brush().color())
        alpha = color.alpha()
        if (alpha != 0 and pen.style() != Qt.PenStyle.NoPen and pen.brush().style() != Qt.BrushStyle.NoBrush):
            element.set('draw:stroke', 'solid' if (pen.style() == Qt.PenStyle.SolidLine) else 'dash')

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

    def _writeTextAlignment(self, element: ElementTree.Element, alignment: Qt.AlignmentFlag) -> None:
        horizontal = (alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
        if (horizontal & Qt.AlignmentFlag.AlignHCenter):
            element.set('draw:textarea-horizontal-align', 'center')
        elif (horizontal & Qt.AlignmentFlag.AlignRight):
            element.set('draw:textarea-horizontal-align', 'right')
        else:
            element.set('draw:textarea-horizontal-align', 'left')

        vertical = (alignment & Qt.AlignmentFlag.AlignVertical_Mask)
        if (vertical & Qt.AlignmentFlag.AlignVCenter):
            element.set('draw:textarea-vertical-align', 'middle')
        elif (vertical & Qt.AlignmentFlag.AlignBottom):
            element.set('draw:textarea-vertical-align', 'bottom')
        else:
            element.set('draw:textarea-vertical-align', 'top')

    def _writeTextBoxMinimumSize(self, element: ElementTree.Element, minimumSize: QSizeF) -> None:
        element.set('draw:auto-grow-width', 'false')
        element.set('draw:auto-grow-height', 'false')
        element.set('fo:min-width', self._lengthToString(minimumSize.width()))
        element.set('fo:min-height', self._lengthToString(minimumSize.height()))

    def _writeTextBoxPadding(self, element: ElementTree.Element, padding: QMarginsF) -> None:
        element.set('fo:padding-left', self._lengthToString(padding.left()))
        element.set('fo:padding-top', self._lengthToString(padding.top()))
        element.set('fo:padding-right', self._lengthToString(padding.right()))
        element.set('fo:padding-bottom', self._lengthToString(padding.bottom()))

    def _writeStartArrow(self, element: ElementTree.Element, arrow: DrawingArrow) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            if (arrow.style() in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
                element.set('draw:marker-start', 'Circle')
                element.set('draw:marker-start-width', self._lengthToString(arrow.size()))
                element.set('draw:marker-start-center', 'true')
            else:
                element.set('draw:marker-start', 'Arrowheads_20_2')
                element.set('draw:marker-start-width', self._lengthToString(arrow.size() / 2 * 1.5))
                element.set('draw:marker-start-center', 'false')

    def _writeEndArrow(self, element: ElementTree.Element, arrow: DrawingArrow) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            if (arrow.style() in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
                element.set('draw:marker-end', 'Circle')
                element.set('draw:marker-end-width', self._lengthToString(arrow.size()))
                element.set('draw:marker-end-center', 'true')
            else:
                element.set('draw:marker-end', 'Arrowheads_20_2')
                element.set('draw:marker-end-width', self._lengthToString(arrow.size() / 2 * 1.5))
                element.set('draw:marker-end-center', 'false')

    # ==================================================================================================================

    def _writeParagraphStyle(self, element: ElementTree.Element, name: str, font: QFont | None = None,
                             alignment: Qt.AlignmentFlag | None = None, textBrush: QBrush | None = None) -> None:
        styleElement = ElementTree.SubElement(element, 'style:style')
        styleElement.set('style:name', name)
        styleElement.set('style:family', 'paragraph')

        paragraphPropertiesElement = ElementTree.SubElement(styleElement, 'style:paragraph-properties')
        if (isinstance(alignment, Qt.AlignmentFlag)):
            horizontal = (alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
            if (horizontal & Qt.AlignmentFlag.AlignHCenter):
                paragraphPropertiesElement.set('fo:text-align', 'center')
            elif (horizontal & Qt.AlignmentFlag.AlignRight):
                paragraphPropertiesElement.set('fo:text-align', 'end')
            else:
                paragraphPropertiesElement.set('fo:text-align', 'start')

        textPropertiesElement = ElementTree.SubElement(styleElement, 'style:text-properties')
        if (isinstance(font, QFont)):
            self._writeFont(textPropertiesElement, font)
        if (isinstance(textBrush, QBrush)):
            self._writeTextBrush(textPropertiesElement, textBrush)

    def _writeTextStyle(self, element: ElementTree.Element, name: str, font: QFont | None = None,
                        textBrush: QBrush | None = None) -> None:
        styleElement = ElementTree.SubElement(element, 'style:style')
        styleElement.set('style:name', name)
        styleElement.set('style:family', 'text')

        textPropertiesElement = ElementTree.SubElement(styleElement, 'style:text-properties')
        if (isinstance(font, QFont)):
            self._writeFont(textPropertiesElement, font)
        if (isinstance(textBrush, QBrush)):
            self._writeTextBrush(textPropertiesElement, textBrush)

    def _writeFont(self, element: ElementTree.Element, font: QFont) -> None:
        # Font
        element.set('style:font-name', font.family())
        element.set('fo:font-size', self._lengthToString(font.pointSizeF()))

        element.set('fo:font-weight', 'bold' if (font.bold()) else 'normal')
        element.set('fo:font-style', 'italic' if (font.italic()) else 'normal')

        if (font.underline()):
            element.set('style:text-underline-style', 'solid')
            element.set('style:text-underline-mode', 'continuous')
            element.set('style:text-underline-type', 'single')
            element.set('style:text-underline-width', 'auto')
            element.set('style:text-underline-color', 'font-color')
        else:
            element.set('style:text-underline-style', 'none')

        if (font.strikeOut()):
            element.set('style:text-line-through-style', 'solid')
            element.set('style:text-line-through-mode', 'continuous')
            element.set('style:text-line-through-type', 'single')
            element.set('style:text-line-through-width', 'auto')
            element.set('style:text-line-through-color', 'font-color')
        else:
            element.set('style:text-line-through-style', 'none')

    def _writeTextBrush(self, element: ElementTree.Element, textBrush: QBrush) -> None:
        # Text color
        color = textBrush.color()
        alpha = color.alpha()
        if (alpha != 0 and textBrush.style() != Qt.BrushStyle.NoBrush):
            color.setAlpha(255)
            element.set('fo:color', color.name(QColor.NameFormat.HexRgb))

            if (alpha != 255):
                element.set('loext:opacity', f'{alpha / 255 * 100:.1f}%')

    # ==================================================================================================================

    def _writeTransform(self, element: ElementTree.Element, position: QPointF, rotation: int, flipped: bool) -> None:
        xStr = self._lengthToString(position.x() + self._pageMargin)
        yStr = self._lengthToString(position.y() + self._pageMargin)
        transformStr = f'translate ({xStr} {yStr})'

        if (flipped):
            transformStr = f'scale (-1 1) {transformStr}'
        if (rotation != 0):
            transformStr = f'rotate ({-rotation * math.pi / 2}) {transformStr}'

        element.set('draw:transform', transformStr)

    def _writeRect(self, element: ElementTree.Element, rect: QRectF) -> None:
        element.set('svg:x', f'{self._lengthToString(rect.left())}')
        element.set('svg:y', f'{self._lengthToString(rect.top())}')
        element.set('svg:width', f'{self._lengthToString(rect.width())}')
        element.set('svg:height', f'{self._lengthToString(rect.height())}')

    def _writePoints(self, element: ElementTree.Element, polygon: QPolygonF) -> None:
        pointsStr = ''
        for polygonIndex in range(polygon.count()):
            point = polygon.at(polygonIndex)
            pointsStr = f'{pointsStr} {point.x()},{point.y()}'

        boundingRect = polygon.boundingRect()
        element.set('svg:viewBox', f'{boundingRect.left()} {boundingRect.top()} '
                                   f'{boundingRect.width()} {boundingRect.height()}')
        element.set('draw:points', pointsStr.strip())

    def _writePath(self, element: ElementTree.Element, path: QPainterPath, pathRect: QRectF) -> None:
        pathStr = ''
        for index in range(path.elementCount()):
            pathElement = path.elementAt(index)
            match (pathElement.type):                                           # type: ignore
                case QPainterPath.ElementType.MoveToElement:
                    pathStr = f'{pathStr} M {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.LineToElement:
                    pathStr = f'{pathStr} L {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.CurveToElement:
                    pathStr = f'{pathStr} C {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.CurveToDataElement:
                    pathStr = f'{pathStr} {pathElement.x} {pathElement.y}'      # type: ignore

        element.set('svg:viewBox', f'{pathRect.left()} {pathRect.top()} {pathRect.width()} {pathRect.height()}')
        element.set('svg:d', pathStr.strip())

    def _writeText(self, element: ElementTree.Element, text: str, paragraphStyleName: str, textStyleName: str) -> None:
        for line in text.split('\n'):
            pElement = ElementTree.SubElement(element, 'text:p')
            pElement.set('text:style-name', paragraphStyleName)

            spanElement = ElementTree.SubElement(pElement, 'text:span')
            spanElement.set('text:style-name', textStyleName)
            spanElement.text = line

    # ==================================================================================================================

    def _lengthToString(self, length: float) -> str:
        return f'{length * self._scale}{self._units}'

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

    def _getUniqueItemStyleNames(self) -> tuple[str, str, str]:
        graphicStyleName = f'item{self._itemIndex}Style'
        paragraphStyleName = f'item{self._itemIndex}ParagraphStyle'
        textStyleName = f'item{self._itemIndex}TextStyle'
        self._itemIndex = self._itemIndex + 1
        return (graphicStyleName, paragraphStyleName, textStyleName)
