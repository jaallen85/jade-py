# vsdxwriter.py
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
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF, QSizeF
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen, QPolygonF
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitemgroup import DrawingItemGroup
from ..drawing.drawingpagewidget import DrawingPageWidget
from ..diagramwidget import DiagramWidget
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


class VsdxWriter:
    def __init__(self, drawing: DiagramWidget, exportEntireDocument: bool, scale: float, units: str) -> None:
        super().__init__()

        self._drawing: DiagramWidget = drawing
        self._exportEntireDocument: bool = exportEntireDocument
        self._scale: float = scale
        self._units: str = units.upper()

        self._pagesToExport: list[DrawingPageWidget] = []
        self._shapeIndex: int = 0
        self._shapeDepth: int = 0

        currentPage = self._drawing.currentPage()
        if (self._exportEntireDocument):
            self._pagesToExport = self._drawing.pages()
        elif (currentPage is not None):
            self._pagesToExport = [currentPage]

    # ==================================================================================================================

    def write(self, path: str) -> None:
        with ZipFile(path, mode='w') as vsdxArchive:
            vsdxArchive.writestr('[Content_Types].xml', self._writeContentTypes())

            vsdxArchive.writestr('_rels/.rels', self._writeRels())

            vsdxArchive.writestr('docProps/app.xml', self._writeApp())
            vsdxArchive.writestr('docProps/core.xml', self._writeCore())
            vsdxArchive.writestr('docProps/custom.xml', self._writeCustom())

            vsdxArchive.writestr('visio/pages/_rels/pages.xml.rels', self._writePagesRels())
            vsdxArchive.writestr('visio/pages/pages.xml', self._writePages())

            for pageIndex, page in enumerate(self._pagesToExport):
                vsdxArchive.writestr(f'visio/pages/page{pageIndex + 1}.xml', self._writePage(page))

            vsdxArchive.writestr('visio/_rels/document.xml.rels', self._writeDocumentRels())
            vsdxArchive.writestr('visio/document.xml', self._writeDocument())
            vsdxArchive.writestr('visio/windows.xml', self._writeWindows())

    # ==================================================================================================================

    def _writeContentTypes(self) -> str:
        typesElement = ElementTree.Element('Types')
        typesElement.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/content-types')

        defaultElement = ElementTree.SubElement(typesElement, 'Default')
        defaultElement.set('Extension', 'rels')
        defaultElement.set('ContentType', 'application/vnd.openxmlformats-package.relationships+xml')

        defaultElement = ElementTree.SubElement(typesElement, 'Default')
        defaultElement.set('Extension', 'xml')
        defaultElement.set('ContentType', 'application/xml')

        overrideElement = ElementTree.SubElement(typesElement, 'Override')
        overrideElement.set('PartName', '/visio/document.xml')
        overrideElement.set('ContentType', 'application/vnd.ms-visio.drawing.main+xml')

        overrideElement = ElementTree.SubElement(typesElement, 'Override')
        overrideElement.set('PartName', '/visio/pages/pages.xml')
        overrideElement.set('ContentType', 'application/vnd.ms-visio.pages+xml')

        for pageIndex, _ in enumerate(self._pagesToExport):
            overrideElement = ElementTree.SubElement(typesElement, 'Override')
            overrideElement.set('PartName', f'/visio/pages/page{pageIndex + 1}.xml')
            overrideElement.set('ContentType', 'application/vnd.ms-visio.page+xml')

        overrideElement = ElementTree.SubElement(typesElement, 'Override')
        overrideElement.set('PartName', '/visio/windows.xml')
        overrideElement.set('ContentType', 'application/vnd.ms-visio.windows+xml')

        overrideElement = ElementTree.SubElement(typesElement, 'Override')
        overrideElement.set('PartName', '/docProps/core.xml')
        overrideElement.set('ContentType', 'application/vnd.openxmlformats-package.core-properties+xml')

        overrideElement = ElementTree.SubElement(typesElement, 'Override')
        overrideElement.set('PartName', '/docProps/app.xml')
        overrideElement.set('ContentType', 'application/vnd.openxmlformats-officedocument.extended-properties+xml')

        overrideElement = ElementTree.SubElement(typesElement, 'Override')
        overrideElement.set('PartName', '/docProps/custom.xml')
        overrideElement.set('ContentType', 'application/vnd.openxmlformats-officedocument.custom-properties+xml')

        return f'{ElementTree.tostring(typesElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeRels(self) -> str:
        relationshipsElement = ElementTree.Element('Relationships')
        relationshipsElement.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
        relationshipElement.set('Id', 'rId3')
        relationshipElement.set(
            'Type', 'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties')
        relationshipElement.set('Target', 'docProps/core.xml')

        relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
        relationshipElement.set('Id', 'rId1')
        relationshipElement.set('Type', 'http://schemas.microsoft.com/visio/2010/relationships/document')
        relationshipElement.set('Target', 'visio/document.xml')

        relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
        relationshipElement.set('Id', 'rId5')
        relationshipElement.set(
            'Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties')
        relationshipElement.set('Target', 'docProps/custom.xml')

        relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
        relationshipElement.set('Id', 'rId4')
        relationshipElement.set(
            'Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties')
        relationshipElement.set('Target', 'docProps/app.xml')

        return f'{ElementTree.tostring(relationshipsElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeApp(self) -> str:
        propertiesElement = ElementTree.Element('Properties')
        propertiesElement.set('xmlns', 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties')
        propertiesElement.set('xmlns:vt', 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes')

        ElementTree.SubElement(propertiesElement, 'Template')

        applicationElement = ElementTree.SubElement(propertiesElement, 'Application')
        applicationElement.text = 'Microsoft Visio'

        scaleCropElement = ElementTree.SubElement(propertiesElement, 'ScaleCrop')
        scaleCropElement.text = 'false'

        headingPairsElement = ElementTree.SubElement(propertiesElement, 'HeadingPairs')
        vectorElement = ElementTree.SubElement(headingPairsElement, 'vt:vector')
        vectorElement.set('size', '2')
        vectorElement.set('baseType', 'variant')
        variantElement = ElementTree.SubElement(vectorElement, 'vt:variant')
        strElement = ElementTree.SubElement(variantElement, 'vt:lpstr')
        strElement.text = 'Pages'
        variantElement = ElementTree.SubElement(vectorElement, 'vt:variant')
        i4Element = ElementTree.SubElement(variantElement, 'vt:i4')
        i4Element.text = f'{len(self._pagesToExport)}'

        titlesOfPartsElement = ElementTree.SubElement(propertiesElement, 'TitlesOfParts')
        vectorElement = ElementTree.SubElement(titlesOfPartsElement, 'vt:vector')
        vectorElement.set('size', f'{len(self._pagesToExport)}')
        vectorElement.set('baseType', 'lpstr')
        for page in self._pagesToExport:
            strElement = ElementTree.SubElement(vectorElement, 'vt:lpstr')
            strElement.text = page.name()

        ElementTree.SubElement(propertiesElement, 'Manager')

        ElementTree.SubElement(propertiesElement, 'Company')

        linksUpToDateElement = ElementTree.SubElement(propertiesElement, 'LinksUpToDate')
        linksUpToDateElement.text = 'false'

        sharedDocElement = ElementTree.SubElement(propertiesElement, 'SharedDoc')
        sharedDocElement.text = 'false'

        ElementTree.SubElement(propertiesElement, 'HyperlinkBase')

        hyperlinksChangedElement = ElementTree.SubElement(propertiesElement, 'HyperlinksChanged')
        hyperlinksChangedElement.text = 'false'

        appVersionElement = ElementTree.SubElement(propertiesElement, 'AppVersion')
        appVersionElement.text = '16.0000'

        return f'{ElementTree.tostring(propertiesElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeCore(self) -> str:
        corePropertiesElement = ElementTree.Element('cp:coreProperties')
        corePropertiesElement.set('xmlns:cp', 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties')
        corePropertiesElement.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
        corePropertiesElement.set('xmlns:dcterms', 'http://purl.org/dc/terms/')
        corePropertiesElement.set('xmlns:dcmitype', 'http://purl.org/dc/dcmitype/')
        corePropertiesElement.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        ElementTree.SubElement(corePropertiesElement, 'dc:title')
        ElementTree.SubElement(corePropertiesElement, 'dc:subject')
        ElementTree.SubElement(corePropertiesElement, 'dc:creator')
        ElementTree.SubElement(corePropertiesElement, 'cp:keywords')
        ElementTree.SubElement(corePropertiesElement, 'dc:description')
        ElementTree.SubElement(corePropertiesElement, 'cp:category')

        languageElement = ElementTree.SubElement(corePropertiesElement, 'dc:language')
        languageElement.text = 'en-US'

        return f'{ElementTree.tostring(corePropertiesElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeCustom(self) -> str:
        propertiesElement = ElementTree.Element('Properties')
        propertiesElement.set('xmlns', 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties')
        propertiesElement.set('xmlns:vt', 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes')

        propertyElement = ElementTree.SubElement(propertiesElement, 'property')
        propertyElement.set('fmtid', '{D5CDD505-2E9C-101B-9397-08002B2CF9AE}')
        propertyElement.set('pid', '2')
        propertyElement.set('name', '_VPID_ALTERNATENAMES')
        ElementTree.SubElement(propertyElement, 'vt:lpwstr')

        propertyElement = ElementTree.SubElement(propertiesElement, 'property')
        propertyElement.set('fmtid', '{D5CDD505-2E9C-101B-9397-08002B2CF9AE}')
        propertyElement.set('pid', '3')
        propertyElement.set('name', 'BuildNumberCreated')
        i4Element = ElementTree.SubElement(propertyElement, 'vt:i4')
        i4Element.text = '1075461591'

        propertyElement = ElementTree.SubElement(propertiesElement, 'property')
        propertyElement.set('fmtid', '{D5CDD505-2E9C-101B-9397-08002B2CF9AE}')
        propertyElement.set('pid', '4')
        propertyElement.set('name', 'BuildNumberEdited')
        i4Element = ElementTree.SubElement(propertyElement, 'vt:i4')
        i4Element.text = '1075461591'

        propertyElement = ElementTree.SubElement(propertiesElement, 'property')
        propertyElement.set('fmtid', '{D5CDD505-2E9C-101B-9397-08002B2CF9AE}')
        propertyElement.set('pid', '5')
        propertyElement.set('name', 'IsMetric')
        boolElement = ElementTree.SubElement(propertyElement, 'vt:bool')
        boolElement.text = 'false' if (self._units == 'IN') else 'true'

        return f'{ElementTree.tostring(propertiesElement, encoding="unicode", xml_declaration=True)}\n'

    def _writePagesRels(self) -> str:
        relationshipsElement = ElementTree.Element('Relationships')
        relationshipsElement.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        for pageIndex, _ in enumerate(self._pagesToExport):
            relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
            relationshipElement.set('Id', f'rId{pageIndex + 1}')
            relationshipElement.set('Type', 'http://schemas.microsoft.com/visio/2010/relationships/page')
            relationshipElement.set('Target', f'page{pageIndex + 1}.xml')

        return f'{ElementTree.tostring(relationshipsElement, encoding="unicode", xml_declaration=True)}\n'

    def _writePages(self) -> str:
        pagesElement = ElementTree.Element('Pages')
        pagesElement.set('xmlns', 'http://schemas.microsoft.com/office/visio/2012/main')
        pagesElement.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        pagesElement.set('xml:space', 'preserve')

        for pageIndex, page in enumerate(self._pagesToExport):
            rulerOrigin = self._getRulerOrigin()
            gridOrigin = rulerOrigin
            finalPageWidth = page.pageSize().width() - 2 * page.pageMargin() + 2 * rulerOrigin
            finalPageHeight = page.pageSize().height() - 2 * page.pageMargin() + 2 * rulerOrigin

            pageElement = ElementTree.SubElement(pagesElement, 'Page')
            pageElement.set('ID', f'{pageIndex + 1}')
            pageElement.set('NameU', page.name())
            pageElement.set('IsCustomNameU', '1')
            pageElement.set('Name', page.name())
            pageElement.set('IsCustomName', '1')

            pageSheetElement = ElementTree.SubElement(pageElement, 'PageSheet')
            pageSheetElement.set('LineStyle', '0')
            pageSheetElement.set('FillStyle', '0')
            pageSheetElement.set('TextStyle', '0')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PageWidth')
            cellElement.set('V', f'{self._lengthToString(finalPageWidth)}')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PageHeight')
            cellElement.set('V', f'{self._lengthToString(finalPageHeight)}')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'ShdwOffsetX')
            cellElement.set('V', '0.125')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'ShdwOffsetY')
            cellElement.set('V', '-0.125')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PageScale')
            cellElement.set('V', '1')
            cellElement.set('U', 'IN_F')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'DrawingScale')
            cellElement.set('V', '1')
            cellElement.set('U', 'IN_F')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'DrawingSizeType')
            cellElement.set('V', '3')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'DrawingScaleType')
            cellElement.set('V', '0')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'InhibitSnap')
            cellElement.set('V', '0')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PageLockReplace')
            cellElement.set('V', '0')
            cellElement.set('U', 'BOOL')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PageLockDuplicate')
            cellElement.set('V', '0')
            cellElement.set('U', 'BOOL')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'UIVisibility')
            cellElement.set('V', '0')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'ShdwType')
            cellElement.set('V', '0')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'ShdwObliqueAngle')
            cellElement.set('V', '0')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'ShdwScaleFactor')
            cellElement.set('V', '1')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'DrawingResizeType')
            cellElement.set('V', '2')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PageShapeSplit')
            cellElement.set('V', '1')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'PrintPageOrientation')
            cellElement.set('V', '2' if (finalPageWidth > finalPageHeight) else '1')

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'XRulerOrigin')
            cellElement.set('V', f'{self._lengthToString(rulerOrigin)}')
            cellElement.set('U', self._units)

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'YRulerOrigin')
            cellElement.set('V', f'{self._lengthToString(rulerOrigin)}')
            cellElement.set('U', self._units)

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'XGridSpacing')
            cellElement.set('V', '0')
            cellElement.set('U', self._units)

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'YGridSpacing')
            cellElement.set('V', '0')
            cellElement.set('U', self._units)

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'XGridOrigin')
            cellElement.set('V', f'{self._lengthToString(gridOrigin)}')
            cellElement.set('U', self._units)

            cellElement = ElementTree.SubElement(pageSheetElement, 'Cell')
            cellElement.set('N', 'YGridOrigin')
            cellElement.set('V', f'{self._lengthToString(gridOrigin)}')
            cellElement.set('U', self._units)

            relElement = ElementTree.SubElement(pageElement, 'Rel')
            relElement.set('r:id', f'rId{pageIndex + 1}')

        return f'{ElementTree.tostring(pagesElement, encoding="unicode", xml_declaration=True)}\n'

    def _writePage(self, page: DrawingPageWidget) -> str:
        pageContentsElement = ElementTree.Element('PageContents')
        pageContentsElement.set('xmlns', 'http://schemas.microsoft.com/office/visio/2012/main')
        pageContentsElement.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        pageContentsElement.set('xml:space', 'preserve')

        shapesElement = ElementTree.SubElement(pageContentsElement, 'Shapes')
        self._writeItems(shapesElement, page, page.items(), True)

        return f'{ElementTree.tostring(pageContentsElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeDocumentRels(self) -> str:
        relationshipsElement = ElementTree.Element('Relationships')
        relationshipsElement.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
        relationshipElement.set('Id', 'rId2')
        relationshipElement.set('Type', 'http://schemas.microsoft.com/visio/2010/relationships/windows')
        relationshipElement.set('Target', 'windows.xml')

        relationshipElement = ElementTree.SubElement(relationshipsElement, 'Relationship')
        relationshipElement.set('Id', 'rId1')
        relationshipElement.set('Type', 'http://schemas.microsoft.com/visio/2010/relationships/pages')
        relationshipElement.set('Target', 'pages/pages.xml')

        return f'{ElementTree.tostring(relationshipsElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeDocument(self) -> str:
        visioDocumentElement = ElementTree.Element('VisioDocument')
        visioDocumentElement.set('xmlns', 'http://schemas.microsoft.com/office/visio/2012/main')
        visioDocumentElement.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        visioDocumentElement.set('xml:space', 'preserve')

        return f'{ElementTree.tostring(visioDocumentElement, encoding="unicode", xml_declaration=True)}\n'

    def _writeWindows(self) -> str:
        windowsElement = ElementTree.Element('Windows')
        windowsElement.set('xmlns', 'http://schemas.microsoft.com/office/visio/2012/main')
        windowsElement.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        windowsElement.set('xml:space', 'preserve')

        return f'{ElementTree.tostring(windowsElement, encoding="unicode", xml_declaration=True)}\n'

    # ==================================================================================================================

    def _writeItems(self, element: ElementTree.Element, page: DrawingPageWidget, items: list[DrawingItem],
                    increaseDepth: bool) -> None:
        if (increaseDepth):
            self._shapeDepth = self._shapeDepth + 1

        for item in items:
            if (isinstance(item, DrawingLineItem)):
                self._writeLineItem(element, page, item)
            elif (isinstance(item, DrawingCurveItem)):
                self._writeCurveItem(element, page, item)
            elif (isinstance(item, DrawingPolylineItem)):
                self._writePolylineItem(element, page, item)
            elif (isinstance(item, DrawingTextRectItem)):
                self._writeTextRectItem(element, page, item)
            elif (isinstance(item, DrawingRectItem)):
                self._writeRectItem(element, page, item)
            elif (isinstance(item, DrawingTextEllipseItem)):
                self._writeTextEllipseItem(element, page, item)
            elif (isinstance(item, DrawingEllipseItem)):
                self._writeEllipseItem(element, page, item)
            elif (isinstance(item, DrawingPolygonItem)):
                self._writePolygonItem(element, page, item)
            elif (isinstance(item, DrawingTextItem)):
                self._writeTextItem(element, page, item)
            elif (isinstance(item, DrawingPathItem)):
                self._writePathItem(element, page, item)
            elif (isinstance(item, DrawingItemGroup)):
                self._writeGroupItem(element, page, item)

        if (increaseDepth):
            self._shapeDepth = self._shapeDepth - 1

    def _writeLineItem(self, element: ElementTree.Element, page: DrawingPageWidget, item: DrawingLineItem) -> None:
        self._shapeIndex = self._shapeIndex + 1

        shapeElement = ElementTree.SubElement(element, 'Shape')
        shapeElement.set('ID', f'{self._shapeIndex}')
        shapeElement.set('Type', 'Shape')
        shapeElement.set('LineStyle', '3')
        shapeElement.set('FillStyle', '3')
        shapeElement.set('TextStyle', '3')

        lineSize = self._writePositionAndSizeForLine(shapeElement, page, QLineF(item.mapToScene(item.line().p1()),
                                                                                item.mapToScene(item.line().p2())))

        self._writeStyle(shapeElement, brush=QBrush(Qt.GlobalColor.transparent), pen=item.pen(),
                         startArrow=item.startArrow(), endArrow=item.endArrow())

        # Geometry
        sectionElement = ElementTree.SubElement(shapeElement, 'Section')
        sectionElement.set('N', 'Geometry')
        sectionElement.set('IX', '0')

        self._writeCommonGeometryElements(sectionElement, True)
        self._writeMoveToGeometryElement(sectionElement, 1, QPointF(0, 0), formulaX='Width*0')
        self._writeLineToGeometryElement(sectionElement, 2, QPointF(lineSize.width(), 0), formulaX='Width*1')

    def _writeCurveItem(self, element: ElementTree.Element, page: DrawingPageWidget, item: DrawingCurveItem) -> None:
        curve = item.curve()
        if (curve.count() == 4):
            self._shapeIndex = self._shapeIndex + 1

            shapeElement = ElementTree.SubElement(element, 'Shape')
            shapeElement.set('ID', f'{self._shapeIndex}')
            shapeElement.set('Type', 'Shape')
            shapeElement.set('LineStyle', '3')
            shapeElement.set('FillStyle', '3')
            shapeElement.set('TextStyle', '3')

            path = QPainterPath()
            path.moveTo(curve.at(0))
            path.cubicTo(curve.at(1), curve.at(2), curve.at(3))
            pathRect = path.boundingRect()

            self._writePositionAndSize(shapeElement, page, item.position(), item.rotation(), item.isFlipped(), pathRect)

            self._writeStyle(shapeElement, brush=QBrush(Qt.GlobalColor.transparent), pen=item.pen(),
                             startArrow=item.startArrow(), endArrow=item.endArrow())

            # Geometry
            sectionElement = ElementTree.SubElement(shapeElement, 'Section')
            sectionElement.set('N', 'Geometry')
            sectionElement.set('IX', '0')

            self._writeCommonGeometryElements(sectionElement, True)

            geometryIndex = 1
            curvePoints = []
            for pathIndex in range(path.elementCount()):
                pathElement = path.elementAt(pathIndex)
                positionX = (pathElement.x - pathRect.left()) / pathRect.width()        # type: ignore
                positionY = (pathRect.bottom() - pathElement.y) / pathRect.height()     # type: ignore
                match (pathElement.type):   # type: ignore
                    case QPainterPath.ElementType.MoveToElement:
                        self._writeRelMoveToGeometryElement(sectionElement, geometryIndex,
                                                            QPointF(positionX, positionY))
                        geometryIndex = geometryIndex + 1
                    case QPainterPath.ElementType.CurveToElement:
                        curvePoints.append(QPointF(positionX, positionY))
                    case QPainterPath.ElementType.CurveToDataElement:
                        if (len(curvePoints) >= 2):
                            curveStartControlPoint = curvePoints[0]
                            curveEndControlPoint = curvePoints[1]
                            self._writeRelCubicBezierCurveToGeometryElement(
                                sectionElement, geometryIndex, curveStartControlPoint, curveEndControlPoint,
                                QPointF(positionX, positionY))
                            geometryIndex = geometryIndex + 1
                            curvePoints = []
                        else:
                            curvePoints.append(QPointF(positionX, positionY))

    def _writePolylineItem(self, element: ElementTree.Element, page: DrawingPageWidget,
                           item: DrawingPolylineItem) -> None:
        self._shapeIndex = self._shapeIndex + 1

        shapeElement = ElementTree.SubElement(element, 'Shape')
        shapeElement.set('ID', f'{self._shapeIndex}')
        shapeElement.set('Type', 'Shape')
        shapeElement.set('LineStyle', '3')
        shapeElement.set('FillStyle', '3')
        shapeElement.set('TextStyle', '3')

        polyline = QPolygonF(item.polyline())
        polylineRect = polyline.boundingRect()
        self._writePositionAndSize(shapeElement, page, item.position(), item.rotation(), item.isFlipped(), polylineRect)

        self._writeStyle(shapeElement, brush=QBrush(Qt.GlobalColor.transparent), pen=item.pen(),
                         startArrow=item.startArrow(), endArrow=item.endArrow())

        # Geometry
        sectionElement = ElementTree.SubElement(shapeElement, 'Section')
        sectionElement.set('N', 'Geometry')
        sectionElement.set('IX', '0')

        self._writeCommonGeometryElements(sectionElement, True)

        for pointIndex in range(polyline.count()):
            point = polyline.at(pointIndex)
            positionX = point.x() - polylineRect.left()
            positionY = polylineRect.bottom() - point.y()
            if (pointIndex == 0):
                self._writeMoveToGeometryElement(sectionElement, pointIndex + 1, QPointF(positionX, positionY),
                                                 formulaX=f'Width*{positionX / polylineRect.width()}',
                                                 formulaY=f'Height*{positionY / polylineRect.height()}')
            else:
                self._writeLineToGeometryElement(sectionElement, pointIndex + 1, QPointF(positionX, positionY),
                                                 formulaX=f'Width*{positionX / polylineRect.width()}',
                                                 formulaY=f'Height*{positionY / polylineRect.height()}')

    def _writeRectItem(self, element: ElementTree.Element, page: DrawingPageWidget, item: DrawingRectItem) -> None:
        self._shapeIndex = self._shapeIndex + 1

        shapeElement = ElementTree.SubElement(element, 'Shape')
        shapeElement.set('ID', f'{self._shapeIndex}')
        shapeElement.set('Type', 'Shape')
        shapeElement.set('LineStyle', '3')
        shapeElement.set('FillStyle', '3')
        shapeElement.set('TextStyle', '3')

        self._writePositionAndSize(shapeElement, page, item.position(), item.rotation(), item.isFlipped(), item.rect())

        if (item.cornerRadius() != 0):
            cellElement = ElementTree.SubElement(shapeElement, 'Cell')
            cellElement.set('N', 'Rounding')
            cellElement.set('V', f'{self._lengthToString(item.cornerRadius())}')

        self._writeStyle(shapeElement, brush=item.brush(), pen=item.pen())

        # Geometry
        sectionElement = ElementTree.SubElement(shapeElement, 'Section')
        sectionElement.set('N', 'Geometry')
        sectionElement.set('IX', '0')

        self._writeCommonGeometryElements(sectionElement, False)
        self._writeRelMoveToGeometryElement(sectionElement, 1, QPointF(0, 0))
        self._writeRelLineToGeometryElement(sectionElement, 2, QPointF(1, 0))
        self._writeRelLineToGeometryElement(sectionElement, 3, QPointF(1, 1))
        self._writeRelLineToGeometryElement(sectionElement, 4, QPointF(0, 1))
        self._writeRelLineToGeometryElement(sectionElement, 5, QPointF(0, 0))

    def _writeEllipseItem(self, element: ElementTree.Element, page: DrawingPageWidget,
                          item: DrawingEllipseItem) -> None:
        self._shapeIndex = self._shapeIndex + 1

        shapeElement = ElementTree.SubElement(element, 'Shape')
        shapeElement.set('ID', f'{self._shapeIndex}')
        shapeElement.set('Type', 'Shape')
        shapeElement.set('LineStyle', '3')
        shapeElement.set('FillStyle', '3')
        shapeElement.set('TextStyle', '3')

        ellipseSize = self._writePositionAndSize(shapeElement, page, item.position(), item.rotation(), item.isFlipped(),
                                                 item.ellipse())

        self._writeStyle(shapeElement, brush=item.brush(), pen=item.pen())

        # Geometry
        sectionElement = ElementTree.SubElement(shapeElement, 'Section')
        sectionElement.set('N', 'Geometry')
        sectionElement.set('IX', '0')

        self._writeCommonGeometryElements(sectionElement, False)
        self._writeEllipseGeometryElement(sectionElement, 1, ellipseSize)

    def _writePolygonItem(self, element: ElementTree.Element, page: DrawingPageWidget,
                          item: DrawingPolygonItem) -> None:
        self._shapeIndex = self._shapeIndex + 1

        shapeElement = ElementTree.SubElement(element, 'Shape')
        shapeElement.set('ID', f'{self._shapeIndex}')
        shapeElement.set('Type', 'Shape')
        shapeElement.set('LineStyle', '3')
        shapeElement.set('FillStyle', '3')
        shapeElement.set('TextStyle', '3')

        polygon = QPolygonF(item.polygon())
        polygonRect = polygon.boundingRect()
        self._writePositionAndSize(shapeElement, page, item.position(), item.rotation(), item.isFlipped(), polygonRect)

        self._writeStyle(shapeElement, brush=item.brush(), pen=item.pen())

        # Geometry
        sectionElement = ElementTree.SubElement(shapeElement, 'Section')
        sectionElement.set('N', 'Geometry')
        sectionElement.set('IX', '0')

        self._writeCommonGeometryElements(sectionElement, False)

        polygon.append(QPointF(polygon.at(0)))
        for pointIndex in range(polygon.count()):
            point = polygon.at(pointIndex)
            positionX = point.x() - polygonRect.left()
            positionY = polygonRect.bottom() - point.y()
            if (pointIndex == 0):
                self._writeMoveToGeometryElement(sectionElement, pointIndex + 1, QPointF(positionX, positionY),
                                                 formulaX=f'Width*{positionX / polygonRect.width()}',
                                                 formulaY=f'Height*{positionY / polygonRect.height()}')
            elif (pointIndex != polygon.count() - 1):
                self._writeLineToGeometryElement(sectionElement, pointIndex + 1, QPointF(positionX, positionY),
                                                 formulaX=f'Width*{positionX / polygonRect.width()}',
                                                 formulaY=f'Height*{positionY / polygonRect.height()}')
            else:
                self._writeLineToGeometryElement(sectionElement, pointIndex + 1, QPointF(positionX, positionY),
                                                 formulaX='Geometry1.X1', formulaY='Geometry1.Y1')

    def _writeTextItem(self, element: ElementTree.Element, page: DrawingPageWidget, item: DrawingTextItem) -> None:
        pass

    def _writeTextRectItem(self, element: ElementTree.Element, page: DrawingPageWidget,
                           item: DrawingTextRectItem) -> None:
        pass

    def _writeTextEllipseItem(self, element: ElementTree.Element, page: DrawingPageWidget,
                              item: DrawingTextEllipseItem) -> None:
        pass

    def _writePathItem(self, element: ElementTree.Element, page: DrawingPageWidget, item: DrawingPathItem) -> None:
        self._shapeIndex = self._shapeIndex + 1

        shapeElement = ElementTree.SubElement(element, 'Shape')
        shapeElement.set('ID', f'{self._shapeIndex}')
        shapeElement.set('Type', 'Shape')
        shapeElement.set('LineStyle', '3')
        shapeElement.set('FillStyle', '3')
        shapeElement.set('TextStyle', '3')

        self._writePositionAndSize(shapeElement, page, item.position(), item.rotation(), item.isFlipped(), item.rect())

        self._writeStyle(shapeElement, brush=QBrush(Qt.GlobalColor.transparent), pen=item.pen())

        # Geometry
        sectionElement = ElementTree.SubElement(shapeElement, 'Section')
        sectionElement.set('N', 'Geometry')
        sectionElement.set('IX', '0')

        self._writeCommonGeometryElements(sectionElement, True)

        path = item.path()
        pathRect = item.pathRect()
        geometryIndex = 1
        curvePoints = []
        for pathIndex in range(path.elementCount()):
            pathElement = path.elementAt(pathIndex)
            positionX = (pathElement.x - pathRect.left()) / pathRect.width()        # type: ignore
            positionY = (pathRect.bottom() - pathElement.y) / pathRect.height()     # type: ignore
            match (pathElement.type):   # type: ignore
                case QPainterPath.ElementType.MoveToElement:
                    self._writeRelMoveToGeometryElement(sectionElement, geometryIndex, QPointF(positionX, positionY))
                    geometryIndex = geometryIndex + 1
                case QPainterPath.ElementType.LineToElement:
                    self._writeRelLineToGeometryElement(sectionElement, geometryIndex, QPointF(positionX, positionY))
                    geometryIndex = geometryIndex + 1
                case QPainterPath.ElementType.CurveToElement:
                    curvePoints.append(QPointF(positionX, positionY))
                case QPainterPath.ElementType.CurveToDataElement:
                    if (len(curvePoints) >= 2):
                        curveStartControlPoint = curvePoints[0]
                        curveEndControlPoint = curvePoints[1]
                        self._writeRelCubicBezierCurveToGeometryElement(
                            sectionElement, geometryIndex, curveStartControlPoint, curveEndControlPoint,
                            QPointF(positionX, positionY))
                        geometryIndex = geometryIndex + 1
                        curvePoints = []
                    else:
                        curvePoints.append(QPointF(positionX, positionY))

    def _writeGroupItem(self, element: ElementTree.Element, page: DrawingPageWidget, item: DrawingItemGroup) -> None:
        pass

    # ==================================================================================================================

    def _writePositionAndSize(self, element: ElementTree.Element, currentPage: DrawingPageWidget, position: QPointF,
                              rotation: int, flipped: bool, rect: QRectF) -> QSizeF:

        rect = rect.normalized()
        position = self._mapFromScene(currentPage, QPointF(position.x() + rect.left(), position.y() + rect.top()))

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'PinX')
        cellElement.set('V', f'{self._lengthToString(position.x())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'PinY')
        cellElement.set('V', f'{self._lengthToString(position.y())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'Width')
        cellElement.set('V', f'{self._lengthToString(rect.width())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'Height')
        cellElement.set('V', f'{self._lengthToString(rect.height())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'LocPinX')
        cellElement.set('V', '0')
        cellElement.set('F', 'Width*0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'LocPinY')
        cellElement.set('V', f'{self._lengthToString(rect.height())}')
        cellElement.set('F', 'Height*1')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'Angle')
        cellElement.set('V', f'{-math.pi / 2 * rotation}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'FlipX')
        cellElement.set('V', '1' if (flipped) else '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'FlipY')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'ResizeMode')
        cellElement.set('V', '0')

        return QSizeF(rect.width(), rect.height())

    def _writePositionAndSizeForLine(self, element: ElementTree.Element, currentPage: DrawingPageWidget,
                                     line: QLineF) -> QSizeF:

        line = QLineF(self._mapFromScene(currentPage, line.p1()), self._mapFromScene(currentPage, line.p2()))
        center = line.center()
        width = line.length()
        angle = math.atan2(line.y2() - line.y1(), line.x2() - line.x1())

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'PinX')
        cellElement.set('V', f'{self._lengthToString(center.x())}')
        cellElement.set('F', '(BeginX+EndX)/2')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'PinY')
        cellElement.set('V', f'{self._lengthToString(center.y())}')
        cellElement.set('F', '(BeginY+EndY)/2')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'Width')
        cellElement.set('V', f'{self._lengthToString(width)}')
        cellElement.set('F', 'SQRT((EndX-BeginX)^2+(EndY-BeginY)^2)')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'Height')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'LocPinX')
        cellElement.set('V', f'{self._lengthToString(width / 2)}')
        cellElement.set('F', 'Width*0.5')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'LocPinY')
        cellElement.set('V', '0')
        cellElement.set('F', 'Height*0.5')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'Angle')
        cellElement.set('V', f'{angle}')
        cellElement.set('F', 'ATAN2(EndY-BeginY,EndX-BeginX)')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'FlipX')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'FlipY')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'ResizeMode')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'BeginX')
        cellElement.set('V', f'{self._lengthToString(line.x1())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'BeginY')
        cellElement.set('V', f'{self._lengthToString(line.y1())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'EndX')
        cellElement.set('V', f'{self._lengthToString(line.x2())}')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'EndY')
        cellElement.set('V', f'{self._lengthToString(line.y2())}')

        return QSizeF(width, 0)

    def _mapFromScene(self, page: DrawingPageWidget, position: QPointF) -> QPointF:
        rulerOrigin = self._getRulerOrigin()
        return QPointF(position.x() + rulerOrigin,
                       page.pageSize().height() - 2 * page.pageMargin() - position.y() + rulerOrigin)

    # ==================================================================================================================

    def _writeStyle(self, element: ElementTree.Element, brush: QBrush | None = None, pen: QPen | None = None,
                    startArrow: DrawingArrow | None = None, endArrow: DrawingArrow | None = None) -> None:
        # Visio boilerplate stuff
        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'QuickStyleLineMatrix')
        cellElement.set('V', '1')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'QuickStyleFillMatrix')
        cellElement.set('V', '1')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'QuickStyleEffectsMatrix')
        cellElement.set('V', '1')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'QuickStyleFontMatrix')
        cellElement.set('V', '1')

        # Our style attributes
        if (isinstance(brush, QBrush)):
            self._writeBrush(element, brush)
        if (isinstance(pen, QPen)):
            self._writePen(element, pen)
            if (isinstance(startArrow, DrawingArrow)):
                self._writeStartArrow(element, startArrow, pen)
            if (isinstance(endArrow, DrawingArrow)):
                self._writeEndArrow(element, endArrow, pen)

    def _writeBrush(self, element: ElementTree.Element, brush: QBrush) -> None:
        color = QColor(brush.color())
        alpha = color.alpha()
        transparency = 1.0 - color.alphaF()

        if (alpha != 0 and brush.style() != Qt.BrushStyle.NoBrush):
            color.setAlpha(255)

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'FillForegnd')
            cellElement.set('V', f'{color.name(QColor.NameFormat.HexRgb)}')

            if (alpha != 255):
                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'FillForegndTrans')
                cellElement.set('V', f'{transparency}')

                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'FillBkgndTrans')
                cellElement.set('V', f'{transparency}')
        else:
            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'FillPattern')
            cellElement.set('V', '0')

    def _writePen(self, element: ElementTree.Element, pen: QPen) -> None:
        color = QColor(pen.brush().color())
        alpha = color.alpha()
        transparency = 1.0 - color.alphaF()
        if (alpha != 0 and pen.style() != Qt.PenStyle.NoPen and pen.brush().style() != Qt.BrushStyle.NoBrush):
            color.setAlpha(255)

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'LineColor')
            cellElement.set('V', f'{color.name(QColor.NameFormat.HexRgb)}')

            if (alpha != 255):
                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'LineColorTrans')
                cellElement.set('V', f'{transparency}')

            if (pen.style() == Qt.PenStyle.DashLine):
                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'LinePattern')
                cellElement.set('V', '9')
            elif (pen.style() == Qt.PenStyle.DotLine):
                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'LinePattern')
                cellElement.set('V', '10')
            elif (pen.style() == Qt.PenStyle.DashDotLine):
                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'LinePattern')
                cellElement.set('V', '11')
            elif (pen.style() == Qt.PenStyle.DashDotDotLine):
                cellElement = ElementTree.SubElement(element, 'Cell')
                cellElement.set('N', 'LinePattern')
                cellElement.set('V', '12')

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'LineWeight')
            cellElement.set('V', f'{self._lengthToString(pen.widthF())}')
        else:
            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'LinePattern')
            cellElement.set('V', '0')

    def _writeStartArrow(self, element: ElementTree.Element, arrow: DrawingArrow, pen: QPen) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            styleStr = '4'
            if (arrow.style() == DrawingArrow.Style.Normal):
                styleStr = '3'
            elif (arrow.style() in (DrawingArrow.Style.Triangle, DrawingArrow.Style.Concave)):
                styleStr = '16'
            elif (arrow.style() == DrawingArrow.Style.CircleFilled):
                styleStr = '10'
            elif (arrow.style() == DrawingArrow.Style.Circle):
                styleStr = '20'

            sizeStr = '2'
            if (arrow.size() < pen.widthF() * 2):
                sizeStr = '0'
            elif (arrow.size() < pen.widthF() * 5):
                sizeStr = '1'

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'BeginArrow')
            cellElement.set('V', styleStr)

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'BeginArrowSize')
            cellElement.set('V', sizeStr)

    def _writeEndArrow(self, element: ElementTree.Element, arrow: DrawingArrow, pen: QPen) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            styleStr = '4'
            if (arrow.style() == DrawingArrow.Style.Normal):
                styleStr = '3'
            elif (arrow.style() in (DrawingArrow.Style.Triangle, DrawingArrow.Style.Concave)):
                styleStr = '16'
            elif (arrow.style() == DrawingArrow.Style.CircleFilled):
                styleStr = '10'
            elif (arrow.style() == DrawingArrow.Style.Circle):
                styleStr = '20'

            sizeStr = '2'
            if (arrow.size() < pen.widthF() * 2):
                sizeStr = '0'
            elif (arrow.size() < pen.widthF() * 5):
                sizeStr = '1'

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'EndArrow')
            cellElement.set('V', styleStr)

            cellElement = ElementTree.SubElement(element, 'Cell')
            cellElement.set('N', 'EndArrowSize')
            cellElement.set('V', sizeStr)

    # ==================================================================================================================

    def _writeCommonGeometryElements(self, element: ElementTree.Element, noFill: bool) -> None:
        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'NoFill')
        cellElement.set('V', '1' if (noFill) else '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'NoLine')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'NoShow')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'NoSnap')
        cellElement.set('V', '0')

        cellElement = ElementTree.SubElement(element, 'Cell')
        cellElement.set('N', 'NoQuickDrag')
        cellElement.set('V', '0')

    def _writeMoveToGeometryElement(self, element: ElementTree.Element, index: int, position: QPointF,
                                    formulaX: str = '', formulaY: str = '') -> None:
        rowElement = ElementTree.SubElement(element, 'Row')
        rowElement.set('T', 'MoveTo')
        rowElement.set('IX', f'{index}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'X')
        cellElement.set('V', f'{self._lengthToString(position.x())}')
        if (formulaX != ''):
            cellElement.set('F', formulaX)

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'Y')
        cellElement.set('V', f'{self._lengthToString(position.y())}')
        if (formulaY != ''):
            cellElement.set('F', formulaY)

    def _writeLineToGeometryElement(self, element: ElementTree.Element, index: int, position: QPointF,
                                    formulaX: str = '', formulaY: str = '') -> None:
        rowElement = ElementTree.SubElement(element, 'Row')
        rowElement.set('T', 'LineTo')
        rowElement.set('IX', f'{index}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'X')
        cellElement.set('V', f'{self._lengthToString(position.x())}')
        if (formulaX != ''):
            cellElement.set('F', formulaX)

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'Y')
        cellElement.set('V', f'{self._lengthToString(position.y())}')
        if (formulaY != ''):
            cellElement.set('F', formulaY)

    def _writeRelMoveToGeometryElement(self, element: ElementTree.Element, index: int, position: QPointF) -> None:
        rowElement = ElementTree.SubElement(element, 'Row')
        rowElement.set('T', 'RelMoveTo')
        rowElement.set('IX', f'{index}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'X')
        cellElement.set('V', f'{position.x()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'Y')
        cellElement.set('V', f'{position.y()}')

    def _writeRelLineToGeometryElement(self, element: ElementTree.Element, index: int, position: QPointF) -> None:
        rowElement = ElementTree.SubElement(element, 'Row')
        rowElement.set('T', 'RelLineTo')
        rowElement.set('IX', f'{index}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'X')
        cellElement.set('V', f'{position.x()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'Y')
        cellElement.set('V', f'{position.y()}')

    def _writeRelCubicBezierCurveToGeometryElement(self, element: ElementTree.Element, index: int, cp1: QPointF,
                                                   cp2: QPointF, p2: QPointF) -> None:
        rowElement = ElementTree.SubElement(element, 'Row')
        rowElement.set('T', 'RelCubBezTo')
        rowElement.set('IX', f'{index}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'X')
        cellElement.set('V', f'{p2.x()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'Y')
        cellElement.set('V', f'{p2.y()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'A')
        cellElement.set('V', f'{cp1.x()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'B')
        cellElement.set('V', f'{cp1.y()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'C')
        cellElement.set('V', f'{cp2.x()}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'D')
        cellElement.set('V', f'{cp2.y()}')

    def _writeEllipseGeometryElement(self, element: ElementTree.Element, index: int, ellipseSize: QSizeF) -> None:
        rowElement = ElementTree.SubElement(element, 'Row')
        rowElement.set('T', 'Ellipse')
        rowElement.set('IX', f'{index}')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'X')
        cellElement.set('V', f'{self._lengthToString(ellipseSize.width() / 2)}')
        cellElement.set('F', 'Width*0.5')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'Y')
        cellElement.set('V', f'{self._lengthToString(ellipseSize.height() / 2)}')
        cellElement.set('F', 'Height*0.5')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'A')
        cellElement.set('V', f'{self._lengthToString(ellipseSize.width())}')
        cellElement.set('F', 'Width*1')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'B')
        cellElement.set('V', f'{self._lengthToString(ellipseSize.height() / 2)}')
        cellElement.set('F', 'Height*0.5')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'C')
        cellElement.set('V', f'{self._lengthToString(ellipseSize.width() / 2)}')
        cellElement.set('F', 'Width*0.5')

        cellElement = ElementTree.SubElement(rowElement, 'Cell')
        cellElement.set('N', 'D')
        cellElement.set('V', f'{self._lengthToString(ellipseSize.height())}')
        cellElement.set('F', 'Height*1')

    # ==================================================================================================================

    def _lengthToString(self, length: float) -> str:
        return f'{length * self._scale}'

    def _lengthToPointsString(self, length: float) -> str:
        if (self._units == 'IN'):
            return f'{length * self._scale * 72}'
        return f'{length * self._scale * 72 / 25}'

    def _getRulerOrigin(self) -> float:
        return 0.25 / self._scale if (self._units == 'IN') else 6.35 / self._scale
