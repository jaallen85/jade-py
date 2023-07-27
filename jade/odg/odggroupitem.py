# odggroupitem.py
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

from enum import IntEnum
from typing import Any
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgItemStyle
from .odgreader import OdgReader
from .odgwriter import OdgWriter


class OdgGroupItem(OdgItem):
    class PointIndex(IntEnum):
        TopLeft = 0
        TopMiddle = 1
        TopRight = 2
        MiddleRight = 3
        BottomRight = 4
        BottomMiddle = 5
        BottomLeft = 6
        MiddleLeft = 7

    # ==================================================================================================================

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._items: list[OdgItem] = []

        for _ in range(8):
            self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.NoType))

    def __copy__(self) -> 'OdgGroupItem':
        copiedItem = OdgGroupItem(self.name())
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
        copiedItem.style().copyFromStyle(self.style())
        copiedItem.setItems(OdgItem.copyItems(self.items()))
        return copiedItem

    def __del__(self) -> None:
        self.setItems([])
        super().__del__()

    # ==================================================================================================================

    def type(self) -> str:
        return 'group'

    def prettyType(self) -> str:
        return 'Group'

    def qualifiedType(self) -> str:
        return 'draw:g'

    # ==================================================================================================================

    def setItems(self, items: list[OdgItem]) -> None:
        del self._items[:]
        self._items = items
        self._updatePointPositions()

    def items(self) -> list[OdgItem]:
        return self._items

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        pass

    def property(self, name: str) -> Any:
        if (name == 'position'):
            return self.position()
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = QRectF()
        for item in self._items:
            rect = rect.united(item.mapRectToScene(item.boundingRect()))
        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()
        shape.addRect(self.boundingRect())
        return shape

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

    def scale(self, scale: float) -> None:
        super().scale(scale)
        for item in self._items:
            item.scale(scale)

    # ==================================================================================================================

    def writeStyles(self, writer: OdgWriter) -> None:
        for item in self._items:
            item.writeStyles(writer)

    def write(self, writer: OdgWriter) -> None:
        originalPosition = QPointF(self._position)
        originalRotation = self._rotation
        originalFlipped = self._flipped
        originalItemPosition = {}
        originalItemRotation = {}
        originalItemFlipped = {}
        for item in self._items:
            originalItemPosition[item] = item.position()
            originalItemRotation[item] = item.rotation()
            originalItemFlipped[item] = item.isFlipped()

        # Apply the group's position/transform to each item
        for item in self._items:
            item.setPosition(self.mapToScene(item.position()))
            item.setRotation(item.rotation() + self.rotation())
            if (self.isFlipped()):
                item.setFlipped(not item.isFlipped())
        # Clear group's position/transform
        self.setPosition(QPointF(0, 0))
        self.setRotation(0)
        self.setFlipped(False)

        # Write group to XML
        if (self._name != ''):
            writer.writeAttribute('draw:name', self._name)
        OdgItem.writeItems(writer, self._items)

        # Restore items' original position/transform
        for item in self._items:
            item.setPosition(originalItemPosition[item])
            item.setRotation(originalItemRotation[item])
            item.setFlipped(originalItemFlipped[item])
        self.setPosition(originalPosition)
        self.setRotation(originalRotation)
        self.setFlipped(originalFlipped)

    def read(self, reader: OdgReader, automaticItemStyles: list[OdgItemStyle]) -> None:
        super().read(reader, automaticItemStyles)
        self.setItems(OdgItem.readItems(reader, automaticItemStyles))

        # Put the group position equal to the position of the last item and adjust each item's position
        # accordingly
        self.setPosition(self._items[-1].position())
        for item in self._items:
            item.setPosition(self.mapFromScene(item.position()))
        self._updatePointPositions()

    # ==================================================================================================================

    def _updatePointPositions(self) -> None:
        # Set point positions to match self.boundingRect()
        if (len(self._points) >= 8):
            rect = self.boundingRect()
            center = rect.center()
            self._points[OdgGroupItem.PointIndex.TopLeft].setPosition(QPointF(rect.left(), rect.top()))
            self._points[OdgGroupItem.PointIndex.TopMiddle].setPosition(QPointF(center.x(), rect.top()))
            self._points[OdgGroupItem.PointIndex.TopRight].setPosition(QPointF(rect.right(), rect.top()))
            self._points[OdgGroupItem.PointIndex.MiddleRight].setPosition(QPointF(rect.right(), center.y()))
            self._points[OdgGroupItem.PointIndex.BottomRight].setPosition(QPointF(rect.right(), rect.bottom()))
            self._points[OdgGroupItem.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), rect.bottom()))
            self._points[OdgGroupItem.PointIndex.BottomLeft].setPosition(QPointF(rect.left(), rect.bottom()))
            self._points[OdgGroupItem.PointIndex.MiddleLeft].setPosition(QPointF(rect.left(), center.y()))
