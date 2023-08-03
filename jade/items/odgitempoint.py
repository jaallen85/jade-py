# odgitempoint.py
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

from enum import Enum
from typing import Any
from PySide6.QtCore import QPointF


class OdgItemPoint:
    class Type(Enum):
        NoType = 0
        Control = 1
        Connection = 2
        ControlAndConnection = 3
        FreeControlAndConnection = 4

    # ==================================================================================================================

    def __init__(self, position: QPointF = QPointF(), pointType: Type = Type.NoType) -> None:
        self._item: Any = None
        self._position: QPointF = QPointF(position)
        self._type: OdgItemPoint.Type = pointType
        self._connections: list[OdgItemPoint] = []

    def __del__(self) -> None:
        self.clearConnections()

    # ==================================================================================================================

    def item(self) -> Any:
        return self._item

    # ==================================================================================================================

    def setPosition(self, position: QPointF) -> None:
        self._position = QPointF(position)

    def position(self) -> QPointF:
        return self._position

    # ==================================================================================================================

    def setType(self, pointType: Type) -> None:
        self._type = pointType

    def type(self) -> Type:
        return self._type

    def isControlPoint(self) -> bool:
        return (self._type in (OdgItemPoint.Type.Control, OdgItemPoint.Type.ControlAndConnection,
                               OdgItemPoint.Type.FreeControlAndConnection))

    def isConnectionPoint(self) -> bool:
        return (self._type in (OdgItemPoint.Type.Connection, OdgItemPoint.Type.ControlAndConnection,
                               OdgItemPoint.Type.FreeControlAndConnection))

    def isFree(self) -> bool:
        return (self._type == OdgItemPoint.Type.FreeControlAndConnection)

    # ==================================================================================================================

    def addConnection(self, point: 'OdgItemPoint') -> None:
        if (point not in self._connections):
            self._connections.append(point)

    def removeConnection(self, point: 'OdgItemPoint') -> None:
        if (point in self._connections):
            self._connections.remove(point)

    def clearConnections(self) -> None:
        while (len(self._connections) > 0):
            point = self._connections[-1]
            self.removeConnection(point)
            point.removeConnection(self)

    def connections(self) -> list['OdgItemPoint']:
        return self._connections

    def isConnected(self, point: 'OdgItemPoint') -> bool:
        return (point in self._connections)

    def isItemConnected(self, item: Any) -> bool:
        # Returns True if any of this point's connections are to the specified item, False otherwise
        for point in self._connections:
            if (point.item() == item):
                return True
        return False
