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

from zipfile import ZipFile
from PySide6.QtCore import QXmlStreamAttributes, QXmlStreamReader


class OdgReader:
    def __init__(self, path: str) -> None:
        self._path: str = path

        self._content: str = ''
        self._settings: str = ''
        self._styles: str = ''
        with ZipFile(self._path, 'r') as odgFile:
            with odgFile.open('settings.xml', 'r') as settingsFile:
                self._settings = settingsFile.read().decode('utf-8')
            with odgFile.open('styles.xml', 'r') as stylesFile:
                self._styles = stylesFile.read().decode('utf-8')
            with odgFile.open('content.xml', 'r') as contentFile:
                self._content = contentFile.read().decode('utf-8')

        self._xml: QXmlStreamReader = QXmlStreamReader()

    # ==================================================================================================================

    def startContentDocument(self) -> None:
        self._xml = QXmlStreamReader(self._content)

        if (self._xml.readNextStartElement() and self._xml.qualifiedName() == 'office:document-content'):
            pass
        else:
            self._xml.skipCurrentElement()

    def startSettingsDocument(self) -> None:
        self._xml = QXmlStreamReader(self._settings)

        if (self._xml.readNextStartElement() and self._xml.qualifiedName() == 'office:document-settings'):
            pass
        else:
            self._xml.skipCurrentElement()

    def startStylesDocument(self) -> None:
        self._xml = QXmlStreamReader(self._styles)

        if (self._xml.readNextStartElement() and self._xml.qualifiedName() == 'office:document-styles'):
            pass
        else:
            self._xml.skipCurrentElement()

    def endDocument(self) -> None:
        pass

    # ==================================================================================================================

    def readNextStartElement(self) -> bool:
        return self._xml.readNextStartElement()

    def skipCurrentElement(self) -> None:
        self._xml.skipCurrentElement()

    def qualifiedName(self) -> str:
        return self._xml.qualifiedName()

    def attributes(self) -> QXmlStreamAttributes:
        return self._xml.attributes()

    def readElementText(self) -> str:
        return self._xml.readElementText()
