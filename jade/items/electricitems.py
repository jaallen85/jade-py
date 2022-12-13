# electricitems.py
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


class ElectricItems:
    @staticmethod
    def create() -> list[tuple[DrawingPathItem, str]]:
        items = []
        items.append((ElectricItems.createResistor1(), 'icons:items/resistor1.png'))
        items.append((ElectricItems.createResistor2(), 'icons:items/resistor2.png'))
        items.append((ElectricItems.createCapacitor1(), 'icons:items/capacitor1.png'))
        items.append((ElectricItems.createCapacitor2(), 'icons:items/capacitor2.png'))
        items.append((ElectricItems.createInductor1(), 'icons:items/inductor1.png'))
        items.append((ElectricItems.createDiode(), 'icons:items/diode.png'))
        items.append((ElectricItems.createZenerDiode(), 'icons:items/zener_diode.png'))
        items.append((ElectricItems.createSchottkyDiode(), 'icons:items/schottky_diode.png'))
        items.append((ElectricItems.createNpnBjt(), 'icons:items/npn_bjt.png'))
        items.append((ElectricItems.createPnpBjt(), 'icons:items/pnp_bjt.png'))
        items.append((ElectricItems.createNmosFet(), 'icons:items/nmos_fet.png'))
        items.append((ElectricItems.createPmosFet(), 'icons:items/pmos_fet.png'))
        items.append((ElectricItems.createGround1(), 'icons:items/ground1.png'))
        items.append((ElectricItems.createGround2(), 'icons:items/ground2.png'))
        items.append((ElectricItems.createOpAmp(), 'icons:items/opamp.png'))
        items.append((ElectricItems.createLed(), 'icons:items/led.png'))
        items.append((ElectricItems.createVdc(), 'icons:items/vdc.png'))
        items.append((ElectricItems.createVac(), 'icons:items/vac.png'))
        items.append((ElectricItems.createIdc(), 'icons:items/idc.png'))
        items.append((ElectricItems.createIac(), 'icons:items/iac.png'))
        return items

    # ==================================================================================================================

    @staticmethod
    def createResistor1() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.0, 8.0, 2.0)

        path = QPainterPath()
        path.moveTo(-4.0, 0.0)
        path.lineTo(-3.0, 0.0)
        path.moveTo(-3.0, 0.0)
        path.lineTo(-2.5, -1.0)
        path.moveTo(-2.5, -1.0)
        path.lineTo(-1.5, 1.0)
        path.moveTo(-1.5, 1.0)
        path.lineTo(-0.5, -1.0)
        path.moveTo(-0.5, -1.0)
        path.lineTo(0.5, 1.0)
        path.moveTo(0.5, 1.0)
        path.lineTo(1.5, -1.0)
        path.moveTo(1.5, -1.0)
        path.lineTo(2.5, 1.0)
        path.moveTo(2.5, 1.0)
        path.lineTo(3.0, 0.0)
        path.moveTo(3.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Resistor 1')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createResistor2() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.0, 8.0, 2.0)

        path = QPainterPath()
        path.moveTo(-3.0, -1.0)
        path.lineTo(3.0, -1.0)
        path.lineTo(3.0, 1.0)
        path.lineTo(-3.0, 1.0)
        path.lineTo(-3.0, -1.0)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-3.0, 0.0)
        path.moveTo(4.0, 0.0)
        path.lineTo(3.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Resistor 2')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createCapacitor1() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(-4.0, 0.0)
        path.lineTo(-0.5, 0.0)

        path.moveTo(-0.5, -1.5)
        path.lineTo(-0.5, 1.5)
        path.moveTo(0.5, -1.5)
        path.lineTo(0.5, 1.5)

        path.moveTo(0.5, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Capacitor 1')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createCapacitor2() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(-4.0, 0.0)
        path.lineTo(-0.5, 0.0)

        path.moveTo(-0.5, -1.5)
        path.lineTo(-0.5, 1.5)
        path.moveTo(0.9, -1.5)
        path.cubicTo(0.1, -1.2, 0.1, 1.2, 0.9, 1.5)

        path.moveTo(0.4, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Capacitor 2')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createInductor1() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.0, 8.0, 1.0)

        path = QPainterPath()
        path.moveTo(-4.0, 0.0)
        path.lineTo(-3.6, 0.0)
        for index in range(4):
            x = -3.6 + index * 1.8
            path.moveTo(x, 0.0)
            path.cubicTo(x, -1.4, x + 1.8, -1.4, x + 1.8, 0.0)
        path.moveTo(3.6, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Inductor 1')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createDiode() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -1.5, 8.0, 3.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)
        path.moveTo(1.0, -1.5)
        path.lineTo(1.0, 1.5)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(1.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Diode')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createZenerDiode() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.5, 8.0, 5.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)
        path.moveTo(2.0, -2.5)
        path.lineTo(1.0, -1.5)
        path.moveTo(1.0, -1.5)
        path.lineTo(1.0, 1.5)
        path.moveTo(1.0, 1.5)
        path.lineTo(0.0, 2.5)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(1.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Zener Diode')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createSchottkyDiode() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -2.0, 8.0, 4.0)

        path = QPainterPath()
        path.moveTo(1.0, 0.0)
        path.lineTo(-1.0, -1.5)
        path.lineTo(-1.0, 1.5)
        path.lineTo(1.0, 0.0)
        path.moveTo(0.2, 1.2)
        path.lineTo(0.2, 2.0)
        path.moveTo(0.2, 2.0)
        path.lineTo(1.0, 2.0)
        path.moveTo(1.0, 2.0)
        path.lineTo(1.0, -2.0)
        path.moveTo(1.0, -2.0)
        path.lineTo(1.8, -2.0)
        path.moveTo(1.8, -2.0)
        path.lineTo(1.8, -1.2)

        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.0, 0.0)
        path.moveTo(1.0, 0.0)
        path.lineTo(4.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('Schottky Diode')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createNpnBjt() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(3.5, 0.0)
        path.cubicTo(3.5, -4.5255, -2.9, -4.5255, -2.9, 0)
        path.cubicTo(-2.9, 4.5255, 3.5, 4.5255, 3.5, 0)

        path.moveTo(2.0, -4.0)
        path.lineTo(2.0, -2.0)
        path.moveTo(2.0, -2.0)
        path.lineTo(-1.5, -1.0)
        path.moveTo(-1.5, 1.0)
        path.lineTo(2.0, 2.0)
        path.moveTo(2.0, 2.0)
        path.lineTo(2.0, 4.0)

        path.moveTo(-1.5, -2.0)
        path.lineTo(-1.5, 2.0)
        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.5, 0.0)

        path.moveTo(1.4172, 0.951)
        path.lineTo(2.0, 2.0)
        path.moveTo(2.0, 2.0)
        path.lineTo(0.831, 2.5228)

        item = DrawingPathItem()
        item.setPathName('NPN BJT')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(2.0, -4.0))
        item.addConnectionPoint(QPointF(2.0, 4.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createPnpBjt() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(3.5, 0.0)
        path.cubicTo(3.5, -4.5255, -2.9, -4.5255, -2.9, 0)
        path.cubicTo(-2.9, 4.5255, 3.5, 4.5255, 3.5, 0)

        path.moveTo(2.0, -4.0)
        path.lineTo(2.0, -2.0)
        path.moveTo(2.0, -2.0)
        path.lineTo(-1.5, -1.0)
        path.moveTo(-1.5, 1.0)
        path.lineTo(2.0, 2.0)
        path.moveTo(2.0, 2.0)
        path.lineTo(2.0, 4.0)

        path.moveTo(-1.5, -2.0)
        path.lineTo(-1.5, 2.0)
        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.5, 0.0)

        path.moveTo(-0.451, 0.4172)
        path.lineTo(-1.5, 1.0)
        path.moveTo(-1.5, 1.0)
        path.lineTo(-0.9172, 2.049)

        item = DrawingPathItem()
        item.setPathName('PNP BJT')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(2.0, -4.0))
        item.addConnectionPoint(QPointF(2.0, 4.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createNmosFet() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(3.5, 0.0)
        path.cubicTo(3.5, -4.5255, -2.9, -4.5255, -2.9, 0)
        path.cubicTo(-2.9, 4.5255, 3.5, 4.5255, 3.5, 0)

        path.moveTo(2.0, -4.0)
        path.lineTo(2.0, -1.5)
        path.moveTo(2.0, -1.5)
        path.lineTo(0.0, -1.5)

        path.moveTo(0.0, 0.0)
        path.lineTo(2.0, 0.0)
        path.moveTo(2.0, 0.0)
        path.lineTo(2.0, 4.0)
        path.moveTo(0.0, 1.5)
        path.lineTo(2.0, 1.5)

        path.moveTo(0.0, 2.0)
        path.lineTo(0.0, 1.0)
        path.moveTo(0.0, 0.5)
        path.lineTo(0.0, -0.5)
        path.moveTo(0.0, -1.0)
        path.lineTo(0.0, -2.0)

        path.moveTo(-1.5, -2.0)
        path.lineTo(-1.5, 2.0)
        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.5, 0.0)

        path.moveTo(0.8486, -0.8486)
        path.lineTo(0.0, 0.0)
        path.moveTo(0.0, 0.0)
        path.lineTo(0.8486, 0.8486)

        item = DrawingPathItem()
        item.setPathName('NMOS FET')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(2.0, -4.0))
        item.addConnectionPoint(QPointF(2.0, 4.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createPmosFet() -> DrawingPathItem:
        pathRect = QRectF(-4.0, -4.0, 8.0, 8.0)

        path = QPainterPath()
        path.moveTo(3.5, 0.0)
        path.cubicTo(3.5, -4.5255, -2.9, -4.5255, -2.9, 0)
        path.cubicTo(-2.9, 4.5255, 3.5, 4.5255, 3.5, 0)

        path.moveTo(2.0, -4.0)
        path.lineTo(2.0, -1.5)
        path.moveTo(2.0, -1.5)
        path.lineTo(0.0, -1.5)

        path.moveTo(0.0, 0.0)
        path.lineTo(2.0, 0.0)
        path.moveTo(2.0, 0.0)
        path.lineTo(2.0, 4.0)
        path.moveTo(0.0, 1.5)
        path.lineTo(2.0, 1.5)

        path.moveTo(0.0, 2.0)
        path.lineTo(0.0, 1.0)
        path.moveTo(0.0, 0.5)
        path.lineTo(0.0, -0.5)
        path.moveTo(0.0, -1.0)
        path.lineTo(0.0, -2.0)

        path.moveTo(-1.5, -2.0)
        path.lineTo(-1.5, 2.0)
        path.moveTo(-4.0, 0.0)
        path.lineTo(-1.5, 0.0)

        path.moveTo(1.1514, -0.8486)
        path.lineTo(2.0, 0.0)
        path.moveTo(2.0, 0.0)
        path.lineTo(1.1514, 0.8486)

        item = DrawingPathItem()
        item.setPathName('PMOS FET')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(2.0, -4.0))
        item.addConnectionPoint(QPointF(2.0, 4.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createGround1() -> DrawingPathItem:
        pathRect = QRectF(-2.0, 0.0, 4.0, 3.0)

        path = QPainterPath()
        path.moveTo(0.0, 0.0)
        path.lineTo(0.0, 1.0)

        path.moveTo(-2.0, 1.0)
        path.lineTo(2.0, 1.0)
        path.moveTo(-1.5, 2.0)
        path.lineTo(1.5, 2.0)
        path.moveTo(-1.0, 3.0)
        path.lineTo(1.0, 3.0)

        item = DrawingPathItem()
        item.setPathName('Ground 1')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(0.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createGround2() -> DrawingPathItem:
        pathRect = QRectF(-2.0, 0.0, 4.0, 3.0)

        path = QPainterPath()
        path.moveTo(0.0, 0.0)
        path.lineTo(0.0, 1.0)

        path.moveTo(-2.0, 1.0)
        path.lineTo(2.0, 1.0)
        path.moveTo(2.0, 1.0)
        path.lineTo(0.0, 3.0)
        path.moveTo(0.0, 3.0)
        path.lineTo(-2.0, 1.0)

        item = DrawingPathItem()
        item.setPathName('Ground 2')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(0.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createOpAmp() -> DrawingPathItem:
        pathRect = QRectF(-6.0, -4.0, 12.0, 8.0)

        path = QPainterPath()
        path.moveTo(-4.0, -4.0)
        path.lineTo(-4.0, 4.0)
        path.lineTo(4.0, 0.0)
        path.lineTo(-4.0, -4.0)

        path.moveTo(-6.0, -2.0)
        path.lineTo(-4.0, -2.0)
        path.moveTo(-6.0, 2.0)
        path.lineTo(-4.0, 2.0)
        path.moveTo(6.0, 0.0)
        path.lineTo(4.0, 0.0)

        path.moveTo(-3.4, -2.0)
        path.lineTo(-1.8, -2.0)
        path.moveTo(-2.6, -2.8)
        path.lineTo(-2.6, -1.2)

        path.moveTo(-3.4, 2.0)
        path.lineTo(-1.8, 2.0)

        item = DrawingPathItem()
        item.setPathName('Op Amp')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-6.0, -2.0))
        item.addConnectionPoint(QPointF(-6.0, 2.0))
        item.addConnectionPoint(QPointF(6.0, 0.0))
        item.addConnectionPoint(QPointF(0.0, -2.0))
        item.addConnectionPoint(QPointF(0.0, 2.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createLed() -> DrawingPathItem:
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

        for x in (0.6, 1.6):
            path.moveTo(x, -0.7)
            path.lineTo(x + 0.8, -1.5)
            path.moveTo(x + 0.4, -1.5)
            path.lineTo(x + 0.8, -1.5)
            path.moveTo(x + 0.8, -1.5)
            path.lineTo(x + 0.8, -1.1)

        item = DrawingPathItem()
        item.setPathName('LED')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(-4.0, 0.0))
        item.addConnectionPoint(QPointF(4.0, 0.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createVdc() -> DrawingPathItem:
        pathRect = QRectF(-3.0, -6.0, 6.0, 12.0)

        path = QPainterPath()
        path.moveTo(3.0, 0.0)
        path.cubicTo(3.0, -5.3, -3.0, -5.3, -3.0, 0.0)
        path.cubicTo(-3.0, 5.3, 3.0, 5.3, 3.0, 0.0)

        path.moveTo(0.0, -6.0)
        path.lineTo(0.0, -4.0)
        path.moveTo(0.0, 4.0)
        path.lineTo(0.0, 6.0)

        path.moveTo(-0.8, -1.3)
        path.lineTo(0.8, -1.3)
        path.moveTo(0.0, -2.1)
        path.lineTo(0.0, -0.5)

        path.moveTo(-0.8, 1.8)
        path.lineTo(0.8, 1.8)

        item = DrawingPathItem()
        item.setPathName('DC Voltage')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(0.0, -6.0))
        item.addConnectionPoint(QPointF(0.0, 6.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createVac() -> DrawingPathItem:
        pathRect = QRectF(-3.0, -6.0, 6.0, 12.0)

        path = QPainterPath()
        path.moveTo(3.0, 0.0)
        path.cubicTo(3.0, -5.3, -3.0, -5.3, -3.0, 0.0)
        path.cubicTo(-3.0, 5.3, 3.0, 5.3, 3.0, 0.0)

        path.moveTo(0.0, -6.0)
        path.lineTo(0.0, -4.0)
        path.moveTo(0.0, 4.0)
        path.lineTo(0.0, 6.0)

        path.moveTo(-1.0, 0.0)
        path.cubicTo(-0.2, -2.4, 0.2, 2.4, 1.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('AC Voltage')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(0.0, -6.0))
        item.addConnectionPoint(QPointF(0.0, 6.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createIdc() -> DrawingPathItem:
        pathRect = QRectF(-3.0, -6.0, 6.0, 12.0)

        path = QPainterPath()
        path.moveTo(3.0, 0.0)
        path.cubicTo(3.0, -5.3, -3.0, -5.3, -3.0, 0.0)
        path.cubicTo(-3.0, 5.3, 3.0, 5.3, 3.0, 0.0)

        path.moveTo(0.0, -6.0)
        path.lineTo(0.0, -4.0)
        path.moveTo(0.0, 4.0)
        path.lineTo(0.0, 6.0)

        path.moveTo(0.0, 2.0)
        path.lineTo(0.0, -2.0)
        path.moveTo(-0.8486, -1.1514)
        path.lineTo(0.0, -2.0)
        path.moveTo(0.0, -2.0)
        path.lineTo(0.8486, -1.1514)

        item = DrawingPathItem()
        item.setPathName('DC Current')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(0.0, -6.0))
        item.addConnectionPoint(QPointF(0.0, 6.0))
        return item

    # ==================================================================================================================

    @staticmethod
    def createIac() -> DrawingPathItem:
        pathRect = QRectF(-3.0, -6.0, 6.0, 12.0)

        path = QPainterPath()
        path.moveTo(3.0, 0.0)
        path.cubicTo(3.0, -5.3, -3.0, -5.3, -3.0, 0.0)
        path.cubicTo(-3.0, 5.3, 3.0, 5.3, 3.0, 0.0)

        path.moveTo(0.0, -6.0)
        path.lineTo(0.0, -4.0)
        path.moveTo(0.0, 4.0)
        path.lineTo(0.0, 6.0)

        path.moveTo(0.0, 2.0)
        path.lineTo(0.0, -2.0)
        path.moveTo(-0.8486, -1.1514)
        path.lineTo(0.0, -2.0)
        path.moveTo(0.0, -2.0)
        path.lineTo(0.8486, -1.1514)

        path.moveTo(-1.0, 0.0)
        path.cubicTo(-0.2, -2.4, 0.2, 2.4, 1.0, 0.0)

        item = DrawingPathItem()
        item.setPathName('AC Current')
        item.setRect(pathRect)
        item.setPath(path, pathRect)
        item.addConnectionPoint(QPointF(0.0, -6.0))
        item.addConnectionPoint(QPointF(0.0, 6.0))
        return item
