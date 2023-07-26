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

import re
from zipfile import ZipFile
from PySide6.QtCore import QMarginsF, QSizeF, QXmlStreamAttributes, QXmlStreamReader
from .odgunits import OdgUnits


class OdgReader:
    def __init__(self, path: str) -> None:
        self._path: str = path

        self._units: OdgUnits = OdgUnits.Millimeters
        self._pageSize: QSizeF = QSizeF(0, 0)
        self._pageMargins: QMarginsF = QMarginsF(0, 0, 0, 0)

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

    def setUnits(self, units: OdgUnits) -> None:
        self._units = units

    def setPageSize(self, size: QSizeF) -> None:
        self._pageSize = size

    def setPageMargins(self, margins: QMarginsF) -> None:
        self._pageMargins = margins

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

    # ==================================================================================================================

    def lengthFromString(self, text: str) -> float:
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

    def xCoordinateFromString(self, text: str) -> float:
        return self.lengthFromString(text) - self._pageMargins.left()

    def yCoordinateFromString(self, text: str) -> float:
        return self.lengthFromString(text) - self._pageMargins.top()

    def percentFromString(self, text: str) -> float:
        text = text.strip()
        try:
            if (text.endswith('%')):
                return float(text[:-1]) / 100.0
            return float(text)
        except ValueError:
            pass
        return 0
