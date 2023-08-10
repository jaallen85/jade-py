# odgcurve.py
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

import math
from PySide6.QtCore import QLineF, QPointF


class OdgCurve:
    def __init__(self, p1: QPointF = QPointF(), cp1: QPointF = QPointF(), cp2: QPointF = QPointF(),
                 p2: QPointF = QPointF()) -> None:
        self._p1: QPointF = QPointF(p1)
        self._cp1: QPointF = QPointF(cp1)
        self._cp2: QPointF = QPointF(cp2)
        self._p2: QPointF = QPointF(p2)

    def __eq__(self, other: object) -> bool:
        if (isinstance(other, OdgCurve)):
            return (self._p1 == other.p1() and self._cp1 == other.cp1() and
                    self._cp2 == other.cp2() and self._p2 == other.p2())
        return False

    # ==================================================================================================================

    def setP1(self, p1: QPointF) -> None:
        self._p1 = QPointF(p1)

    def setCP1(self, cp1: QPointF) -> None:
        self._cp1 = QPointF(cp1)

    def setCP2(self, cp2: QPointF) -> None:
        self._cp2 = QPointF(cp2)

    def setP2(self, p2: QPointF) -> None:
        self._p2 = QPointF(p2)

    def p1(self) -> QPointF:
        return self._p1

    def cp1(self) -> QPointF:
        return self._cp1

    def cp2(self) -> QPointF:
        return self._cp2

    def p2(self) -> QPointF:
        return self._p2

    # ==================================================================================================================

    def center(self) -> QPointF:
        return QLineF(self._p1, self._p2).center()

    def length(self) -> float:
        return QLineF(self._p1, self._p2).length()

    def startAngle(self) -> float:
        p1 = self._p1
        p2 = self._pointFromRatio(0.05)
        return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi

    def endAngle(self) -> float:
        p1 = self._p2
        p2 = self._pointFromRatio(0.95)
        return math.atan2(p1.y() - p2.y(), p1.x() - p2.x()) * 180 / math.pi

    # ==================================================================================================================

    def translate(self, offset: QPointF) -> None:
        self._p1.setX(self._p1.x() + offset.x())
        self._p1.setY(self._p1.y() + offset.y())
        self._cp1.setX(self._cp1.x() + offset.x())
        self._cp1.setY(self._cp1.y() + offset.y())
        self._cp2.setX(self._cp2.x() + offset.x())
        self._cp2.setY(self._cp2.y() + offset.y())
        self._p2.setX(self._p2.x() + offset.x())
        self._p2.setY(self._p2.y() + offset.y())

    def scale(self, scale: float) -> None:
        self._p1.setX(self._p1.x() * scale)
        self._p1.setY(self._p1.y() * scale)
        self._cp1.setX(self._cp1.x() * scale)
        self._cp1.setY(self._cp1.y() * scale)
        self._cp2.setX(self._cp2.x() * scale)
        self._cp2.setY(self._cp2.y() * scale)
        self._p2.setX(self._p2.x() * scale)
        self._p2.setY(self._p2.y() * scale)

    # ==================================================================================================================

    def _pointFromRatio(self, ratio: float) -> QPointF:
        x = ((1 - ratio) * (1 - ratio) * (1 - ratio) * self._p1.x() +
             3 * ratio * (1 - ratio) * (1 - ratio) * self._cp1.x() +
             3 * ratio * ratio * (1 - ratio) * self._cp2.x() +
             ratio * ratio * ratio * self._p2.x())
        y = ((1 - ratio) * (1 - ratio) * (1 - ratio) * self._p1.y() +
             3 * ratio * (1 - ratio) * (1 - ratio) * self._cp1.y() +
             3 * ratio * ratio * (1 - ratio) * self._cp2.y() +
             ratio * ratio * ratio * self._p2.y())
        return QPointF(x, y)

    # ==================================================================================================================

    @classmethod
    def copy(cls, other: 'OdgCurve') -> 'OdgCurve':
        newCurve = cls()
        newCurve.setP1(other.p1())
        newCurve.setCP1(other.cp1())
        newCurve.setCP2(other.cp2())
        newCurve.setP2(other.p2())
        return newCurve
