# odgfontstyle.py
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

class OdgFontStyle:
    def __init__(self, bold: bool = False, italic: bool = False, underline: bool = False,
                 strikeOut: bool = False) -> None:
        self._bold: bool = bold
        self._italic: bool = italic
        self._underline: bool = underline
        self._strikeOut: bool = strikeOut

    def __eq__(self, other: object) -> bool:
        if (isinstance(other, OdgFontStyle)):
            return (self._bold == other.bold() and self._italic == other.italic() and
                    self._underline == other.underline() and self._strikeOut == other.strikeOut())
        return False

    # ==================================================================================================================

    def setBold(self, bold: bool) -> None:
        self._bold = bold

    def setItalic(self, italic: bool) -> None:
        self._italic = italic

    def setUnderline(self, underline: bool) -> None:
        self._underline = underline

    def setStrikeOut(self, strikeOut: bool) -> None:
        self._strikeOut = strikeOut

    def bold(self) -> bool:
        return self._bold

    def italic(self) -> bool:
        return self._italic

    def underline(self) -> bool:
        return self._underline

    def strikeOut(self) -> bool:
        return self._strikeOut

    # ==================================================================================================================

    @classmethod
    def copy(cls, other: 'OdgFontStyle') -> 'OdgFontStyle':
        newStyle = cls()
        newStyle.setBold(other.bold())
        newStyle.setItalic(other.italic())
        newStyle.setUnderline(other.underline())
        newStyle.setStrikeOut(other.strikeOut())
        return newStyle
