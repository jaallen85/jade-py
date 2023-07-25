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
from .odgunits import OdgUnits
from .odgwriter import OdgWriter


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

    # ==================================================================================================================

    def write(self, writer: OdgWriter) -> None:
        if (self._name != ''):
            writer.writeAttribute('style:name', self._name)
        writer.writeAttribute('style:family', 'graphic')
        if (isinstance(self._parent, OdgItemStyle)):
            writer.writeAttribute('style:parent-style-name', self._parent.name())

        writer.writeStartElement('style:graphic-properties')

        # Pen style
        if (isinstance(self._penStyle, Qt.PenStyle)):
            match (self._penStyle):
                case Qt.PenStyle.SolidLine:
                    writer.writeAttribute('draw:stroke', 'solid')
                case Qt.PenStyle.DashLine:
                    writer.writeAttribute('draw:stroke', 'dash')
                    writer.writeAttribute('draw:stroke-dash', 'Dash_20__28_Rounded_29_')
                case Qt.PenStyle.DotLine:
                    writer.writeAttribute('draw:stroke', 'dash')
                    writer.writeAttribute('draw:stroke-dash', 'Dot_20__28_Rounded_29_')
                case Qt.PenStyle.DashDotLine:
                    writer.writeAttribute('draw:stroke', 'dash')
                    writer.writeAttribute('draw:stroke-dash', 'Dash_20_Dot_20__28_Rounded_29_')
                case Qt.PenStyle.DashDotDotLine:
                    writer.writeAttribute('draw:stroke', 'dash')
                    writer.writeAttribute('draw:stroke-dash', 'Dash_20_Dot_20_Dot_20__28_Rounded_29_')
                case _:
                    writer.writeAttribute('draw:stroke', 'none')

        # Pen width
        if (isinstance(self._penWidth, float)):
            writer.writeLengthAttribute('svg:stroke-width', self._penWidth)

        # Pen color
        if (isinstance(self._penColor, QColor)):
            writer.writeAttribute('svg:stroke-color', self._penColor.name(QColor.NameFormat.HexRgb))
            if (self._penColor.alpha() != 255):
                writer.writeAttribute('svg:stroke-opacity', f'{self._penColor.alphaF() * 100:.1f}%')

        # Pen cap style
        if (isinstance(self._penCapStyle, Qt.PenCapStyle)):
            match (self._penCapStyle):
                case Qt.PenCapStyle.FlatCap:
                    writer.writeAttribute('svg:stroke-linecap', 'butt')
                case Qt.PenCapStyle.SquareCap:
                    writer.writeAttribute('svg:stroke-linecap', 'square')
                case _:
                    writer.writeAttribute('svg:stroke-linecap', 'round')

        # Pen join style
        if (isinstance(self._penJoinStyle, Qt.PenJoinStyle)):
            match (self._penJoinStyle):
                case (Qt.PenJoinStyle.MiterJoin | Qt.PenJoinStyle.SvgMiterJoin):
                    writer.writeAttribute('draw:stroke-linejoin', 'miter')
                case Qt.PenJoinStyle.BevelJoin:
                    writer.writeAttribute('draw:stroke-linejoin', 'bevel')
                case _:
                    writer.writeAttribute('draw:stroke-linejoin', 'round')

        # Brush color
        if (isinstance(self._brushColor, QColor)):
            writer.writeFillAttributes(self._brushColor)

        # Start marker style
        if (isinstance(self._startMarkerStyle, OdgMarker.Style)):
            match (self._startMarkerStyle):
                case OdgMarker.Style.Triangle:
                    writer.writeAttribute('draw:marker-start', 'Triangle')
                    writer.writeAttribute('draw:marker-start-center', 'false')
                case OdgMarker.Style.Circle:
                    writer.writeAttribute('draw:marker-start', 'Circle')
                    writer.writeAttribute('draw:marker-start-center', 'true')
                case _:
                    pass

        # Start marker size
        if (isinstance(self._startMarkerSize, float)):
            writer.writeLengthAttribute('draw:marker-start-width', self._startMarkerSize)

        # End marker style
        if (isinstance(self._endMarkerStyle, OdgMarker.Style)):
            match (self._endMarkerStyle):
                case OdgMarker.Style.Triangle:
                    writer.writeAttribute('draw:marker-end', 'Triangle')
                    writer.writeAttribute('draw:marker-end-center', 'false')
                case OdgMarker.Style.Circle:
                    writer.writeAttribute('draw:marker-end', 'Circle')
                    writer.writeAttribute('draw:marker-end-center', 'true')
                case _:
                    pass

        # End marker size
        if (isinstance(self._endMarkerSize, float)):
            writer.writeLengthAttribute('draw:marker-end-width', self._endMarkerSize)

        writer.writeEndElement()

    # ==================================================================================================================

    @staticmethod
    def writeDashStyles(writer: OdgWriter) -> None:
        # OpenOffice built-in dash styles
        writer.writeStartElement('draw:stroke-dash')
        writer.writeAttribute('draw:name', 'Dash_20__28_Rounded_29_')
        writer.writeAttribute('draw:display-name', 'Dash (Rounded)')
        writer.writeAttribute('draw:style', 'round')
        writer.writeAttribute('draw:dots1', '1')
        writer.writeAttribute('draw:dots1-length', '201%')
        writer.writeAttribute('draw:distance', '199%')
        writer.writeEndElement()

        writer.writeStartElement('draw:stroke-dash')
        writer.writeAttribute('draw:name', 'Dot_20__28_Rounded_29_')
        writer.writeAttribute('draw:display-name', 'Dot (Rounded)')
        writer.writeAttribute('draw:style', 'round')
        writer.writeAttribute('draw:dots1', '1')
        writer.writeAttribute('draw:dots1-length', '1%')
        writer.writeAttribute('draw:distance', '199%')
        writer.writeEndElement()

        writer.writeStartElement('draw:stroke-dash')
        writer.writeAttribute('draw:name', 'Dash_20_Dot_20__28_Rounded_29_')
        writer.writeAttribute('draw:display-name', 'Dash Dot (Rounded)')
        writer.writeAttribute('draw:style', 'round')
        writer.writeAttribute('draw:dots1', '1')
        writer.writeAttribute('draw:dots1-length', '201%')
        writer.writeAttribute('draw:dots2', '1')
        writer.writeAttribute('draw:dots2-length', '1%')
        writer.writeAttribute('draw:distance', '199%')
        writer.writeEndElement()

        writer.writeStartElement('draw:stroke-dash')
        writer.writeAttribute('draw:name', 'Dash_20_Dot_20_Dot_20__28_Rounded_29_')
        writer.writeAttribute('draw:display-name', 'Dash Dot Dot (Rounded)')
        writer.writeAttribute('draw:style', 'round')
        writer.writeAttribute('draw:dots1', '1')
        writer.writeAttribute('draw:dots1-length', '201%')
        writer.writeAttribute('draw:dots2', '2')
        writer.writeAttribute('draw:dots2-length', '1%')
        writer.writeAttribute('draw:distance', '199%')
        writer.writeEndElement()

    @staticmethod
    def writeMarkerStyles(writer: OdgWriter) -> None:
        writer.writeStartElement('draw:marker')
        writer.writeAttribute('draw:name', 'Triangle')
        writer.writeAttribute('svg:viewBox', '0 0 1013 1130')
        writer.writeAttribute('svg:d', ('M1009 1050l-449-1008-22-30-29-12-34 12-21 26-449 1012-5 13v8l5 21 12 21 17 '
                                        '13 21 4h903l21-4 21-13 9-21 4-21v-8z'))
        writer.writeEndElement()

        writer.writeStartElement('draw:marker')
        writer.writeAttribute('draw:name', 'Circle')
        writer.writeAttribute('svg:viewBox', '0 0 1131 1131')
        writer.writeAttribute('svg:d', ('M462 1118l-102-29-102-51-93-72-72-93-51-102-29-102-13-105 13-102 29-106 '
                                        '51-102 72-89 93-72 102-50 102-34 106-9 101 9 106 34 98 50 93 72 72 89 51 102 '
                                        '29 106 13 102-13 105-29 102-51 102-72 93-93 72-98 51-106 29-101 13z'))
        writer.writeEndElement()

    # ==================================================================================================================

    @classmethod
    def createDefaultStyle(cls, units: OdgUnits) -> 'OdgItemStyle':
        style = cls('standard')

        style.setBrushColor(QColor(255, 255, 255))

        style.setPenStyle(Qt.PenStyle.SolidLine)
        style.setPenWidth(0.01 if (units == OdgUnits.Inches) else 0.25)
        style.setPenColor(QColor(0, 0, 0))
        style.setPenCapStyle(Qt.PenCapStyle.RoundCap)
        style.setPenJoinStyle(Qt.PenJoinStyle.RoundJoin)

        style.setStartMarkerStyle(OdgMarker.Style.NoMarker)
        style.setStartMarkerSize(0.06 if (units == OdgUnits.Inches) else 1.5)
        style.setEndMarkerStyle(OdgMarker.Style.NoMarker)
        style.setEndMarkerSize(0.06 if (units == OdgUnits.Inches) else 1.5)

        return style
