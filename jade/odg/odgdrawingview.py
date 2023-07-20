# odgdrawingview.py
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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractScrollArea
from .odgitem import OdgItem


class OdgDrawingView(QAbstractScrollArea):
    scaleChanged = Signal(float)
    modeChanged = Signal(int)
    modeTextChanged = Signal(str)
    mouseInfoChanged = Signal(str)

    # ==================================================================================================================

    def selectAll(self) -> None:
        pass

    def selectNone(self) -> None:
        pass

    # ==================================================================================================================

    def setScale(self, scale: float) -> None:
        pass

    def zoomIn(self) -> None:
        pass

    def zoomOut(self) -> None:
        pass

    def zoomFit(self) -> None:
        pass

    # ==================================================================================================================

    def setSelectMode(self) -> None:
        pass

    def setScrollMode(self) -> None:
        pass

    def setZoomMode(self) -> None:
        pass

    def setPlaceMode(self, items: list[OdgItem]) -> None:
        pass
