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
    def _writeBrush(self, element: ElementTree.Element, name: str, brush: QBrush) -> None:
        element.set(f'{name}Color', self._toColorStr(brush.color()))

    def _writePen(self, element: ElementTree.Element, name: str, pen: QPen) -> None:
        styleStr = 'solid'
        match (pen.style()):
            case Qt.PenStyle.NoPen:
                styleStr = 'none'
            case Qt.PenStyle.DashLine:
                styleStr = 'dash'
            case Qt.PenStyle.DotLine:
                styleStr = 'dot'
            case Qt.PenStyle.DashDotLine:
                styleStr = 'dash-dot'
            case Qt.PenStyle.DashDotDotLine:
                styleStr = 'dash-dot-dot'

        element.set(f'{name}Style', styleStr)
        element.set(f'{name}Color', self._toColorStr(pen.brush().color()))
        element.set(f'{name}Width', self._toSizeStr(pen.widthF()))

    def _readBrush(self, element: ElementTree.Element, name: str) -> QBrush:
        return QBrush(self._fromColorStr(element.get(f'{name}Color', '#FFFFFF')))

    def _readPen(self, element: ElementTree.Element, name: str) -> QPen:
        # Get pen style
        penStyle = Qt.PenStyle.SolidLine
        match (element.get(f'{name}Style', 'solid').lower()):
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

        return QPen(QBrush(self._fromColorStr(element.get(f'{name}Color', '#000000'))),
                    self._fromSizeStr(element.get(f'{name}Width', '0')),
                    penStyle, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    # ==================================================================================================================

    def _writeArrow(self, element: ElementTree.Element, name: str, arrow: DrawingArrow) -> None:
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

        element.set(f'{name}Style', styleStr)
        element.set(f'{name}Size', self._toSizeStr(arrow.size()))

    def _readArrow(self, element: ElementTree.Element, name: str) -> DrawingArrow:
        style = DrawingArrow.Style.NoStyle
        match (element.get(f'{name}Style', 'none').lower()):
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

        return DrawingArrow(style, self._fromSizeStr(element.get(f'{name}Size', '0')))

    # ==================================================================================================================

    def _writeFont(self, element: ElementTree.Element, name: str, font: QFont) -> None:
        element.set(f'{name}Name', font.family())
        element.set(f'{name}Size', self._toSizeStr(font.pointSizeF()))
        if (font.bold()):
            element.set(f'{name}Bold', 'true')
        if (font.italic()):
            element.set(f'{name}Italic', 'true')
        if (font.underline()):
            element.set(f'{name}Underline', 'true')
        if (font.strikeOut()):
            element.set(f'{name}StrikeThrough', 'true')

    def _readFont(self, element: ElementTree.Element, name: str) -> QFont:
        font = QFont()
        font.setFamily(element.get(f'{name}Name', font.family()))
        font.setPointSizeF(self._fromSizeStr(element.get(f'{name}Size', '0')))
        font.setBold(element.get(f'{name}Bold', 'false').lower() == 'true')
        font.setItalic(element.get(f'{name}Italic', 'false').lower() == 'true')
        font.setUnderline(element.get(f'{name}Underline', 'false').lower() == 'true')
        font.setStrikeOut(element.get(f'{name}StrikeThrough', 'false').lower() == 'true')
        return font

    # ==================================================================================================================

    def _writeAlignment(self, element: ElementTree.Element, name: str, alignment: Qt.AlignmentFlag) -> None:
        hAlignment = (alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
        hAlignmentStr = 'left'
        if (hAlignment & Qt.AlignmentFlag.AlignHCenter):
            hAlignmentStr = 'center'
        elif (hAlignment & Qt.AlignmentFlag.AlignRight):
            hAlignmentStr = 'right'
        element.set(f'{name}Horizontal', hAlignmentStr)

        vAlignment = (alignment & Qt.AlignmentFlag.AlignVertical_Mask)
        vAlignmentStr = 'top'
        if (vAlignment & Qt.AlignmentFlag.AlignVCenter):
            vAlignmentStr = 'center'
        elif (vAlignment & Qt.AlignmentFlag.AlignBottom):
            vAlignmentStr = 'bottom'
        element.set(f'{name}Vertical', vAlignmentStr)

    def _readAlignment(self, element: ElementTree.Element, name: str) -> Qt.AlignmentFlag:
        hAlignmentStr = element.get(f'{name}Horizontal', 'left').lower()
        hAlignment = Qt.AlignmentFlag.AlignLeft
        if (hAlignmentStr == 'center'):
            hAlignment = Qt.AlignmentFlag.AlignHCenter
        elif (hAlignmentStr == 'right'):
            hAlignment = Qt.AlignmentFlag.AlignRight

        vAlignmentStr = element.get(f'{name}Vertical', 'top').lower()
        vAlignment = Qt.AlignmentFlag.AlignTop
        if (vAlignmentStr == 'center'):
            vAlignment = Qt.AlignmentFlag.AlignVCenter
        elif (vAlignmentStr == 'bottom'):
            vAlignment = Qt.AlignmentFlag.AlignBottom

        return (hAlignment | vAlignment)

    # ==================================================================================================================

    def _toPositionStr(self, position: float) -> str:
        return f'{position}'

    def _toSizeStr(self, size: float) -> str:
        return f'{size}'

    def _toColorStr(self, color: QColor) -> str:
        if (color.alpha() == 255):
            return f'#{color.red():02X}{color.green():02X}{color.blue():02X}'
        return f'#{color.red():02X}{color.green():02X}{color.blue():02X}{color.alpha():02X}'

    def _fromPositionStr(self, text: str) -> float:
        return float(text)

    def _fromSizeStr(self, text: str) -> float:
        return float(text)

    def _fromColorStr(self, text: str) -> QColor:
        color = QColor()
        if (text.startswith('#')):
            if (len(text) in (7, 9)):
                color.setRed(int(text[1:3], 16))
                color.setGreen(int(text[3:5], 16))
                color.setBlue(int(text[5:7], 16))
            if (len(text) == 9):
                color.setAlpha(int(text[7:9], 16))
        return color

    # ==================================================================================================================

    def _toPointsStr(self, points: QPolygonF) -> str:
        pointsStr = ''
        for index in range(points.size()):
            point = points.at(index)
            pointsStr = pointsStr + f'{self._toPositionStr(point.x())},{self._toPositionStr(point.y())} '
        return pointsStr.strip()

    def _fromPointsStr(self, text: str) -> QPolygonF:
        try:
            points = QPolygonF()
            for token in text:
                coords = token.split(',')
                points.append(QPointF(self._fromPositionStr(coords[0]), self._fromPositionStr(coords[1])))
            return points
        except (KeyError, ValueError):
            pass
        return QPolygonF()

    # ==================================================================================================================

    def _toPathStr(self, path: QPainterPath) -> str:
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
        return pathStr.strip()

    def _fromPathStr(self, text: str) -> QPainterPath:
        try:
            path = QPainterPath()

            tokenList = text.split(' ')
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
