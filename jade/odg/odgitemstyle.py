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

from abc import ABC, abstractmethod
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from .odgmarker import OdgMarker
from .odgunits import OdgUnits


class OdgItemStyleBase(ABC):
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

    @abstractmethod
    def setParent(self, parent: 'OdgItemStyle | None') -> None:
        pass

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


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgItemStyle(OdgItemStyleBase):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._children: list[OdgItemStyle] = []

    def __del__(self) -> None:
        self.clearChildren()

    # ==================================================================================================================

    def setParent(self, parent: 'OdgItemStyle | None') -> None:
        if (isinstance(self._parent, OdgItemStyle)):
            self._parent.removeChild(self)
        self._parent = parent
        if (isinstance(self._parent, OdgItemStyle)):
            self._parent.addChild(self)

    def addChild(self, style: 'OdgItemStyle') -> None:
        self.insertChild(len(self._children), style)

    def insertChild(self, index: int, style: 'OdgItemStyle') -> None:
        if (style not in self._children):
            self._children.insert(index, style)
            # pylint: disable-next=W0212
            style._parent = self

    def removeChild(self, style: 'OdgItemStyle') -> None:
        if (style in self._children):
            self._children.remove(style)
            # pylint: disable-next=W0212
            style._parent = None

    def clearChildren(self) -> None:
        while (len(self._children) > 0):
            style = self._children[-1]
            self.removeChild(style)
            del style

    def children(self) -> 'list[OdgItemStyle]':
        return self._children

    # ==================================================================================================================

    def sort(self, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self._children = sorted(self._children, key=(lambda x: x.name()),
                                reverse=(order == Qt.SortOrder.DescendingOrder))
        for child in self._children:
            child.sort(order)

    # ==================================================================================================================

    @classmethod
    def createDefault(cls, units: OdgUnits) -> 'OdgItemStyle':
        style = cls('Default')

        style.setBrushColor(QColor(255, 255, 255))

        style.setPenStyle(Qt.PenStyle.SolidLine)
        style.setPenWidth(0.01 if (units == OdgUnits.Inches) else 0.25)
        style.setPenColor(QColor(0, 0, 0))
        style.setPenCapStyle(Qt.PenCapStyle.RoundCap)
        style.setPenJoinStyle(Qt.PenJoinStyle.RoundJoin)

        style.setStartMarkerStyle(OdgMarker.Style.NoMarker)
        style.setStartMarkerSize(0.1 if (units == OdgUnits.Inches) else 2.5)
        style.setEndMarkerStyle(OdgMarker.Style.NoMarker)
        style.setEndMarkerSize(0.1 if (units == OdgUnits.Inches) else 2.5)

        return style


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgItemAutomaticStyle(OdgItemStyleBase):
    def setParent(self, parent: OdgItemStyle | None) -> None:
        self._parent = parent
