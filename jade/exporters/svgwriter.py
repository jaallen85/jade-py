# svgwriter.py
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

import math
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QLineF, QPointF
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitemgroup import DrawingItemGroup
from ..drawing.drawingpagewidget import DrawingPageWidget
from ..drawing.drawingxmlinterface import DrawingXmlInterface
from ..items.drawingcurveitem import DrawingCurveItem
from ..items.drawingellipseitem import DrawingEllipseItem
from ..items.drawinglineitem import DrawingLineItem
from ..items.drawingpathitem import DrawingPathItem
from ..items.drawingpolygonitem import DrawingPolygonItem
from ..items.drawingpolylineitem import DrawingPolylineItem
from ..items.drawingrectitem import DrawingRectItem
from ..items.drawingtextellipseitem import DrawingTextEllipseItem
from ..items.drawingtextitem import DrawingTextItem
from ..items.drawingtextrectitem import DrawingTextRectItem


class SvgWriter(DrawingXmlInterface):
    def __init__(self, page: DrawingPageWidget, scale: float) -> None:
        super().__init__()

        self._page: DrawingPageWidget = page
        self._scale: float = scale

    # ==================================================================================================================

    def write(self, path: str) -> None:
        svgElement = ElementTree.Element('svg')

        rect = self._page.sceneRect()
        self.writeInt(svgElement, 'width', round(rect.width() * self._scale), writeIfDefault=True)
        self.writeInt(svgElement, 'height', round(rect.height() * self._scale), writeIfDefault=True)
        self.writeStr(svgElement, 'viewBox', f'{rect.left()} {rect.top()} {rect.width()} {rect.height()}')

        backgroundColor = QColor(self._page.backgroundBrush().color())
        self.writeStr(svgElement, 'style', f'background-color:{backgroundColor.name(QColor.NameFormat.HexRgb)}')

        self.writeStr(svgElement, 'xmlns', 'http://www.w3.org/2000/svg')

        self._writeItems(svgElement, self._page.items())

        ElementTree.indent(svgElement, space='  ')
        with open(path, 'w', encoding='utf-8') as file:
            file.write(ElementTree.tostring(svgElement, encoding='unicode', xml_declaration=True))
            file.write('\n')

    # ==================================================================================================================

    def _writeItems(self, element: ElementTree.Element, items: list[DrawingItem]) -> None:
        for item in items:
            if (isinstance(item, DrawingLineItem)):
                self._writeLineItem(element, item)
            elif (isinstance(item, DrawingCurveItem)):
                self._writeCurveItem(element, item)
            elif (isinstance(item, DrawingPolylineItem)):
                self._writePolylineItem(element, item)
            elif (isinstance(item, DrawingTextRectItem)):
                self._writeTextRectItem(element, item)
            elif (isinstance(item, DrawingRectItem)):
                self._writeRectItem(element, item)
            elif (isinstance(item, DrawingTextEllipseItem)):
                self._writeTextEllipseItem(element, item)
            elif (isinstance(item, DrawingEllipseItem)):
                self._writeEllipseItem(element, item)
            elif (isinstance(item, DrawingPolygonItem)):
                self._writePolygonItem(element, item)
            elif (isinstance(item, DrawingTextItem)):
                self._writeTextItem(element, item)
            elif (isinstance(item, DrawingPathItem)):
                self._writePathItem(element, item)
            elif (isinstance(item, DrawingItemGroup)):
                self._writeGroupItem(element, item)

    def _writeLineItem(self, element: ElementTree.Element, item: DrawingLineItem) -> None:
        if (item.startArrow().style() != DrawingArrow.Style.NoStyle or
                item.endArrow().style() != DrawingArrow.Style.NoStyle):
            groupElement = ElementTree.SubElement(element, 'g')
            lineElement = ElementTree.SubElement(groupElement, 'line')
        else:
            lineElement = ElementTree.SubElement(element, 'line')

        # Write line
        p1 = item.mapToScene(item.line().p1())
        p2 = item.mapToScene(item.line().p2())
        self.writeFloat(lineElement, 'x1', p1.x(), writeIfDefault=True)
        self.writeFloat(lineElement, 'y1', p1.y(), writeIfDefault=True)
        self.writeFloat(lineElement, 'x2', p2.x(), writeIfDefault=True)
        self.writeFloat(lineElement, 'y2', p2.y(), writeIfDefault=True)

        self._writePenToSvg(lineElement, item.pen())

        # Write arrows
        line = QLineF(p1, p2)
        lineLength = line.length()
        startArrowAngle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x()) * 180 / math.pi
        endArrowAngle = 180 + startArrowAngle
        if (lineLength >= item.startArrow().size()):
            self._writeArrowToSvg(groupElement, item.startArrow(), item.pen(), p1, startArrowAngle)
        if (lineLength >= item.endArrow().size()):
            self._writeArrowToSvg(groupElement, item.endArrow(), item.pen(), p2, endArrowAngle)

    def _writeCurveItem(self, element: ElementTree.Element, item: DrawingCurveItem) -> None:
        pass

    def _writePolylineItem(self, element: ElementTree.Element, item: DrawingPolylineItem) -> None:
        pass

    def _writeRectItem(self, element: ElementTree.Element, item: DrawingRectItem) -> None:
        rectElement = ElementTree.SubElement(element, 'rect')

        rect = item.mapRectToScene(item.rect())
        self.writeFloat(rectElement, 'x', rect.left(), writeIfDefault=True)
        self.writeFloat(rectElement, 'y', rect.top(), writeIfDefault=True)
        self.writeFloat(rectElement, 'width', rect.width(), writeIfDefault=True)
        self.writeFloat(rectElement, 'height', rect.height(), writeIfDefault=True)

        self.writeFloat(rectElement, 'rx', item.cornerRadius())
        self.writeFloat(rectElement, 'ry', item.cornerRadius())

        self._writeBrushToSvg(rectElement, item.brush())
        self._writePenToSvg(rectElement, item.pen())

    def _writeEllipseItem(self, element: ElementTree.Element, item: DrawingEllipseItem) -> None:
        ellipseElement = ElementTree.SubElement(element, 'ellipse')

        ellipse = item.mapRectToScene(item.ellipse())
        center = ellipse.center()
        self.writeFloat(ellipseElement, 'cx', center.x(), writeIfDefault=True)
        self.writeFloat(ellipseElement, 'cy', center.y(), writeIfDefault=True)
        self.writeFloat(ellipseElement, 'rx', ellipse.width() / 2, writeIfDefault=True)
        self.writeFloat(ellipseElement, 'ry', ellipse.height() / 2, writeIfDefault=True)

        self._writeBrushToSvg(ellipseElement, item.brush())
        self._writePenToSvg(ellipseElement, item.pen())

    def _writePolygonItem(self, element: ElementTree.Element, item: DrawingPolygonItem) -> None:
        polygonElement = ElementTree.SubElement(element, 'polygon')

        self.writePoints(polygonElement, 'points', item.mapPolygonToScene(item.polygon()))

        self._writeBrushToSvg(polygonElement, item.brush())
        self._writePenToSvg(polygonElement, item.pen())

    def _writeTextItem(self, element: ElementTree.Element, item: DrawingTextItem) -> None:
        pass

    def _writeTextRectItem(self, element: ElementTree.Element, item: DrawingTextRectItem) -> None:
        pass

    def _writeTextEllipseItem(self, element: ElementTree.Element, item: DrawingTextEllipseItem) -> None:
        pass

    def _writePathItem(self, element: ElementTree.Element, item: DrawingPathItem) -> None:
        pass

    def _writeGroupItem(self, element: ElementTree.Element, item: DrawingItemGroup) -> None:
        pass

    # ==================================================================================================================

    def _writePenToSvg(self, element: ElementTree.Element, pen: QPen) -> None:
        alpha = pen.brush().color().alpha()
        if (alpha != 0 and pen.style() != Qt.PenStyle.NoPen):
            color = QColor(pen.brush().color())
            color.setAlpha(255)
            self.writeColor(element, 'stroke', color, writeIfDefault=True)
            if (alpha != 255):
                self.writeStr(element, 'stroke-opacity', f'{alpha / 255 * 100:.1f}%')

            self.writeFloat(element, 'stroke-width', pen.widthF())

            dashLength = 4 * pen.widthF()
            dotLength = pen.widthF()
            spaceLength = 2 * pen.widthF()
            match (pen.style()):
                case Qt.PenStyle.DashLine:
                    self.writeStr(element, 'stroke-dasharray', f'{dashLength} {spaceLength}')
                case Qt.PenStyle.DotLine:
                    self.writeStr(element, 'stroke-dasharray', f'{dotLength} {spaceLength}')
                case Qt.PenStyle.DashDotLine:
                    self.writeStr(element, 'stroke-dasharray', f'{dashLength} {spaceLength} {dotLength} {spaceLength}')
                case Qt.PenStyle.DashDotDotLine:
                    self.writeStr(element, 'stroke-dasharray', f'{dashLength} {spaceLength} {dotLength} {spaceLength} '
                                                               f'{dotLength} {spaceLength}')

            match (pen.capStyle()):
                case Qt.PenCapStyle.SquareCap:
                    self.writeStr(element, 'stroke-linecap', 'square')
                case Qt.PenCapStyle.RoundCap:
                    self.writeStr(element, 'stroke-linecap', 'round')

            match (pen.joinStyle()):
                case Qt.PenJoinStyle.BevelJoin:
                    self.writeStr(element, 'stroke-linejoin', 'bevel')
                case Qt.PenJoinStyle.RoundJoin:
                    self.writeStr(element, 'stroke-linejoin', 'round')
        else:
            self.writeStr(element, 'stroke', 'none')

    def _writeBrushToSvg(self, element: ElementTree.Element, brush: QBrush) -> None:
        alpha = brush.color().alpha()
        if (alpha != 0):
            color = QColor(brush.color())
            color.setAlpha(255)
            self.writeColor(element, 'fill', color, writeIfDefault=True)
            if (alpha != 255):
                self.writeStr(element, 'fill-opacity', f'{alpha / 255 * 100:.1f}%')
        else:
            self.writeStr(element, 'fill', 'none')

    def _writeArrowToSvg(self, element: ElementTree.Element, arrow: DrawingArrow, pen: QPen, position: QPointF,
                         angle: float) -> None:
        originalPenStyle = pen.style()
        pen.setStyle(Qt.PenStyle.SolidLine)

        if (arrow.style() in (DrawingArrow.Style.Normal, DrawingArrow.Style.Triangle, DrawingArrow.Style.TriangleFilled,
                              DrawingArrow.Style.Concave, DrawingArrow.Style.ConcaveFilled)):
            pathElement = ElementTree.SubElement(element, 'path')

            path = QPainterPath(arrow._path)

            self.writeStr(pathElement, 'transform', f'translate({position.x()},{position.y()}) rotate({angle})')

            self.writePath(pathElement, 'd', path)

            if (arrow.style() in (DrawingArrow.Style.TriangleFilled, DrawingArrow.Style.ConcaveFilled)):
                self._writeBrushToSvg(pathElement, pen.brush())
            elif (arrow.style() in (DrawingArrow.Style.Triangle, DrawingArrow.Style.Concave)):
                self._writeBrushToSvg(pathElement, self._page.backgroundBrush())
            else:
                self._writeBrushToSvg(pathElement, QBrush(Qt.GlobalColor.transparent))

            self._writePenToSvg(pathElement, pen)

        elif (arrow.style() in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
            ellipseElement = ElementTree.SubElement(element, 'ellipse')

            self.writeFloat(ellipseElement, 'cx', position.x(), writeIfDefault=True)
            self.writeFloat(ellipseElement, 'cy', position.y(), writeIfDefault=True)
            self.writeFloat(ellipseElement, 'rx', arrow.size() / 2, writeIfDefault=True)
            self.writeFloat(ellipseElement, 'ry', arrow.size() / 2, writeIfDefault=True)

            if (arrow.style() == DrawingArrow.Style.CircleFilled):
                self._writeBrushToSvg(ellipseElement, pen.brush())
            else:
                self._writeBrushToSvg(ellipseElement, self._page.backgroundBrush())

            self._writePenToSvg(ellipseElement, pen)

        pen.setStyle(originalPenStyle)
