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
        items.append((LogicItems.createXnorGate(), 'icons:items/xnor_gate.png'))
        items.append((LogicItems.createNandGate(), 'icons:items/nand_gate.png'))
        items.append((LogicItems.createNorGate(), 'icons:items/nor_gate.png'))
        items.append((LogicItems.createMultiplexer(), 'icons:items/multiplexer.png'))
        items.append((LogicItems.createDemultiplexer(), 'icons:items/demultiplexer.png'))
        items.append((LogicItems.createBuffer(), 'icons:items/buffer.png'))
        items.append((LogicItems.createNotGate(), 'icons:items/not_gate.png'))
        items.append((LogicItems.createTristateBuffer1(), 'icons:items/tristate_buffer.png'))
        items.append((LogicItems.createTristateBuffer2(), 'icons:items/tristate_buffer2.png'))
        items.append((LogicItems.createFlipFlop1(), 'icons:items/flip_flop.png'))
        items.append((LogicItems.createFlipFlop2(), 'icons:items/flip_flop2.png'))
        return items

    # ==================================================================================================================

    @staticmethod
    def createAndGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.lineTo(0.0, -2.0)
        path.cubicTo(4.0, -2.0, 4.0, 2.0, 0.0, 2.0)
        path.lineTo(-3.0, 2.0)
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

    # ==================================================================================================================

    @staticmethod
    def createOrGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.lineTo(0.0, -2.0)
        path.cubicTo(4.0, -2.0, 4.0, 2.0, 0.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.cubicTo(-1.4, 1.4, -1.4, -1.4, -3.0, -2.0)

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

    # ==================================================================================================================

    @staticmethod
    def createXorGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.lineTo(0.0, -2.0)
        path.cubicTo(4.0, -2.0, 4.0, 2.0, 0.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.cubicTo(-1.4, 1.4, -1.4, -1.4, -3.0, -2.0)

        path.moveTo(-4.0, 2.0)
        path.cubicTo(-2.4, 1.4, -2.4, -1.4, -4.0, -2.0)

        path.moveTo(-4.0, -1.0)
        path.lineTo(-2.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-2.0, 1.0)
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

    # ==================================================================================================================

    @staticmethod
    def createXnorGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.lineTo(0.0, -2.0)
        path.cubicTo(4.0, -2.0, 4.0, 2.0, 0.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.cubicTo(-1.4, 1.4, -1.4, -1.4, -3.0, -2.0)

        path.moveTo(-4.0, 2.0)
        path.cubicTo(-2.4, 1.4, -2.4, -1.4, -4.0, -2.0)

        path.moveTo(-4.0, -1.0)
        path.lineTo(-2.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-2.0, 1.0)

        path.moveTo(3.5, -0.5)
        path.cubicTo(2.8, -0.5, 2.8, 0.5, 3.5, 0.5)
        path.moveTo(3.5, -0.5)
        path.cubicTo(4.2, -0.5, 4.2, 0.5, 3.5, 0.5)

        item = DrawingPathItem()
        item.setPathName('XNOR Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -1.0))
        item.addConnectionPoint(QPointF(-4.0, 1.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createNandGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.lineTo(0.0, -2.0)
        path.cubicTo(4.0, -2.0, 4.0, 2.0, 0.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.closeSubpath()

        path.moveTo(-4.0, -1.0)
        path.lineTo(-3.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-3.0, 1.0)

        path.moveTo(3.5, -0.5)
        path.cubicTo(2.8, -0.5, 2.8, 0.5, 3.5, 0.5)
        path.moveTo(3.5, -0.5)
        path.cubicTo(4.2, -0.5, 4.2, 0.5, 3.5, 0.5)

        item = DrawingPathItem()
        item.setPathName('NAND Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -1.0))
        item.addConnectionPoint(QPointF(-4.0, 1.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createNorGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(-3.0, -2.0)
        path.lineTo(0.0, -2.0)
        path.cubicTo(4.0, -2.0, 4.0, 2.0, 0.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.cubicTo(-1.4, 1.4, -1.4, -1.4, -3.0, -2.0)

        path.moveTo(-4.0, -1.0)
        path.lineTo(-2.0, -1.0)
        path.moveTo(-4.0, 1.0)
        path.lineTo(-2.0, 1.0)

        path.moveTo(3.5, -0.5)
        path.cubicTo(2.8, -0.5, 2.8, 0.5, 3.5, 0.5)
        path.moveTo(3.5, -0.5)
        path.cubicTo(4.2, -0.5, 4.2, 0.5, 3.5, 0.5)

        item = DrawingPathItem()
        item.setPathName('NOR Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -1.0))
        item.addConnectionPoint(QPointF(-4.0, 1.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createMultiplexer() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(-2.0, -4.0)
        path.lineTo(-2.0, 4.0)
        path.lineTo(2.0, 2.0)
        path.lineTo(2.0, -2.0)
        path.lineTo(-2.0, -4.0)

        path.moveTo(-4.0, -2.0)
        path.lineTo(-2.0, -2.0)
        path.moveTo(-4.0, 2.0)
        path.lineTo(-2.0, 2.0)
        path.moveTo(2.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Multiplexer')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -2.0))
        item.addConnectionPoint(QPointF(-4.0, 2.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        item.addConnectionPoint(QPointF(0.0, -3.0))
        item.addConnectionPoint(QPointF(0.0, 3.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createDemultiplexer() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(2.0, -4.0)
        path.lineTo(2.0, 4.0)
        path.lineTo(-2.0, 2.0)
        path.lineTo(-2.0, -2.0)
        path.lineTo(2.0, -4.0)

        path.moveTo(4.0, -2.0)
        path.lineTo(2.0, -2.0)
        path.moveTo(4.0, 2.0)
        path.lineTo(2.0, 2.0)
        path.moveTo(-2.0, 0.0)
        path.lineTo(-4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Demultiplexer')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(4.0, -2.0))
        item.addConnectionPoint(QPointF(4.0, 2.0))
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(0.0, -3.0))
        item.addConnectionPoint(QPointF(0.0, 3.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createBuffer() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(1.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Buffer')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createNotGate() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)

        path.moveTo(1.5, -0.5)
        path.cubicTo(0.8, -0.5, 0.8, 0.5, 1.5, 0.5)
        path.moveTo(1.5, -0.5)
        path.cubicTo(2.2, -0.5, 2.2, 0.5, 1.5, 0.5)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(2.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('NOT Gate')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createTristateBuffer1() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(1.0, 0.0)
        path.lineTo(4.0, 0.0)

        path.moveTo(0, -0.75)
        path.lineTo(0, -1.5)

        item = DrawingPathItem()
        item.setPathName('Tristate Buffer 1')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        item.addConnectionPoint(QPointF(0.0, -1.5))
        return item

    # ==================================================================================================================

    @staticmethod
    def createTristateBuffer2() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)

        path.moveTo(1.5, -0.5)
        path.cubicTo(0.8, -0.5, 0.8, 0.5, 1.5, 0.5)
        path.moveTo(1.5, -0.5)
        path.cubicTo(2.2, -0.5, 2.2, 0.5, 1.5, 0.5)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(2.0, 0.0)
        path.lineTo(4.0, 0.0)

        path.moveTo(0, -0.75)
        path.lineTo(0, -1.5)

        item = DrawingPathItem()
        item.setPathName('Tristate Buffer 2')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        item.addConnectionPoint(QPointF(0.0, -1.5))
        return item

    # ==================================================================================================================

    @staticmethod
    def createFlipFlop1() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(-3.0, -4.0)
        path.lineTo(-3.0, 4.0)
        path.lineTo(3.0, 4.0)
        path.lineTo(3.0, -4.0)
        path.lineTo(-3.0, -4.0)

        path.moveTo(-4.0, -2.0)
        path.lineTo(-3.0, -2.0)
        path.moveTo(-4.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.moveTo(4.0, -2.0)
        path.lineTo(3.0, -2.0)
        path.moveTo(4.0, 2.0)
        path.lineTo(3.0, 2.0)

        item = DrawingPathItem()
        item.setPathName('Flip-Flop 1')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -2.0))
        item.addConnectionPoint(QPointF(-4.0, 2.0))
        item.addConnectionPoint(QPointF(0.0, -4.0))
        item.addConnectionPoint(QPointF(0.0, 4.0))
        item.addConnectionPoint(QPointF(4.0, -2.0))
        item.addConnectionPoint(QPointF(4.0, 2.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createFlipFlop2() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(-3.0, -4.0)
        path.lineTo(-3.0, 4.0)
        path.lineTo(3.0, 4.0)
        path.lineTo(3.0, -4.0)
        path.lineTo(-3.0, -4.0)

        path.moveTo(-4.0, -2.0)
        path.lineTo(-3.0, -2.0)
        path.moveTo(-4.0, 2.0)
        path.lineTo(-3.0, 2.0)
        path.moveTo(4.0, -2.0)
        path.lineTo(3.0, -2.0)
        path.moveTo(4.0, 2.0)
        path.lineTo(3.0, 2.0)

        path.moveTo(-3.0, 1.0)
        path.lineTo(-2.0, 2.0)
        path.moveTo(-2.0, 2.0)
        path.lineTo(-3.0, 3.0)

        item = DrawingPathItem()
        item.setPathName('Flip-Flop 2')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, -2.0))
        item.addConnectionPoint(QPointF(-4.0, 2.0))
        item.addConnectionPoint(QPointF(0.0, -4.0))
        item.addConnectionPoint(QPointF(0.0, 4.0))
        item.addConnectionPoint(QPointF(4.0, -2.0))
        item.addConnectionPoint(QPointF(4.0, 2.0))
        return item
