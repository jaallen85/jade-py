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
from .odgitem import OdgItem


class OdgPage:
    def __init__(self, name: str) -> None:
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
        self._name = name

    def name(self) -> str:
        return self._name

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
