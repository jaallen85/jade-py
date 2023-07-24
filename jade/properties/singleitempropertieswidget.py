# singleitempropertieswidget.py
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

from PySide6.QtCore import QPointF, Signal
from PySide6.QtWidgets import QWidget
from ..odg.odgitem import OdgItem
from ..odg.odgitempoint import OdgItemPoint


class SingleItemPropertiesWidget(QWidget):
    itemMoved = Signal(QPointF)
    itemResized = Signal(OdgItemPoint, QPointF)
    itemResized2 = Signal(OdgItemPoint, QPointF, OdgItemPoint, QPointF)
    itemPropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

    # ==================================================================================================================

    def setItem(self, item: OdgItem) -> None:
        pass
