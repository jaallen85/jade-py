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
from PySide6.QtCore import QMarginsF, QSizeF
from PySide6.QtGui import QColor
from ..diagramwidget import DiagramWidget


class OdgWriter:
    def __init__(self, drawing: DiagramWidget, units: str, scale: float, pageSize: QSizeF,
                 pageMargins: QMarginsF, backgroundColor: QColor) -> None:
        super().__init__()

        self._drawing: DiagramWidget = drawing
        self._units: str = str(units)
        self._scale: float = scale
        self._pageSize: QSizeF = QSizeF(pageSize)
        self._pageMargins: QMarginsF = QMarginsF(pageMargins)
        self._backgroundColor: QColor = QColor(backgroundColor)

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

    def _writeStyles(self) -> str:
        stylesElement = ElementTree.Element('office:document-styles')
        stylesElement.set('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        stylesElement.set('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        stylesElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        stylesElement.set('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        stylesElement.set('manifest:version', '1.3')

        ElementTree.SubElement(stylesElement, 'office:font-face-decls')
        ElementTree.SubElement(stylesElement, 'office:styles')

        # Automatic styles
        automaticStylesElement = ElementTree.SubElement(stylesElement, 'office:automatic-styles')

        pageLayoutElement = ElementTree.SubElement(automaticStylesElement, 'style:page-layout')
        pageLayoutElement.set('style:name', 'PM0')

        pageLayoutPropertiesElement = ElementTree.SubElement(pageLayoutElement, 'style:page-layout-properties')
        pageLayoutPropertiesElement.set('fo:margin-top', f'{self._pageMargins.top()}{self._units}')
        pageLayoutPropertiesElement.set('fo:margin-bottom', f'{self._pageMargins.bottom()}{self._units}')
        pageLayoutPropertiesElement.set('fo:margin-left', f'{self._pageMargins.left()}{self._units}')
        pageLayoutPropertiesElement.set('fo:margin-right', f'{self._pageMargins.right()}{self._units}')
        pageLayoutPropertiesElement.set('fo:page-width', f'{self._pageSize.width()}{self._units}')
        pageLayoutPropertiesElement.set('fo:page-height', f'{self._pageSize.height()}{self._units}')
        printOrientation = 'portrait' if (self._pageSize.width() > self._pageSize.height()) else 'landscape'
        pageLayoutPropertiesElement.set('style:print-orientation', printOrientation)

        styleElement = ElementTree.SubElement(automaticStylesElement, 'style:style')
        styleElement.set('style:name', 'Mdp1')
        styleElement.set('style:family', 'drawing-page')

        drawingPagePropertiesElement = ElementTree.SubElement(styleElement, 'style:drawing-page-properties')
        drawingPagePropertiesElement.set('draw:background-size', 'border')
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

    def _writeContent(self) -> str:
        contentElement = ElementTree.Element('office:document-content')
        contentElement.set('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        contentElement.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        contentElement.set('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        contentElement.set('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        contentElement.set('manifest:version', '1.3')

        ElementTree.SubElement(contentElement, 'office:scripts')
        ElementTree.SubElement(contentElement, 'office:font-face-decls')
        ElementTree.SubElement(contentElement, 'office:automatic-styles')

        bodyElement = ElementTree.SubElement(contentElement, 'office:body')
        ElementTree.SubElement(bodyElement, 'office:drawing')

        # Todo

        ElementTree.indent(contentElement, space='  ')
        return f'{ElementTree.tostring(contentElement, encoding="unicode", xml_declaration=True)}\n'
