# odgpage.py
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

from typing import Any
from PySide6.QtCore import QObject, Signal
from ..items.odgitem import OdgItem


class OdgPage(QObject):
    propertyChanged = Signal(str, object)

    def __init__(self, name: str) -> None:
        super().__init__()
        self._parent: Any = None
        self._name: str = name
        self._items: list[OdgItem] = []

    def __del__(self) -> None:
        self.clearItems()

    # ==================================================================================================================

    def parent(self) -> Any:
        return self._parent

    # ==================================================================================================================

    def setName(self, name: str) -> None:
        if (self._name != name):
            self._name = name
            self.propertyChanged.emit('name', self._name)

    def name(self) -> str:
        return self._name

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> bool:
        match (name):
            case 'name':
                if (isinstance(value, str)):
                    self.setName(value)
        return True

    def property(self, name: str) -> Any:
        match (name):
            case 'name':
                return self.name()
        return None

    # ==================================================================================================================

    def addItem(self, item: OdgItem) -> None:
        self.insertItem(len(self._items), item)

    def insertItem(self, index: int, item: OdgItem) -> None:
        if (item not in self._items):
            self._items.insert(index, item)
            # pylint: disable-next=W0212
            item._parent = self

    def removeItem(self, item: OdgItem) -> None:
        if (item in self._items):
            self._items.remove(item)
            # pylint: disable-next=W0212
            item._parent = None

    def clearItems(self) -> None:
        while (len(self._items) > 0):
            item = self._items[-1]
            self.removeItem(item)
            del item

    def items(self) -> list[OdgItem]:
        return self._items
