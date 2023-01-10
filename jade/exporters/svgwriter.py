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
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPolygonF
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawinggroupitem import DrawingGroupItem
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingpagewidget import DrawingPageWidget
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


class SvgWriter:
    def __init__(self, page: DrawingPageWidget, scale: float) -> None:
        super().__init__()

        self._page: DrawingPageWidget = page
        self._scale: float = scale

    # ==================================================================================================================

    def write(self, path: str) -> None:
        svgElement = ElementTree.Element('svg')

        rect = self._page.pageRect()
        svgElement.set('width', f'{round(rect.width() * self._scale)}')
        svgElement.set('height', f'{round(rect.height() * self._scale)}')
        svgElement.set('viewBox', f'{rect.left()} {rect.top()} {rect.width()} {rect.height()}')

        backgroundColor = QColor(self._page.backgroundBrush().color())
        svgElement.set('style', f'background-color:{backgroundColor.name(QColor.NameFormat.HexRgb)}')

        svgElement.set('xmlns', 'http://www.w3.org/2000/svg')

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
            elif (isinstance(item, DrawingGroupItem)):
                self._writeArrows(element, item.items())

    def _writeArrow(self, element: ElementTree.Element, arrow: DrawingArrow, pen: QPen) -> None:
        if (arrow.style() != DrawingArrow.Style.NoStyle):
            markerName = self._arrowMarkerName(arrow, pen)
            markerElement = element.find(f'marker[@id="{markerName}"]')
            if (markerElement is None):
                markerElement = ElementTree.SubElement(element, 'marker')
                markerElement.set('id', markerName)

                originalPenStyle = pen.style()
                pen.setStyle(Qt.PenStyle.SolidLine)

                if (arrow.style() in (DrawingArrow.Style.Normal,
                                      DrawingArrow.Style.Triangle, DrawingArrow.Style.TriangleFilled,
                                      DrawingArrow.Style.Concave, DrawingArrow.Style.ConcaveFilled)):
                    path = arrow.path()
                    rect = path.boundingRect().normalized()
                    rect.adjust(-pen.widthF(), -pen.widthF(), pen.widthF(), pen.widthF())

                    markerElement.set('viewBox', f'{rect.left()} {rect.top()} {rect.width()} {rect.height()}')
                    markerElement.set('markerWidth', f'{rect.width()}')
                    markerElement.set('markerHeight', f'{rect.height()}')
                    markerElement.set('orient', 'auto-start-reverse')

                    pathElement = ElementTree.SubElement(markerElement, 'path')

                    pathElement.set('d', self._pathToString(path))

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

                    markerElement.set('viewBox', f'{rect.left()} {rect.top()} {rect.width()} {rect.height()}')
                    markerElement.set('markerWidth', f'{rect.width()}')
                    markerElement.set('markerHeight', f'{rect.height()}')

                    circleElement = ElementTree.SubElement(markerElement, 'circle')
                    circleElement.set('r', f'{radius}')

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
            elif (isinstance(item, DrawingGroupItem)):
                self._writeGroupItem(element, item)

    def _writeLineItem(self, element: ElementTree.Element, item: DrawingLineItem) -> None:
        lineElement = ElementTree.SubElement(element, 'line')

        # Write line
        p1 = item.mapToScene(item.line().p1())
        p2 = item.mapToScene(item.line().p2())
        lineElement.set('x1', f'{p1.x()}')
        lineElement.set('y1', f'{p1.y()}')
        lineElement.set('x2', f'{p2.x()}')
        lineElement.set('y2', f'{p2.y()}')

        self._writePenAndBrush(lineElement, QBrush(Qt.GlobalColor.transparent), item.pen())

        # Write arrows
        lineLength = QLineF(p1, p2).length()
        if (item.startArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.startArrow().size()):
            lineElement.set('marker-start', f'url(#{self._arrowMarkerName(item.startArrow(), item.pen())})')
        if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.endArrow().size()):
            lineElement.set('marker-end', f'url(#{self._arrowMarkerName(item.endArrow(), item.pen())})')

    def _writeCurveItem(self, element: ElementTree.Element, item: DrawingCurveItem) -> None:
        curve = item.mapPolygonToScene(item.curve())
        if (curve.size() == 4):
            pathElement = ElementTree.SubElement(element, 'path')

            # Write curve
            p1 = curve.at(0)
            cp1 = curve.at(1)
            cp2 = curve.at(2)
            p2 = curve.at(3)
            pathElement.set('d', f'M {p1.x()},{p1.y()} C {cp1.x()},{cp1.y()} {cp2.x()},{cp2.y()} {p2.x()},{p2.y()}')

            self._writePenAndBrush(pathElement, QBrush(Qt.GlobalColor.transparent), item.pen())

            # Write arrows
            lineLength = QLineF(curve.at(0), curve.at(curve.size() - 1)).length()
            if (item.startArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.startArrow().size()):
                pathElement.set('marker-start', f'url(#{self._arrowMarkerName(item.startArrow(), item.pen())})')     # noqa
            if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lineLength >= item.endArrow().size()):
                pathElement.set('marker-end', f'url(#{self._arrowMarkerName(item.endArrow(), item.pen())})')         # noqa

    def _writePolylineItem(self, element: ElementTree.Element, item: DrawingPolylineItem) -> None:
        polylineElement = ElementTree.SubElement(element, 'polyline')

        # Write polyline
        polyline = item.mapPolygonToScene(item.polyline())
        polylineElement.set('points', self._polygonToString(polyline))

        self._writePenAndBrush(polylineElement, QBrush(Qt.GlobalColor.transparent), item.pen())

        # Write arrows
        if (polyline.size() >= 2):
            firstLength = QLineF(polyline.at(0), polyline.at(1)).length()
            lastLength = QLineF(polyline.at(polyline.size() - 1), polyline.at(polyline.size() - 2)).length()
            if (item.startArrow().style() != DrawingArrow.Style.NoStyle and firstLength >= item.startArrow().size()):
                polylineElement.set('marker-start', f'url(#{self._arrowMarkerName(item.startArrow(), item.pen())})')     # noqa
            if (item.endArrow().style() != DrawingArrow.Style.NoStyle and lastLength >= item.endArrow().size()):
                polylineElement.set('marker-end', f'url(#{self._arrowMarkerName(item.endArrow(), item.pen())})')         # noqa

    def _writeRectItem(self, element: ElementTree.Element, item: DrawingRectItem) -> None:
        rectElement = ElementTree.SubElement(element, 'rect')

        rect = item.mapRectToScene(item.rect())
        rectElement.set('x', f'{rect.left()}')
        rectElement.set('y', f'{rect.top()}')
        rectElement.set('width', f'{rect.width()}')
        rectElement.set('height', f'{rect.height()}')

        if (item.cornerRadius() != 0):
            rectElement.set('rx', f'{item.cornerRadius()}')
            rectElement.set('ry', f'{item.cornerRadius()}')

        self._writePenAndBrush(rectElement, item.brush(), item.pen())

    def _writeEllipseItem(self, element: ElementTree.Element, item: DrawingEllipseItem) -> None:
        ellipseElement = ElementTree.SubElement(element, 'ellipse')

        ellipse = item.mapRectToScene(item.ellipse())
        center = ellipse.center()
        ellipseElement.set('cx', f'{center.x()}')
        ellipseElement.set('cy', f'{center.y()}')
        ellipseElement.set('rx', f'{ellipse.width() / 2}')
        ellipseElement.set('ry', f'{ellipse.height() / 2}')

        self._writePenAndBrush(ellipseElement, item.brush(), item.pen())

    def _writePolygonItem(self, element: ElementTree.Element, item: DrawingPolygonItem) -> None:
        polygonElement = ElementTree.SubElement(element, 'polygon')

        polygonElement.set('points', self._polygonToString(item.mapPolygonToScene(item.polygon())))

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
        rectElement.set('x', f'{rect.left()}')
        rectElement.set('y', f'{rect.top()}')
        rectElement.set('width', f'{rect.width()}')
        rectElement.set('height', f'{rect.height()}')

        if (item.cornerRadius() != 0):
            rectElement.set('rx', f'{item.cornerRadius()}')
            rectElement.set('ry', f'{item.cornerRadius()}')
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
        ellipseElement.set('cx', f'{center.x()}')
        ellipseElement.set('cy', f'{center.y()}')
        ellipseElement.set('rx', f'{ellipse.width() / 2}')
        ellipseElement.set('ry', f'{ellipse.height() / 2}')

        self._writePenAndBrush(ellipseElement, item.brush(), item.pen())

        # Text
        textElement = ElementTree.SubElement(groupElement, 'text')

        self._writePenAndBrush(textElement, item.textBrush(), QPen(Qt.PenStyle.NoPen))
        self._writeText(textElement, item.caption(), item.font(), Qt.AlignmentFlag.AlignCenter)

    def _writePathItem(self, element: ElementTree.Element, item: DrawingPathItem) -> None:
        pathElement = ElementTree.SubElement(element, 'path')

        pathElement.set('d', self._pathToString(item.mapPathToScene(item.transformedPath())))

        self._writePenAndBrush(pathElement, QBrush(Qt.GlobalColor.transparent), item.pen())

    def _writeGroupItem(self, element: ElementTree.Element, item: DrawingGroupItem) -> None:
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

        element.set('transform', transformStr)

    def _writePenAndBrush(self, element: ElementTree.Element, brush: QBrush, pen: QPen) -> None:
        # Brush
        alpha = brush.color().alpha()
        if (alpha != 0):
            color = QColor(brush.color())
            color.setAlpha(255)
            element.set('fill', color.name(QColor.NameFormat.HexRgb))
            if (alpha != 255):
                element.set('fill-opacity', f'{alpha / 255 * 100:.1f}%')
        else:
            element.set('fill', 'none')

        # Pen
        alpha = pen.brush().color().alpha()
        if (alpha != 0 and pen.style() != Qt.PenStyle.NoPen):
            color = QColor(pen.brush().color())
            color.setAlpha(255)
            element.set('stroke', color.name(QColor.NameFormat.HexRgb))
            if (alpha != 255):
                element.set('stroke-opacity', f'{alpha / 255 * 100:.1f}%')

            element.set('stroke-width', f'{pen.widthF()}')

            dashLength = 4 * pen.widthF()
            dotLength = pen.widthF()
            spaceLength = 2 * pen.widthF()
            match (pen.style()):
                case Qt.PenStyle.DashLine:
                    element.set('stroke-dasharray', f'{dashLength} {spaceLength}')
                case Qt.PenStyle.DotLine:
                    element.set('stroke-dasharray', f'{dotLength} {spaceLength}')
                case Qt.PenStyle.DashDotLine:
                    element.set('stroke-dasharray', f'{dashLength} {spaceLength} {dotLength} {spaceLength}')
                case Qt.PenStyle.DashDotDotLine:
                    element.set('stroke-dasharray', f'{dashLength} {spaceLength} {dotLength} {spaceLength} '
                                                    f'{dotLength} {spaceLength}')

            match (pen.capStyle()):
                case Qt.PenCapStyle.SquareCap:
                    element.set('stroke-linecap', 'square')
                case Qt.PenCapStyle.RoundCap:
                    element.set('stroke-linecap', 'round')

            match (pen.joinStyle()):
                case Qt.PenJoinStyle.BevelJoin:
                    element.set('stroke-linejoin', 'bevel')
                case Qt.PenJoinStyle.RoundJoin:
                    element.set('stroke-linejoin', 'round')
        else:
            element.set('stroke', 'none')

    def _writeText(self, element: ElementTree.Element, text: str, font: QFont, alignment: Qt.AlignmentFlag) -> None:
        # Font
        element.set('font-family', font.family())
        element.set('font-size', f'{font.pointSizeF()}')

        if (font.bold()):
            element.set('font-weight', 'bold')
        if (font.italic()):
            element.set('font-style', 'italic')
        if (font.underline()):
            element.set('text-decoration', 'underline')
        if (font.strikeOut()):
            element.set('text-decoration', 'line-through')

        # Horizontal alignment
        if (alignment & Qt.AlignmentFlag.AlignHCenter):
            element.set('text-anchor', 'middle')
        elif (alignment & Qt.AlignmentFlag.AlignRight):
            element.set('text-anchor', 'end')

        # Vertical alignment
        element.set('dominant-baseline', 'central')

        if (alignment & Qt.AlignmentFlag.AlignTop):
            element.set('y', f'{font.pointSizeF() * 3 / 4}')
        elif (alignment & Qt.AlignmentFlag.AlignBottom):
            element.set('y', f'{-font.pointSizeF() * 3 / 4}')

        # Text
        lines = text.split('\n')
        if (len(lines) > 1):
            for index, line in enumerate(lines):
                tspanElement = ElementTree.SubElement(element, 'tspan')
                tspanElement.set('x', '0')
                if (index > 0):
                    tspanElement.set('dy', '1.0em')
                tspanElement.text = line
        else:
            element.text = str(text)

    # ==================================================================================================================

    def _polygonToString(self, polygon: QPolygonF) -> str:
        polygonStr = ''
        for index in range(polygon.size()):
            point = polygon.at(index)
            polygonStr = polygonStr + f'{point.x()},{point.y()} '
        return polygonStr.strip()

    def _pathToString(self, path: QPainterPath) -> str:
        pathStr = ''
        for index in range(path.elementCount()):
            pathElement = path.elementAt(index)
            match (pathElement.type):                                           # type: ignore
                case QPainterPath.ElementType.MoveToElement:
                    pathStr = f'{pathStr} M {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.LineToElement:
                    pathStr = f'{pathStr} L {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.CurveToElement:
                    pathStr = f'{pathStr} C {pathElement.x} {pathElement.y}'    # type: ignore
                case QPainterPath.ElementType.CurveToDataElement:
                    pathStr = f'{pathStr} {pathElement.x} {pathElement.y}'      # type: ignore
        return pathStr.strip()
