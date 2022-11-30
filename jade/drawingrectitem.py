# drawingrectitem.py
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
from .drawingitem import DrawingRectResizeItem


class DrawingRectItem(DrawingRectResizeItem):
    def __init__(self) -> None:
        super().__init__()

        self._cornerRadius: float = 0.0
        self._brush: QBrush = QBrush()

        self._cachedShape: QPainterPath = QPainterPath()

        self.setPlaceType(DrawingRectResizeItem.PlaceType.PlaceByMousePressAndRelease)

    # ==================================================================================================================

    def key(self) -> str:
        return 'rect'

    def clone(self) -> 'DrawingRectItem':
        clonedItem = DrawingRectItem()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setPen(QPen(self.pen()))
        clonedItem.setBrush(QBrush(self.brush()))
        clonedItem.setCornerRadius(self.cornerRadius())
        clonedItem.setRect(QRectF(self.rect()))
        return clonedItem

    # ==================================================================================================================

    def setCornerRadius(self, radius: float) -> None:
        self._cornerRadius = radius
        self._updateGeometry()

    def cornerRadius(self) -> float:
        return self._cornerRadius

    # ==================================================================================================================

    def setBrush(self, brush: QBrush) -> None:
        self._brush = brush
        self._updateGeometry()

    def brush(self) -> QBrush:
        return self._brush

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
        if (name == 'cornerRadius' and isinstance(value, float)):
            self.setCornerRadius(value)
        elif (name == 'pen' and isinstance(value, QPen)):
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
        if (name == 'cornerRadius'):
            return self.cornerRadius()
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
            painter.drawRoundedRect(self._rect.normalized(), self._cornerRadius, self._cornerRadius)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        super().writeToXml(element)

        # Rect and corner radius
        self.writeFloatAttribute(element, 'left', self._rect.left(), 0)
        self.writeFloatAttribute(element, 'top', self._rect.top(), 0)
        self.writeFloatAttribute(element, 'width', self._rect.width())
        self.writeFloatAttribute(element, 'height', self._rect.height())
        self.writeFloatAttribute(element, 'cornerRadius', self._cornerRadius, 0)

        # Pen and brush
        self.writePenToXml(element, 'pen', self._pen)
        self.writeBrushToXml(element, 'brush', self._brush)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        super().readFromXml(element)

        # Rect and corner radius
        self.setRect(QRectF(self.readFloatAttribute(element, 'left', 0),
                            self.readFloatAttribute(element, 'top', 0),
                            self.readFloatAttribute(element, 'width', 0),
                            self.readFloatAttribute(element, 'height', 0)))
        self.setCornerRadius(self.readFloatAttribute(element, 'cornerRadius', 0))

        # Pen and brush
        self.setPen(self.readPenFromXml(element, 'pen'))
        self.setBrush(self.readBrushFromXml(element, 'brush'))

    # ==================================================================================================================

    def _updateGeometry(self):
        # Update bounding rect
        super()._updateGeometry()

        # Update shape
        self._cachedShape.clear()
        if (self.isValid()):
            normalizedRect = self._rect.normalized()
            if (self._pen.style() != Qt.PenStyle.NoPen):
                drawPath = QPainterPath()
                drawPath.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)
                self._cachedShape = self.strokePath(drawPath, self._pen)
                if (self._brush.color().alpha() > 0):
                    self._cachedShape.addPath(drawPath)
            else:
                self._cachedShape.addRoundedRect(normalizedRect, self._cornerRadius, self._cornerRadius)
