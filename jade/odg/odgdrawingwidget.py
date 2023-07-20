# odgdrawingwidget.py
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
from .odgdrawingview import OdgDrawingView


class OdgDrawingWidget(OdgDrawingView):
    cleanTextChanged = Signal(str)

    # ==================================================================================================================

    def undo(self) -> None:
        pass

    def redo(self) -> None:
        pass

    # ==================================================================================================================

    def cut(self) -> None:
        pass

    def copy(self) -> None:
        pass

    def paste(self) -> None:
        pass

    def delete(self) -> None:
        pass

    # ==================================================================================================================

    def rotateCurrentItems(self) -> None:
        pass

    def rotateBackCurrentItems(self) -> None:
        pass

    def flipCurrentItemsHorizontal(self) -> None:
        pass

    def flipCurrentItemsVertical(self) -> None:
        pass

    # ==================================================================================================================

    def bringCurrentItemsForward(self) -> None:
        pass

    def sendCurrentItemsBackward(self) -> None:
        pass

    def bringCurrentItemsToFront(self) -> None:
        pass

    def sendCurrentItemsToBack(self) -> None:
        pass

    # ==================================================================================================================

    def groupCurrentItems(self) -> None:
        pass

    def ungroupCurrentItem(self) -> None:
        pass

    # ==================================================================================================================

    def insertNewItemPoint(self) -> None:
        pass

    def removeCurrentItemPoint(self) -> None:
        pass

    # ==================================================================================================================

    def insertNewPage(self) -> None:
        pass

    def removeCurrentPage(self) -> None:
        pass
