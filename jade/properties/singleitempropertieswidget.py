# singleitempropertieswidget.py
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

from PySide6.QtCore import Qt, QLineF, QPointF, QRectF, QSizeF, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPolygonF
from PySide6.QtWidgets import (QComboBox, QFontComboBox, QFormLayout, QFrame, QGroupBox, QHBoxLayout, QPlainTextEdit,
                               QToolButton, QVBoxLayout, QWidget)
from ..items.odgcurve import OdgCurve
from ..items.odgfontstyle import OdgFontStyle
from ..items.odgitem import OdgItem
from ..items.odgitempoint import OdgItemPoint
from ..items.odgmarker import OdgMarker
from ..drawing.odgunits import OdgUnits
from .helperwidgets import ColorWidget, PositionWidget, LengthEdit, SizeWidget


class SingleItemPropertiesWidget(QWidget):
    itemMoved = Signal(QPointF)
    itemResized = Signal(OdgItemPoint, QPointF)
    itemResized2 = Signal(OdgItemPoint, QPointF, OdgItemPoint, QPointF)
    itemPropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._item: OdgItem | None = None

        self._labelWidth: int = QFontMetrics(super().font()).boundingRect('Bottom-Right Margin:').width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createPositionAndSizeGroup())
        layout.addWidget(self._createLineGroup())
        layout.addWidget(self._createCurveGroup())
        layout.addWidget(self._createRectGroup())
        layout.addWidget(self._createEllipseGroup())
        layout.addWidget(self._createPolygonGroup())
        layout.addWidget(self._createPolylineGroup())
        layout.addWidget(self._createPenBrushGroup())
        layout.addWidget(self._createMarkerGroup())
        layout.addWidget(self._createTextGroup())
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    def _createPositionAndSizeGroup(self) -> QGroupBox:
        self._positionWidget: PositionWidget = PositionWidget()
        self._positionWidget.positionChanged.connect(self._handlePositionChange)

        self._sizeWidget: SizeWidget = SizeWidget()
        self._sizeWidget.sizeChanged.connect(self._handleSizeChange)

        self._positionAndSizeGroup: QGroupBox = QGroupBox('Position')
        self._positionAndSizeLayout: QFormLayout = QFormLayout()
        self._positionAndSizeLayout.addRow('Position:', self._positionWidget)
        self._positionAndSizeLayout.addRow('Size:', self._sizeWidget)
        self._positionAndSizeLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._positionAndSizeLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._positionAndSizeLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._positionAndSizeLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._positionAndSizeGroup.setLayout(self._positionAndSizeLayout)
        self._positionAndSizeGroup.setVisible(False)

        return self._positionAndSizeGroup

    def _createLineGroup(self) -> QGroupBox:
        self._lineStartWidget: PositionWidget = PositionWidget()
        self._lineStartWidget.positionChanged.connect(self._handleLineStartChange)

        self._lineEndWidget: PositionWidget = PositionWidget()
        self._lineEndWidget.positionChanged.connect(self._handleLineEndChange)

        self._lineGroup: QGroupBox = QGroupBox('Line')
        self._lineLayout: QFormLayout = QFormLayout()
        self._lineLayout.addRow('Start Point:', self._lineStartWidget)
        self._lineLayout.addRow('End Point:', self._lineEndWidget)
        self._lineLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._lineLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._lineLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._lineLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._lineGroup.setLayout(self._lineLayout)
        self._lineGroup.setVisible(False)

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
        self._curveGroup.setVisible(False)

        return self._curveGroup

    def _createRectGroup(self) -> QGroupBox:
        self._rectPositionWidget: PositionWidget = PositionWidget()
        self._rectPositionWidget.positionChanged.connect(self._handleRectPositionChange)

        self._rectSizeWidget: SizeWidget = SizeWidget()
        self._rectSizeWidget.sizeChanged.connect(self._handleRectSizeChange)

        self._rectCornerRadiusEdit: LengthEdit = LengthEdit()
        self._rectCornerRadiusEdit.lengthChanged.connect(self._handleRectCornerRadiusChange)

        self._rectGroup: QGroupBox = QGroupBox('Rect')
        self._rectLayout: QFormLayout = QFormLayout()
        self._rectLayout.addRow('Position:', self._rectPositionWidget)
        self._rectLayout.addRow('Size:', self._rectSizeWidget)
        self._rectLayout.addRow('Corner Radius:', self._rectCornerRadiusEdit)
        self._rectLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._rectLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._rectLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._rectLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._rectGroup.setLayout(self._rectLayout)
        self._rectGroup.setVisible(False)

        return self._rectGroup

    def _createEllipseGroup(self) -> QGroupBox:
        self._ellipsePositionWidget: PositionWidget = PositionWidget()
        self._ellipsePositionWidget.positionChanged.connect(self._handleEllipsePositionChange)

        self._ellipseSizeWidget: SizeWidget = SizeWidget()
        self._ellipseSizeWidget.sizeChanged.connect(self._handleEllipseSizeChange)

        self._ellipseGroup: QGroupBox = QGroupBox('Ellipse')
        self._ellipseLayout: QFormLayout = QFormLayout()
        self._ellipseLayout.addRow('Position:', self._ellipsePositionWidget)
        self._ellipseLayout.addRow('Size:', self._ellipseSizeWidget)
        self._ellipseLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._ellipseLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._ellipseLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._ellipseLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._ellipseGroup.setLayout(self._ellipseLayout)
        self._ellipseGroup.setVisible(False)

        return self._ellipseGroup

    def _createPolygonGroup(self) -> QGroupBox:
        self._polygonWidgets: list[PositionWidget] = []

        self._polygonGroup: QGroupBox = QGroupBox('Polygon')
        self._polygonLayout: QFormLayout = QFormLayout()
        self._polygonLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._polygonLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._polygonLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._polygonGroup.setLayout(self._polygonLayout)
        self._polygonGroup.setVisible(False)

        return self._polygonGroup

    def _createPolylineGroup(self) -> QGroupBox:
        self._polylineWidgets: list[PositionWidget] = []

        self._polylineGroup: QGroupBox = QGroupBox('Polyline')
        self._polylineLayout: QFormLayout = QFormLayout()
        self._polylineLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._polylineLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._polylineLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._polylineGroup.setLayout(self._polylineLayout)
        self._polylineGroup.setVisible(False)

        return self._polylineGroup

    def _createPenBrushGroup(self) -> QGroupBox:
        self._penStyleCombo: QComboBox = QComboBox()
        self._penStyleCombo.addItems(['None', 'Solid', 'Dashed', 'Dotted', 'Dash-Dotted', 'Dash-Dot-Dotted'])
        self._penStyleCombo.activated.connect(self._handlePenStyleChange)   # type: ignore

        self._penWidthEdit: LengthEdit = LengthEdit()
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
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-triangle-start.png'), 'Triangle')
        self._startMarkerStyleCombo.addItem(QIcon('icons:marker/marker-circle-start.png'), 'Circle')
        self._startMarkerStyleCombo.activated.connect(self._handleStartMarkerStyleChange)   # type: ignore

        self._startMarkerSizeEdit: LengthEdit = LengthEdit()
        self._startMarkerSizeEdit.lengthChanged.connect(self._handleStartMarkerSizeChange)

        self._endMarkerStyleCombo: QComboBox = QComboBox()
        self._endMarkerStyleCombo.addItem(QIcon('icons:marker/marker-none.png'), 'None')
        self._endMarkerStyleCombo.addItem(QIcon('icons:marker/marker-triangle-end.png'), 'Triangle')
        self._endMarkerStyleCombo.addItem(QIcon('icons:marker/marker-circle-end.png'), 'Circle')
        self._endMarkerStyleCombo.activated.connect(self._handleEndMarkerStyleChange)       # type: ignore

        self._endMarkerSizeEdit: LengthEdit = LengthEdit()
        self._endMarkerSizeEdit.lengthChanged.connect(self._handleEndMarkerSizeChange)

        self._markerGroup: QGroupBox = QGroupBox('Marker')
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
        self._fontFamilyCombo.setMaximumWidth(162)
        self._fontFamilyCombo.activated.connect(self._handleFontFamilyChange)       # type: ignore

        self._fontSizeEdit: LengthEdit = LengthEdit()
        self._fontSizeEdit.lengthChanged.connect(self._handleFontSizeChange)

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
        self._textAlignmentBottomButton.setIcon(QIcon('icons:align-vertical-bottom.png'))
        self._textAlignmentBottomButton.setToolTip('Align Bottom')
        self._textAlignmentBottomButton.setCheckable(True)
        self._textAlignmentBottomButton.setAutoExclusive(True)
        self._textAlignmentBottomButton.clicked.connect(self._handleTextAlignmentChange)    # type: ignore

        self._textPaddingWidget: SizeWidget = SizeWidget()
        self._textPaddingWidget.sizeChanged.connect(self._handleTextPaddingChange)

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
        self._textLayout.addRow('Text Padding:', self._textPaddingWidget)
        self._textLayout.addRow('Text Color:', self._textColorWidget)
        self._textLayout.addRow('Text:', self._textWidget)
        self._textLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self._textLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._textLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._textLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(self._labelWidth)
        self._textLayout.setRowVisible(self._textWidget, False)
        self._textGroup.setLayout(self._textLayout)

        return self._textGroup

    # ==================================================================================================================

    def setItem(self, item: OdgItem | None) -> None:
        self._item = item
        self.blockSignals(True)
        self._updatePositionAndSizeGroup()
        self._updateLineGroup()
        self._updateCurveGroup()
        self._updateRectGroup()
        self._updateEllipseGroup()
        self._updatePolygonGroup()
        self._updatePolylineGroup()
        self._updatePenBrushGroup()
        self._updateMarkerGroup()
        self._updateTextGroup()
        self.blockSignals(False)

    def _updatePositionAndSizeGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            position = self._item.property('position')
            size = self._item.property('size')

            # Position
            showPosition = False
            if (isinstance(position, QPointF)):
                showPosition = True
                self._positionWidget.setPosition(position)

            # Size
            showSize = False
            if (isinstance(size, QSizeF)):
                showSize = True
                self._sizeWidget.setSize(size)

            # Set position group visibility
            self._positionAndSizeLayout.setRowVisible(self._positionWidget, showPosition)
            self._positionAndSizeLayout.setRowVisible(self._sizeWidget, showSize)
            self._positionAndSizeGroup.setVisible(showPosition or showSize)
        else:
            self._positionAndSizeGroup.setVisible(False)

    def _updateLineGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            line = self._item.property('line')

            # Line
            showLine = False
            if (isinstance(line, QLineF)):
                showLine = True
                self._lineStartWidget.setPosition(self._item.mapToScene(line.p1()))
                self._lineEndWidget.setPosition(self._item.mapToScene(line.p2()))

            # Set line group visibility
            self._lineGroup.setVisible(showLine)
        else:
            self._lineGroup.setVisible(False)

    def _updateCurveGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            curve = self._item.property('curve')

            # Curve
            showCurve = False
            if (isinstance(curve, OdgCurve)):
                showCurve = True
                self._curveStartWidget.setPosition(self._item.mapToScene(curve.p1()))
                self._curveStartControlWidget.setPosition(self._item.mapToScene(curve.cp1()))
                self._curveEndControlWidget.setPosition(self._item.mapToScene(curve.cp2()))
                self._curveEndWidget.setPosition(self._item.mapToScene(curve.p2()))

            # Set curve group visibility
            self._curveGroup.setVisible(showCurve)
        else:
            self._curveGroup.setVisible(False)

    def _updateRectGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            rect = self._item.property('rect')
            cornerRadius = self._item.property('cornerRadius')

            # Rect
            showRect = False
            if (isinstance(rect, QRectF)):
                showRect = True
                self._rectPositionWidget.setPosition(self._item.mapToScene(rect.center()))
                size = rect.size()
                if (self._item.rotation() in (1, 3)):
                    size = QSizeF(size.height(), size.width())
                self._rectSizeWidget.setSize(size)

            # Corner radius
            showCornerRadius = False
            if (isinstance(cornerRadius, float)):
                showCornerRadius = True
                self._rectCornerRadiusEdit.setLength(cornerRadius)

            # Set rect group visibility
            self._rectLayout.setRowVisible(self._rectPositionWidget, showRect)
            self._rectLayout.setRowVisible(self._rectSizeWidget, showRect)
            self._rectLayout.setRowVisible(self._rectCornerRadiusEdit, showCornerRadius)
            self._rectGroup.setVisible(showRect or showCornerRadius)
        else:
            self._rectGroup.setVisible(False)

    def _updateEllipseGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            ellipse = self._item.property('ellipse')

            # Ellipse
            showEllipse = False
            if (isinstance(ellipse, QRectF)):
                showEllipse = True
                self._ellipsePositionWidget.setPosition(self._item.mapToScene(ellipse.center()))
                size = ellipse.size()
                if (self._item.rotation() in (1, 3)):
                    size = QSizeF(size.height(), size.width())
                self._ellipseSizeWidget.setSize(size)

            # Set ellipse group visibility
            self._ellipseGroup.setVisible(showEllipse)
        else:
            self._ellipseGroup.setVisible(False)

    def _updatePolygonGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            polygon = self._item.property('polygon')

            # Polygon
            showPolygon = False
            if (isinstance(polygon, QPolygonF)):
                showPolygon = True
                if (len(self._polygonWidgets) != polygon.size()):
                    while (self._polygonLayout.rowCount() > 0):
                        self._polygonLayout.removeRow(0)
                    self._polygonWidgets.clear()

                    for index in range(polygon.size()):
                        newPolygonWidget = PositionWidget()
                        newPolygonWidget.positionChanged.connect(self._handlePolygonChange)
                        if (index == 0):
                            self._polygonLayout.addRow('First Point:', newPolygonWidget)
                            self._polygonLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(
                                self._labelWidth)
                        elif (index == polygon.size() - 1):
                            self._polygonLayout.addRow('Last Point:', newPolygonWidget)
                        else:
                            self._polygonLayout.addRow('', newPolygonWidget)
                        self._polygonWidgets.append(newPolygonWidget)

                for index in range(polygon.size()):
                    self._polygonWidgets[index].setPosition(self._item.mapToScene(polygon.at(index)))

            # Set polygon group visibility
            self._polygonGroup.setVisible(showPolygon)
        else:
            self._polygonGroup.setVisible(False)

    def _updatePolylineGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            polyline = self._item.property('polyline')

            # Polyline
            showPolyline = False
            if (isinstance(polyline, QPolygonF)):
                showPolyline = True
                if (len(self._polylineWidgets) != polyline.size()):
                    while (self._polylineLayout.rowCount() > 0):
                        self._polylineLayout.removeRow(0)
                    self._polylineWidgets.clear()

                    for index in range(polyline.size()):
                        newPolylineWidget = PositionWidget()
                        newPolylineWidget.positionChanged.connect(self._handlePolylineChange)
                        if (index == 0):
                            self._polylineLayout.addRow('Start Point:', newPolylineWidget)
                            self._polylineLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(
                                self._labelWidth)
                        elif (index == polyline.size() - 1):
                            self._polylineLayout.addRow('End Point:', newPolylineWidget)
                        else:
                            self._polylineLayout.addRow('', newPolylineWidget)
                        self._polylineWidgets.append(newPolylineWidget)

                for index in range(polyline.size()):
                    self._polylineWidgets[index].setPosition(self._item.mapToScene(polyline.at(index)))

            # Set polyline group visibility
            self._polylineGroup.setVisible(showPolyline)
        else:
            self._polylineGroup.setVisible(False)

    def _updatePenBrushGroup(self) -> None:
        if (isinstance(self._item, OdgItem)):
            penStyle = self._item.property('penStyle')
            penWidth = self._item.property('penWidth')
            penColor = self._item.property('penColor')
            brushColor = self._item.property('brushColor')

            # Pen
            showPenStyle = False
            if (isinstance(penStyle, Qt.PenStyle)):
                showPenStyle = True
                self.setPenStyle(penStyle)

            showPenWidth = False
            if (isinstance(penWidth, float)):
                showPenWidth = True
                self.setPenWidth(penWidth)

            showPenColor = False
            if (isinstance(penColor, QColor)):
                showPenColor = True
                self.setPenColor(penColor)

            # Brush
            showBrushColor = False
            if (isinstance(brushColor, QColor)):
                showBrushColor = True
                self.setBrushColor(brushColor)

            # Set pen/brush group visibility
            self._penBrushLayout.setRowVisible(self._penStyleCombo, showPenStyle)
            self._penBrushLayout.setRowVisible(self._penWidthEdit, showPenWidth)
            self._penBrushLayout.setRowVisible(self._penColorWidget, showPenColor)
            self._penBrushLayout.setRowVisible(self._brushColorWidget, showBrushColor)
            self._penBrushGroup.setVisible(showPenStyle or showPenWidth or showPenColor or showBrushColor)
        else:
            self._penBrushLayout.setRowVisible(self._penStyleCombo, True)
            self._penBrushLayout.setRowVisible(self._penWidthEdit, True)
            self._penBrushLayout.setRowVisible(self._penColorWidget, True)
            self._penBrushLayout.setRowVisible(self._brushColorWidget, True)
            self._penBrushGroup.setVisible(True)

    def _updateMarkerGroup(self) -> None:
        if (self._item is not None):
            startMarkerStyle = self._item.property('startMarkerStyle')
            startMarkerSize = self._item.property('startMarkerSize')
            endMarkerStyle = self._item.property('endMarkerStyle')
            endMarkerSize = self._item.property('endMarkerSize')

            # Start marker
            showStartMarkerStyle = False
            if (isinstance(startMarkerStyle, OdgMarker.Style)):
                showStartMarkerStyle = True
                self.setStartMarkerStyle(startMarkerStyle)

            showStartMarkerSize = False
            if (isinstance(startMarkerSize, float)):
                showStartMarkerSize = True
                self.setStartMarkerSize(startMarkerSize)

            # End marker
            showEndMarkerStyle = False
            if (isinstance(endMarkerStyle, OdgMarker.Style)):
                showEndMarkerStyle = True
                self.setEndMarkerStyle(endMarkerStyle)

            showEndMarkerSize = False
            if (isinstance(endMarkerSize, float)):
                showEndMarkerSize = True
                self.setEndMarkerSize(endMarkerSize)

            # Set marker group visibility
            self._markerLayout.setRowVisible(self._startMarkerStyleCombo, showStartMarkerStyle)
            self._markerLayout.setRowVisible(self._startMarkerSizeEdit, showStartMarkerSize)
            self._markerLayout.setRowVisible(self._endMarkerStyleCombo, showEndMarkerStyle)
            self._markerLayout.setRowVisible(self._endMarkerSizeEdit, showEndMarkerSize)
            self._markerGroup.setVisible(showStartMarkerStyle or showStartMarkerSize or showEndMarkerStyle or
                                         showEndMarkerSize)
        else:
            self._markerLayout.setRowVisible(self._startMarkerStyleCombo, True)
            self._markerLayout.setRowVisible(self._startMarkerSizeEdit, True)
            self._markerLayout.setRowVisible(self._endMarkerStyleCombo, True)
            self._markerLayout.setRowVisible(self._endMarkerSizeEdit, True)
            self._markerGroup.setVisible(True)

    def _updateTextGroup(self) -> None:
        if (self._item is not None):
            fontFamily = self._item.property('fontFamily')
            fontSize = self._item.property('fontSize')
            fontStyle = self._item.property('fontStyle')
            textAlignment = self._item.property('textAlignment')
            textColor = self._item.property('textColor')
            textPadding = self._item.property('textPadding')
            text = self._item.property('caption')

            # Font
            showFontFamily = False
            if (isinstance(fontFamily, str)):
                showFontFamily = True
                self.setFontFamily(fontFamily)

            showFontSize = False
            if (isinstance(fontSize, float)):
                showFontSize = True
                self.setFontSize(fontSize)

            showFontStyle = False
            if (isinstance(fontStyle, OdgFontStyle)):
                showFontStyle = True
                self.setFontBold(fontStyle.bold())
                self.setFontItalic(fontStyle.italic())
                self.setFontUnderline(fontStyle.underline())
                self.setFontStrikeOut(fontStyle.strikeOut())

            # Text Alignment
            showTextAlignment = False
            if (isinstance(textAlignment, Qt.AlignmentFlag)):
                showTextAlignment = True
                self.setTextAlignment(textAlignment)

            # Text Padding
            showTextPadding = False
            if (isinstance(textPadding, QSizeF)):
                showTextPadding = True
                self.setTextPadding(textPadding)

            # Text Color
            showTextColor = False
            if (isinstance(textColor, QColor)):
                showTextColor = True
                self.setTextColor(textColor)

            # Text
            showText = False
            if (isinstance(text, str)):
                showText = True
                if (self._textWidget.toPlainText() != text):
                    self._textWidget.setPlainText(text)

            # Set text group visibility
            self._textLayout.setRowVisible(self._fontFamilyCombo, showFontFamily)
            self._textLayout.setRowVisible(self._fontSizeEdit, showFontSize)
            self._textLayout.setRowVisible(self._fontStyleWidget, showFontStyle)
            self._textLayout.setRowVisible(self._textAlignmentWidget, showTextAlignment)
            self._textLayout.setRowVisible(self._textPaddingWidget, showTextPadding)
            self._textLayout.setRowVisible(self._textColorWidget, showTextColor)
            self._textLayout.setRowVisible(self._textWidget, showText)
            self._textGroup.setVisible(showFontFamily or showFontSize or showFontStyle or showTextAlignment or
                                       showTextPadding or showTextColor or showText)
        else:
            self._textLayout.setRowVisible(self._fontFamilyCombo, True)
            self._textLayout.setRowVisible(self._fontSizeEdit, True)
            self._textLayout.setRowVisible(self._fontStyleWidget, True)
            self._textLayout.setRowVisible(self._textAlignmentWidget, True)
            self._textLayout.setRowVisible(self._textPaddingWidget, True)
            self._textLayout.setRowVisible(self._textColorWidget, True)
            self._textLayout.setRowVisible(self._textWidget, False)
            self._textGroup.setVisible(True)

    # ==================================================================================================================

    def setUnits(self, units: OdgUnits) -> None:
        self._positionWidget.setUnits(units)
        self._sizeWidget.setUnits(units)

        self._lineStartWidget.setUnits(units)
        self._lineEndWidget.setUnits(units)

        self._curveStartWidget.setUnits(units)
        self._curveStartControlWidget.setUnits(units)
        self._curveEndControlWidget.setUnits(units)
        self._curveEndWidget.setUnits(units)

        self._rectPositionWidget.setUnits(units)
        self._rectSizeWidget.setUnits(units)
        self._rectCornerRadiusEdit.setUnits(units)

        self._ellipsePositionWidget.setUnits(units)
        self._ellipseSizeWidget.setUnits(units)

        for widget in self._polygonWidgets:
            widget.setUnits(units)
        for widget in self._polylineWidgets:
            widget.setUnits(units)

        self._penWidthEdit.setUnits(units)
        self._startMarkerSizeEdit.setUnits(units)
        self._endMarkerSizeEdit.setUnits(units)
        self._fontSizeEdit.setUnits(units)
        self._textPaddingWidget.setUnits(units)

    # ==================================================================================================================

    def setPenStyle(self, style: Qt.PenStyle) -> None:
        self._penStyleCombo.setCurrentIndex(style.value)    # type: ignore

    def setPenWidth(self, width: float) -> None:
        self._penWidthEdit.setLength(width)

    def setPenColor(self, color: QColor) -> None:
        self._penColorWidget.setColor(color)

    def setBrushColor(self, color: QColor) -> None:
        self._brushColorWidget.setColor(color)

    def setStartMarkerStyle(self, style: OdgMarker.Style) -> None:
        self._startMarkerStyleCombo.setCurrentIndex(style)

    def setStartMarkerSize(self, size: float) -> None:
        self._startMarkerSizeEdit.setLength(size)

    def setEndMarkerStyle(self, style: OdgMarker.Style) -> None:
        self._endMarkerStyleCombo.setCurrentIndex(style)

    def setEndMarkerSize(self, size: float) -> None:
        self._endMarkerSizeEdit.setLength(size)

    def setFontFamily(self, family: str) -> None:
        font = QFont()
        font.setFamily(family)
        self._fontFamilyCombo.setCurrentFont(font)

    def setFontSize(self, size: float) -> None:
        self._fontSizeEdit.setLength(size)

    def setFontBold(self, bold: bool) -> None:
        self._fontBoldButton.setChecked(bold)

    def setFontItalic(self, bold: bool) -> None:
        self._fontItalicButton.setChecked(bold)

    def setFontUnderline(self, bold: bool) -> None:
        self._fontUnderlineButton.setChecked(bold)

    def setFontStrikeOut(self, bold: bool) -> None:
        self._fontStrikeOutButton.setChecked(bold)

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

    def setTextPadding(self, padding: QSizeF) -> None:
        self._textPaddingWidget.setSize(padding)

    def setTextColor(self, color: QColor) -> None:
        self._textColorWidget.setColor(color)

    def penStyle(self) -> Qt.PenStyle:
        return Qt.PenStyle(self._penStyleCombo.currentIndex())

    def penWidth(self) -> float:
        return self._penWidthEdit.length()

    def penColor(self) -> QColor:
        return self._penColorWidget.color()

    def brushColor(self) -> QColor:
        return self._brushColorWidget.color()

    def startMarkerStyle(self) -> OdgMarker.Style:
        return OdgMarker.Style(self._startMarkerStyleCombo.currentIndex())

    def startMarkerSize(self) -> float:
        return self._startMarkerSizeEdit.length()

    def endMarkerStyle(self) -> OdgMarker.Style:
        return OdgMarker.Style(self._endMarkerStyleCombo.currentIndex())

    def endMarkerSize(self) -> float:
        return self._endMarkerSizeEdit.length()

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
        vertical = Qt.AlignmentFlag.AlignTop
        if (self._textAlignmentVCenterButton.isChecked()):
            vertical = Qt.AlignmentFlag.AlignVCenter
        elif (self._textAlignmentBottomButton.isChecked()):
            vertical = Qt.AlignmentFlag.AlignBottom
        return (horizontal | vertical)

    def textPadding(self) -> QSizeF:
        return self._textPaddingWidget.size()

    def textColor(self) -> QColor:
        return self._textColorWidget.color()

    # ==================================================================================================================

    def _handlePositionChange(self, position: QPointF) -> None:
        self.itemMoved.emit(position)

    def _handleSizeChange(self, size: QSizeF) -> None:
        if (isinstance(self._item, OdgItem)):
            self.itemResized2.emit(self._item.placeResizeStartPoint(),
                                   self._item.mapToScene(QPointF(-size.width() / 2, -size.height() / 2)),
                                   self._item.placeResizeEndPoint(),
                                   self._item.mapToScene(QPointF(size.width() / 2, size.height() / 2)))

    # ==================================================================================================================

    def _handleLineStartChange(self, position: QPointF) -> None:
        if (self._item is not None):
            self.itemResized.emit(self._item.placeResizeStartPoint(), position)

    def _handleLineEndChange(self, position: QPointF) -> None:
        if (self._item is not None):
            self.itemResized.emit(self._item.placeResizeEndPoint(), position)

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

    def _handleRectPositionChange(self, position: QPointF) -> None:
        self.itemMoved.emit(position)

    def _handleRectSizeChange(self, size: QSizeF) -> None:
        if (isinstance(self._item, OdgItem)):
            if (self._item.rotation() in (1, 3)):
                size = QSizeF(size.height(), size.width())
            self.itemResized2.emit(self._item.placeResizeStartPoint(),
                                   self._item.mapToScene(QPointF(-size.width() / 2, -size.height() / 2)),
                                   self._item.placeResizeEndPoint(),
                                   self._item.mapToScene(QPointF(size.width() / 2, size.height() / 2)))

    def _handleRectCornerRadiusChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('cornerRadius', size)

    # ==================================================================================================================

    def _handleEllipsePositionChange(self, position: QPointF) -> None:
        self._handleRectPositionChange(position)

    def _handleEllipseSizeChange(self, size: QSizeF) -> None:
        self._handleRectSizeChange(size)

    # ==================================================================================================================

    def _handlePolygonChange(self, position: QPointF) -> None:
        if (self._item is not None):
            sender = self.sender()
            if (isinstance(sender, PositionWidget) and sender in self._polygonWidgets):
                index = self._polygonWidgets.index(sender)
                points = self._item.points()
                if (0 <= index < len(points)):
                    self.itemResized.emit(points[index], position)

    # ==================================================================================================================

    def _handlePolylineChange(self, position: QPointF) -> None:
        if (self._item is not None):
            sender = self.sender()
            if (isinstance(sender, PositionWidget) and sender in self._polylineWidgets):
                index = self._polylineWidgets.index(sender)
                points = self._item.points()
                if (0 <= index < len(points)):
                    self.itemResized.emit(points[index], position)

    # ==================================================================================================================

    def _handlePenStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('penStyle', Qt.PenStyle(index))

    def _handlePenWidthChange(self, width: float) -> None:
        self.itemPropertyChanged.emit('penWidth', width)

    def _handlePenColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('penColor', color)

    def _handleBrushColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('brushColor', color)

    # ==================================================================================================================

    def _handleStartMarkerStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('startMarkerStyle', OdgMarker.Style(index))

    def _handleStartMarkerSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('startMarkerSize', size)

    def _handleEndMarkerStyleChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('endMarkerStyle', OdgMarker.Style(index))

    def _handleEndMarkerSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('endMarkerSize', size)

    # ==================================================================================================================

    def _handleFontFamilyChange(self, index: int) -> None:
        self.itemPropertyChanged.emit('fontFamily', self._fontFamilyCombo.currentFont().family())

    def _handleFontSizeChange(self, size: float) -> None:
        self.itemPropertyChanged.emit('fontSize', size)

    def _handleFontStyleChange(self) -> None:
        style = OdgFontStyle()
        style.setBold(self._fontBoldButton.isChecked())
        style.setItalic(self._fontItalicButton.isChecked())
        style.setUnderline(self._fontUnderlineButton.isChecked())
        style.setStrikeOut(self._fontStrikeOutButton.isChecked())
        self.itemPropertyChanged.emit('fontStyle', style)

    def _handleTextAlignmentChange(self) -> None:
        self.itemPropertyChanged.emit('textAlignment', self.textAlignment())

    def _handleTextPaddingChange(self, size: QSizeF) -> None:
        self.itemPropertyChanged.emit('textPadding', size)

    def _handleTextColorChange(self, color: QColor) -> None:
        self.itemPropertyChanged.emit('textColor', color)

    def _handleTextChange(self) -> None:
        self.itemPropertyChanged.emit('caption', self._textWidget.toPlainText())
