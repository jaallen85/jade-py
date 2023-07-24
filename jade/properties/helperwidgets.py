# helperwidgets.py
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

import re
from PySide6.QtCore import Qt, QPointF, QRect, QSize, QSizeF, Signal
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QIcon, QMouseEvent, QPaintEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QColorDialog, QComboBox, QHBoxLayout, QMenu, QLineEdit, QPushButton, QSizePolicy,
                               QWidget, QWidgetAction)
from ..odg.odgunits import OdgUnits


class UnitsCombo(QComboBox):
    unitsChanged = Signal(OdgUnits)

    def __init__(self, units: OdgUnits = OdgUnits.Millimeters) -> None:
        super().__init__()
        self._units: OdgUnits = units
        self.addItems(['Millimeters', 'Inches'])
        self.setCurrentIndex(units)
        self.currentIndexChanged.connect(self._handleUnitsChange)

    def setUnits(self, units: OdgUnits) -> None:
        self.setCurrentIndex(units)     # Will call _handleUnitsChange if and only if units.value != self.currentIndex()

    def units(self) -> OdgUnits:
        return self._units

    def _handleUnitsChange(self, index: int) -> None:
        self._units = OdgUnits(index)
        self.unitsChanged.emit(self._units)


# ======================================================================================================================

class LengthEdit(QLineEdit):
    lengthChanged = Signal(float)

    def __init__(self, length: float = 0, units: OdgUnits = OdgUnits.Millimeters,
                 lengthMustBeNonNegative: bool = False) -> None:
        super().__init__()
        self._length: float = 0 if (lengthMustBeNonNegative and length < 0) else length
        self._units: OdgUnits = units
        self._lengthMustBeNonNegative: bool = lengthMustBeNonNegative
        self._updateText()
        self.editingFinished.connect(self._handleEditingFinished)    # type: ignore

    def setLength(self, length: float) -> None:
        if (not (self._lengthMustBeNonNegative and length < 0)):
            lengthChanged = (self._length != length)
            self._length = length
            self._updateText()
            if (lengthChanged):
                self.lengthChanged.emit(self._length)
        else:
            self.setText(self._cachedText)

    def setUnits(self, units: OdgUnits) -> None:
        self._length = OdgUnits.convert(self._length, self._units, units)
        self._units = units
        self._updateText()

    def length(self) -> float:
        return self._length

    def units(self) -> OdgUnits:
        return self._units

    def _handleEditingFinished(self) -> None:
        text = self.text()
        pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
        match = re.match(pattern, text, re.VERBOSE)
        if (match is not None):
            try:
                length = float(match.group(0))
                unitsStr = text[match.end():].strip()
                if (unitsStr == ''):
                    # Assume the value provided is in the same units as self._units
                    self.setLength(length)
                    self.blockSignals(True)
                    self.clearFocus()
                    self.blockSignals(False)
                else:
                    # Try to convert the provided value to the same units as self._units; fail if unrecognized units
                    # are provided
                    try:
                        units = OdgUnits.fromStr(unitsStr)
                        self.setLength(OdgUnits.convert(length, units, self._units))
                        self.blockSignals(True)
                        self.clearFocus()
                        self.blockSignals(False)
                    except ValueError:
                        self.setText(self._cachedText)
            except ValueError:
                self.setText(self._cachedText)
        else:
            self.setText(self._cachedText)

    def _updateText(self) -> None:
        if (isinstance(self._length, int) or self._length.is_integer()):
            self._cachedText = f'{int(self._length)} {self._units}'
        else:
            self._cachedText = f'{self._length:.8g} {self._units}'
        self.setText(self._cachedText)


# ======================================================================================================================

class PositionWidget(QWidget):
    positionChanged = Signal(QPointF)

    def __init__(self, position: QPointF = QPointF(0, 0), units: OdgUnits = OdgUnits.Millimeters) -> None:
        super().__init__()
        self._xEdit: LengthEdit = LengthEdit(position.x(), units, lengthMustBeNonNegative=False)
        self._yEdit: LengthEdit = LengthEdit(position.y(), units, lengthMustBeNonNegative=False)

        layout = QHBoxLayout()
        layout.addWidget(self._xEdit)
        layout.addWidget(self._yEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self._xEdit.lengthChanged.connect(self._sendPositionChanged)
        self._yEdit.lengthChanged.connect(self._sendPositionChanged)

    def setPosition(self, position: QPointF) -> None:
        self._xEdit.setLength(position.x())
        self._yEdit.setLength(position.y())

    def setUnits(self, units: OdgUnits) -> None:
        self._xEdit.setUnits(units)
        self._yEdit.setUnits(units)

    def position(self) -> QPointF:
        return QPointF(self._xEdit.length(), self._yEdit.length())

    def units(self) -> OdgUnits:
        return self._xEdit.units()

    def _sendPositionChanged(self) -> None:
        self.positionChanged.emit(self.position())


# ======================================================================================================================

class SizeWidget(QWidget):
    sizeChanged = Signal(QSizeF)

    def __init__(self, size: QSizeF = QSizeF(0, 0), units: OdgUnits = OdgUnits.Millimeters,
                 sizeMustBeNonNegative: bool = False) -> None:
        super().__init__()
        self._widthEdit: LengthEdit = LengthEdit(size.width(), units, sizeMustBeNonNegative)
        self._heightEdit: LengthEdit = LengthEdit(size.height(), units, sizeMustBeNonNegative)

        layout = QHBoxLayout()
        layout.addWidget(self._widthEdit)
        layout.addWidget(self._heightEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self._widthEdit.lengthChanged.connect(self._sendSizeChanged)
        self._heightEdit.lengthChanged.connect(self._sendSizeChanged)

    def setSize(self, size: QSizeF) -> None:
        self._widthEdit.setLength(size.width())
        self._heightEdit.setLength(size.height())

    def setUnits(self, units: OdgUnits) -> None:
        self._widthEdit.setUnits(units)
        self._heightEdit.setUnits(units)

    def size(self) -> QSizeF:       # type: ignore
        return QSizeF(self._widthEdit.length(), self._heightEdit.length())

    def units(self) -> OdgUnits:
        return self._widthEdit.units()

    def _sendSizeChanged(self) -> None:
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
            if (self._hoverRect.width() > 0 and self._hoverRect.height() > 0):
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
        if (self._hoverRect.width() > 0 and self._hoverRect.height() > 0):
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
