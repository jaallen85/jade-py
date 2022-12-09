# singleitempropertieswidget.py
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

from PySide6.QtCore import Qt, QLineF, QPointF, QRectF, QSizeF, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetrics, QIcon, QPen, QPolygonF
from PySide6.QtWidgets import (QComboBox, QFontComboBox, QFormLayout, QFrame, QGroupBox, QHBoxLayout, QPlainTextEdit,
                               QToolButton, QVBoxLayout, QWidget)
from ..drawing.drawingarrow import DrawingArrow
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint
from ..drawing.drawingunits import DrawingUnits
from .helperwidgets import ColorWidget, PositionWidget, SizeWidget, SizeEdit


class SingleItemPropertiesWidget(QWidget):
    itemMoved = Signal(QPointF)
    itemResized = Signal(DrawingItemPoint, QPointF)
    itemPropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._item: DrawingItem | None = None

        self._labelWidth: int = QFontMetrics(self.font()).boundingRect("Minor Grid Spacing:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createLineGroup())
        layout.addWidget(self._createCurveGroup())
        layout.addWidget(self._createRectGroup())
        layout.addWidget(self._createPenBrushGroup())
        layout.addWidget(self._createArrowGroup())
        layout.addWidget(self._createTextGroup())
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    def _createLineGroup(self) -> QGroupBox:
        self._lineStartWidget: PositionWidget = PositionWidget()
        self._lineStartWidget.positionChanged.connect(self._handleLineStartChange)

        self._lineEndWidget: PositionWidget = PositionWidget()
        self._lineEndWidget.positionChanged.connect(self._handleLineEndChange)

        self._lineSizeWidget: SizeWidget = SizeWidget()
        self._lineSizeWidget.sizeChanged.connect(self._handleLineSizeChange)

        self._lineGroup: QGroupBox = QGroupBox('Line')
        self._lineLayout: QFormLayout = QFormLayout()
        self._lineLayout.addRow('Start Point:', self._lineStartWidget)
        self._lineLayout.addRow('End Point:', self._lineEndWidget)
        self._lineLayout.addRow('Size:', self._lineSizeWidget)
        self._lineLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._lineLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._lineLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._lineLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._lineGroup.setLayout(self._lineLayout)

        return self._lineGroup

    def _createCurveGroup(self) -> QGroupBox:
        self._curveStartWidget: PositionWidget = PositionWidget()
        self._curveStartWidget.positionChanged.connect(self._handleCurveStartChange)

        self._curveStartControlWidget: PositionWidget = PositionWidget()
        self._curveStartControlWidget.positionChanged.connect(self._handleCurveStartControlChange)

        self._curveEndControlWidget: PositionWidget = PositionWidget()
        self._curveEndControlWidget.positionChanged.connect(self._handleCurveEndControlChange)

        self._curveEndWidget: PositionWidget = PositionWidget()
        self._curveEndWidget.positionChanged.connect(self._handleCurveEndChange)

        self._curveGroup: QGroupBox = QGroupBox('Curve')
        self._curveLayout: QFormLayout = QFormLayout()
        self._curveLayout.addRow('Start Point:', self._curveStartWidget)
        self._curveLayout.addRow('Start Control Point:', self._curveStartControlWidget)
        self._curveLayout.addRow('End Control Point:', self._curveEndControlWidget)
        self._curveLayout.addRow('End Point:', self._curveEndWidget)
        self._curveLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._curveLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._curveLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._curveLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._curveGroup.setLayout(self._curveLayout)

        return self._curveGroup

    def _createRectGroup(self) -> QGroupBox:
        self._rectTopLeftWidget: PositionWidget = PositionWidget()
        self._rectTopLeftWidget.positionChanged.connect(self._handleRectTopLeftChange)

        self._rectBottomRightWidget: PositionWidget = PositionWidget()
        self._rectBottomRightWidget.positionChanged.connect(self._handleRectBottomRightChange)

        self._rectSizeWidget: SizeWidget = SizeWidget()
        self._rectSizeWidget.sizeChanged.connect(self._handleRectSizeChange)

        self._rectCornerRadiusEdit: SizeEdit = SizeEdit()
        self._rectCornerRadiusEdit.sizeChanged.connect(self._handleRectCornerRadiusChange)

        self._rectGroup: QGroupBox = QGroupBox('Rect')
        self._rectLayout: QFormLayout = QFormLayout()
        self._rectLayout.addRow('Top-Left:', self._rectTopLeftWidget)
        self._rectLayout.addRow('Bottom-Right:', self._rectBottomRightWidget)
        self._rectLayout.addRow('Size:', self._rectSizeWidget)
        self._rectLayout.addRow('Corner Radius:', self._rectCornerRadiusEdit)
        self._rectLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._rectLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._rectLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._rectLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._rectGroup.setLayout(self._rectLayout)

        return self._rectGroup

    def _createPenBrushGroup(self) -> QGroupBox:
        self._penStyleCombo: QComboBox = QComboBox()
        self._penStyleCombo.addItems(['None', 'Solid', 'Dashed', 'Dotted', 'Dash-Dotted', 'Dash-Dot-Dotted'])
        self._penStyleCombo.activated.connect(self._handlePenStyleChange)   # type: ignore

        self._penWidthEdit: SizeEdit = SizeEdit()
        self._penWidthEdit.sizeChanged.connect(self._handlePenWidthChange)

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
        self._startArrowStyleCombo.activated.connect(self._handleStartArrowStyleChange)     # type: ignore

        self._startArrowSizeEdit: SizeEdit = SizeEdit()
        self._startArrowSizeEdit.sizeChanged.connect(self._handleStartArrowSizeChange)

        self._endArrowStyleCombo: QComboBox = QComboBox()
        for index in range(self._startArrowStyleCombo.count()):
            self._endArrowStyleCombo.addItem(self._startArrowStyleCombo.itemIcon(index),
                                             self._startArrowStyleCombo.itemText(index))
        self._endArrowStyleCombo.activated.connect(self._handleEndArrowStyleChange)         # type: ignore

        self._endArrowSizeEdit: SizeEdit = SizeEdit()
        self._endArrowSizeEdit.sizeChanged.connect(self._handleEndArrowSizeChange)

        self._arrowGroup: QGroupBox = QGroupBox('Arrow')
        self._arrowLayout: QFormLayout = QFormLayout()
        self._arrowLayout.addRow('Start Arrow Style:', self._startArrowStyleCombo)
        self._arrowLayout.addRow('Start Arrow Size:', self._startArrowSizeEdit)
        self._arrowLayout.addRow('End Arrow Style:', self._endArrowStyleCombo)
        self._arrowLayout.addRow('End Arrow Size:', self._endArrowSizeEdit)
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

        self._fontSizeEdit: SizeEdit = SizeEdit()
        self._fontSizeEdit.sizeChanged.connect(self._handleFontSizeChange)

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

        self._textColorWidget: ColorWidget = ColorWidget()
        self._textColorWidget.colorChanged.connect(self._handleTextColorChange)

        self._textWidget: QPlainTextEdit = QPlainTextEdit()
        self._textWidget.setMaximumHeight(QFontMetrics(self._textWidget.font()).height() * 4 + 8)
        self._textWidget.textChanged.connect(self._handleTextChange)    # type: ignore

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
        self._textLayout.addRow('Text:', self._textWidget)
        self._textLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._textLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._textLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._textLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._textGroup.setLayout(self._textLayout)

        return self._textGroup

    # ==================================================================================================================

    def setUnits(self, units: DrawingUnits) -> None:
        self.blockSignals(True)

        self._lineStartWidget.setUnits(units)
        self._lineEndWidget.setUnits(units)
        self._lineSizeWidget.setUnits(units)

        self._curveStartWidget.setUnits(units)
        self._curveStartControlWidget.setUnits(units)
        self._curveEndControlWidget.setUnits(units)
        self._curveEndWidget.setUnits(units)

        self._rectTopLeftWidget.setUnits(units)
        self._rectBottomRightWidget.setUnits(units)
        self._rectSizeWidget.setUnits(units)
        self._rectCornerRadiusEdit.setUnits(units)

        self._penWidthEdit.setUnits(units)

        self._startArrowSizeEdit.setUnits(units)
        self._endArrowSizeEdit.setUnits(units)

        self._fontSizeEdit.setUnits(units)

        self.blockSignals(False)

    # ==================================================================================================================

    def setItem(self, item: DrawingItem) -> None:
        self._item = item
        self.blockSignals(True)
        self._updateLineGroup()
        self._updateCurveGroup()
        self._updateRectGroup()
        self._updatePenBrushGroup()
        self._updateArrowGroup()
        self._updateTextGroup()
        self.blockSignals(False)

    def _updateLineGroup(self) -> None:
        if (self._item is not None):
            line = self._item.property('line')

            # Line
            showLine = False
            if (isinstance(line, QLineF)):
                showLine = True
                self._lineStartWidget.setPosition(line.p1())
                self._lineEndWidget.setPosition(line.p2())
                self._lineSizeWidget.setSize(QSizeF(line.x2() - line.x1(), line.y2() - line.y1()))

            # Set line group visibility
            self._lineGroup.setVisible(showLine)
        else:
            self._lineGroup.setVisible(False)

    def _updateCurveGroup(self) -> None:
        if (self._item is not None):
            curve = self._item.property('curve')

            # Curve
            showCurve = False
            if (isinstance(curve, QPolygonF) and curve.size() >= 4):
                showCurve = True
                self._curveStartWidget.setPosition(curve.at(0))
                self._curveStartControlWidget.setPosition(curve.at(1))
                self._curveEndControlWidget.setPosition(curve.at(2))
                self._curveEndWidget.setPosition(curve.at(3))

            # Set curve group visibility
            self._curveGroup.setVisible(showCurve)
        else:
            self._curveGroup.setVisible(False)

    def _updateRectGroup(self) -> None:
        if (self._item is not None):
            rect = self._item.property('rect')
            cornerRadius = self._item.property('cornerRadius')

            # Rect
            showRect = False
            if (isinstance(rect, QRectF)):
                showRect = True
                self._rectTopLeftWidget.setPosition(rect.topLeft())
                self._rectBottomRightWidget.setPosition(rect.bottomRight())
                self._rectSizeWidget.setSize(rect.size())

            # Corner radius
            showCornerRadius = False
            if (isinstance(cornerRadius, float)):
                showCornerRadius = True
                self._rectCornerRadiusEdit.setSize(cornerRadius)

            # Set rect group visibility
            self._rectLayout.setRowVisible(self._rectTopLeftWidget, showRect)
            self._rectLayout.setRowVisible(self._rectBottomRightWidget, showRect)
            self._rectLayout.setRowVisible(self._rectSizeWidget, showRect)
            self._rectLayout.setRowVisible(self._rectCornerRadiusEdit, showCornerRadius)
            self._rectGroup.setVisible(showRect or showCornerRadius)
        else:
            self._rectGroup.setVisible(False)

    def _updatePenBrushGroup(self) -> None:
        if (self._item is not None):
            pen = self._item.property('pen')
            brush = self._item.property('brush')

            # Pen
            showPen = False
            if (isinstance(pen, QPen)):
                showPen = True
                self._penStyleCombo.setCurrentIndex(pen.style().value)      # type: ignore
                self._penWidthEdit.setSize(pen.widthF())
                self._penColorWidget.setColor(pen.brush().color())

            # Brush
            showBrush = False
            if (isinstance(brush, QBrush)):
                showBrush = True
                self._brushColorWidget.setColor(brush.color())

            # Set pen/brush group visibility
            self._penBrushLayout.setRowVisible(self._penStyleCombo, showPen)
            self._penBrushLayout.setRowVisible(self._penWidthEdit, showPen)
            self._penBrushLayout.setRowVisible(self._penColorWidget, showPen)
            self._penBrushLayout.setRowVisible(self._brushColorWidget, showBrush)
            self._penBrushGroup.setVisible(showPen or showBrush)
        else:
            self._penBrushGroup.setVisible(False)

    def _updateArrowGroup(self) -> None:
        if (self._item is not None):
            startArrow = self._item.property('startArrow')
            endArrow = self._item.property('endArrow')

            # Start arrow
            showStartArrow = False
            if (isinstance(startArrow, DrawingArrow)):
                showStartArrow = True
                self._startArrowStyleCombo.setCurrentIndex(startArrow.style().value)
                self._startArrowSizeEdit.setSize(startArrow.size())

            # End arrow
            showEndArrow = False
            if (isinstance(endArrow, DrawingArrow)):
                showEndArrow = True
                self._endArrowStyleCombo.setCurrentIndex(endArrow.style().value)
                self._endArrowSizeEdit.setSize(endArrow.size())

            # Set arrow group visibility
            self._arrowLayout.setRowVisible(self._startArrowStyleCombo, showStartArrow)
            self._arrowLayout.setRowVisible(self._startArrowSizeEdit, showStartArrow)
            self._arrowLayout.setRowVisible(self._endArrowStyleCombo, showEndArrow)
            self._arrowLayout.setRowVisible(self._endArrowSizeEdit, showEndArrow)
            self._arrowGroup.setVisible(showStartArrow or showEndArrow)
        else:
            self._arrowGroup.setVisible(False)

    def _updateTextGroup(self) -> None:
        if (self._item is not None):
            font = self._item.property('font')
            textAlignment = self._item.property('textAlignment')
            textColor = self._item.property('textColor')
            text = self._item.property('caption')

            # Font
            showFont = False
            if (isinstance(font, QFont)):
                showFont = True
                self._fontFamilyCombo.setCurrentFont(font)
                self._fontSizeEdit.setSize(font.pointSizeF())
                self._fontBoldButton.setChecked(font.bold())
                self._fontItalicButton.setChecked(font.italic())
                self._fontUnderlineButton.setChecked(font.underline())
                self._fontStrikeOutButton.setChecked(font.strikeOut())

            # Text Alignment
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

            # Text Color
            showTextColor = False
            if (isinstance(textColor, QColor)):
                showTextColor = True
                self._textColorWidget.setColor(textColor)

            # Text
            showText = False
            if (isinstance(text, str)):
                showText = True
                if (self._textWidget.toPlainText() != text):
                    self._textWidget.setPlainText(text)

            # Set text group visibility
            self._textLayout.setRowVisible(self._fontFamilyCombo, showFont)
            self._textLayout.setRowVisible(self._fontSizeEdit, showFont)
            self._textLayout.setRowVisible(self._fontStyleWidget, showFont)
            self._textLayout.setRowVisible(self._textAlignmentWidget, showTextAlignment)
            self._textLayout.setRowVisible(self._textColorWidget, showTextColor)
            self._textLayout.setRowVisible(self._textWidget, showText)
            self._textGroup.setVisible(showFont or showTextAlignment or showTextColor or showText)
        else:
            self._textGroup.setVisible(False)

    # ==================================================================================================================

    def _handleLineStartChange(self, position: QPointF) -> None:
        if (self._item is not None):
            self.itemResized.emit(self._item.resizeStartPoint(), position)

    def _handleLineEndChange(self, position: QPointF) -> None:
        if (self._item is not None):
            self.itemResized.emit(self._item.resizeEndPoint(), position)

    def _handleLineSizeChange(self, size: QSizeF) -> None:
        position = QPointF(self._lineStartWidget.position().x() + size.width(),
                           self._lineStartWidget.position().y() + size.height())
        if (self._item is not None):
            self.itemResized.emit(self._item.resizeEndPoint(), position)

    # ==================================================================================================================

    def _handleCurveStartChange(self, position: QPointF) -> None:
        if (self._item is not None):
            points = self._item.points()
            if (len(points) >= 4):
                self.itemResized.emit(points[0], position)

    def _handleCurveStartControlChange(self, position: QPointF) -> None:
        if (self._item is not None):
            points = self._item.points()
            if (len(points) >= 4):
                self.itemResized.emit(points[1], position)

    def _handleCurveEndControlChange(self, position: QPointF) -> None:
        if (self._item is not None):
            points = self._item.points()
            if (len(points) >= 4):
                self.itemResized.emit(points[2], position)

    def _handleCurveEndChange(self, position: QPointF) -> None:
        if (self._item is not None):
            points = self._item.points()
            if (len(points) >= 4):
                self.itemResized.emit(points[3], position)

    # ==================================================================================================================

    def _handleRectTopLeftChange(self, position: QPointF) -> None:
        if (self._item is not None):
            self.itemResized.emit(self._item.resizeStartPoint(), position)

    def _handleRectBottomRightChange(self, position: QPointF) -> None:
        if (self._item is not None):
            self.itemResized.emit(self._item.resizeEndPoint(), position)

    def _handleRectSizeChange(self, size: QSizeF) -> None:
        if (self._item is not None):
            position = QPointF(self._rectTopLeftWidget.position().x() + size.width(),
                               self._rectTopLeftWidget.position().y() + size.height())
            self.itemResized.emit(self._item.resizeEndPoint(), position)

    def _handleRectCornerRadiusChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('cornerRadius', size)

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

    def _handleStartArrowStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('startArrowStyle', index)

    def _handleStartArrowSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('startArrowSize', size)

    def _handleEndArrowStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('endArrowStyle', index)

    def _handleEndArrowSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('endArrowSize', size)

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
        self.itemPropertyChanged.emit('textAlignment', horizontal | vertical)

    def _handleTextColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('textColor', color)

    def _handleTextChange(self) -> None:
        self.itemPropertyChanged.emit('caption', self._textWidget.toPlainText())
