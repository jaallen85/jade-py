# mainwindow.py
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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QFont, QIcon, QPen
from PyQt6.QtWidgets import QMainWindow
from .drawingarrow import DrawingArrow
from .drawingitem import DrawingItem
from .drawinglineitem import DrawingLineItem
from .drawingrectitem import DrawingRectItem

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        DrawingItem.register(DrawingLineItem())
        # DrawingItem.register(DrawingCurveItem())
        # DrawingItem.register(DrawingPolylineItem())
        DrawingItem.register(DrawingRectItem())
        # DrawingItem.register(DrawingEllipseItem())
        # DrawingItem.register(DrawingPolygonItem())
        # DrawingItem.register(DrawingTextItem())
        # DrawingItem.register(DrawingTextRectItem())
        # DrawingItem.register(DrawingTextEllipseItem())
        # DrawingItem.register(DrawingPathItem())
        # DrawingItem.register(DrawingItemGroup())

        font = QFont('Arial')
        font.setPointSizeF(100)

        DrawingItem.setDefaultProperty(
           'pen', QPen(QBrush(Qt.GlobalColor.black), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin))
        DrawingItem.setDefaultProperty('brush', QBrush(Qt.GlobalColor.white))
        DrawingItem.setDefaultProperty('startArrow', DrawingArrow(DrawingArrow.Style.NoStyle, 100))
        DrawingItem.setDefaultProperty('endArrow', DrawingArrow(DrawingArrow.Style.NoStyle, 100))
        DrawingItem.setDefaultProperty('font', font)
        DrawingItem.setDefaultProperty('textAlignment', Qt.AlignmentFlag.AlignCenter)
        DrawingItem.setDefaultProperty('textBrush', QBrush(Qt.GlobalColor.black))

        self.setWindowTitle('Jade')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(1690, 900)

    # ==================================================================================================================

    def newDrawing(self) -> None:
        pass

    def openDrawing(self, path: str) -> None:
        pass
