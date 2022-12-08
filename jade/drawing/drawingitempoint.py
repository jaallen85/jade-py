# drawingitempoint.py
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
from enum import Enum
from PySide6.QtCore import QPointF


class DrawingItemPoint:
    class Type(Enum):
        NoType = 0
        Control = 1
        Connection = 2
        ControlAndConnection = 3
        FreeControlAndConnection = 4

    # ==================================================================================================================

    def __init__(self, position: QPointF = QPointF(), pointType: Type = Type.NoType) -> None:
        self._item: typing.Any = None
        self._position: QPointF = QPointF(position)
        self._type: DrawingItemPoint.Type = pointType
        self._connections: list[DrawingItemPoint] = []

    def __del__(self) -> None:
        self.clearConnections()

    # ==================================================================================================================

    def item(self) -> typing.Any:
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
        return (self._type in (DrawingItemPoint.Type.Control, DrawingItemPoint.Type.ControlAndConnection,
                               DrawingItemPoint.Type.FreeControlAndConnection))

    def isConnectionPoint(self) -> bool:
        return (self._type in (DrawingItemPoint.Type.Connection, DrawingItemPoint.Type.ControlAndConnection,
                               DrawingItemPoint.Type.FreeControlAndConnection))

    def isFree(self) -> bool:
        return (self._type == DrawingItemPoint.Type.FreeControlAndConnection)

    # ==================================================================================================================

    def addConnection(self, point: 'DrawingItemPoint') -> None:
        if (point not in self._connections):
            self._connections.append(point)

    def removeConnection(self, point: 'DrawingItemPoint') -> None:
        if (point in self._connections):
            self._connections.remove(point)

    def clearConnections(self) -> None:
        while (len(self._connections) > 0):
            point = self._connections[-1]
            self.removeConnection(point)
            point.removeConnection(self)

    def connections(self) -> list['DrawingItemPoint']:
        return self._connections

    def isConnected(self, point: 'DrawingItemPoint') -> bool:
        return (point in self._connections)

    def isItemConnected(self, item: typing.Any) -> bool:
        # Returns True if any of this point's connections are to the specified item, False otherwise
        for point in self._connections:
            if (point.item() == item):
                return True
        return False
