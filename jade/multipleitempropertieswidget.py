# multipleitempropertieswidget.py
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
from PyQt6.QtCore import pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QColor, QFontMetrics, QIcon
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGroupBox, QVBoxLayout, QWidget
from .drawingitem import DrawingItem
from .drawingtypes import DrawingUnits
from .helperwidgets import ColorWidget, SizeEdit


class MultipleItemPropertiesWidget(QWidget):
    itemsMovedDelta = pyqtSignal(QPointF)
    itemsPropertyChanged = pyqtSignal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._items: list[DrawingItem] = []

        self._labelWidth = QFontMetrics(self.font()).boundingRect("Minor Grid Spacing:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createRectGroup())
        layout.addWidget(self._createPenBrushGroup())
        layout.addWidget(self._createArrowGroup())
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    # ==================================================================================================================

    def _createRectGroup(self) -> QGroupBox:
        self._rectCornerRadiusEdit: SizeEdit = SizeEdit()
        self._rectCornerRadiusEdit.sizeChanged.connect(self._handleRectCornerRadiusChange)
        self._rectCornerRadiusCheck: QCheckBox = QCheckBox('Corner Radius:')
        self._rectCornerRadiusCheck.clicked.connect(self._handleRectCornerRadiusCheckClicked)   # type: ignore

        self._rectGroup: QGroupBox = QGroupBox('Rect')
        self._rectLayout: QFormLayout = QFormLayout()
        self._rectLayout.addRow(self._rectCornerRadiusCheck, self._rectCornerRadiusEdit)
        self._rectLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._rectLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._rectLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._rectLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._rectGroup.setLayout(self._rectLayout)

        return self._rectGroup

    def _createPenBrushGroup(self) -> QGroupBox:
        self._penStyleCombo: QComboBox = QComboBox()
        self._penStyleCombo.addItems(['None', 'Solid', 'Dashed', 'Dotted', 'Dash-Dotted', 'Dash-Dot-Dotted'])
        self._penStyleCombo.activated.connect(self._handlePenStyleChange)           # type: ignore
        self._penStyleCheck: QCheckBox = QCheckBox('Pen Style:')
        self._penStyleCheck.clicked.connect(self._handlePenStyleCheckClicked)       # type: ignore

        self._penWidthEdit: SizeEdit = SizeEdit()
        self._penWidthEdit.sizeChanged.connect(self._handlePenWidthChange)
        self._penWidthCheck: QCheckBox = QCheckBox('Pen Width:')
        self._penWidthCheck.clicked.connect(self._handlePenWidthCheckClicked)       # type: ignore

        self._penColorWidget: ColorWidget = ColorWidget()
        self._penColorWidget.colorChanged.connect(self._handlePenColorChange)
        self._penColorCheck: QCheckBox = QCheckBox('Pen Color:')
        self._penColorCheck.clicked.connect(self._handlePenColorCheckClicked)       # type: ignore

        self._brushColorWidget: ColorWidget = ColorWidget()
        self._brushColorWidget.colorChanged.connect(self._handleBrushColorChange)
        self._brushColorCheck: QCheckBox = QCheckBox('Brush Color:')
        self._brushColorCheck.clicked.connect(self._handleBrushColorCheckClicked)   # type: ignore

        self._penBrushGroup: QGroupBox = QGroupBox('Pen / Brush')
        self._penBrushLayout: QFormLayout = QFormLayout()
        self._penBrushLayout.addRow(self._penStyleCheck, self._penStyleCombo)
        self._penBrushLayout.addRow(self._penWidthCheck, self._penWidthEdit)
        self._penBrushLayout.addRow(self._penColorCheck, self._penColorWidget)
        self._penBrushLayout.addRow(self._brushColorCheck, self._brushColorWidget)
        self._penBrushLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._penBrushLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._penBrushLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._penBrushLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._penBrushGroup.setLayout(self._penBrushLayout)

        return self._penBrushGroup

    def _createArrowGroup(self) -> QGroupBox:
        self._startArrowStyleCombo: QComboBox = QComboBox()
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-none.png'), 'None')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-normal.png'), 'Normal')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-triangle.png'), 'Triangle')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-triangle-filled.png'), 'Triangle Filled')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-concave.png'), 'Concave')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-concave-filled.png'), 'Concave Filled')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-circle.png'), 'Circle')
        self._startArrowStyleCombo.addItem(QIcon('icons:arrow/arrow-circle-filled.png'), 'Circle Filled')
        self._startArrowStyleCombo.activated.connect(self._handleStartArrowStyleChange)         # type: ignore
        self._startArrowStyleCheck: QCheckBox = QCheckBox('Start Arrow Style:')
        self._startArrowStyleCheck.clicked.connect(self._handleStartArrowStyleCheckClicked)     # type: ignore

        self._startArrowSizeEdit: SizeEdit = SizeEdit()
        self._startArrowSizeEdit.sizeChanged.connect(self._handleStartArrowSizeChange)
        self._startArrowSizeCheck: QCheckBox = QCheckBox('Start Arrow Size:')
        self._startArrowSizeCheck.clicked.connect(self._handleStartArrowSizeCheckClicked)       # type: ignore

        self._endArrowStyleCombo: QComboBox = QComboBox()
        for index in range(self._startArrowStyleCombo.count()):
            self._endArrowStyleCombo.addItem(self._startArrowStyleCombo.itemIcon(index),
                                             self._startArrowStyleCombo.itemText(index))
        self._endArrowStyleCombo.activated.connect(self._handleEndArrowStyleChange)         # type: ignore
        self._endArrowStyleCheck: QCheckBox = QCheckBox('End Arrow Style:')
        self._endArrowStyleCheck.clicked.connect(self._handleEndArrowStyleCheckClicked)     # type: ignore

        self._endArrowSizeEdit: SizeEdit = SizeEdit()
        self._endArrowSizeEdit.sizeChanged.connect(self._handleEndArrowSizeChange)
        self._endArrowSizeCheck: QCheckBox = QCheckBox('End Arrow Size:')
        self._endArrowSizeCheck.clicked.connect(self._handleEndArrowSizeCheckClicked)       # type: ignore

        self._arrowGroup: QGroupBox = QGroupBox('Arrow')
        self._arrowLayout: QFormLayout = QFormLayout()
        self._arrowLayout.addRow(self._startArrowStyleCheck, self._startArrowStyleCombo)
        self._arrowLayout.addRow(self._startArrowSizeCheck, self._startArrowSizeEdit)
        self._arrowLayout.addRow(self._endArrowStyleCheck, self._endArrowStyleCombo)
        self._arrowLayout.addRow(self._endArrowSizeCheck, self._endArrowSizeEdit)
        self._arrowLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._arrowLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._arrowLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._arrowLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._arrowGroup.setLayout(self._arrowLayout)

        return self._arrowGroup

    # ==================================================================================================================

    def setDrawingProperty(self, name: str, value: typing.Any) -> None:
        self.blockSignals(True)
        if (name == 'units' and isinstance(value, DrawingUnits)):
            self._rectCornerRadiusEdit.setUnits(value)
            self._penWidthEdit.setUnits(value)
            self._startArrowSizeEdit.setUnits(value)
            self._endArrowSizeEdit.setUnits(value)
        self.blockSignals(False)

    # ==================================================================================================================

    def setItems(self, items: list[DrawingItem]) -> None:
        self._items = items
        self.blockSignals(True)
        self._updateRectGroup()
        self._updatePenBrushGroup()
        self._updateArrowGroup()
        self.blockSignals(False)

    def _updateRectGroup(self) -> None:
        (cornerRadius, cornerRadiusMatches) = self._checkForProperty('cornerRadius')

        showRectGroup = isinstance(cornerRadius, float)
        self._rectGroup.setVisible(showRectGroup)

        if (showRectGroup):
            self._rectCornerRadiusEdit.setSize(cornerRadius)
            self._rectCornerRadiusEdit.setEnabled(cornerRadiusMatches)
            self._rectCornerRadiusCheck.setChecked(cornerRadiusMatches)

    def _updatePenBrushGroup(self) -> None:
        (penStyle, penStylesMatch) = self._checkForProperty('penStyle')
        (penWidth, penWidthsMatch) = self._checkForProperty('penWidth')
        (penColor, penColorsMatch) = self._checkForProperty('penColor')
        (brushColor, brushColorsMatch) = self._checkForProperty('brushColor')

        showPenBrushGroup = (isinstance(penStyle, int) or isinstance(penWidth, float) or isinstance(penColor, QColor) or
                             isinstance(brushColor, QColor))
        self._penBrushGroup.setVisible(showPenBrushGroup)

        if (showPenBrushGroup):
            # Pen style
            if (isinstance(penStyle, int)):
                self._penBrushLayout.setRowVisible(self._penStyleCombo, True)
                self._penStyleCombo.setCurrentIndex(penStyle)
                self._penStyleCombo.setEnabled(penStylesMatch)
                self._penStyleCheck.setChecked(penStylesMatch)
            else:
                self._penBrushLayout.setRowVisible(self._penStyleCombo, False)

            # Pen width
            if (isinstance(penWidth, float)):
                self._penBrushLayout.setRowVisible(self._penWidthEdit, True)
                self._penWidthEdit.setSize(penWidth)
                self._penWidthEdit.setEnabled(penWidthsMatch)
                self._penWidthCheck.setChecked(penWidthsMatch)
            else:
                self._penBrushLayout.setRowVisible(self._penWidthEdit, False)

            # Pen color
            if (isinstance(penColor, QColor)):
                self._penBrushLayout.setRowVisible(self._penColorWidget, True)
                self._penColorWidget.setColor(penColor)
                self._penColorWidget.setEnabled(penColorsMatch)
                self._penColorCheck.setChecked(penColorsMatch)
            else:
                self._penBrushLayout.setRowVisible(self._penColorWidget, False)

            # Brush color
            if (isinstance(brushColor, QColor)):
                self._penBrushLayout.setRowVisible(self._brushColorWidget, True)
                self._brushColorWidget.setColor(brushColor)
                self._brushColorWidget.setEnabled(brushColorsMatch)
                self._brushColorCheck.setChecked(brushColorsMatch)
            else:
                self._penBrushLayout.setRowVisible(self._brushColorWidget, False)

    def _updateArrowGroup(self) -> None:
        (startArrowStyle, startArrowStylesMatch) = self._checkForProperty('startArrowStyle')
        (startArrowSize, startArrowSizesMatch) = self._checkForProperty('startArrowSize')
        (endArrowStyle, endArrowStylesMatch) = self._checkForProperty('endArrowStyle')
        (endArrowSize, endArrowSizesMatch) = self._checkForProperty('endArrowSize')

        showArrowGroup = (isinstance(startArrowStyle, int) or isinstance(startArrowSize, float) or
                          isinstance(endArrowStyle, int) or isinstance(endArrowSize, float))
        self._arrowGroup.setVisible(showArrowGroup)

        if (showArrowGroup):
            # Start arrow style
            if (isinstance(startArrowStyle, int)):
                self._arrowLayout.setRowVisible(self._startArrowStyleCombo, True)
                self._startArrowStyleCombo.setCurrentIndex(startArrowStyle)
                self._startArrowStyleCombo.setEnabled(startArrowStylesMatch)
                self._startArrowStyleCheck.setChecked(startArrowStylesMatch)
            else:
                self._arrowLayout.setRowVisible(self._startArrowStyleCombo, False)

            # Start arrow size
            if (isinstance(startArrowSize, float)):
                self._arrowLayout.setRowVisible(self._startArrowSizeEdit, True)
                self._startArrowSizeEdit.setSize(startArrowSize)
                self._startArrowSizeEdit.setEnabled(startArrowSizesMatch)
                self._startArrowSizeCheck.setChecked(startArrowSizesMatch)
            else:
                self._arrowLayout.setRowVisible(self._startArrowSizeEdit, False)

            # End arrow style
            if (isinstance(endArrowStyle, int)):
                self._arrowLayout.setRowVisible(self._endArrowStyleCombo, True)
                self._endArrowStyleCombo.setCurrentIndex(endArrowStyle)
                self._endArrowStyleCombo.setEnabled(endArrowStylesMatch)
                self._endArrowStyleCheck.setChecked(endArrowStylesMatch)
            else:
                self._arrowLayout.setRowVisible(self._endArrowStyleCombo, False)

            # End arrow size
            if (isinstance(endArrowSize, float)):
                self._arrowLayout.setRowVisible(self._endArrowSizeEdit, True)
                self._endArrowSizeEdit.setSize(endArrowSize)
                self._endArrowSizeEdit.setEnabled(endArrowSizesMatch)
                self._endArrowSizeCheck.setChecked(endArrowSizesMatch)
            else:
                self._arrowLayout.setRowVisible(self._endArrowSizeEdit, False)

    def _checkForProperty(self, name: str) -> tuple[typing.Any, bool]:
        propertyValue, propertyValuesMatch = (None, False)

        # Check whether any item in items has the specified property
        for item in self._items:
            propertyValue = item.property(name)
            if (propertyValue is not None):
                break

        # Check whether all items that have the property have the same value
        if (propertyValue is not None):
            propertyValuesMatch = True
            for item in self._items:
                compareValue = item.property(name)
                if (compareValue is not None):
                    propertyValuesMatch = (propertyValue == compareValue)
                    if (not propertyValuesMatch):
                        break

        return (propertyValue, propertyValuesMatch)

    # ==================================================================================================================

    def _handleRectCornerRadiusChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('cornerRadius', size)

    def _handleRectCornerRadiusCheckClicked(self, checked: bool) -> None:
        self._rectCornerRadiusEdit.setEnabled(checked)
        if (checked):
            self._handleRectCornerRadiusChange(self._rectCornerRadiusEdit.size())

    # ==================================================================================================================

    def _handlePenStyleChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('penStyle', index)

    def _handlePenWidthChange(self, width: float) -> None:
        self.itemsPropertyChanged.emit('penWidth', width)

    def _handlePenColorChange(self, color: QColor) -> None:
        self.itemsPropertyChanged.emit('penColor', color)

    def _handleBrushColorChange(self, color: QColor) -> None:
        self.itemsPropertyChanged.emit('brushColor', color)

    def _handlePenStyleCheckClicked(self, checked: bool) -> None:
        self._penStyleCombo.setEnabled(checked)
        if (checked):
            self._handlePenStyleChange(self._penStyleCombo.currentIndex())

    def _handlePenWidthCheckClicked(self, checked: bool) -> None:
        self._penWidthEdit.setEnabled(checked)
        if (checked):
            self._handlePenWidthChange(self._penWidthEdit.size())

    def _handlePenColorCheckClicked(self, checked: bool) -> None:
        self._penColorWidget.setEnabled(checked)
        if (checked):
            self._handlePenColorChange(self._penColorWidget.color())

    def _handleBrushColorCheckClicked(self, checked: bool) -> None:
        self._brushColorWidget.setEnabled(checked)
        if (checked):
            self._handleBrushColorChange(self._brushColorWidget.color())

    # ==================================================================================================================

    def _handleStartArrowStyleChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('startArrowStyle', index)

    def _handleStartArrowSizeChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('startArrowSize', size)

    def _handleEndArrowStyleChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('endArrowStyle', index)

    def _handleEndArrowSizeChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('endArrowSize', size)

    def _handleStartArrowStyleCheckClicked(self, checked: bool) -> None:
        self._startArrowStyleCombo.setEnabled(checked)
        if (checked):
            self._handleStartArrowStyleChange(self._startArrowStyleCombo.currentIndex())

    def _handleStartArrowSizeCheckClicked(self, checked: bool) -> None:
        self._startArrowSizeEdit.setEnabled(checked)
        if (checked):
            self._handleStartArrowSizeChange(self._startArrowSizeEdit.size())

    def _handleEndArrowStyleCheckClicked(self, checked: bool) -> None:
        self._endArrowStyleCombo.setEnabled(checked)
        if (checked):
            self._handleEndArrowStyleChange(self._endArrowStyleCombo.currentIndex())

    def _handleEndArrowSizeCheckClicked(self, checked: bool) -> None:
        self._endArrowSizeEdit.setEnabled(checked)
        if (checked):
            self._handleEndArrowSizeChange(self._endArrowSizeEdit.size())
