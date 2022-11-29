# pagepropertieswidget.py
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

import typing
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from .drawingwidget import DrawingWidget


class PagePropertiesWidget(QWidget):
    drawingPropertyChanged = pyqtSignal(str, object)
    pagePropertyChanged = pyqtSignal(str, object)

    def __init__(self) -> None:
        super().__init__()

    # ==================================================================================================================

    def setDrawingProperty(self, name: str, value: typing.Any) -> None:
        pass

    def setPage(self, page: DrawingWidget) -> None:
        pass

    def setPageProperty(self, name: str, value: typing.Any) -> None:
        pass
