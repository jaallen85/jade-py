# drawingitemgroup.py
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
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPainter, QPainterPath
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint


class DrawingItemGroup(DrawingItem):
    def __init__(self) -> None:
        super().__init__()

        self._items: list[DrawingItem] = []

        self._cachedBoundingRect: QRectF = QRectF()
        self._cachedShape: QPainterPath = QPainterPath()

        for _ in range(8):
            self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.NoType))

    def __del__(self) -> None:
        self.setItems([])

    # ==================================================================================================================

    def key(self) -> str:
        return 'group'

    def clone(self) -> 'DrawingItemGroup':
        clonedItem = DrawingItemGroup()
        clonedItem.copyBaseClassValues(self)
        clonedItem.setItems(DrawingItem.cloneItems(self.items()))
        return clonedItem

    # ==================================================================================================================

    def setItems(self, items: list[DrawingItem]) -> None:
        del self._items[:]
        self._items = items
        self._updateGeometry()

    def items(self) -> list[DrawingItem]:
        return self._items

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        return self._cachedBoundingRect

    def shape(self) -> QPainterPath:
        return self._cachedShape

    def isValid(self) -> bool:
        return (len(self._items) > 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        for item in self._items:
            painter.translate(item.position())
            painter.setTransform(item.transform(), True)
            item.paint(painter)
            painter.setTransform(item.transformInverse(), True)
            painter.translate(-item.position())

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)
        DrawingItem.writeItemsToXml(element, self._items)

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)
        self.setItems(DrawingItem.readItemsFromXml(element))

    # ==================================================================================================================

    def _updateGeometry(self):
        self._cachedBoundingRect = QRectF()
        self._cachedShape = QPainterPath()

        if (self.isValid()):
            # Update bounding rect
            for item in self._items:
                self._cachedBoundingRect = self._cachedBoundingRect.united(item.mapRectToScene(item.boundingRect()))

            # Update shape
            self._cachedShape.addRect(self._cachedBoundingRect)

            # Update points
            points = self.points()
            if (len(points) >= 8):
                center = self._cachedBoundingRect.center()
                points[0].setPosition(QPointF(self._cachedBoundingRect.left(), self._cachedBoundingRect.top()))
                points[1].setPosition(QPointF(center.x(), self._cachedBoundingRect.top()))
                points[2].setPosition(QPointF(self._cachedBoundingRect.right(), self._cachedBoundingRect.top()))
                points[3].setPosition(QPointF(self._cachedBoundingRect.right(), center.y()))
                points[4].setPosition(QPointF(self._cachedBoundingRect.right(), self._cachedBoundingRect.bottom()))
                points[5].setPosition(QPointF(center.x(), self._cachedBoundingRect.bottom()))
                points[6].setPosition(QPointF(self._cachedBoundingRect.left(), self._cachedBoundingRect.bottom()))
                points[7].setPosition(QPointF(self._cachedBoundingRect.left(), center.y()))
