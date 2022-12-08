# drawingxmlinterface.py
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
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPolygonF
from .drawingarrow import DrawingArrow


class DrawingXmlInterface:
    def writeStr(self, element: ElementTree.Element, name: str, value: str, writeIfDefault: bool = False) -> None:
        if (writeIfDefault or value != '0'):
            element.set(name, value)

    def writeInt(self, element: ElementTree.Element, name: str, value: int, writeIfDefault: bool = False) -> None:
        if (writeIfDefault or value != 0):
            element.set(name, f'{value}')

    def writeFloat(self, element: ElementTree.Element, name: str, value: float, writeIfDefault: bool = False) -> None:
        if (writeIfDefault or value != 0.0):
            element.set(name, f'{value}')

    def writeBool(self, element: ElementTree.Element, name: str, value: bool, writeIfDefault: bool = False) -> None:
        if (writeIfDefault or value):
            element.set(name, 'true' if (value) else 'false')

    def writeColor(self, element: ElementTree.Element, name: str, color: QColor, writeIfDefault: bool = False) -> None:
        if (writeIfDefault or color != QColor(0, 0, 0)):
            if (color.alpha() == 255):
                element.set(name, f'#{color.red():02X}{color.green():02X}{color.blue():02X}')
            else:
                element.set(name, f'#{color.red():02X}{color.green():02X}{color.blue():02X}{color.alpha():02X}')

    def readStr(self, element: ElementTree.Element, name: str) -> str:
        return element.get(name, '')

    def readInt(self, element: ElementTree.Element, name: str) -> int:
        try:
            return int(element.get(name, '0'))
        except ValueError:
            pass
        return 0

    def readFloat(self, element: ElementTree.Element, name: str) -> float:
        try:
            return float(element.get(name, '0'))
        except ValueError:
            pass
        return 0.0

    def readBool(self, element: ElementTree.Element, name: str) -> bool:
        return (element.get(name, 'false').lower() == 'true')

    def readColor(self, element: ElementTree.Element, name: str) -> QColor:
        try:
            colorStr = element.get(name, '#000000')
            if (len(colorStr) == 9):
                return QColor(int(colorStr[1:3], 16), int(colorStr[3:5], 16), int(colorStr[5:7], 16),
                              int(colorStr[7:9], 16))
            return QColor(int(colorStr[1:3], 16), int(colorStr[3:5], 16), int(colorStr[5:7], 16))
        except ValueError:
            pass
        return QColor(0, 0, 0)

    # ==================================================================================================================

    def writeBrush(self, element: ElementTree.Element, name: str, brush: QBrush) -> None:
        self.writeColor(element, f'{name}Color', brush.color(), writeIfDefault=True)

    def writePen(self, element: ElementTree.Element, name: str, pen: QPen) -> None:
        self.writeColor(element, f'{name}Color', pen.brush().color(), writeIfDefault=True)
        self.writeFloat(element, f'{name}Width', pen.widthF(), writeIfDefault=True)

        # Set pen style
        penStyle = 'solid'
        match (pen.style()):
            case Qt.PenStyle.NoPen:
                penStyle = 'none'
            case Qt.PenStyle.DashLine:
                penStyle = 'dash'
            case Qt.PenStyle.DotLine:
                penStyle = 'dot'
            case Qt.PenStyle.DashDotLine:
                penStyle = '"dash-dot'
            case Qt.PenStyle.DashDotDotLine:
                penStyle = 'dash-dot-dot'
        self.writeStr(element, name, penStyle)

    def writeFont(self, element: ElementTree.Element, name: str, font: QFont) -> None:
        self.writeStr(element, f'{name}Name', font.family())
        self.writeFloat(element, f'{name}Size', font.pointSizeF(), writeIfDefault=True)
        self.writeBool(element, f'{name}Bold', font.bold())
        self.writeBool(element, f'{name}Italic', font.italic())
        self.writeBool(element, f'{name}Underline', font.underline())
        self.writeBool(element, f'{name}StrikeThrough', font.strikeOut())

    def writeAlignment(self, element: ElementTree.Element, name: str, alignment: Qt.AlignmentFlag) -> None:
        hAlignment = (alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
        hAlignmentStr = 'left'
        if (hAlignment & Qt.AlignmentFlag.AlignHCenter):
            hAlignmentStr = 'center'
        elif (hAlignment & Qt.AlignmentFlag.AlignRight):
            hAlignmentStr = 'right'
        self.writeStr(element, f'{name}Horizontal', hAlignmentStr)

        vAlignment = (alignment & Qt.AlignmentFlag.AlignVertical_Mask)
        vAlignmentStr = 'top'
        if (vAlignment & Qt.AlignmentFlag.AlignVCenter):
            vAlignmentStr = 'center'
        elif (vAlignment & Qt.AlignmentFlag.AlignBottom):
            vAlignmentStr = 'bottom'
        self.writeStr(element, f'{name}Vertical', vAlignmentStr)

    def writeArrow(self, element: ElementTree.Element, name: str, arrow: DrawingArrow) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            styleStr = 'none'
            match (arrow.style()):
                case DrawingArrow.Style.Normal:
                    styleStr = 'normal'
                case DrawingArrow.Style.Triangle:
                    styleStr = 'triangle'
                case DrawingArrow.Style.TriangleFilled:
                    styleStr = 'triangleFilled'
                case DrawingArrow.Style.Concave:
                    styleStr = 'concave'
                case DrawingArrow.Style.ConcaveFilled:
                    styleStr = 'concaveFilled'
                case DrawingArrow.Style.Circle:
                    styleStr = 'circle'
                case DrawingArrow.Style.CircleFilled:
                    styleStr = 'circleFilled'
            self.writeStr(element, f'{name}Style', styleStr)
        self.writeFloat(element, f'{name}Size', arrow.size())

    def writePoints(self, element: ElementTree.Element, name: str, points: QPolygonF) -> None:
        pointsStr = ''
        for index in range(points.size()):
            point = points.at(index)
            pointsStr = pointsStr + f'{point.x()},{point.y()} '
        self.writeStr(element, name, pointsStr.strip())

    def writePath(self, element: ElementTree.Element, name: str, path: QPainterPath) -> None:
        pathStr = ''
        for index in range(path.elementCount()):
            pathElement = path.elementAt(index)
            match (pathElement.type):                                       # type: ignore
                case QPainterPath.ElementType.MoveToElement:
                    pathStr = f'{pathStr} M {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.LineToElement:
                    pathStr = f'{pathStr} L {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.CurveToElement:
                    pathStr = f'{pathStr} C {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.CurveToDataElement:
                    pathStr = f'{pathStr} {pathElement.x} {pathElement.y}'      # type: ignore
        self.writeStr(element, name, pathStr.strip())

    def readBrush(self, element: ElementTree.Element, name: str) -> QBrush:
        return QBrush(self.readColor(element, f'{name}Color'))

    def readPen(self, element: ElementTree.Element, name: str) -> QPen:
        # Get pen style
        penStyle = Qt.PenStyle.SolidLine
        match (self.readStr(element, f'{name}Style').lower()):
            case 'none':
                penStyle = Qt.PenStyle.NoPen
            case 'dash':
                penStyle = Qt.PenStyle.DashLine
            case 'dot':
                penStyle = Qt.PenStyle.DotLine
            case 'dash-dot':
                penStyle = Qt.PenStyle.DashDotLine
            case 'dash-dot-dot':
                penStyle = Qt.PenStyle.DashDotDotLine

        return QPen(QBrush(self.readColor(element, f'{name}Color')),
                    self.readFloat(element, f'{name}Width'),
                    penStyle, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    def readFont(self, element: ElementTree.Element, name: str) -> QFont:
        font = QFont()
        font.setFamily(self.readStr(element, f'{name}Name'))
        font.setPointSizeF(self.readFloat(element, f'{name}Size'))
        font.setBold(self.readBool(element, f'{name}Bold'))
        font.setItalic(self.readBool(element, f'{name}Italic'))
        font.setUnderline(self.readBool(element, f'{name}Underline'))
        font.setStrikeOut(self.readBool(element, f'{name}StrikeThrough'))
        return font

    def readAlignment(self, element: ElementTree.Element, name: str) -> Qt.AlignmentFlag:
        hAlignmentStr = self.readStr(element, f'{name}Horizontal').lower()
        hAlignment = Qt.AlignmentFlag.AlignLeft
        if (hAlignmentStr == 'center'):
            hAlignment = Qt.AlignmentFlag.AlignHCenter
        elif (hAlignmentStr == 'right'):
            hAlignment = Qt.AlignmentFlag.AlignRight

        vAlignmentStr = self.readStr(element, f'{name}Vertical').lower()
        vAlignment = Qt.AlignmentFlag.AlignTop
        if (vAlignmentStr == 'center'):
            vAlignment = Qt.AlignmentFlag.AlignVCenter
        elif (vAlignmentStr == 'bottom'):
            vAlignment = Qt.AlignmentFlag.AlignBottom

        return (hAlignment | vAlignment)

    def readArrow(self, element: ElementTree.Element, name: str) -> DrawingArrow:
        style = DrawingArrow.Style.NoStyle
        match (self.readStr(element, f'{name}Style').lower()):
            case 'normal':
                style = DrawingArrow.Style.Normal
            case 'triangle':
                style = DrawingArrow.Style.Triangle
            case 'trianglefilled':
                style = DrawingArrow.Style.TriangleFilled
            case 'concave':
                style = DrawingArrow.Style.Concave
            case 'concavefilled':
                style = DrawingArrow.Style.ConcaveFilled
            case 'circle':
                style = DrawingArrow.Style.Circle
            case 'circlefilled':
                style = DrawingArrow.Style.CircleFilled

        return DrawingArrow(style, self.readFloat(element, f'{name}Size'))

    def readPoints(self, element: ElementTree.Element, name: str) -> QPolygonF:
        try:
            points = QPolygonF()
            for token in self.readStr(element, name).split(' '):
                coords = token.split(',')
                points.append(QPointF(float(coords[0]), float(coords[1])))
            return points
        except (KeyError, ValueError):
            pass
        return QPolygonF()

    def readPath(self, element: ElementTree.Element, name: str) -> QPainterPath:
        try:
            path = QPainterPath()

            tokenList = self.readStr(element, name).split(' ')
            for index, token in enumerate(tokenList):
                if (token == 'M'):
                    path.moveTo(float(tokenList[index + 1]), float(tokenList[index + 2]))
                elif (token == 'L'):
                    path.lineTo(float(tokenList[index + 1]), float(tokenList[index + 2]))
                elif (token == 'C'):
                    path.cubicTo(float(tokenList[index + 1]), float(tokenList[index + 2]),
                                 float(tokenList[index + 3]), float(tokenList[index + 4]),
                                 float(tokenList[index + 5]), float(tokenList[index + 6]))

            return path
        except (ValueError, IndexError):
            pass
        return QPainterPath()
