# stylepropertieswidget.py
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

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon
from PySide6.QtWidgets import (QComboBox, QFontComboBox, QFormLayout, QFrame, QGroupBox, QHBoxLayout, QLineEdit,
                               QToolButton, QVBoxLayout, QWidget)
from ..items.odgmarker import OdgMarker
from ..drawing.odgunits import OdgUnits
from .helperwidgets import ColorWidget, LengthEdit


class StylePropertiesWidget(QWidget):
    itemPropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._labelWidth: int = QFontMetrics(super().font()).boundingRect("Minor Grid Spacing:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createOrganizerGroup())
        layout.addWidget(self._createPenBrushGroup())
        layout.addWidget(self._createMarkerGroup())
        layout.addWidget(self._createTextGroup())
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    # ==================================================================================================================

    def _createOrganizerGroup(self) -> QGroupBox:
        self._nameEdit: QLineEdit = QLineEdit()
        self._parentCombo: QComboBox = QComboBox()

        self._organizerGroup: QGroupBox = QGroupBox('Organizer')
        self._organizerLayout: QFormLayout = QFormLayout()
        self._organizerLayout.addRow('Name:', self._nameEdit)
        self._organizerLayout.addRow('Parent Style:', self._parentCombo)
        self._organizerLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._organizerLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._organizerLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._organizerLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._organizerGroup.setLayout(self._organizerLayout)

        return self._organizerGroup

    def _createPenBrushGroup(self) -> QGroupBox:
        self._penStyleCombo: QComboBox = QComboBox()
        self._penStyleCombo.addItems(['None', 'Solid', 'Dashed', 'Dotted', 'Dash-Dotted', 'Dash-Dot-Dotted'])
        self._penStyleCombo.activated.connect(self._handlePenStyleChange)   # type: ignore

        self._penWidthEdit: LengthEdit = LengthEdit(0, OdgUnits.Inches, lengthMustBeNonNegative=True)
        self._penWidthEdit.lengthChanged.connect(self._handlePenWidthChange)

        self._penColorWidget: ColorWidget = ColorWidget()
        self._penColorWidget.colorChanged.connect(self._handlePenColorChange)

        self._brushColorWidget: ColorWidget = ColorWidget()
        self._brushColorWidget.colorChanged.connect(self._handleBrushColorChange)

        self._penBrushGroup: QGroupBox = QGroupBox('Pen / Brush')
        self._penBrushLayout: QFormLayout = QFormLayout()
        self._penBrushLayout.addRow('Pen Style:', self._penStyleCombo)
        self._penBrushLayout.addRow('Pen Width:', self._penWidthEdit)
        self._penBrushLayout.addRow('Pen Color:', self._penColorWidget)
        self._penBrushLayout.addRow('Brush Color:', self._brushColorWidget)
        self._penBrushLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._penBrushLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._penBrushLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._penBrushLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._penBrushGroup.setLayout(self._penBrushLayout)

        return self._penBrushGroup

    def _createMarkerGroup(self) -> QGroupBox:
        self._startMarkerStyleCombo: QComboBox = QComboBox()
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-none.png'), 'None')
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-triangle.png'), 'Triangle')
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-circle.png'), 'Circle')
        self._startMarkerStyleCombo.activated.connect(self._handleStartMarkerStyleChange)     # type: ignore

        self._startMarkerSizeEdit: LengthEdit = LengthEdit(0, OdgUnits.Inches, lengthMustBeNonNegative=True)
        self._startMarkerSizeEdit.lengthChanged.connect(self._handleStartMarkerSizeChange)

        self._endMarkerStyleCombo: QComboBox = QComboBox()
        for index in range(self._startMarkerStyleCombo.count()):
            self._endMarkerStyleCombo.addItem(self._startMarkerStyleCombo.itemIcon(index),
                                              self._startMarkerStyleCombo.itemText(index))
        self._endMarkerStyleCombo.activated.connect(self._handleEndMarkerStyleChange)         # type: ignore

        self._endMarkerSizeEdit: LengthEdit = LengthEdit(0, OdgUnits.Inches, lengthMustBeNonNegative=True)
        self._endMarkerSizeEdit.lengthChanged.connect(self._handleEndMarkerSizeChange)

        self._markerGroup: QGroupBox = QGroupBox('Markers')
        self._markerLayout: QFormLayout = QFormLayout()
        self._markerLayout.addRow('Start Marker Style:', self._startMarkerStyleCombo)
        self._markerLayout.addRow('Start Marker Size:', self._startMarkerSizeEdit)
        self._markerLayout.addRow('End Marker Style:', self._endMarkerStyleCombo)
        self._markerLayout.addRow('End Marker Size:', self._endMarkerSizeEdit)
        self._markerLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._markerLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._markerLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._markerLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._markerGroup.setLayout(self._markerLayout)

        return self._markerGroup

    def _createTextGroup(self) -> QGroupBox:
        self._fontFamilyCombo: QFontComboBox = QFontComboBox()
        self._fontFamilyCombo.setMinimumWidth(140)

        self._fontSizeEdit: LengthEdit = LengthEdit(0, OdgUnits.Inches, lengthMustBeNonNegative=True)

        self._fontBoldButton: QToolButton = self._createToolButton('icons:format-text-bold.png', 'Bold', True)
        self._fontItalicButton: QToolButton = self._createToolButton('icons:format-text-italic.png', 'Italic', True)
        self._fontUnderlineButton: QToolButton = self._createToolButton('icons:format-text-underline.png',
                                                                        'Underline', True)
        self._fontStrikeOutButton: QToolButton = self._createToolButton('icons:format-text-strikethrough.png',
                                                                        'Strike-Through', True)

        self._textAlignmentLeftButton: QToolButton = self._createToolButton('icons:align-horizontal-left.png',
                                                                            'Align Left', True, True)
        self._textAlignmentHCenterButton: QToolButton = self._createToolButton('icons:align-horizontal-center.png',
                                                                               'Align Center', True, True)
        self._textAlignmentRightButton: QToolButton = self._createToolButton('icons:align-horizontal-right.png',
                                                                             'Align Right', True, True)

        self._textAlignmentTopButton: QToolButton = self._createToolButton('icons:align-vertical-top.png',
                                                                           'Align Top', True, True)
        self._textAlignmentVCenterButton: QToolButton = self._createToolButton('icons:align-vertical-center.png',
                                                                               'Align Center', True, True)
        self._textAlignmentBottomButton: QToolButton = self._createToolButton('icons:align-vertical-bottom.png',
                                                                              'Align Bottom', True, True)

        self._textColorWidget: ColorWidget = ColorWidget()

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
        self._textLayout.addRow('Font:', self._fontFamilyCombo)
        self._textLayout.addRow('Font Size:', self._fontSizeEdit)
        self._textLayout.addRow('Font Style:', self._fontStyleWidget)
        self._textLayout.addRow('Text Alignment:', self._textAlignmentWidget)
        self._textLayout.addRow('Text Color:', self._textColorWidget)
        self._textLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._textLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._textLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._textLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._textGroup.setLayout(self._textLayout)

        return self._textGroup

    def _createToolButton(self, iconPath: str, toolTip: str, checkable: bool,
                          autoExclusive: bool = False) -> QToolButton:
        toolButton = QToolButton()
        toolButton.setIcon(QIcon(iconPath))
        toolButton.setToolTip(toolTip)
        toolButton.setCheckable(checkable)
        if (autoExclusive):
            toolButton.setAutoExclusive(True)
        return toolButton

    # ==================================================================================================================

    def sizeHint(self) -> QSize:
        return QSize(-1, -1)

    # ==================================================================================================================

    def setPenStyle(self, style: Qt.PenStyle) -> None:
        self._penStyleCombo.setCurrentIndex(style.value)      # type: ignore

    def setPenWidth(self, width: float) -> None:
        self._penWidthEdit.setLength(width)

    def setPenColor(self, color: QColor) -> None:
        self._penColorWidget.setColor(color)

    def setBrushColor(self, color: QColor) -> None:
        self._brushColorWidget.setColor(color)

    def penStyle(self) -> Qt.PenStyle:
        return Qt.PenStyle(self._penStyleCombo.currentIndex())

    def penWidth(self) -> float:
        return self._penWidthEdit.length()

    def penColor(self) -> QColor:
        return self._penColorWidget.color()

    def brushColor(self) -> QColor:
        return self._brushColorWidget.color()

    # ==================================================================================================================

    def setStartMarkerStyle(self, style: OdgMarker.Style) -> None:
        self._startMarkerStyleCombo.setCurrentIndex(style)

    def setStartMarkerSize(self, size: float) -> None:
        self._startMarkerSizeEdit.setLength(size)

    def setEndMarkerStyle(self, style: OdgMarker.Style) -> None:
        self._endMarkerStyleCombo.setCurrentIndex(style)

    def setEndMarkerSize(self, size: float) -> None:
        self._endMarkerSizeEdit.setLength(size)

    def startMarkerStyle(self) -> OdgMarker.Style:
        return OdgMarker.Style(self._startMarkerStyleCombo.currentIndex())

    def startMarkerSize(self) -> float:
        return self._startMarkerSizeEdit.length()

    def endMarkerStyle(self) -> OdgMarker.Style:
        return OdgMarker.Style(self._endMarkerStyleCombo.currentIndex())

    def endMarkerSize(self) -> float:
        return self._endMarkerSizeEdit.length()

    # ==================================================================================================================

    def setFontFamily(self, family: str) -> None:
        self._fontFamilyCombo.setCurrentFont(QFont(family))

    def setFontSize(self, size: float) -> None:
        self._fontSizeEdit.setLength(size)

    def setFontBold(self, bold: bool) -> None:
        self._fontBoldButton.setChecked(bold)

    def setFontItalic(self, italic: bool) -> None:
        self._fontItalicButton.setChecked(italic)

    def setFontUnderline(self, underline: bool) -> None:
        self._fontUnderlineButton.setChecked(underline)

    def setFontStrikeOut(self, strikeOut: bool) -> None:
        self._fontStrikeOutButton.setChecked(strikeOut)

    def setTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        horizontal = (alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
        if (horizontal & Qt.AlignmentFlag.AlignHCenter):
            self._textAlignmentHCenterButton.setChecked(True)
        elif (horizontal & Qt.AlignmentFlag.AlignRight):
            self._textAlignmentRightButton.setChecked(True)
        else:
            self._textAlignmentLeftButton.setChecked(True)

        vertical = (alignment & Qt.AlignmentFlag.AlignVertical_Mask)
        if (vertical & Qt.AlignmentFlag.AlignVCenter):
            self._textAlignmentVCenterButton.setChecked(True)
        elif (vertical & Qt.AlignmentFlag.AlignBottom):
            self._textAlignmentBottomButton.setChecked(True)
        else:
            self._textAlignmentTopButton.setChecked(True)

    def setTextColor(self, color: QColor) -> None:
        self._textColorWidget.setColor(color)

    def fontFamily(self) -> str:
        return self._fontFamilyCombo.currentFont().family()

    def fontSize(self) -> float:
        return self._fontSizeEdit.length()

    def fontBold(self) -> bool:
        return self._fontBoldButton.isChecked()

    def fontItalic(self) -> bool:
        return self._fontItalicButton.isChecked()

    def fontUnderline(self) -> bool:
        return self._fontUnderlineButton.isChecked()

    def fontStrikeOut(self) -> bool:
        return self._fontStrikeOutButton.isChecked()

    def textAlignment(self) -> Qt.AlignmentFlag:
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

        return (horizontal | vertical)

    def textColor(self) -> QColor:
        return self._textColorWidget.color()

    # ==================================================================================================================

    def _handlePenStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('penStyle', index)

    def _handlePenWidthChange(self, width: float) -> None:
        self.itemPropertyChanged.emit('penWidth', width)

    def _handlePenColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('penColor', color)

    def _handleBrushColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('brushColor', color)

    # ==================================================================================================================

    def _handleStartMarkerStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('startMarkerStyle', index)

    def _handleStartMarkerSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('startMarkerSize', size)

    def _handleEndMarkerStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('endMarkerStyle', index)

    def _handleEndMarkerSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('endMarkerSize', size)

    # ==================================================================================================================

    def _handleFontFamilyChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('fontFamily', self._fontFamilyCombo.currentFont().family())

    def _handleFontSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('fontSize', size)

    def _handleFontStyleChange(self) -> None:
        styles = []
        styles.append(self._fontBoldButton.isChecked())
        styles.append(self._fontItalicButton.isChecked())
        styles.append(self._fontUnderlineButton.isChecked())
        styles.append(self._fontStrikeOutButton.isChecked())
        self.itemPropertyChanged.emit('fontStyle', styles)

    def _handleTextAlignmentChange(self) -> None:
        self.itemPropertyChanged.emit('textAlignment', self.textAlignment())

    def _handleTextColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('textColor', color)
