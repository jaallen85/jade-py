# drawingellipseitem.py
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

import typing
from xml.etree import ElementTree
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from .drawingitempoint import DrawingItemPoint
from .drawingrectresizeitem import DrawingRectResizeItem


class DrawingEllipseItem(DrawingRectResizeItem):
    def __init__(self) -> None:
        super().__init__()

        self._brush: QBrush = QBrush()

        self._cachedShape: QPainterPath = QPainterPath()

        self._points[DrawingEllipseItem.PointIndex.TopLeft.value].setType(DrawingItemPoint.Type.Control)
        self._points[DrawingEllipseItem.PointIndex.TopRight.value].setType(DrawingItemPoint.Type.Control)
        self._points[DrawingEllipseItem.PointIndex.BottomRight.value].setType(DrawingItemPoint.Type.Control)
        self._points[DrawingEllipseItem.PointIndex.BottomLeft.value].setType(DrawingItemPoint.Type.Control)

        self.setPlaceType(DrawingRectResizeItem.PlaceType.PlaceByMousePressAndRelease)

    # ==================================================================================================================

    def key(self) -> str:
        return 'ellipse'

    def clone(self) -> 'DrawingEllipseItem':
        clonedItem = DrawingEllipseItem()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setPen(QPen(self.pen()))
        clonedItem.setBrush(QBrush(self.brush()))
        clonedItem.setRect(self.rect())
        return clonedItem

    # ==================================================================================================================

    def setBrush(self, brush: QBrush) -> None:
        self._brush = brush
        self._updateGeometry()

    def brush(self) -> QBrush:
        return self._brush

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
        if (name == 'pen' and isinstance(value, QPen)):
            self.setPen(value)
        elif (name == 'penStyle' and isinstance(value, int)):
            pen = self.pen()
            pen.setStyle(Qt.PenStyle(value))
            self.setPen(pen)
        elif (name == 'penWidth' and isinstance(value, float)):
            pen = self.pen()
            pen.setWidthF(value)
            self.setPen(pen)
        elif (name == 'penColor' and isinstance(value, QColor)):
            pen = self.pen()
            pen.setBrush(QBrush(QColor(value)))
            self.setPen(pen)
        elif (name == 'brush' and isinstance(value, QBrush)):
            self.setBrush(value)
        elif (name == 'brushColor' and isinstance(value, QColor)):
            self.setBrush(QBrush(QColor(value)))

    def property(self, name: str) -> typing.Any:
        if (name == 'rect'):
            return self.mapRectToScene(self.rect())
        if (name == 'pen'):
            return self.pen()
        if (name == 'penStyle'):
            return self.pen().style().value
        if (name == 'penWidth'):
            return self.pen().widthF()
        if (name == 'penColor'):
            return self.pen().brush().color()
        if (name == 'brush'):
            return self.brush()
        if (name == 'brushColor'):
            return self.brush().color()
        return None

    # ==================================================================================================================

    def shape(self) -> QPainterPath:
        return self._cachedShape

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        if (self.isValid()):
            painter.setBrush(self._brush)
            painter.setPen(self._pen)
            painter.drawEllipse(self.rect().normalized())

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Rect
        rect = self.rect()
        self.writeFloatAttribute(element, 'left', rect.left(), 0)
        self.writeFloatAttribute(element, 'top', rect.top(), 0)
        self.writeFloatAttribute(element, 'width', rect.width())
        self.writeFloatAttribute(element, 'height', rect.height())

        # Pen and brush
        self.writePenToXml(element, 'pen', self._pen)
        self.writeBrushToXml(element, 'brush', self._brush)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        super().readFromXml(element)

        # Rect
        self.setRect(QRectF(self.readFloatAttribute(element, 'left', 0.0),
                            self.readFloatAttribute(element, 'top', 0.0),
                            self.readFloatAttribute(element, 'width', 0.0),
                            self.readFloatAttribute(element, 'height', 0.0)))

        # Pen and brush
        self.setPen(self.readPenFromXml(element, 'pen'))
        self.setBrush(self.readBrushFromXml(element, 'brush'))

    # ==================================================================================================================

    def _updateGeometry(self) -> None:
        # Update bounding rect
        super()._updateGeometry()

        self._cachedShape.clear()
        if (self.isValid()):
            # Update shape
            normalizedRect = self.rect().normalized()
            if (self._pen.style() != Qt.PenStyle.NoPen):
                drawPath = QPainterPath()
                drawPath.addEllipse(normalizedRect)
                self._cachedShape = self.strokePath(drawPath, self._pen)
                if (self._brush.color().alpha() > 0):
                    self._cachedShape.addPath(drawPath)
            else:
                self._cachedShape.addEllipse(normalizedRect)
