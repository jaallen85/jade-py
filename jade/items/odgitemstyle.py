# odgitemstyle.py
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from .odgmarker import OdgMarker


class OdgItemStyle:
    def __init__(self, name: str) -> None:
        self._name: str = name

        self._parent: OdgItemStyle | None = None

        self._penStyle: Qt.PenStyle | None = None
        self._penWidth: float | None = None
        self._penColor: QColor | None = None
        self._penCapStyle: Qt.PenCapStyle | None = None
        self._penJoinStyle: Qt.PenJoinStyle | None = None
        self._brushColor: QColor | None = None

        self._startMarkerStyle: OdgMarker.Style | None = None
        self._startMarkerSize: float | None = None
        self._endMarkerStyle: OdgMarker.Style | None = None
        self._endMarkerSize: float | None = None

    # ==================================================================================================================

    def setName(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        return self._name

    # ==================================================================================================================

    def setParent(self, parent: 'OdgItemStyle | None') -> None:
        self._parent = parent

    def parent(self) -> 'OdgItemStyle | None':
        return self._parent

    # ==================================================================================================================

    def setPenStyle(self, style: Qt.PenStyle | None) -> None:
        self._penStyle = style

    def setPenWidth(self, width: float | None) -> None:
        self._penWidth = width

    def setPenColor(self, color: QColor | None) -> None:
        if (isinstance(color, QColor)):
            self._penColor = QColor(color)
        else:
            self._penColor = None

    def setPenCapStyle(self, style: Qt.PenCapStyle | None) -> None:
        self._penCapStyle = style

    def setPenJoinStyle(self, style: Qt.PenJoinStyle | None) -> None:
        self._penJoinStyle = style

    def setBrushColor(self, color: QColor | None) -> None:
        if (isinstance(color, QColor)):
            self._brushColor = QColor(color)
        else:
            self._brushColor = None

    def penStyle(self) -> Qt.PenStyle | None:
        return self._penStyle

    def penWidth(self) -> float | None:
        return self._penWidth

    def penColor(self) -> QColor | None:
        return self._penColor

    def penCapStyle(self) -> Qt.PenCapStyle | None:
        return self._penCapStyle

    def penJoinStyle(self) -> Qt.PenJoinStyle | None:
        return self._penJoinStyle

    def brushColor(self) -> QColor | None:
        return self._brushColor

    # ==================================================================================================================

    def setStartMarkerStyle(self, style: OdgMarker.Style | None) -> None:
        self._startMarkerStyle = style

    def setStartMarkerSize(self, size: float | None) -> None:
        self._startMarkerSize = size

    def setEndMarkerStyle(self, style: OdgMarker.Style | None) -> None:
        self._endMarkerStyle = style

    def setEndMarkerSize(self, size: float | None) -> None:
        self._endMarkerSize = size

    def startMarkerStyle(self) -> OdgMarker.Style | None:
        return self._startMarkerStyle

    def startMarkerSize(self) -> float | None:
        return self._startMarkerSize

    def endMarkerStyle(self) -> OdgMarker.Style | None:
        return self._endMarkerStyle

    def endMarkerSize(self) -> float | None:
        return self._endMarkerSize

    # ==================================================================================================================

    def clear(self) -> None:
        self.setName('')
        self.setParent(None)

        self.setPenStyle(None)
        self.setPenWidth(None)
        self.setPenColor(None)
        self.setPenCapStyle(None)
        self.setPenJoinStyle(None)
        self.setBrushColor(None)

        self.setStartMarkerStyle(None)
        self.setStartMarkerSize(None)
        self.setEndMarkerStyle(None)
        self.setEndMarkerSize(None)

    def copyFromStyle(self, other: 'OdgItemStyle') -> None:
        self.setParent(other.parent())

        self.setPenStyle(other.penStyle())
        self.setPenWidth(other.penWidth())
        self.setPenColor(other.penColor())
        self.setPenCapStyle(other.penCapStyle())
        self.setPenJoinStyle(other.penJoinStyle())
        self.setBrushColor(other.brushColor())

        self.setStartMarkerStyle(other.startMarkerStyle())
        self.setStartMarkerSize(other.startMarkerSize())
        self.setEndMarkerStyle(other.endMarkerStyle())
        self.setEndMarkerSize(other.endMarkerSize())

    def scale(self, scale: float) -> None:
        if (isinstance(self._penWidth, float)):
            self._penWidth = self._penWidth * scale
        if (isinstance(self._startMarkerSize, float)):
            self._startMarkerSize = self._startMarkerSize * scale
        if (isinstance(self._endMarkerSize, float)):
            self._endMarkerSize = self._endMarkerSize * scale

    # ==================================================================================================================

    def lookupPen(self) -> QPen:
        return QPen(QBrush(self.lookupPenColor()), self.lookupPenWidth(), self.lookupPenStyle(),
                    self.lookupPenCapStyle(), self.lookupPenJoinStyle())

    def lookupPenStyle(self) -> Qt.PenStyle:
        if (isinstance(self._penStyle, Qt.PenStyle)):
            return self._penStyle
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupPenStyle()
        return Qt.PenStyle.NoPen

    def lookupPenColor(self) -> QColor:
        if (isinstance(self._penColor, QColor)):
            return self._penColor
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupPenColor()
        return QColor(0, 0, 0)

    def lookupPenWidth(self) -> float:
        if (isinstance(self._penWidth, float)):
            return self._penWidth
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupPenWidth()
        return 1.0

    def lookupPenCapStyle(self) -> Qt.PenCapStyle:
        if (isinstance(self._penCapStyle, Qt.PenCapStyle)):
            return self._penCapStyle
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupPenCapStyle()
        return Qt.PenCapStyle.RoundCap

    def lookupPenJoinStyle(self) -> Qt.PenJoinStyle:
        if (isinstance(self._penJoinStyle, Qt.PenJoinStyle)):
            return self._penJoinStyle
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupPenJoinStyle()
        return Qt.PenJoinStyle.RoundJoin

    # ==================================================================================================================

    def lookupBrush(self) -> QBrush:
        return QBrush(self.lookupBrushColor())

    def lookupBrushColor(self) -> QColor:
        if (isinstance(self._brushColor, QColor)):
            return self._brushColor
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupBrushColor()
        return QColor(255, 255, 255)

    # ==================================================================================================================

    def lookupStartMarker(self) -> OdgMarker:
        return OdgMarker(self.lookupStartMarkerStyle(), self.lookupStartMarkerSize())

    def lookupEndMarker(self) -> OdgMarker:
        return OdgMarker(self.lookupEndMarkerStyle(), self.lookupEndMarkerSize())

    def lookupStartMarkerStyle(self) -> OdgMarker.Style:
        if (isinstance(self._startMarkerStyle, OdgMarker.Style)):
            return self._startMarkerStyle
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupStartMarkerStyle()
        return OdgMarker.Style.NoMarker

    def lookupStartMarkerSize(self) -> float:
        if (isinstance(self._startMarkerSize, float)):
            return self._startMarkerSize
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupStartMarkerSize()
        return 0.0

    def lookupEndMarkerStyle(self) -> OdgMarker.Style:
        if (isinstance(self._endMarkerStyle, OdgMarker.Style)):
            return self._endMarkerStyle
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupEndMarkerStyle()
        return OdgMarker.Style.NoMarker

    def lookupEndMarkerSize(self) -> float:
        if (isinstance(self._endMarkerSize, float)):
            return self._endMarkerSize
        if (isinstance(self._parent, OdgItemStyle)):
            return self._parent.lookupEndMarkerSize()
        return 0.0

    # ==================================================================================================================

    def setPenStyleIfUnique(self, style: Qt.PenStyle) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupPenStyle() == style):
            self._penStyle = None
        else:
            self._penStyle = style

    def setPenWidthIfUnique(self, width: float) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupPenWidth() == width):
            self._penWidth = None
        else:
            self._penWidth = width

    def setPenColorIfUnique(self, color: QColor) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupPenColor() == color):
            self._penColor = None
        else:
            self._penColor = QColor(color)

    def setPenCapStyleIfUnique(self, style: Qt.PenCapStyle) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupPenCapStyle() == style):
            self._penCapStyle = None
        else:
            self._penCapStyle = style

    def setPenJoinStyleIfUnique(self, style: Qt.PenJoinStyle) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupPenJoinStyle() == style):
            self._penJoinStyle = None
        else:
            self._penJoinStyle = style

    def setBrushColorIfUnique(self, color: QColor) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupBrushColor() == color):
            self._brushColor = None
        else:
            self._brushColor = QColor(color)

    # ==================================================================================================================

    def setStartMarkerStyleIfUnique(self, style: OdgMarker.Style) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupStartMarkerStyle() == style):
            self._startMarkerStyle = None
        else:
            self._startMarkerStyle = style

    def setStartMarkerSizeIfUnique(self, size: float) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupStartMarkerSize() == size):
            self._startMarkerSize = None
        else:
            self._startMarkerSize = size

    def setEndMarkerStyleIfUnique(self, style: OdgMarker.Style) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupEndMarkerStyle() == style):
            self._endMarkerStyle = None
        else:
            self._endMarkerStyle = style

    def setEndMarkerSizeIfUnique(self, size: float) -> None:
        if (isinstance(self._parent, OdgItemStyle) and self._parent.lookupEndMarkerSize() == size):
            self._endMarkerSize = None
        else:
            self._endMarkerSize = size

    # ==================================================================================================================

    @classmethod
    def createDefaultStyle(cls, penWidth: float) -> 'OdgItemStyle':
        style = cls('standard')

        style.setBrushColor(QColor(255, 255, 255))

        style.setPenStyle(Qt.PenStyle.SolidLine)
        style.setPenWidth(penWidth)
        style.setPenColor(QColor(0, 0, 0))
        style.setPenCapStyle(Qt.PenCapStyle.RoundCap)
        style.setPenJoinStyle(Qt.PenJoinStyle.RoundJoin)

        style.setStartMarkerStyle(OdgMarker.Style.NoMarker)
        style.setStartMarkerSize(6 * penWidth)
        style.setEndMarkerStyle(OdgMarker.Style.NoMarker)
        style.setEndMarkerSize(6 * penWidth)

        return style
