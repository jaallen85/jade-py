# odgmarker.py
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

import math
from enum import IntEnum
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QPainterPathStroker, QPen, QTransform


class OdgMarker:
    class Style(IntEnum):
        NoMarker = 0
        Triangle = 1
        Circle = 2

    # ==================================================================================================================

    def __init__(self, style: 'OdgMarker.Style' = Style.NoMarker, size: float = 0.0) -> None:
        self._style: OdgMarker.Style = style
        self._size: float = size

    # ==================================================================================================================

    def setStyle(self, style: 'OdgMarker.Style') -> None:
        self._style = style

    def setSize(self, size: float) -> None:
        self._size = size

    def style(self) -> 'OdgMarker.Style':
        return self._style

    def size(self) -> float:
        return self._size

    # ==================================================================================================================

    def shape(self, pen: QPen, position: QPointF, angle: float) -> QPainterPath:
        shape = QPainterPath()
        if (self._style != OdgMarker.Style.NoMarker and pen.style() != Qt.PenStyle.NoPen):
            # Transform the path to the specified position and angle
            transform = QTransform()
            transform.translate(position.x(), position.y())
            transform.rotate(angle)
            transformedPath = transform.map(self._path())

            # Create a shape representing the outline of the path
            pathStroker = QPainterPathStroker()
            pathStroker.setWidth(1E-6 if (pen.widthF() <= 0.0) else pen.widthF())
            pathStroker.setCapStyle(Qt.PenCapStyle.SquareCap)
            pathStroker.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            shape = pathStroker.createStroke(transformedPath)

            # The final shape includes both the outline and the interior of the arrow
            shape = shape.united(transformedPath)
        return shape

    # ==================================================================================================================

    def paint(self, painter: QPainter, pen: QPen, position: QPointF, angle: float) -> None:
        if (self._style != OdgMarker.Style.NoMarker and pen.style() != Qt.PenStyle.NoPen):
            # Set pen
            originalPenStyle = pen.style()

            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            # Set brush
            painter.setBrush(pen.brush())

            # Draw arrow
            painter.translate(position)
            painter.rotate(angle)
            painter.drawPath(self._path())
            painter.rotate(-angle)
            painter.translate(-position)

            # Cleanup tasks
            pen.setStyle(originalPenStyle)

    # ==================================================================================================================

    def _path(self) -> QPainterPath:
        path = QPainterPath()

        if (self._style == OdgMarker.Style.Triangle):
            angle = math.pi / 6     # Makes the arrowhead a 60 degree angle
            sqrt2 = math.sqrt(2)
            x = self._size / sqrt2 * math.cos(angle)
            y = self._size / sqrt2 * math.sin(angle)

            path.moveTo(QPointF(0, 0))
            path.lineTo(QPointF(-x, -y))
            path.lineTo(QPointF(-x, y))
            path.closeSubpath()
        elif (self._style == OdgMarker.Style.Circle):
            path.addEllipse(QPointF(0, 0), self._size / 2, self._size / 2)

        return path
