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
        return items

    # ======================================================================================================================

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

    # ======================================================================================================================

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
