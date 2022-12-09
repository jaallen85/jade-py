# drawingarrow.py
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

import math
from enum import Enum
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QPainterPathStroker, QPen, QTransform


class DrawingArrow:
    class Style(Enum):
        NoStyle = 0
        Normal = 1
        Triangle = 2
        TriangleFilled = 3
        Concave = 4
        ConcaveFilled = 5
        Circle = 6
        CircleFilled = 7

    # ==================================================================================================================

    def __init__(self, style: 'DrawingArrow.Style' = Style.NoStyle, size: float = 0.0) -> None:
        self._style: DrawingArrow.Style = style
        self._size: float = size

        self._path: QPainterPath = QPainterPath()
        self._updateGeometry()

    # ==================================================================================================================

    def setStyle(self, style: 'DrawingArrow.Style') -> None:
        self._style = style
        self._updateGeometry()

    def setSize(self, size: float) -> None:
        self._size = size
        self._updateGeometry()

    def style(self) -> 'DrawingArrow.Style':
        return self._style

    def size(self) -> float:
        return self._size

    # ==================================================================================================================

    def shape(self, pen: QPen, position: QPointF, angle: float) -> QPainterPath:
        shape = QPainterPath()
        if (self._style != DrawingArrow.Style.NoStyle and pen.style() != Qt.PenStyle.NoPen):
            # Transform the path to the specified position and angle
            transform = QTransform()
            transform.translate(position.x(), position.y())
            transform.rotate(-angle)
            transformedPath = transform.map(self._path)

            # Create a shape representing the outline of the path
            pathStroker = QPainterPathStroker()
            pathStroker.setWidth(1E-6 if (pen.widthF() <= 0.0) else pen.widthF())
            pathStroker.setCapStyle(Qt.PenCapStyle.SquareCap)
            pathStroker.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            shape = pathStroker.createStroke(transformedPath)

            # The final shape includes both the outline and the interior of the arrow
            shape = shape.united(transformedPath)
        return shape

    def paint(self, painter: QPainter, pen: QPen, position: QPointF, angle: float) -> None:
        if (self._style != DrawingArrow.Style.NoStyle and pen.style() != Qt.PenStyle.NoPen):
            # Set pen
            originalPenStyle = pen.style()

            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            # Set brush
            if (self._style in (DrawingArrow.Style.TriangleFilled, DrawingArrow.Style.ConcaveFilled,
                                DrawingArrow.Style.CircleFilled)):
                painter.setBrush(pen.brush())
            elif (self._style in (DrawingArrow.Style.Triangle, DrawingArrow.Style.Concave,
                                  DrawingArrow.Style.Circle)):
                painter.setBrush(painter.background())
            else:
                painter.setBrush(QBrush(Qt.GlobalColor.transparent))

            # Draw arrow
            painter.translate(position)
            painter.rotate(-angle)
            painter.drawPath(self._path)
            painter.rotate(angle)
            painter.translate(-position)

            # Cleanup tasks
            pen.setStyle(originalPenStyle)

    # ==================================================================================================================

    def _updateGeometry(self) -> None:
        self._path.clear()
        if (self._style == DrawingArrow.Style.Normal):
            angle = math.pi / 6     # Makes the arrowhead a 60 degree angle
            sqrt2 = math.sqrt(2)
            x = self._size / sqrt2 * math.cos(angle)
            y = self._size / sqrt2 * math.sin(angle)

            self._path.moveTo(QPointF(0, 0))
            self._path.lineTo(QPointF(-x, -y))
            self._path.moveTo(QPointF(0, 0))
            self._path.lineTo(QPointF(-x, y))

        elif (self._style in (DrawingArrow.Style.Triangle, DrawingArrow.Style.TriangleFilled)):
            angle = math.pi / 6     # Makes the arrowhead a 60 degree angle
            sqrt2 = math.sqrt(2)
            x = self._size / sqrt2 * math.cos(angle)
            y = self._size / sqrt2 * math.sin(angle)

            self._path.moveTo(QPointF(0, 0))
            self._path.lineTo(QPointF(x, -y))
            self._path.lineTo(QPointF(x, y))
            self._path.closeSubpath()

        elif (self._style in (DrawingArrow.Style.Concave, DrawingArrow.Style.ConcaveFilled)):
            angle = math.pi / 6     # Makes the arrowhead a 60 degree angle
            sqrt2 = math.sqrt(2)
            x = self._size / sqrt2 * math.cos(angle)
            x2 = self._size / sqrt2 / 2
            y = self._size / sqrt2 * math.sin(angle)

            self._path.moveTo(QPointF(0, 0))
            self._path.lineTo(QPointF(-x, -y))
            self._path.lineTo(QPointF(-x2, 0))
            self._path.lineTo(QPointF(-x, y))
            self._path.closeSubpath()

        elif (self._style in (DrawingArrow.Style.Circle, DrawingArrow.Style.CircleFilled)):
            self._path.addEllipse(QPointF(0, 0), self._size / 2, self._size / 2)
