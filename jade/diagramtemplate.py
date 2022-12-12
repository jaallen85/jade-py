# diagramtemplate.py
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

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor
from .properties.units import Units


class DiagramTemplate:
    def __init__(self, name: str, description: str) -> None:
        super().__init__()

        self._name: str = name
        self._description: str = description

        self._units: Units = Units.Millimeters
        self._sceneRect: QRectF = QRectF()
        self._backgroundBrush: QBrush = QBrush(QColor(255, 255, 255))
        self._grid: float = 0
        self._gridVisible: bool = True
        self._gridBrush: QBrush = QBrush(QColor(0, 128, 128))
        self._gridSpacingMajor: int = 8
        self._gridSpacingMinor: int = 2

    # ==================================================================================================================

    def setName(self, name: str) -> None:
        self._name = name

    def setDescription(self, description: str) -> None:
        self._description = description

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    # ==================================================================================================================

    def setUnits(self, units: Units) -> None:
        self._units = units

    def setSceneRect(self, rect: QRectF) -> None:
        self._sceneRect = QRectF(rect)

    def setBackgroundBrush(self, brush: QBrush) -> None:
        self._backgroundBrush = QBrush(brush)

    def setGrid(self, grid: float) -> None:
        self._grid = grid

    def setGridVisible(self, visible: bool) -> None:
        self._gridVisible = visible

    def setGridBrush(self, brush: QBrush) -> None:
        self._gridBrush = QBrush(brush)

    def setGridSpacingMajor(self, spacing: int) -> None:
        self._gridSpacingMajor = spacing

    def setGridSpacingMinor(self, spacing: int) -> None:
        self._gridSpacingMinor = spacing

    def units(self) -> Units:
        return self._units

    def sceneRect(self) -> QRectF:
        return self._sceneRect

    def backgroundBrush(self) -> QBrush:
        return self._backgroundBrush

    def grid(self) -> float:
        return self._grid

    def isGridVisible(self) -> bool:
        return self._gridVisible

    def gridBrush(self) -> QBrush:
        return self._gridBrush

    def gridSpacingMajor(self) -> int:
        return self._gridSpacingMajor

    def gridSpacingMinor(self) -> int:
        return self._gridSpacingMinor

    # ==================================================================================================================

    @staticmethod
    def createDefaultTemplates() -> list['DiagramTemplate']:
        blankMetric = DiagramTemplate('Blank Diagram using Metric Units (millimeters)',
                                      'A blank diagram with default settings using Metric units.')
        blankMetric.setUnits(Units.Millimeters)
        blankMetric.setSceneRect(QRectF(-5.0, -5.0, 300.0, 200.0))
        blankMetric.setGrid(1.0)

        blankUs = DiagramTemplate('Blank Diagram using US Units (inches)',
                                  'A blank diagram with default settings using US units.')
        blankUs.setUnits(Units.Inches)
        blankUs.setSceneRect(QRectF(-0.2, -0.2, 12.0, 8.0))
        blankUs.setGrid(0.05)

        return [blankMetric, blankUs]
