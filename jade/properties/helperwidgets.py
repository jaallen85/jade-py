# helperwidgets.py
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

import re
from PySide6.QtCore import Qt, QPointF, QRect, QSize, QSizeF, Signal
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QIcon, QMouseEvent, QPaintEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QMenu, QLineEdit, QPushButton, QSizePolicy, QWidget, \
                            QWidgetAction
from ..drawing.drawingunits import DrawingUnits


class PositionEdit(QLineEdit):
    positionChanged = Signal(float)

    def __init__(self, position: float = 0.0, units: DrawingUnits = DrawingUnits.Millimeters) -> None:
        super().__init__()
        self._position: float = position
        self._units: DrawingUnits = units
        self._cachedText: str = self.positionToString(self._position, self._units)
        self.setText(self._cachedText)
        self.editingFinished.connect(self.validateInputAndSendPositionChanged)  # type: ignore

    def sizeHint(self) -> QSize:
        return QFontMetrics(self.font()).boundingRect('-8888.88 888').size() + QSize(16, 2)     # type: ignore

    def setPosition(self, position: float) -> None:
        if (self._position != position or self._position == 0):
            self._position = position
            self._cachedText = self.positionToString(self._position, self._units)
            self.setText(self._cachedText)
            self.positionChanged.emit(self._position)
        else:
            self.setText(self._cachedText)

    def setUnits(self, units: DrawingUnits) -> None:
        if (self._units != units):
            newPosition = DrawingUnits.convert(self._position, self._units, units)
            self._units = units
            self.setPosition(newPosition)

    def position(self) -> float:
        return self._position

    def units(self) -> DrawingUnits:
        return self._units

    def positionToString(self, position: float, units: DrawingUnits) -> str:
        return f'{position:.8g} {units.toString()}'

    def validateInputAndSendPositionChanged(self) -> None:
        unitsExpression = re.compile('[a-zA-Z]+$')
        match = unitsExpression.search(self.text())
        if (match):
            try:
                position = float(match.string[:match.start(0)].strip())
                units = DrawingUnits.fromString(match.group(0))
                self.setPosition(DrawingUnits.convert(position, units, self._units))
                self.blockSignals(True)
                self.clearFocus()
                self.blockSignals(False)
            except ValueError:
                self.setText(self._cachedText)
        else:
            try:
                self.setPosition(float(self.text()))
                self.blockSignals(True)
                self.clearFocus()
                self.blockSignals(False)
            except ValueError:
                self.setText(self._cachedText)


# ======================================================================================================================

class SizeEdit(QLineEdit):
    sizeChanged = Signal(float)

    def __init__(self, size: float = 0.0, units: DrawingUnits = DrawingUnits.Millimeters) -> None:
        super().__init__()
        size = max(size, 0)
        self._size: float = size
        self._units: DrawingUnits = units
        self._cachedText: str = self.sizeToString(self._size, self._units)
        self.setText(self._cachedText)
        self.editingFinished.connect(self.validateInputAndSendSizeChanged)  # type: ignore

    def sizeHint(self) -> QSize:
        return QFontMetrics(self.font()).boundingRect('-8888.88 888').size() + QSize(16, 2)     # type: ignore

    def setSize(self, size: float) -> None:
        if (self._size != size or self._size == 0):
            self._size = size
            self._cachedText = self.sizeToString(self._size, self._units)
            self.setText(self._cachedText)
            self.sizeChanged.emit(self._size)
        else:
            self.setText(self._cachedText)

    def setUnits(self, units: DrawingUnits) -> None:
        if (self._units != units):
            newSize = DrawingUnits.convert(self._size, self._units, units)
            self._units = units
            self.setSize(newSize)

    def size(self) -> float:    # type: ignore
        return self._size

    def units(self) -> DrawingUnits:
        return self._units

    def sizeToString(self, size: float, units: DrawingUnits):
        return f'{size:.8g} {units.toString()}'

    def validateInputAndSendSizeChanged(self) -> None:
        unitsExpression = re.compile('[a-zA-Z]+$')
        match = unitsExpression.search(self.text())
        if (match):
            try:
                size = float(match.string[:match.start(0)].strip())
                units = DrawingUnits.fromString(match.group(0))
                self.setSize(DrawingUnits.convert(size, units, self._units))
                self.blockSignals(True)
                self.clearFocus()
                self.blockSignals(False)
            except ValueError:
                self.setText(self._cachedText)
        else:
            try:
                self.setSize(float(self.text()))
                self.blockSignals(True)
                self.clearFocus()
                self.blockSignals(False)
            except ValueError:
                self.setText(self._cachedText)


