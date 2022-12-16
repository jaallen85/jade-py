# vsdxwriter.py
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

from ..drawing.drawingxmlinterface import DrawingXmlInterface
from ..diagramwidget import DiagramWidget


class VsdxWriter(DrawingXmlInterface):
    def __init__(self, drawing: DiagramWidget, exportEntireDocument: bool, scale: float, units: str) -> None:
        super().__init__()

        self._drawing: DiagramWidget = drawing
        self._exportEntireDocument: bool = exportEntireDocument
        self._scale: float = scale
        self._units: str = str(units)

    # ==================================================================================================================

    def write(self, path: str) -> None:
        pass
