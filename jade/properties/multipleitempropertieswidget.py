# multipleitempropertieswidget.py
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

from typing import Any
from PySide6.QtCore import Qt, QPointF, QSizeF, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFontComboBox, QFormLayout, QFrame, QGroupBox, QHBoxLayout,
                               QToolButton, QVBoxLayout, QWidget)
from ..items.odgfontstyle import OdgFontStyle
from ..items.odgitem import OdgItem
from ..items.odgmarker import OdgMarker
from ..drawing.odgunits import OdgUnits
from .helperwidgets import ColorWidget, LengthEdit, SizeWidget


class MultipleItemPropertiesWidget(QWidget):
    itemsMovedDelta = Signal(QPointF)
    itemsPropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._items: list[OdgItem] = []

        self._labelWidth = QFontMetrics(self.font()).boundingRect('Bottom-Right Margin:').width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createRectGroup())
        layout.addWidget(self._createPenBrushGroup())
        layout.addWidget(self._createMarkerGroup())
        layout.addWidget(self._createTextGroup())
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    # ==================================================================================================================

    def _createRectGroup(self) -> QGroupBox:
        self._rectCornerRadiusEdit: LengthEdit = LengthEdit()
        self._rectCornerRadiusEdit.lengthChanged.connect(self._handleRectCornerRadiusChange)
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

        self._penWidthEdit: LengthEdit = LengthEdit()
        self._penWidthEdit.lengthChanged.connect(self._handlePenWidthChange)
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

    def _createMarkerGroup(self) -> QGroupBox:
        self._startMarkerStyleCombo: QComboBox = QComboBox()
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-none.png'), 'None')
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-triangle-start.png'), 'Triangle')
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-circle-start.png'), 'Circle')
        self._startMarkerStyleCombo.activated.connect(self._handleStartMarkerStyleChange)         # type: ignore
        self._startMarkerStyleCheck: QCheckBox = QCheckBox('Start Marker Style:')
        self._startMarkerStyleCheck.clicked.connect(self._handleStartMarkerStyleCheckClicked)     # type: ignore

        self._startMarkerSizeEdit: LengthEdit = LengthEdit()
        self._startMarkerSizeEdit.lengthChanged.connect(self._handleStartMarkerSizeChange)
        self._startMarkerSizeCheck: QCheckBox = QCheckBox('Start Marker Size:')
        self._startMarkerSizeCheck.clicked.connect(self._handleStartMarkerSizeCheckClicked)       # type: ignore

        self._endMarkerStyleCombo: QComboBox = QComboBox()
        self._endMarkerStyleCombo.addItem(QIcon('icons:marker/marker-none.png'), 'None')
        self._endMarkerStyleCombo.addItem(QIcon('icons:marker/marker-triangle-end.png'), 'Triangle')
        self._endMarkerStyleCombo.addItem(QIcon('icons:marker/marker-circle-end.png'), 'Circle')
        self._endMarkerStyleCombo.activated.connect(self._handleEndMarkerStyleChange)             # type: ignore
        self._endMarkerStyleCheck: QCheckBox = QCheckBox('End Marker Style:')
        self._endMarkerStyleCheck.clicked.connect(self._handleEndMarkerStyleCheckClicked)         # type: ignore

        self._endMarkerSizeEdit: LengthEdit = LengthEdit()
        self._endMarkerSizeEdit.lengthChanged.connect(self._handleEndMarkerSizeChange)
        self._endMarkerSizeCheck: QCheckBox = QCheckBox('End Marker Size:')
        self._endMarkerSizeCheck.clicked.connect(self._handleEndMarkerSizeCheckClicked)           # type: ignore

        self._markerGroup: QGroupBox = QGroupBox('Marker')
        self._markerLayout: QFormLayout = QFormLayout()
        self._markerLayout.addRow(self._startMarkerStyleCheck, self._startMarkerStyleCombo)
        self._markerLayout.addRow(self._startMarkerSizeCheck, self._startMarkerSizeEdit)
        self._markerLayout.addRow(self._endMarkerStyleCheck, self._endMarkerStyleCombo)
        self._markerLayout.addRow(self._endMarkerSizeCheck, self._endMarkerSizeEdit)
        self._markerLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._markerLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._markerLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._markerLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._markerGroup.setLayout(self._markerLayout)

        return self._markerGroup

    def _createTextGroup(self) -> QGroupBox:
        self._fontFamilyCombo: QFontComboBox = QFontComboBox()
        self._fontFamilyCombo.setMaximumWidth(162)
        self._fontFamilyCombo.activated.connect(self._handleFontFamilyChange)       # type: ignore
        self._fontFamilyCheck: QCheckBox = QCheckBox('Font:')
        self._fontFamilyCheck.clicked.connect(self._handleFontFamilyCheckClicked)   # type: ignore

        self._fontSizeEdit: LengthEdit = LengthEdit()
        self._fontSizeEdit.lengthChanged.connect(self._handleFontSizeChange)
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
        self._textAlignmentBottomButton.setIcon(QIcon('icons:align-vertical-bottom.png'))
        self._textAlignmentBottomButton.setToolTip('Align Bottom')
        self._textAlignmentBottomButton.setCheckable(True)
        self._textAlignmentBottomButton.setAutoExclusive(True)
        self._textAlignmentBottomButton.clicked.connect(self._handleTextAlignmentChange)    # type: ignore

        self._textAlignmentCheck: QCheckBox = QCheckBox('Text Alignment:')
        self._textAlignmentCheck.clicked.connect(self._handleTextAlignmentCheckClicked)     # type: ignore

        self._textPaddingWidget: SizeWidget = SizeWidget()
        self._textPaddingWidget.sizeChanged.connect(self._handleTextPaddingChange)
        self._textPaddingCheck: QCheckBox = QCheckBox('Text Padding:')
        self._textPaddingCheck.clicked.connect(self._handleTextPaddingCheckClicked)         # type: ignore

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
        self._textLayout.addRow(self._textPaddingCheck, self._textPaddingWidget)
        self._textLayout.addRow(self._textColorCheck, self._textColorWidget)
        self._textLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._textLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._textLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._textLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._textGroup.setLayout(self._textLayout)

        return self._textGroup

    # ==================================================================================================================

    def setItems(self, items: list[OdgItem]) -> None:
        self._items = items
        self.blockSignals(True)
        self._updateRectGroup()
        self._updatePenBrushGroup()
        self._updateMarkerGroup()
        self._updateTextGroup()
        self.blockSignals(False)

    def _updateRectGroup(self) -> None:
        (cornerRadius, cornerRadiusMatches) = self._checkForProperty('cornerRadius')

        # Corner radius
        showRectGroup = False
        if (isinstance(cornerRadius, float)):
            showRectGroup = True
            self._rectCornerRadiusEdit.setLength(cornerRadius)
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
            self._penWidthEdit.setLength(penWidth)
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

    def _updateMarkerGroup(self) -> None:
        (startMarkerStyle, startMarkerStylesMatch) = self._checkForProperty('startMarkerStyle')
        (startMarkerSize, startMarkerSizesMatch) = self._checkForProperty('startMarkerSize')
        (endMarkerStyle, endMarkerStylesMatch) = self._checkForProperty('endMarkerStyle')
        (endMarkerSize, endMarkerSizesMatch) = self._checkForProperty('endMarkerSize')

        # Start marker style
        showStartMarkerStyle = False
        if (isinstance(startMarkerStyle, int)):
            showStartMarkerStyle = True
            self._startMarkerStyleCombo.setCurrentIndex(startMarkerStyle)
            self._startMarkerStyleCombo.setEnabled(startMarkerStylesMatch)
            self._startMarkerStyleCheck.setChecked(startMarkerStylesMatch)

        # Start marker size
        showStartMarkerSize = False
        if (isinstance(startMarkerSize, float)):
            showStartMarkerSize = True
            self._startMarkerSizeEdit.setLength(startMarkerSize)
            self._startMarkerSizeEdit.setEnabled(startMarkerSizesMatch)
            self._startMarkerSizeCheck.setChecked(startMarkerSizesMatch)

        # End marker style
        showEndMarkerStyle = False
        if (isinstance(endMarkerStyle, int)):
            showEndMarkerStyle = True
            self._endMarkerStyleCombo.setCurrentIndex(endMarkerStyle)
            self._endMarkerStyleCombo.setEnabled(endMarkerStylesMatch)
            self._endMarkerStyleCheck.setChecked(endMarkerStylesMatch)

        # End marker size
        showEndMarkerSize = False
        if (isinstance(endMarkerSize, float)):
            showEndMarkerSize = True
            self._endMarkerSizeEdit.setLength(endMarkerSize)
            self._endMarkerSizeEdit.setEnabled(endMarkerSizesMatch)
            self._endMarkerSizeCheck.setChecked(endMarkerSizesMatch)

        # Set marker group visibility
        self._markerLayout.setRowVisible(self._startMarkerStyleCombo, showStartMarkerStyle)
        self._markerLayout.setRowVisible(self._startMarkerSizeEdit, showStartMarkerSize)
        self._markerLayout.setRowVisible(self._endMarkerStyleCombo, showEndMarkerStyle)
        self._markerLayout.setRowVisible(self._endMarkerSizeEdit, showEndMarkerSize)
        self._markerGroup.setVisible(showStartMarkerStyle or showStartMarkerSize or showEndMarkerStyle or
                                     showEndMarkerSize)

    def _updateTextGroup(self) -> None:
        (fontFamily, fontFamiliesMatch) = self._checkForProperty('fontFamily')
        (fontSize, fontSizesMatch) = self._checkForProperty('fontSize')
        (fontStyle, fontStylesMatch) = self._checkForProperty('fontStyle')
        (textAlignment, textAlignmentsMatch) = self._checkForProperty('textAlignment')
        (textPadding, textPaddingsMatch) = self._checkForProperty('textPadding')
        (textColor, textColorsMatch) = self._checkForProperty('textColor')

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
            self._fontSizeEdit.setLength(fontSize)
            self._fontSizeEdit.setEnabled(fontSizesMatch)
            self._fontSizeCheck.setChecked(fontSizesMatch)

        # Font style
        showFontStyle = False
        if (isinstance(fontStyle, OdgFontStyle)):
            showFontStyle = True
            self._fontBoldButton.setChecked(fontStyle.bold())
            self._fontItalicButton.setChecked(fontStyle.italic())
            self._fontUnderlineButton.setChecked(fontStyle.underline())
            self._fontStrikeOutButton.setChecked(fontStyle.strikeOut())
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

        # Text padding
        showTextPadding = False
        if (isinstance(textPadding, QSizeF)):
            showTextPadding = True
            self._textPaddingWidget.setSize(textPadding)
            self._textPaddingWidget.setEnabled(textPaddingsMatch)
            self._textPaddingCheck.setChecked(textPaddingsMatch)

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
        self._textLayout.setRowVisible(self._textPaddingWidget, showTextPadding)
        self._textLayout.setRowVisible(self._textColorWidget, showTextColor)
        self._textGroup.setVisible(showFontFamily or showFontSize or showFontStyle or showTextAlignment or
                                   showTextPadding or showTextColor)

    def _checkForProperty(self, name: str) -> tuple[Any, bool]:
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

    def setUnits(self, units: OdgUnits) -> None:
        self._rectCornerRadiusEdit.setUnits(units)
        self._penWidthEdit.setUnits(units)
        self._startMarkerSizeEdit.setUnits(units)
        self._endMarkerSizeEdit.setUnits(units)
        self._fontSizeEdit.setUnits(units)
        self._textPaddingWidget.setUnits(units)

    # ==================================================================================================================

    def _handleRectCornerRadiusChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('cornerRadius', size)

    def _handleRectCornerRadiusCheckClicked(self, checked: bool) -> None:
        self._rectCornerRadiusEdit.setEnabled(checked)
        if (checked):
            self._handleRectCornerRadiusChange(self._rectCornerRadiusEdit.length())

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
            self._handlePenWidthChange(self._penWidthEdit.length())

    def _handlePenColorCheckClicked(self, checked: bool) -> None:
        self._penColorWidget.setEnabled(checked)
        if (checked):
            self._handlePenColorChange(self._penColorWidget.color())

    def _handleBrushColorCheckClicked(self, checked: bool) -> None:
        self._brushColorWidget.setEnabled(checked)
        if (checked):
            self._handleBrushColorChange(self._brushColorWidget.color())

    # ==================================================================================================================

    def _handleStartMarkerStyleChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('startMarkerStyle', index)

    def _handleStartMarkerSizeChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('startMarkerSize', size)

    def _handleEndMarkerStyleChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('endMarkerStyle', index)

    def _handleEndMarkerSizeChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('endMarkerSize', size)

    def _handleStartMarkerStyleCheckClicked(self, checked: bool) -> None:
        self._startMarkerStyleCombo.setEnabled(checked)
        if (checked):
            self._handleStartMarkerStyleChange(self._startMarkerStyleCombo.currentIndex())

    def _handleStartMarkerSizeCheckClicked(self, checked: bool) -> None:
        self._startMarkerSizeEdit.setEnabled(checked)
        if (checked):
            self._handleStartMarkerSizeChange(self._startMarkerSizeEdit.length())

    def _handleEndMarkerStyleCheckClicked(self, checked: bool) -> None:
        self._endMarkerStyleCombo.setEnabled(checked)
        if (checked):
            self._handleEndMarkerStyleChange(self._endMarkerStyleCombo.currentIndex())

    def _handleEndMarkerSizeCheckClicked(self, checked: bool) -> None:
        self._endMarkerSizeEdit.setEnabled(checked)
        if (checked):
            self._handleEndMarkerSizeChange(self._endMarkerSizeEdit.length())

    # ==================================================================================================================

    def _handleFontFamilyChange(self, index: int) -> None:
        self.itemsPropertyChanged.emit('fontFamily', self._fontFamilyCombo.currentFont().family())

    def _handleFontSizeChange(self, size: float) -> None:
        self.itemsPropertyChanged.emit('fontSize', size)

    def _handleFontStyleChange(self) -> None:
        style = OdgFontStyle()
        style.setBold(self._fontBoldButton.isChecked())
        style.setItalic(self._fontItalicButton.isChecked())
        style.setUnderline(self._fontUnderlineButton.isChecked())
        style.setStrikeOut(self._fontStrikeOutButton.isChecked())
        self.itemsPropertyChanged.emit('fontStyle', style)

    def _handleTextAlignmentChange(self) -> None:
        horizontal = Qt.AlignmentFlag.AlignLeft
        if (self._textAlignmentHCenterButton.isChecked()):
            horizontal = Qt.AlignmentFlag.AlignHCenter
        elif (self._textAlignmentRightButton.isChecked()):
            horizontal = Qt.AlignmentFlag.AlignRight
        vertical = Qt.AlignmentFlag.AlignTop
        if (self._textAlignmentVCenterButton.isChecked()):
            vertical = Qt.AlignmentFlag.AlignVCenter
        elif (self._textAlignmentBottomButton.isChecked()):
            vertical = Qt.AlignmentFlag.AlignBottom
        self.itemsPropertyChanged.emit('textAlignment', horizontal | vertical)

    def _handleTextPaddingChange(self, size: QSizeF) -> None:
        self.itemsPropertyChanged.emit('textPadding', size)

    def _handleTextColorChange(self, color: QColor) -> None:
        self.itemsPropertyChanged.emit('textColor', color)

    def _handleFontFamilyCheckClicked(self, checked: bool) -> None:
        self._fontFamilyCombo.setEnabled(checked)
        if (checked):
            self._handleFontFamilyChange(self._fontFamilyCombo.currentIndex())

    def _handleFontSizeCheckClicked(self, checked: bool) -> None:
        self._fontSizeEdit.setEnabled(checked)
        if (checked):
            self._handleFontSizeChange(self._fontSizeEdit.length())

    def _handleFontStyleCheckClicked(self, checked: bool) -> None:
        self._fontStyleWidget.setEnabled(checked)
        if (checked):
            self._handleFontStyleChange()

    def _handleTextAlignmentCheckClicked(self, checked: bool) -> None:
        self._textAlignmentWidget.setEnabled(checked)
        if (checked):
            self._handleTextAlignmentChange()

    def _handleTextPaddingCheckClicked(self, checked: bool) -> None:
        self._textPaddingWidget.setEnabled(checked)
        if (checked):
            self._handleTextPaddingChange(self._textPaddingWidget.size())

    def _handleTextColorCheckClicked(self, checked: bool) -> None:
        self._textColorWidget.setEnabled(checked)
        if (checked):
            self._handleTextColorChange(self._textColorWidget.color())