# ======================================================================================================================

class PositionWidget(QWidget):
    positionChanged = Signal(QPointF)

    def __init__(self, position: QPointF = QPointF(0, 0), units: DrawingUnits = DrawingUnits.Millimeters) -> None:
        super().__init__()
        self._xEdit: PositionEdit = PositionEdit(position.x(), units)
        self._yEdit: PositionEdit = PositionEdit(position.y(), units)

        layout = QHBoxLayout()
        layout.addWidget(self._xEdit)
        layout.addWidget(self._yEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self._xEdit.positionChanged.connect(self.sendPositionChanged)
        self._yEdit.positionChanged.connect(self.sendPositionChanged)

    def setPosition(self, position: QPointF) -> None:
        self._xEdit.setPosition(position.x())
        self._yEdit.setPosition(position.y())

    def setUnits(self, units: DrawingUnits) -> None:
        self._xEdit.setUnits(units)
        self._yEdit.setUnits(units)

    def position(self) -> QPointF:
        return QPointF(self._xEdit.position(), self._yEdit.position())

    def units(self) -> DrawingUnits:
        return self._xEdit.units()

    def sendPositionChanged(self) -> None:
        self.positionChanged.emit(self.position())


# ======================================================================================================================

class SizeWidget(QWidget):
    sizeChanged = Signal(QSizeF)

    def __init__(self, size: QSizeF = QSizeF(0, 0), units: DrawingUnits = DrawingUnits.Millimeters) -> None:
        super().__init__()
        self._widthEdit: SizeEdit = SizeEdit(size.width(), units)
        self._heightEdit: SizeEdit = SizeEdit(size.height(), units)

        layout = QHBoxLayout()
        layout.addWidget(self._widthEdit)
        layout.addWidget(self._heightEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self._widthEdit.sizeChanged.connect(self.sendSizeChanged)
        self._heightEdit.sizeChanged.connect(self.sendSizeChanged)

    def setSize(self, size: QSizeF) -> None:
        self._widthEdit.setSize(size.width())
        self._heightEdit.setSize(size.height())

    def setUnits(self, units: DrawingUnits) -> None:
        self._widthEdit.setUnits(units)
        self._heightEdit.setUnits(units)

    def size(self) -> QSizeF:   # type: ignore
        return QSizeF(self._widthEdit.size(), self._heightEdit.size())

    def units(self) -> DrawingUnits:
        return self._widthEdit.units()

    def sendSizeChanged(self) -> None:
        self.sizeChanged.emit(self.size())


# ======================================================================================================================

class ColorWidget(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, color: QColor = QColor(0, 0, 0)) -> None:
        super().__init__()

        self._color: QColor = QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())
        self.setColor(color)

        selectWidget = ColorSelectWidget()
        selectWidgetAction = QWidgetAction(self)
        selectWidgetAction.setDefaultWidget(selectWidget)

        moreColorsButton = QPushButton('More Colors...')
        moreColorsAction = QWidgetAction(self)
        moreColorsAction.setDefaultWidget(moreColorsButton)

        menu = QMenu(self)
        menu.addAction(selectWidgetAction)
        menu.addAction(moreColorsAction)
        self.setMenu(menu)

        selectWidget.colorSelected.connect(menu.hide)
        selectWidget.colorSelected.connect(self.setColor)
        moreColorsButton.clicked.connect(menu.hide)             # type: ignore
        moreColorsButton.clicked.connect(self.runColorDialog)   # type: ignore

    def setColor(self, color: QColor) -> None:
        if (color != self._color):
            self._color = QColor(color)
            if (color.alpha() == 255):
                self.setText(' ' + color.name(QColor.NameFormat.HexRgb).upper())
            else:
                self.setText(' ' + color.name(QColor.NameFormat.HexArgb).upper())
            self.setIcon(self.createIcon(color))
            self.colorChanged.emit(color)

    def color(self) -> QColor:
        return self._color

    def runColorDialog(self) -> None:
        colorDialog = QColorDialog(self)
        colorDialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel |
                               QColorDialog.ColorDialogOption.DontUseNativeDialog)

        for index, color in enumerate(ColorSelectWidget.standardColors):
            QColorDialog.setStandardColor(index, color)
        for index, color in enumerate(ColorSelectWidget.customColors):
            QColorDialog.setCustomColor(index, color)

        colorDialog.setCurrentColor(self._color)

        if (colorDialog.exec() == QColorDialog.DialogCode.Accepted):
            for index, _ in enumerate(ColorSelectWidget.customColors):
                ColorSelectWidget.customColors[index] = QColorDialog.customColor(index)

            self.setColor(colorDialog.currentColor())

    def createIcon(self, color: QColor) -> QIcon:
        if (color.alpha() == 0):
            pixmap = ColorSelectWidget.createTransparentPixmap(QSize(32, 32))
        else:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(color.red(), color.green(), color.blue()))

            with QPainter(pixmap) as painter:
                painter.setPen(QPen(QBrush(Qt.GlobalColor.black), 0))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)

        return QIcon(pixmap)


