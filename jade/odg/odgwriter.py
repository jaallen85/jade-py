# odgwriter.py
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

from zipfile import ZipFile
from PySide6.QtCore import QByteArray, QMarginsF, QSizeF, QXmlStreamWriter
from PySide6.QtGui import QColor
from .odgunits import OdgUnits


class OdgWriter:
    def __init__(self, path: str, units: OdgUnits, pageSize: QSizeF, pageMargins: QMarginsF) -> None:
        self._path: str = path
        self._units: OdgUnits = units
        self._pageSize: QSizeF = pageSize
        self._pageMargins: QMarginsF = pageMargins

        self._content: QByteArray = QByteArray()
        self._meta: QByteArray = QByteArray()
        self._settings: QByteArray = QByteArray()
        self._styles: QByteArray = QByteArray()
        self._xml: QXmlStreamWriter = QXmlStreamWriter()

    # ==================================================================================================================

    def startContentDocument(self) -> None:
        self._xml = QXmlStreamWriter(self._content)
        self._xml.setAutoFormatting(True)
        self._xml.setAutoFormattingIndent(2)

        self._xml.writeStartDocument()
        self._xml.writeStartElement('office:document-content')
        self._xml.writeAttribute('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        self._xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        self._xml.writeAttribute('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        self._xml.writeAttribute('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        self._xml.writeAttribute('office:version', '1.3')

    def startMetaDocument(self) -> None:
        self._xml = QXmlStreamWriter(self._meta)
        self._xml.setAutoFormatting(True)
        self._xml.setAutoFormattingIndent(2)

        self._xml.writeStartDocument()
        self._xml.writeStartElement('office:document-meta')
        self._xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        self._xml.writeAttribute('office:version', '1.3')

    def startSettingsDocument(self) -> None:
        self._xml = QXmlStreamWriter(self._settings)
        self._xml.setAutoFormatting(True)
        self._xml.setAutoFormattingIndent(2)

        self._xml.writeStartDocument()
        self._xml.writeStartElement('office:document-settings')
        self._xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        self._xml.writeAttribute('xmlns:config', 'urn:oasis:names:tc:opendocument:xmlns:config:1.0')
        self._xml.writeAttribute('office:version', '1.3')

    def startStylesDocument(self) -> None:
        self._xml = QXmlStreamWriter(self._styles)
        self._xml.setAutoFormatting(True)
        self._xml.setAutoFormattingIndent(2)

        self._xml.writeStartDocument()
        self._xml.writeStartElement('office:document-styles')
        self._xml.writeAttribute('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
        self._xml.writeAttribute('xmlns:fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        self._xml.writeAttribute('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        self._xml.writeAttribute('xmlns:style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        self._xml.writeAttribute('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        self._xml.writeAttribute('office:version', '1.3')

    def endDocument(self) -> None:
        self._xml.writeEndElement()
        self._xml.writeEndDocument()

    # ==================================================================================================================

    def commit(self) -> None:
        with ZipFile(self._path, 'w') as odgFile:
            with odgFile.open('mimetype', 'w') as mimetypeFile:
                mimetypeFile.write(b'application/vnd.oasis.opendocument.graphics')
            with odgFile.open('META-INF/manifest.xml', 'w') as manifestFile:
                manifestFile.write(self._createManifest())
            with odgFile.open('content.xml', 'w') as contentFile:
                contentFile.write(self._content.data())
            with odgFile.open('meta.xml', 'w') as metaFile:
                metaFile.write(self._meta.data())
            with odgFile.open('settings.xml', 'w') as settingsFile:
                settingsFile.write(self._settings.data())
            with odgFile.open('styles.xml', 'w') as stylesFile:
                stylesFile.write(self._styles.data())

    def _createManifest(self) -> bytes:
        manifestBytes = QByteArray()
        xml = QXmlStreamWriter(manifestBytes)
        xml.setAutoFormatting(True)
        xml.setAutoFormattingIndent(2)

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

        return manifestBytes.data()

    # ==================================================================================================================

    def writeStartElement(self, qualifiedName: str) -> None:
        self._xml.writeStartElement(qualifiedName)

    def writeAttribute(self, qualifiedName: str, value: str) -> None:
        self._xml.writeAttribute(qualifiedName, value)

    def writeCharacters(self, text: str) -> None:
        self._xml.writeCharacters(text)

    def writeEndElement(self) -> None:
        self._xml.writeEndElement()

    # ==================================================================================================================

    def lengthToString(self, value: float) -> str:
        return f'{value:.8g}{str(self._units)}'

    def xCoordinateToString(self, x: float) -> str:
        return f'{x + self._pageMargins.left():.8g}{str(self._units)}'

    def yCoordinateToString(self, y: float) -> str:
        return f'{y + self._pageMargins.top():.8g}{str(self._units)}'

    def writeLengthAttribute(self, qualifiedName: str, value: float) -> None:
        self.writeAttribute(qualifiedName, self.lengthToString(value))

    def writeXCoordinateAttribute(self, qualifiedName: str, x: float) -> None:
        self.writeAttribute(qualifiedName, self.xCoordinateToString(x))

    def writeYCoordinateAttribute(self, qualifiedName: str, y: float) -> None:
        self.writeAttribute(qualifiedName, self.yCoordinateToString(y))

    # ==================================================================================================================

    def writeFillAttributes(self, color: QColor) -> None:
        if (color == QColor(0, 0, 0, 0)):
            self.writeAttribute('draw:fill', 'none')
        else:
            self.writeAttribute('draw:fill', 'solid')
            self.writeAttribute('draw:fill-color', color.name(QColor.NameFormat.HexRgb))
            if (color.alpha() != 255):
                self.writeAttribute('draw:opacity', f'{color.alphaF():.4f}%')
