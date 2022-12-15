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

from xml.etree import ElementTree
from PySide6.QtCore import Qt, QLineF, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPen
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

        defElement = ElementTree.SubElement(svgElement, 'defs')
        self._writeArrows(defElement, self._page.items())

        self._writeItems(svgElement, self._page.items())

        ElementTree.indent(svgElement, space='  ')
        with open(path, 'w', encoding='utf-8') as file:
            file.write(ElementTree.tostring(svgElement, encoding='unicode', xml_declaration=True))
            file.write('\n')

    # ==================================================================================================================

    def _writeArrows(self, element: ElementTree.Element, items: list[DrawingItem]) -> None:
        for item in items:
            if (isinstance(item, DrawingLineItem)):
                self._writeArrow(element, item.startArrow(), item.pen())
                self._writeArrow(element, item.endArrow(), item.pen())
            elif (isinstance(item, DrawingCurveItem)):
                self._writeArrow(element, item.startArrow(), item.pen())
                self._writeArrow(element, item.endArrow(), item.pen())
            elif (isinstance(item, DrawingPolylineItem)):
                self._writeArrow(element, item.startArrow(), item.pen())
                self._writeArrow(element, item.endArrow(), item.pen())
            elif (isinstance(item, DrawingItemGroup)):
                self._writeArrows(element, item.items())

    def _writeArrow(self, element: ElementTree.Element, arrow: DrawingArrow, pen: QPen) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            markerName = self._arrowMarkerName(arrow, pen)
            markerElement = element.find(f'marker[@id="{markerName}"]')
            if (markerElement is None):
                markerElement = ElementTree.SubElement(element, 'marker')
                self.writeStr(markerElement, 'id', markerName)

                originalPenStyle = pen.style()
                pen.setStyle(Qt.PenStyle.SolidLine)

                if (arrow.style() in (DrawingArrow.Style.Normal,
                                      DrawingArrow.Style.Triangle, DrawingArrow.Style.TriangleFilled,
                                      DrawingArrow.Style.Concave, DrawingArrow.Style.ConcaveFilled)):
                    path = arrow.path()
                    rect = path.boundingRect().normalized()
                    rect.adjust(-pen.widthF(), -pen.widthF(), pen.widthF(), pen.widthF())

                    self.writeStr(markerElement, 'viewBox',
                                  f'{rect.left()} {rect.top()} {rect.width()} {rect.height()}')
                    self.writeFloat(markerElement, 'markerWidth', rect.width())
                    self.writeFloat(markerElement, 'markerHeight', rect.height())
                    self.writeStr(markerElement, 'orient', 'auto-start-reverse')

                    pathElement = ElementTree.SubElement(markerElement, 'path')

                    self.writePath(pathElement, 'd', path)

                    if (arrow.style() in (DrawingArrow.Style.TriangleFilled, DrawingArrow.Style.ConcaveFilled)):
                        brush = pen.brush()
                    elif (arrow.style() in (DrawingArrow.Style.Triangle, DrawingArrow.Style.Concave)):
                        brush = self._page.backgroundBrush()
                    else:
                        brush = QBrush(Qt.GlobalColor.transparent)

                    self._writePenAndBrush(pathElement, brush, pen)

                elif (arrow.style() in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
                    radius = arrow.size() / 2
                    rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
                    rect.adjust(-pen.widthF(), -pen.widthF(), pen.widthF(), pen.widthF())

                    self.writeStr(markerElement, 'viewBox',
                                  f'{rect.left()} {rect.top()} {rect.width()} {rect.height()}')
                    self.writeFloat(markerElement, 'markerWidth', rect.width())
                    self.writeFloat(markerElement, 'markerHeight', rect.height())

                    circleElement = ElementTree.SubElement(markerElement, 'circle')
                    self.writeFloat(circleElement, 'r', radius, writeIfDefault=True)

                    if (arrow.style() == DrawingArrow.Style.CircleFilled):
                        brush = pen.brush()
                    else:
                        brush = self._page.backgroundBrush()

                    self._writePenAndBrush(circleElement, brush, pen)

                pen.setStyle(originalPenStyle)

    def _arrowMarkerName(self, arrow: DrawingArrow, pen: QPen) -> str:
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

        alpha = pen.brush().color().alpha()
        color = QColor(pen.brush().color())
        color.setAlpha(255)

        return (f'{styleStr}_{arrow.size()}_'
                f'{color.name(QColor.NameFormat.HexRgb)}_{alpha / 255 * 100:.1f}_{pen.widthF()}')

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
        lineElement = ElementTree.SubElement(element, 'line')

        # Write line
        p1 = item.mapToScene(item.line().p1())
        p2 = item.mapToScene(item.line().p2())
        self.writeFloat(lineElement, 'x1', p1.x(), writeIfDefault=True)
        self.writeFloat(lineElement, 'y1', p1.y(), writeIfDefault=True)
        self.writeFloat(lineElement, 'x2', p2.x(), writeIfDefault=True)
        self.writeFloat(lineElement, 'y2', p2.y(), writeIfDefault=True)

        self._writePenAndBrush(lineElement, QBrush(Qt.GlobalColor.transparent), item.pen())

        # Write arrows
        lineLength = QLineF(p1, p2).length()
        if (item.startArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.startArrow().size()):
            self.writeStr(lineElement, 'marker-start', f'url(#{self._arrowMarkerName(item.startArrow(), item.pen())})')
        if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.endArrow().size()):
            self.writeStr(lineElement, 'marker-end', f'url(#{self._arrowMarkerName(item.endArrow(), item.pen())})')

    def _writeCurveItem(self, element: ElementTree.Element, item: DrawingCurveItem) -> None:
        curve = item.mapPolygonToScene(item.curve())
        if (curve.size() == 4):
            pathElement = ElementTree.SubElement(element, 'path')

            # Write curve
            p1 = curve.at(0)
            cp1 = curve.at(1)
            cp2 = curve.at(2)
            p2 = curve.at(3)
            pathStr = f'M {p1.x()},{p1.y()} C {cp1.x()},{cp1.y()} {cp2.x()},{cp2.y()} {p2.x()},{p2.y()}'
            self.writeStr(pathElement, 'd', pathStr)

            self._writePenAndBrush(pathElement, QBrush(Qt.GlobalColor.transparent), item.pen())

            # Write arrows
            lineLength = QLineF(curve.at(0), curve.at(curve.size() - 1)).length()
            if (item.startArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.startArrow().size()):
                self.writeStr(pathElement, 'marker-start', f'url(#{self._arrowMarkerName(item.startArrow(), item.pen())})')     # noqa
            if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.endArrow().size()):
                self.writeStr(pathElement, 'marker-end', f'url(#{self._arrowMarkerName(item.endArrow(), item.pen())})')         # noqa

    def _writePolylineItem(self, element: ElementTree.Element, item: DrawingPolylineItem) -> None:
        polylineElement = ElementTree.SubElement(element, 'polyline')

        # Write polyline
        polyline = item.mapPolygonToScene(item.polyline())
        self.writePoints(polylineElement, 'points', polyline)

        self._writePenAndBrush(polylineElement, QBrush(Qt.GlobalColor.transparent), item.pen())

        # Write arrows
        if (polyline.size() >= 2):
            firstLength = QLineF(polyline.at(0), polyline.at(1)).length()
            lastLength = QLineF(polyline.at(polyline.size() - 1), polyline.at(polyline.size() - 2)).length()
            if (item.startArrow().style() != DrawingArrow.Style.NoStyle and firstLength >= item.startArrow().size()):
                self.writeStr(polylineElement, 'marker-start', f'url(#{self._arrowMarkerName(item.startArrow(), item.pen())})')     # noqa
            if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lastLength >= item.endArrow().size()):
                self.writeStr(polylineElement, 'marker-end', f'url(#{self._arrowMarkerName(item.endArrow(), item.pen())})')         # noqa

    def _writeRectItem(self, element: ElementTree.Element, item: DrawingRectItem) -> None:
        rectElement = ElementTree.SubElement(element, 'rect')

        rect = item.mapRectToScene(item.rect())
        self.writeFloat(rectElement, 'x', rect.left(), writeIfDefault=True)
        self.writeFloat(rectElement, 'y', rect.top(), writeIfDefault=True)
        self.writeFloat(rectElement, 'width', rect.width(), writeIfDefault=True)
        self.writeFloat(rectElement, 'height', rect.height(), writeIfDefault=True)

        self.writeFloat(rectElement, 'rx', item.cornerRadius())
        self.writeFloat(rectElement, 'ry', item.cornerRadius())

        self._writePenAndBrush(rectElement, item.brush(), item.pen())

    def _writeEllipseItem(self, element: ElementTree.Element, item: DrawingEllipseItem) -> None:
        ellipseElement = ElementTree.SubElement(element, 'ellipse')

        ellipse = item.mapRectToScene(item.ellipse())
        center = ellipse.center()
        self.writeFloat(ellipseElement, 'cx', center.x(), writeIfDefault=True)
        self.writeFloat(ellipseElement, 'cy', center.y(), writeIfDefault=True)
        self.writeFloat(ellipseElement, 'rx', ellipse.width() / 2, writeIfDefault=True)
        self.writeFloat(ellipseElement, 'ry', ellipse.height() / 2, writeIfDefault=True)

        self._writePenAndBrush(ellipseElement, item.brush(), item.pen())

    def _writePolygonItem(self, element: ElementTree.Element, item: DrawingPolygonItem) -> None:
        polygonElement = ElementTree.SubElement(element, 'polygon')

        self.writePoints(polygonElement, 'points', item.mapPolygonToScene(item.polygon()))

        self._writePenAndBrush(polygonElement, item.brush(), item.pen())

    def _writeTextItem(self, element: ElementTree.Element, item: DrawingTextItem) -> None:
        textElement = ElementTree.SubElement(element, 'text')

        self._writeTransform(textElement, item)
        self._writePenAndBrush(textElement, item.brush(), QPen(Qt.PenStyle.NoPen))
        self._writeText(textElement, item.caption(), item.font(), item.alignment())

    def _writeTextRectItem(self, element: ElementTree.Element, item: DrawingTextRectItem) -> None:
        groupElement = ElementTree.SubElement(element, 'g')

        self._writeTransform(groupElement, item)

        # Rect
        rectElement = ElementTree.SubElement(groupElement, 'rect')

        rect = item.rect().normalized()
        self.writeFloat(rectElement, 'x', rect.left(), writeIfDefault=True)
        self.writeFloat(rectElement, 'y', rect.top(), writeIfDefault=True)
        self.writeFloat(rectElement, 'width', rect.width(), writeIfDefault=True)
        self.writeFloat(rectElement, 'height', rect.height(), writeIfDefault=True)

        self.writeFloat(rectElement, 'rx', item.cornerRadius())
        self.writeFloat(rectElement, 'ry', item.cornerRadius())

        self._writePenAndBrush(rectElement, item.brush(), item.pen())

        # Text
        textElement = ElementTree.SubElement(groupElement, 'text')

        self._writePenAndBrush(textElement, item.textBrush(), QPen(Qt.PenStyle.NoPen))
        self._writeText(textElement, item.caption(), item.font(), Qt.AlignmentFlag.AlignCenter)

    def _writeTextEllipseItem(self, element: ElementTree.Element, item: DrawingTextEllipseItem) -> None:
        groupElement = ElementTree.SubElement(element, 'g')

        self._writeTransform(groupElement, item)

        # Ellipse
        ellipseElement = ElementTree.SubElement(groupElement, 'ellipse')

        ellipse = item.ellipse().normalized()
        center = ellipse.center()
        self.writeFloat(ellipseElement, 'cx', center.x(), writeIfDefault=True)
        self.writeFloat(ellipseElement, 'cy', center.y(), writeIfDefault=True)
        self.writeFloat(ellipseElement, 'rx', ellipse.width() / 2, writeIfDefault=True)
        self.writeFloat(ellipseElement, 'ry', ellipse.height() / 2, writeIfDefault=True)

        self._writePenAndBrush(ellipseElement, item.brush(), item.pen())

        # Text
        textElement = ElementTree.SubElement(groupElement, 'text')

        self._writePenAndBrush(textElement, item.textBrush(), QPen(Qt.PenStyle.NoPen))
        self._writeText(textElement, item.caption(), item.font(), Qt.AlignmentFlag.AlignCenter)

    def _writePathItem(self, element: ElementTree.Element, item: DrawingPathItem) -> None:
        pathElement = ElementTree.SubElement(element, 'path')

        self.writePath(pathElement, 'd', item.mapPathToScene(item.transformedPath()))

        self._writePenAndBrush(pathElement, QBrush(Qt.GlobalColor.transparent), item.pen())

    def _writeGroupItem(self, element: ElementTree.Element, item: DrawingItemGroup) -> None:
        groupElement = ElementTree.SubElement(element, 'g')
        self._writeTransform(groupElement, item)
        self._writeItems(groupElement, item.items())

    # ==================================================================================================================

    def _writeTransform(self, element: ElementTree.Element, item: DrawingItem) -> None:
        transformStr = f'translate({item.position().x()},{item.position().y()})'
        if (item.isFlipped()):
            transformStr = f'{transformStr} scale(-1,1)'
        if (item.rotation() != 0):
            transformStr = f'{transformStr} rotate({item.rotation() * 90})'

        self.writeStr(element, 'transform', transformStr)

    def _writePenAndBrush(self, element: ElementTree.Element, brush: QBrush, pen: QPen) -> None:
        # Brush
        alpha = brush.color().alpha()
        if (alpha != 0):
            color = QColor(brush.color())
            color.setAlpha(255)
            self.writeColor(element, 'fill', color, writeIfDefault=True)
            if (alpha != 255):
                self.writeStr(element, 'fill-opacity', f'{alpha / 255 * 100:.1f}%')
        else:
            self.writeStr(element, 'fill', 'none')

        # Pen
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

    def _writeText(self, element: ElementTree.Element, text: str, font: QFont, alignment: Qt.AlignmentFlag) -> None:
        # Font
        self.writeStr(element, 'font-family', font.family())
        self.writeFloat(element, 'font-size', font.pointSizeF(), writeIfDefault=True)

        if (font.bold()):
            self.writeStr(element, 'font-weight', 'bold')
        if (font.italic()):
            self.writeStr(element, 'font-style', 'italic')
        if (font.underline()):
            self.writeStr(element, 'text-decoration', 'underline')
        if (font.strikeOut()):
            self.writeStr(element, 'text-decoration', 'line-through')

        # Horizontal alignment
        if (alignment & Qt.AlignmentFlag.AlignHCenter):
            self.writeStr(element, 'text-anchor', 'middle')
        elif (alignment & Qt.AlignmentFlag.AlignRight):
            self.writeStr(element, 'text-anchor', 'end')

        # Vertical alignment
        self.writeStr(element, 'dominant-baseline', 'central')

        if (alignment & Qt.AlignmentFlag.AlignTop):
            self.writeFloat(element, 'y', font.pointSizeF() * 3 / 4)
        elif (alignment & Qt.AlignmentFlag.AlignBottom):
            self.writeFloat(element, 'y', -font.pointSizeF() * 3 / 4)

        # Text
        lines = text.split('\n')
        if (len(lines) > 1):
            for index, line in enumerate(lines):
                tspanElement = ElementTree.SubElement(element, 'tspan')
                self.writeStr(tspanElement, 'x', '0', writeIfDefault=True)
                if (index > 0):
                    self.writeStr(tspanElement, 'dy', '1.0em')
                tspanElement.text = line
        else:
            element.text = str(text)