# ======================================================================================================================

class ColorSelectWidget(QWidget):
    # The native Qt color dialog has 48 standard colors and 16 custom colors
    standardColors: list[QColor] = [
        QColor(255, 128, 128), QColor(255, 0, 0), QColor(128, 64, 64), QColor(128, 0, 0), QColor(64, 0, 0), QColor(0, 0, 0),                    # noqa
        QColor(255, 255, 128), QColor(255, 255, 0), QColor(255, 128, 64), QColor(255, 128, 0), QColor(128, 64, 0), QColor(64, 64, 64),          # noqa
        QColor(128, 255, 128), QColor(128, 255, 0), QColor(0, 255, 0), QColor(0, 128, 0), QColor(0, 64, 0), QColor(128, 128, 128),              # noqa
        QColor(0, 255, 128), QColor(0, 255, 64), QColor(0, 128, 128), QColor(0, 128, 64), QColor(0, 64, 64), QColor(160, 160, 160),             # noqa
        QColor(128, 255, 255), QColor(0, 255, 255), QColor(0, 64, 128), QColor(0, 0, 255), QColor(0, 0, 128), QColor(192, 192, 192),            # noqa
        QColor(0, 128, 255), QColor(0, 128, 192), QColor(128, 128, 255), QColor(0, 0, 160), QColor(0, 0, 164), QColor(224, 224, 224),           # noqa
        QColor(255, 128, 192), QColor(128, 128, 192), QColor(128, 0, 64), QColor(128, 0, 128), QColor(64, 0, 64), QColor(255, 255, 255),        # noqa
        QColor(255, 128, 255), QColor(255, 0, 255), QColor(255, 0, 128), QColor(128, 0, 255), QColor(64, 0, 128), QColor(255, 255, 255, 0)]     # noqa
    customColors: list[QColor] = [QColor(255, 255, 255)] * 16

    colorSelected = Signal(QColor)

    def __init__(self) -> None:
        super().__init__()

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._hoverColor: QColor = QColor()
        self._hoverRect: QRect = QRect()

        # Determine widget layout
        FONT_HEIGHT = QFontMetrics(self.font()).height()
        RECT_SIZE = int(FONT_HEIGHT * 1.25)
        PADDING = int(FONT_HEIGHT / 3)
        NUMBER_OF_COLUMNS = 8
        NUMBER_OF_STANDARD_ROWS = 6
        NUMBER_OF_CUSTOM_ROWS = 2

        self._requiredWidth: int = PADDING + (RECT_SIZE + PADDING) * NUMBER_OF_COLUMNS
        self._requiredHeight: int = (PADDING + FONT_HEIGHT + PADDING + (RECT_SIZE + PADDING) * NUMBER_OF_STANDARD_ROWS +
                                     FONT_HEIGHT + PADDING + (RECT_SIZE + PADDING) * NUMBER_OF_CUSTOM_ROWS)

        self._standardColorsLabelRect: QRect = QRect(PADDING, PADDING, self._requiredWidth - 2 * PADDING, FONT_HEIGHT)
        self._customColorsLabelRect: QRect = QRect(
            PADDING, PADDING + FONT_HEIGHT + PADDING + (RECT_SIZE + PADDING) * NUMBER_OF_STANDARD_ROWS,
            self._requiredWidth - 2 * PADDING, FONT_HEIGHT)

        self._standardColorRects: list[QRect] = []
        left = PADDING
        top = self._standardColorsLabelRect.bottom() + PADDING
        for columnIndex in range(NUMBER_OF_COLUMNS):
            for rowIndex in range(NUMBER_OF_STANDARD_ROWS):
                self._standardColorRects.append(QRect(
                    left + (RECT_SIZE + PADDING) * columnIndex, top + (RECT_SIZE + PADDING) * rowIndex,
                    RECT_SIZE, RECT_SIZE))

        self._customColorRects: list[QRect] = []
        left = PADDING
        top = self._customColorsLabelRect.bottom() + PADDING
        for columnIndex in range(NUMBER_OF_COLUMNS):
            for rowIndex in range(NUMBER_OF_CUSTOM_ROWS):
                self._customColorRects.append(QRect(
                    left + (RECT_SIZE + PADDING) * columnIndex, top + (RECT_SIZE + PADDING) * rowIndex,
                    RECT_SIZE, RECT_SIZE))

    def sizeHint(self) -> QSize:
        return QSize(self._requiredWidth, self._requiredHeight)

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self) as painter:
            # Draw section labels
            font = self.font()
            font.setUnderline(True)
            textAlignment = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QBrush(Qt.GlobalColor.black), 0))
            painter.setFont(font)
            painter.drawText(self._standardColorsLabelRect, textAlignment, 'Standard Colors')
            painter.drawText(self._customColorsLabelRect, textAlignment, 'Custom Colors')

            # Draw color items
            for index, rect in enumerate(self._standardColorRects):
                self.drawColorItem(painter, ColorSelectWidget.standardColors[index], rect)
            for index, rect in enumerate(self._customColorRects):
                self.drawColorItem(painter, ColorSelectWidget.customColors[index], rect)

            # Draw hover rect
            if (self._hoverRect.isValid()):
                painter.setPen(QPen(QBrush(QColor(197, 197, 197)), 0))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(self._hoverRect.adjusted(0, 0, -1, -1))
                painter.drawRect(self._hoverRect.adjusted(1, 1, -2, -2))

    def drawColorItem(self, painter: QPainter, color: QColor, rect: QRect) -> None:
        if (color.alpha() == 0):
            painter.drawPixmap(rect, ColorSelectWidget.createTransparentPixmap(rect.size()))
        else:
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue())))
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        foundItem = False
        self._hoverRect = QRect()
        for index, rect in enumerate(self._standardColorRects):
            if (not foundItem and rect.contains(event.pos())):
                self._hoverColor = ColorSelectWidget.standardColors[index]
                self._hoverRect = rect
                foundItem = True
        for index, rect in enumerate(self._customColorRects):
            if (not foundItem and rect.contains(event.pos())):
                self._hoverColor = ColorSelectWidget.customColors[index]
                self._hoverRect = rect
                foundItem = True
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (self._hoverRect.isValid()):
            self.colorSelected.emit(self._hoverColor)

    # ==================================================================================================================

    @staticmethod
    def createTransparentPixmap(size: QSize) -> QPixmap:
        RECT_SIZE = 3

        pixmap = QPixmap(size)
        pixmap.fill(QColor(255, 255, 255))

        with QPainter(pixmap) as painter:
            # Draw checkerboard pattern
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(170, 170, 170)))
            for y in range(1, size.height(), 2 * RECT_SIZE):
                for x in range(1, size.width(), 2 * RECT_SIZE):
                    painter.drawRect(x, y, RECT_SIZE, RECT_SIZE)
                    painter.drawRect(x + RECT_SIZE, y + RECT_SIZE, RECT_SIZE, RECT_SIZE)

            # Draw border
            painter.setPen(QPen(QBrush(Qt.GlobalColor.black), 0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(0, 0, size.width() - 1, size.height() - 1)

        return pixmap
