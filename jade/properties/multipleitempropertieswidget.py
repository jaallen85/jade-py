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
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFontComboBox, QFormLayout, QFrame, QGroupBox, QHBoxLayout,
                               QToolButton, QVBoxLayout, QWidget)
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingunits import DrawingUnits
from .helperwidgets import ColorWidget, SizeEdit


class MultipleItemPropertiesWidget(QWidget):
    itemsMovedDelta = Signal(QPointF)
    itemsPropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._items: list[DrawingItem] = []

        self._labelWidth = QFontMetrics(self.font()).boundingRect("Minor Grid Spacing:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createRectGroup())
        layout.addWidget(self._createPenBrushGroup())
        layout.addWidget(self._createArrowGroup())
        layout.addWidget(self._createTextGroup())
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
        self._endArrowStyleCombo.activated.connect(self._handleEndArrowStyleChange)             # type: ignore
        self._endArrowStyleCheck: QCheckBox = QCheckBox('End Arrow Style:')
        self._endArrowStyleCheck.clicked.connect(self._handleEndArrowStyleCheckClicked)         # type: ignore

        self._endArrowSizeEdit: SizeEdit = SizeEdit()
        self._endArrowSizeEdit.sizeChanged.connect(self._handleEndArrowSizeChange)
        self._endArrowSizeCheck: QCheckBox = QCheckBox('End Arrow Size:')
        self._endArrowSizeCheck.clicked.connect(self._handleEndArrowSizeCheckClicked)           # type: ignore

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

    def _createTextGroup(self) -> QGroupBox:
        self._fontFamilyCombo: QFontComboBox = QFontComboBox()
        self._fontFamilyCombo.setMaximumWidth(182)
        self._fontFamilyCombo.activated.connect(self._handleFontFamilyChange)       # type: ignore
        self._fontFamilyCheck: QCheckBox = QCheckBox('Font:')
        self._fontFamilyCheck.clicked.connect(self._handleFontFamilyCheckClicked)   # type: ignore

        self._fontSizeEdit: SizeEdit = SizeEdit()
        self._fontSizeEdit.sizeChanged.connect(self._handleFontSizeChange)
        self._fontSizeCheck: QCheckBox = QCheckBox('Font Size:')
        self._fontSizeCheck.clicked.connect(self._handleFontSizeCheckClicked)       # type: ignore

        self._fontBoldButton: QToolButton = QToolButton()
        self._fontBoldButton.setIcon(QIcon('icons:format-text-bold.png'))
        self._fontBoldButton.setToolTip('Bold')
        self._fontBoldButton.setCheckable(True)
        self._fontBoldButton.clicked.connect(self._handleFontStyleChange)           # type: ignore

        self._fontItalicButton: QToolButton = QToolButton()
        self._fontItalicButton.setIcon(QIcon('icons:format-text-italic.png'))
        self._fontItalicButton.setToolTip('Italic')
        self._fontItalicButton.setCheckable(True)
        self._fontItalicButton.clicked.connect(self._handleFontStyleChange)         # type: ignore

        self._fontUnderlineButton: QToolButton = QToolButton()
        self._fontUnderlineButton.setIcon(QIcon('icons:format-text-underline.png'))
        self._fontUnderlineButton.setToolTip('Underline')
        self._fontUnderlineButton.setCheckable(True)
        self._fontUnderlineButton.clicked.connect(self._handleFontStyleChange)      # type: ignore

        self._fontStrikeOutButton: QToolButton = QToolButton()
        self._fontStrikeOutButton.setIcon(QIcon('icons:format-text-strikethrough.png'))
        self._fontStrikeOutButton.setToolTip('Strike-Through')
        self._fontStrikeOutButton.setCheckable(True)
        self._fontStrikeOutButton.clicked.connect(self._handleFontStyleChange)      # type: ignore

        self._fontStyleCheck: QCheckBox = QCheckBox('Font Style:')
        self._fontStyleCheck.clicked.connect(self._handleFontStyleCheckClicked)     # type: ignore

        self._textAlignmentLeftButton: QToolButton = QToolButton()
        self._textAlignmentLeftButton.setIcon(QIcon('icons:align-horizontal-left.png'))
        self._textAlignmentLeftButton.setToolTip('Align Left')
        self._textAlignmentLeftButton.setCheckable(True)
        self._textAlignmentLeftButton.setAutoExclusive(True)
        self._textAlignmentLeftButton.clicked.connect(self._handleTextAlignmentChange)      # type: ignore

        self._textAlignmentHCenterButton: QToolButton = QToolButton()
        self._textAlignmentHCenterButton.setIcon(QIcon('icons:align-horizontal-center.png'))
        self._textAlignmentHCenterButton.setToolTip('Align Center')
        self._textAlignmentHCenterButton.setCheckable(True)
        self._textAlignmentHCenterButton.setAutoExclusive(True)
        self._textAlignmentHCenterButton.clicked.connect(self._handleTextAlignmentChange)   # type: ignore

        self._textAlignmentRightButton: QToolButton = QToolButton()
        self._textAlignmentRightButton.setIcon(QIcon('icons:align-horizontal-right.png'))
        self._textAlignmentRightButton.setToolTip('Align Right')
        self._textAlignmentRightButton.setCheckable(True)
        self._textAlignmentRightButton.setAutoExclusive(True)
        self._textAlignmentRightButton.clicked.connect(self._handleTextAlignmentChange)     # type: ignore

        self._textAlignmentTopButton: QToolButton = QToolButton()
        self._textAlignmentTopButton.setIcon(QIcon('icons:align-vertical-top.png'))
        self._textAlignmentTopButton.setToolTip('Align Top')
        self._textAlignmentTopButton.setCheckable(True)
        self._textAlignmentTopButton.setAutoExclusive(True)
        self._textAlignmentTopButton.clicked.connect(self._handleTextAlignmentChange)       # type: ignore

        self._textAlignmentVCenterButton: QToolButton = QToolButton()
        self._textAlignmentVCenterButton.setIcon(QIcon('icons:align-vertical-center.png'))
        self._textAlignmentVCenterButton.setToolTip('Align Center')
        self._textAlignmentVCenterButton.setCheckable(True)
        self._textAlignmentVCenterButton.setAutoExclusive(True)
        self._textAlignmentVCenterButton.clicked.connect(self._handleTextAlignmentChange)   # type: ignore

        self._textAlignmentBottomButton: QToolButton = QToolButton()
        self._textAlignmentBottomButton.setIcon(QIcon('icons:align-vertical-right.png'))
        self._textAlignmentBottomButton.setToolTip('Align Bottom')
        self._textAlignmentBottomButton.setCheckable(True)
        self._textAlignmentBottomButton.setAutoExclusive(True)
        self._textAlignmentBottomButton.clicked.connect(self._handleTextAlignmentChange)    # type: ignore

        self._textAlignmentCheck: QCheckBox = QCheckBox('Text Alignment:')
        self._textAlignmentCheck.clicked.connect(self._handleTextAlignmentCheckClicked)     # type: ignore

        self._textColorWidget: ColorWidget = ColorWidget()
        self._textColorWidget.colorChanged.connect(self._handleTextColorChange)
        self._textColorCheck: QCheckBox = QCheckBox('Text Color:')
        self._textColorCheck.clicked.connect(self._handleTextColorCheckClicked)             # type: ignore

        self._fontStyleWidget = QWidget()
        self._fontStyleLayout = QHBoxLayout()
        self._fontStyleLayout.addWidget(self._fontBoldButton)
        self._fontStyleLayout.addWidget(self._fontItalicButton)
        self._fontStyleLayout.addWidget(self._fontUnderlineButton)
        self._fontStyleLayout.addWidget(self._fontStrikeOutButton)
        self._fontStyleLayout.addWidget(QWidget(), 100)
        self._fontStyleLayout.setSpacing(2)
        self._fontStyleLayout.setContentsMargins(0, 0, 0, 0)
        self._fontStyleWidget.setLayout(self._fontStyleLayout)

        textAlignmentHorizontalWidget = QWidget()
        textAlignmentHorizontalLayout = QHBoxLayout()
        textAlignmentHorizontalLayout.addWidget(self._textAlignmentLeftButton)
        textAlignmentHorizontalLayout.addWidget(self._textAlignmentHCenterButton)
        textAlignmentHorizontalLayout.addWidget(self._textAlignmentRightButton)
        textAlignmentHorizontalLayout.setSpacing(2)
        textAlignmentHorizontalLayout.setContentsMargins(0, 0, 0, 0)
        textAlignmentHorizontalWidget.setLayout(textAlignmentHorizontalLayout)

        textAlignmentVerticalWidget = QWidget()
        textAlignmentVerticalLayout = QHBoxLayout()
        textAlignmentVerticalLayout.addWidget(self._textAlignmentTopButton)
        textAlignmentVerticalLayout.addWidget(self._textAlignmentVCenterButton)
        textAlignmentVerticalLayout.addWidget(self._textAlignmentBottomButton)
        textAlignmentVerticalLayout.setSpacing(2)
        textAlignmentVerticalLayout.setContentsMargins(0, 0, 0, 0)
        textAlignmentVerticalWidget.setLayout(textAlignmentVerticalLayout)

        textAlignmentSeparator = QFrame()
        textAlignmentSeparator.setFrameStyle(QFrame.Shape.VLine | QFrame.Shadow.Raised)

        self._textAlignmentWidget = QWidget()
        self._textAlignmentLayout = QHBoxLayout()
        self._textAlignmentLayout.addWidget(textAlignmentHorizontalWidget)
        self._textAlignmentLayout.addWidget(textAlignmentSeparator)
        self._textAlignmentLayout.addWidget(textAlignmentVerticalWidget)
        self._textAlignmentLayout.addWidget(QWidget(), 100)
        self._textAlignmentLayout.setSpacing(2)
        self._textAlignmentLayout.setContentsMargins(0, 0, 0, 0)
        self._textAlignmentWidget.setLayout(self._textAlignmentLayout)

        self._textGroup: QGroupBox = QGroupBox('Text')
        self._textLayout: QFormLayout = QFormLayout()
        self._textLayout.addRow(self._fontFamilyCheck, self._fontFamilyCombo)
        self._textLayout.addRow(self._fontSizeCheck, self._fontSizeEdit)
        self._textLayout.addRow(self._fontStyleCheck, self._fontStyleWidget)
        self._textLayout.addRow(self._textAlignmentCheck, self._textAlignmentWidget)
        self._textLayout.addRow(self._textColorCheck, self._textColorWidget)
        self._textLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._textLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._textLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._textLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._textGroup.setLayout(self._textLayout)

        return self._textGroup

    # ==================================================================================================================

    def setUnits(self, units: DrawingUnits) -> None:
        self.blockSignals(True)
        self._rectCornerRadiusEdit.setUnits(units)
        self._penWidthEdit.setUnits(units)
        self._startArrowSizeEdit.setUnits(units)
        self._endArrowSizeEdit.setUnits(units)
        self._fontSizeEdit.setUnits(units)
        self.blockSignals(False)

    # ==================================================================================================================

    def setItems(self, items: list[DrawingItem]) -> None:
        self._items = items
        self.blockSignals(True)
        self._updateRectGroup()
        self._updatePenBrushGroup()
        self._updateArrowGroup()
        self._updateTextGroup()
        self.blockSignals(False)

    def _updateRectGroup(self) -> None:
        (cornerRadius, cornerRadiusMatches) = self._checkForProperty('cornerRadius')

        # Corner radius
        showRectGroup = False
        if (isinstance(cornerRadius, float)):
            showRectGroup = True
            self._rectCornerRadiusEdit.setSize(cornerRadius)
            self._rectCornerRadiusEdit.setEnabled(cornerRadiusMatches)
            self._rectCornerRadiusCheck.setChecked(cornerRadiusMatches)

        # Set rect group visiblity
        self._rectGroup.setVisible(showRectGroup)

    def _updatePenBrushGroup(self) -> None:
        (penStyle, penStylesMatch) = self._checkForProperty('penStyle')
        (penWidth, penWidthsMatch) = self._checkForProperty('penWidth')
        (penColor, penColorsMatch) = self._checkForProperty('penColor')
        (brushColor, brushColorsMatch) = self._checkForProperty('brushColor')

        # Pen style
        showPenStyle = False
        if (isinstance(penStyle, int)):
            showPenStyle = True
            self._penStyleCombo.setCurrentIndex(penStyle)
            self._penStyleCombo.setEnabled(penStylesMatch)
            self._penStyleCheck.setChecked(penStylesMatch)

        # Pen width
        showPenWidth = False
        if (isinstance(penWidth, float)):
            showPenWidth = True
            self._penWidthEdit.setSize(penWidth)
            self._penWidthEdit.setEnabled(penWidthsMatch)
            self._penWidthCheck.setChecked(penWidthsMatch)

        # Pen color
        showPenColor = False
        if (isinstance(penColor, QColor)):
            showPenColor = True
            self._penColorWidget.setColor(penColor)
            self._penColorWidget.setEnabled(penColorsMatch)
            self._penColorCheck.setChecked(penColorsMatch)

        # Brush color
        showBrushColor = False
        if (isinstance(brushColor, QColor)):
            showBrushColor = True
            self._brushColorWidget.setColor(brushColor)
            self._brushColorWidget.setEnabled(brushColorsMatch)
            self._brushColorCheck.setChecked(brushColorsMatch)

        # Set pen/brush group visibility
        self._penBrushLayout.setRowVisible(self._penStyleCombo, showPenStyle)
        self._penBrushLayout.setRowVisible(self._penWidthEdit, showPenWidth)
        self._penBrushLayout.setRowVisible(self._penColorWidget, showPenColor)
        self._penBrushLayout.setRowVisible(self._brushColorWidget, showBrushColor)
        self._penBrushGroup.setVisible(showPenStyle or showPenWidth or showPenColor or showBrushColor)

    def _updateArrowGroup(self) -> None:
        (startArrowStyle, startArrowStylesMatch) = self._checkForProperty('startArrowStyle')
        (startArrowSize, startArrowSizesMatch) = self._checkForProperty('startArrowSize')
        (endArrowStyle, endArrowStylesMatch) = self._checkForProperty('endArrowStyle')
        (endArrowSize, endArrowSizesMatch) = self._checkForProperty('endArrowSize')

        # Start arrow style
        showStartArrowStyle = False
        if (isinstance(startArrowStyle, int)):
            showStartArrowStyle = True
            self._startArrowStyleCombo.setCurrentIndex(startArrowStyle)
            self._startArrowStyleCombo.setEnabled(startArrowStylesMatch)
            self._startArrowStyleCheck.setChecked(startArrowStylesMatch)

        # Start arrow size
        showStartArrowSize = False
        if (isinstance(startArrowSize, float)):
            showStartArrowSize = True
            self._startArrowSizeEdit.setSize(startArrowSize)
            self._startArrowSizeEdit.setEnabled(startArrowSizesMatch)
            self._startArrowSizeCheck.setChecked(startArrowSizesMatch)

        # End arrow style
        showEndArrowStyle = False
        if (isinstance(endArrowStyle, int)):
            showEndArrowStyle = True
            self._endArrowStyleCombo.setCurrentIndex(endArrowStyle)
            self._endArrowStyleCombo.setEnabled(endArrowStylesMatch)
            self._endArrowStyleCheck.setChecked(endArrowStylesMatch)

        # End arrow size
        showEndArrowSize = False
        if (isinstance(endArrowSize, float)):
            showEndArrowSize = True
            self._endArrowSizeEdit.setSize(endArrowSize)
            self._endArrowSizeEdit.setEnabled(endArrowSizesMatch)
            self._endArrowSizeCheck.setChecked(endArrowSizesMatch)

        # Set arrow group visibility
        self._arrowLayout.setRowVisible(self._startArrowStyleCombo, showStartArrowStyle)
        self._arrowLayout.setRowVisible(self._startArrowSizeEdit, showStartArrowSize)
        self._arrowLayout.setRowVisible(self._endArrowStyleCombo, showEndArrowStyle)
        self._arrowLayout.setRowVisible(self._endArrowSizeEdit, showEndArrowSize)
        self._arrowGroup.setVisible(showStartArrowStyle or showStartArrowSize or showEndArrowStyle or showEndArrowSize)

    def _updateTextGroup(self) -> None:
        (fontFamily, fontFamiliesMatch) = self._checkForProperty('fontFamily')
        (fontSize, fontSizesMatch) = self._checkForProperty('fontSize')
        (fontBold, fontBoldsMatch) = self._checkForProperty('fontBold')
        (fontItalic, fontItalicsMatch) = self._checkForProperty('fontItalic')
        (fontUnderline, fontUnderlinesMatch) = self._checkForProperty('fontUnderline')
        (fontStrikeOut, fontStrikeOutsMatch) = self._checkForProperty('fontStrikeOut')
        (textAlignment, textAlignmentsMatch) = self._checkForProperty('textAlignment')
        (textColor, textColorsMatch) = self._checkForProperty('textColor')
        fontStylesMatch = (fontBoldsMatch and fontItalicsMatch and fontUnderlinesMatch and fontStrikeOutsMatch)

        # Font family
        showFontFamily = False
        if (isinstance(fontFamily, str)):
            showFontFamily = True
            self._fontFamilyCombo.setCurrentFont(QFont(fontFamily))
            self._fontFamilyCombo.setEnabled(fontFamiliesMatch)
            self._fontFamilyCheck.setChecked(fontFamiliesMatch)

        # Font size
        showFontSize = False
        if (isinstance(fontSize, float)):
            showFontSize = True
            self._fontSizeEdit.setSize(fontSize)
            self._fontSizeEdit.setEnabled(fontSizesMatch)
            self._fontSizeCheck.setChecked(fontSizesMatch)

        # Font style
        showFontStyle = False
        if (isinstance(fontBold, bool) and isinstance(fontItalic, bool) and isinstance(fontUnderline, bool) and
                isinstance(fontUnderline, bool)):
            showFontStyle = True
            self._fontBoldButton.setChecked(fontBold)
            self._fontItalicButton.setChecked(fontItalic)
            self._fontUnderlineButton.setChecked(fontUnderline)
            self._fontStrikeOutButton.setChecked(fontStrikeOut)
            self._fontStyleWidget.setEnabled(fontStylesMatch)
            self._fontStyleCheck.setChecked(fontStylesMatch)

        # Text alignment
        showTextAlignment = False
        if (isinstance(textAlignment, Qt.AlignmentFlag)):
            showTextAlignment = True
            horizontal = (textAlignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
            if (horizontal & Qt.AlignmentFlag.AlignHCenter):
                self._textAlignmentHCenterButton.setChecked(True)
            elif (horizontal & Qt.AlignmentFlag.AlignRight):
                self._textAlignmentRightButton.setChecked(True)
            else:
                self._textAlignmentLeftButton.setChecked(True)
            vertical = (textAlignment & Qt.AlignmentFlag.AlignVertical_Mask)
            if (vertical & Qt.AlignmentFlag.AlignVCenter):
                self._textAlignmentVCenterButton.setChecked(True)
            elif (vertical & Qt.AlignmentFlag.AlignBottom):
                self._textAlignmentBottomButton.setChecked(True)
            else:
                self._textAlignmentTopButton.setChecked(True)
            self._textAlignmentWidget.setEnabled(textAlignmentsMatch)
            self._textAlignmentCheck.setChecked(textAlignmentsMatch)

        # Text color
        showTextColor = False
        if (isinstance(textColor, QColor)):
            showTextColor = True
            self._textColorWidget.setColor(textColor)
            self._textColorWidget.setEnabled(textColorsMatch)
            self._textColorCheck.setChecked(textColorsMatch)

        # Set text group visibility
        self._textLayout.setRowVisible(self._fontFamilyCombo, showFontFamily)
        self._textLayout.setRowVisible(self._fontSizeEdit, showFontSize)
        self._textLayout.setRowVisible(self._fontStyleWidget, showFontStyle)
        self._textLayout.setRowVisible(self._textAlignmentWidget, showTextAlignment)
        self._textLayout.setRowVisible(self._textColorWidget, showTextColor)
        self._textGroup.setVisible(showFontFamily or showFontSize or showFontStyle or showTextAlignment or showTextColor)   # noqa

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

    # ==================================================================================================================

    def _handleFontFamilyChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('fontFamily', self._fontFamilyCombo.currentFont().family())

    def _handleFontSizeChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('fontSize', size)

    def _handleFontStyleChange(self) -> None:
        styles = []
        styles.append(self._fontBoldButton.isChecked())
        styles.append(self._fontItalicButton.isChecked())
        styles.append(self._fontUnderlineButton.isChecked())
        styles.append(self._fontStrikeOutButton.isChecked())
        self.itemsPropertyChanged.emit('fontStyle', styles)

    def _handleTextAlignmentChange(self) -> None:
        horizontal = Qt.AlignmentFlag.AlignLeft
        if (self._textAlignmentHCenterButton.isChecked()):
            horizontal = Qt.AlignmentFlag.AlignHCenter
        elif (self._textAlignmentRightButton.isChecked()):
            horizontal = Qt.AlignmentFlag.AlignRight
        vertical = Qt.AlignmentFlag.AlignLeft
        if (self._textAlignmentVCenterButton.isChecked()):
            vertical = Qt.AlignmentFlag.AlignVCenter
        elif (self._textAlignmentBottomButton.isChecked()):
            vertical = Qt.AlignmentFlag.AlignBottom
        self.itemsPropertyChanged.emit('textAlignment', horizontal | vertical)

    def _handleTextColorChange(self, color: QColor) -> None:
        self.itemsPropertyChanged.emit('textColor', color)

    def _handleFontFamilyCheckClicked(self, checked: bool) -> None:
        self._fontFamilyCombo.setEnabled(checked)
        if (checked):
            self._handleFontFamilyChange(self._fontFamilyCombo.currentIndex())

    def _handleFontSizeCheckClicked(self, checked: bool) -> None:
        self._fontSizeEdit.setEnabled(checked)
        if (checked):
            self._handleFontSizeChange(self._fontSizeEdit.size())

    def _handleFontStyleCheckClicked(self, checked: bool) -> None:
        self._fontStyleWidget.setEnabled(checked)
        if (checked):
            self._handleFontStyleChange()

    def _handleTextAlignmentCheckClicked(self, checked: bool) -> None:
        self._textAlignmentWidget.setEnabled(checked)
        if (checked):
            self._handleTextAlignmentChange()

    def _handleTextColorCheckClicked(self, checked: bool) -> None:
        self._textColorWidget.setEnabled(checked)
        if (checked):
            self._handleTextColorChange(self._textColorWidget.color())
