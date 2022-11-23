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
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QPainter, QPainterPath, QPainterPathStroker, QPen, QTransform


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

    def __init__(self, style: 'DrawingArrow.Style' = Style.NoStyle, size: float = 0) -> None:
        self._style: DrawingArrow.Style = style
        self._size: float = size
        self._path: QPainterPath = QPainterPath()
        self._updateGeometry()

    def clone(self) -> 'DrawingArrow':
        return DrawingArrow(self.style(), self.size())

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
            transform = QTransform()
            transform.translate(position.x(), position.y())
            transform.rotate(angle)
            mappedPath = transform.map(self._path)
            shape = DrawingArrow.strokePath(mappedPath, pen)
            shape = shape.united(mappedPath)
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
            painter.rotate(angle)
            painter.drawPath(self._path)
            painter.rotate(-angle)
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

        elif (self._style == DrawingArrow.Style.Triangle or self._style == DrawingArrow.Style.TriangleFilled):
            angle = math.pi / 6     # Makes the arrowhead a 60 degree angle
            sqrt2 = math.sqrt(2)
            x = self._size / sqrt2 * math.cos(angle)
            y = self._size / sqrt2 * math.sin(angle)

            self._path.moveTo(QPointF(0, 0))
            self._path.lineTo(QPointF(-x, -y))
            self._path.lineTo(QPointF(-x, y))
            self._path.closeSubpath()

        elif (self._style == DrawingArrow.Style.Concave or self._style == DrawingArrow.Style.ConcaveFilled):
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

        elif (self._style == DrawingArrow.Style.Circle or self._style == DrawingArrow.Style.CircleFilled):
            self._path.addEllipse(QPointF(0, 0), self._size / 2, self._size / 2)

    # ==================================================================================================================

    @staticmethod
    def strokePath(path: QPainterPath, pen: QPen) -> QPainterPath:
        if (path.isEmpty()):
            return path
        ps = QPainterPathStroker()
        ps.setWidth(1E-6 if (pen.widthF() <= 0.0) else pen.widthF())
        ps.setCapStyle(Qt.PenCapStyle.SquareCap)
        ps.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
        return ps.createStroke(path)

    # ==================================================================================================================

    @staticmethod
    def styleToString(style: 'DrawingArrow.Style') -> str:
        styleStr = 'none'
        match (style):
            case DrawingArrow.Style.Normal:
                styleStr = 'normal'
            case DrawingArrow.Style.Triangle:
                styleStr = 'triangle'
            case DrawingArrow.Style.TriangleFilled:
                styleStr = 'triangleFilled'
            case DrawingArrow.Style.Concave:
                styleStr = 'concave'
            case DrawingArrow.Style.ConcaveFilled:
                styleStr = 'concaveFilled'
            case DrawingArrow.Style.Circle:
                styleStr = 'circle'
            case DrawingArrow.Style.CircleFilled:
                styleStr = 'circleFilled'
        return styleStr

    @staticmethod
    def styleFromString(text: str) -> 'DrawingArrow.Style':
        style = DrawingArrow.Style.NoStyle
        match (text.lower()):
            case 'normal':
                style = DrawingArrow.Style.Normal
            case 'triangle':
                style = DrawingArrow.Style.Triangle
            case 'trianglefilled':
                style = DrawingArrow.Style.TriangleFilled
            case 'concave':
                style = DrawingArrow.Style.Concave
            case 'concavefilled':
                style = DrawingArrow.Style.ConcaveFilled
            case 'circle':
                style = DrawingArrow.Style.Circle
            case 'circlefilled':
                style = DrawingArrow.Style.CircleFilled
        return style
