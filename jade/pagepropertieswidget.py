# pagepropertieswidget.py
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
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QSizeF
from PyQt6.QtGui import QColor, QFontMetrics, QIntValidator
from PyQt6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLineEdit, QVBoxLayout, QWidget
from .drawingwidget import DrawingWidget
from .helperwidgets import ColorWidget, PositionWidget, SizeEdit, SizeWidget


class PagePropertiesWidget(QWidget):
    drawingPropertyChanged = pyqtSignal(str, object)
    pagePropertyChanged = pyqtSignal(str, object)

    def __init__(self) -> None:
        super().__init__()

        labelWidth = QFontMetrics(self.font()).boundingRect("Minor Grid Spacing:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createDrawingGroup(labelWidth))
        layout.addWidget(self._createPageGroup(labelWidth))
        layout.addWidget(self._createGridGroup(labelWidth))
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    def _createDrawingGroup(self, labelWidth: int) -> QGroupBox:
        self._unitsCombo: QComboBox = QComboBox()
        self._unitsCombo.addItems(['Millimeters', 'Centimeters', 'Meters', 'Kilometers', 'Mils', 'Inches', 'Feet',
                                   'Miles'])
        self._unitsCombo.activated.connect(self._handleUnitsChange)     # type: ignore

        drawingGroup = QGroupBox('Drawing')
        drawingLayout = QFormLayout()
        drawingLayout.addRow('Units:', self._unitsCombo)
        drawingLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        drawingLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        drawingLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        drawingLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        drawingGroup.setLayout(drawingLayout)

        return drawingGroup

    def _createPageGroup(self, labelWidth: int) -> QGroupBox:
        self._sceneRectTopLeftWidget: PositionWidget = PositionWidget()
        self._sceneRectTopLeftWidget.positionChanged.connect(self._handleSceneRectTopLeftChange)

        self._sceneRectSizeWidget: SizeWidget = SizeWidget()
        self._sceneRectSizeWidget.sizeChanged.connect(self._handleSceneRectSizeChange)

        self._backgroundColorWidget: ColorWidget = ColorWidget()
        self._backgroundColorWidget.colorChanged.connect(self._handleBackgroundColorChange)

        pageGroup = QGroupBox('Page')
        pageLayout = QFormLayout()
        pageLayout.addRow('Top-Left:', self._sceneRectTopLeftWidget)
        pageLayout.addRow('Size:', self._sceneRectSizeWidget)
        pageLayout.addRow('Background Color:', self._backgroundColorWidget)
        pageLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        pageLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        pageLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        pageLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        pageGroup.setLayout(pageLayout)

        return pageGroup

    def _createGridGroup(self, labelWidth: int) -> QGroupBox:
        self._gridEdit: SizeEdit = SizeEdit()
        self._sceneRectSizeWidget.sizeChanged.connect(self._handleGridChange)

        self._gridVisibleCombo: QComboBox = QComboBox()
        self._gridVisibleCombo.addItems(['Hidden', 'Visible'])
        self._gridVisibleCombo.activated.connect(self._handleGridVisibleChange)                     # type: ignore

        self._gridColorWidget: ColorWidget = ColorWidget()
        self._gridColorWidget.colorChanged.connect(self._handleGridColorChange)

        self._gridSpacingMajorWidget: QLineEdit = QLineEdit('1')
        self._gridSpacingMajorWidget.setValidator(QIntValidator(1, int(1E6), self._gridSpacingMajorWidget))
        self._gridSpacingMajorWidget.editingFinished.connect(self._handleGridSpacingMajorChange)    # type: ignore

        self._gridSpacingMinorWidget: QLineEdit = QLineEdit('1')
        self._gridSpacingMinorWidget.setValidator(QIntValidator(1, int(1E6), self._gridSpacingMinorWidget))
        self._gridSpacingMinorWidget.editingFinished.connect(self._handleGridSpacingMinorChange)    # type: ignore

        gridGroup = QGroupBox('Grid')
        gridLayout = QFormLayout()
        gridLayout.addRow('Grid:', self._gridEdit)
        gridLayout.addRow('Grid Visible:', self._gridVisibleCombo)
        gridLayout.addRow('Grid Color:', self._gridColorWidget)
        gridLayout.addRow('Major Grid Spacing:', self._gridSpacingMajorWidget)
        gridLayout.addRow('Minor Grid Spacing:', self._gridSpacingMinorWidget)
        gridLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        gridLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        gridLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        gridLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        gridGroup.setLayout(gridLayout)

        return gridGroup

    # ==================================================================================================================

    def setDrawingProperty(self, name: str, value: typing.Any) -> None:
        pass

    def setPage(self, page: DrawingWidget) -> None:
        pass

    def setPageProperty(self, name: str, value: typing.Any) -> None:
        pass

    # ==================================================================================================================

    def _handleUnitsChange(self, index: int) -> None:
        pass

    # ==================================================================================================================

    def _handleSceneRectTopLeftChange(self, position: QPointF) -> None:
        pass

    def _handleSceneRectSizeChange(self, size: QSizeF) -> None:
        pass

    def _handleBackgroundColorChange(self, color: QColor) -> None:
        pass

    # ==================================================================================================================

    def _handleGridChange(self, value: float) -> None:
        pass

    def _handleGridVisibleChange(self, index: int) -> None:
        pass

    def _handleGridColorChange(self, color: QColor) -> None:
        pass

    def _handleGridSpacingMajorChange(self, text: str) -> None:
        pass

    def _handleGridSpacingMinorChange(self, text: str) -> None:
        pass
