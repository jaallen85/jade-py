# logicitems.py
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

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath
from ..items.drawingpathitem import DrawingPathItem


class LogicItems:
    @staticmethod
    def create() -> list[tuple[DrawingPathItem, str]]:
        items = []
        items.append((LogicItems.createAndGate(), 'icons:items/and_gate.png'))
        items.append((LogicItems.createOrGate(), 'icons:items/or_gate.png'))
        items.append((LogicItems.createXorGate(), 'icons:items/xor_gate.png'))
        return items

    # ======================================================================================================================

    @staticmethod
    def createAndGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.cubicTo(5.0, -2.0, 5.0, 2.0, -3.0, 2.0)
        path.closeSubpath()

        path.moveTo(-4.0, -1.0)
        path.lineTo(-3.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-3.0, 1.0)
        path.moveTo(4.0, 0.0)
        path.lineTo(3.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('AND Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -1.0))
        item.addConnectionPoint(QPointF(-4.0, 1.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ======================================================================================================================

    @staticmethod
    def createOrGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.cubicTo(5.0, -2.0, 5.0, 2.0, -3.0, 2.0)
        path.cubicTo(-1.4, 2.0, -1.4, -2.0, -3.0, -2.0)

        path.moveTo(-4.0, -1.0)
        path.lineTo(-2.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-2.0, 1.0)
        path.moveTo(4.0, 0.0)
        path.lineTo(3.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('OR Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -1.0))
        item.addConnectionPoint(QPointF(-4.0, 1.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ======================================================================================================================

    @staticmethod
    def createXorGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.cubicTo(5.0, -2.0, 5.0, 2.0, -3.0, 2.0)
        path.cubicTo(-1.4, 2.0, -1.4, -2.0, -3.0, -2.0)

        path.moveTo(-4.0, -2.0)
        path.cubicTo(-2.4, -2.0, -2.4, 2.0, -4.0, 2.0)

        path.moveTo(-4.0, -1.0)
        path.lineTo(-3.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-3.0, 1.0)
        path.moveTo(4.0, 0.0)
        path.lineTo(3.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('XOR Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -1.0))
        item.addConnectionPoint(QPointF(-4.0, 1.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item
