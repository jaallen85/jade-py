# drawingpropertieswidget.py
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
from PySide6.QtCore import Qt, QMarginsF, QSizeF, Signal
from PySide6.QtGui import QColor, QFontMetrics, QIntValidator
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLineEdit, QVBoxLayout, QWidget
from ..drawing.odgunits import OdgUnits
from .helperwidgets import ColorWidget, LengthEdit, SizeWidget, UnitsCombo


class DrawingPropertiesWidget(QWidget):
    drawingPropertyChanged = Signal(str, object)
    unitsChanged = Signal(OdgUnits)

    def __init__(self) -> None:
        super().__init__()

        self._cachedGridSpacingMajor: int = 0
        self._cachedGridSpacingMinor: int = 0

        labelWidth = QFontMetrics(self.font()).boundingRect("Bottom-Right Margin:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createPageGroup(labelWidth))
        layout.addWidget(self._createGridGroup(labelWidth))
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

    # ==================================================================================================================

    def _createPageGroup(self, labelWidth: int) -> QGroupBox:
        self._unitsCombo: UnitsCombo = UnitsCombo()
        self._unitsCombo.unitsChanged.connect(self._handleUnitsChange)
        self._unitsCombo.unitsChanged.connect(self.unitsChanged)

        self._pageSizeWidget: SizeWidget = SizeWidget()
        self._pageSizeWidget.sizeChanged.connect(self._handlePageSizeChange)
        self._unitsCombo.unitsChanged.connect(self._pageSizeWidget.setUnits)

        self._pageMarginsTopLeftEdit: SizeWidget = SizeWidget()
        self._pageMarginsTopLeftEdit.sizeChanged.connect(self._handlePageMarginsChange)
        self._unitsCombo.unitsChanged.connect(self._pageMarginsTopLeftEdit.setUnits)

        self._pageMarginsBottomRightEdit: SizeWidget = SizeWidget()
        self._pageMarginsBottomRightEdit.sizeChanged.connect(self._handlePageMarginsChange)
        self._unitsCombo.unitsChanged.connect(self._pageMarginsBottomRightEdit.setUnits)

        self._backgroundColorWidget: ColorWidget = ColorWidget()
        self._backgroundColorWidget.colorChanged.connect(self._handleBackgroundColorChange)

        pageGroup = QGroupBox('Page')
        pageLayout = QFormLayout()
        pageLayout.addRow('Units:', self._unitsCombo)
        pageLayout.addRow('Page Size:', self._pageSizeWidget)
        pageLayout.addRow('Top-Left Margin:', self._pageMarginsTopLeftEdit)
        pageLayout.addRow('Bottom-Right Margin:', self._pageMarginsBottomRightEdit)
        pageLayout.addRow('Background Color:', self._backgroundColorWidget)
        pageLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        pageLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        pageLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        pageLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        pageGroup.setLayout(pageLayout)

        return pageGroup

    def _createGridGroup(self, labelWidth: int) -> QGroupBox:
        self._gridEdit: LengthEdit = LengthEdit()
        self._gridEdit.lengthChanged.connect(self._handleGridChange)
        self._unitsCombo.unitsChanged.connect(self._gridEdit.setUnits)

        self._gridVisibleCombo: QComboBox = QComboBox()
        self._gridVisibleCombo.addItems(['Hidden', 'Visible'])
        self._gridVisibleCombo.activated.connect(self._handleGridVisibleChange)     # type: ignore

        self._gridColorWidget: ColorWidget = ColorWidget()
        self._gridColorWidget.colorChanged.connect(self._handleGridColorChange)

        self._gridSpacingMajorWidget: QLineEdit = QLineEdit('1')
        self._gridSpacingMajorWidget.setValidator(QIntValidator(1, int(1E6), self._gridSpacingMajorWidget))
        self._gridSpacingMajorWidget.editingFinished.connect(self._handleGridSpacingMajorChange)        # type: ignore

        self._gridSpacingMinorWidget: QLineEdit = QLineEdit('1')
        self._gridSpacingMinorWidget.setValidator(QIntValidator(1, int(1E6), self._gridSpacingMinorWidget))
        self._gridSpacingMinorWidget.editingFinished.connect(self._handleGridSpacingMinorChange)        # type: ignore

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

    def setUnits(self, units: OdgUnits) -> None:
        self._unitsCombo.setUnits(units)

    def setPageSize(self, size: QSizeF) -> None:
        self._pageSizeWidget.setSize(size)

    def setPageMargins(self, margins: QMarginsF) -> None:
        self._pageMarginsTopLeftEdit.setSize(QSizeF(margins.left(), margins.top()))
        self._pageMarginsBottomRightEdit.setSize(QSizeF(margins.right(), margins.bottom()))

    def setBackgroundColor(self, color: QColor) -> None:
        self._backgroundColorWidget.setColor(color)

    def setGrid(self, grid: float) -> None:
        self._gridEdit.setLength(grid)

    def setGridVisible(self, visible: bool) -> None:
        self._gridVisibleCombo.setCurrentIndex(1 if visible else 0)

    def setGridColor(self, color: QColor) -> None:
        self._gridColorWidget.setColor(color)

    def setGridSpacingMajor(self, spacing: int) -> None:
        self._gridSpacingMajorWidget.setText(str(spacing))
        self._cachedGridSpacingMajor = spacing

    def setGridSpacingMinor(self, spacing: int) -> None:
        self._gridSpacingMinorWidget.setText(str(spacing))
        self._cachedGridSpacingMinor = spacing

    def units(self) -> OdgUnits:
        return self._unitsCombo.units()

    def pageSize(self) -> QSizeF:
        return self._pageSizeWidget.size()

    def pageMargins(self) -> QMarginsF:
        return QMarginsF(self._pageMarginsTopLeftEdit.size().width(),
                         self._pageMarginsTopLeftEdit.size().height(),
                         self._pageMarginsBottomRightEdit.size().width(),
                         self._pageMarginsBottomRightEdit.size().height())

    def backgroundColor(self) -> QColor:
        return self._backgroundColorWidget.color()

    def grid(self) -> float:
        return self._gridEdit.length()

    def isGridVisible(self) -> bool:
        return (self._gridVisibleCombo.currentIndex() == 1)

    def gridColor(self) -> QColor:
        return self._gridColorWidget.color()

    def gridSpacingMajor(self) -> int:
        try:
            return int(self._gridSpacingMajorWidget.text())
        except ValueError:
            pass
        return self._cachedGridSpacingMajor

    def gridSpacingMinor(self) -> int:
        try:
            return int(self._gridSpacingMinorWidget.text())
        except ValueError:
            pass
        return self._cachedGridSpacingMinor

    # ==================================================================================================================

    def setDrawingProperty(self, name: str, value: Any) -> None:
        self.blockSignals(True)
        if (name == 'units' and isinstance(value, OdgUnits)):
            self.setUnits(value)
        elif (name == 'pageSize' and isinstance(value, QSizeF)):
            self.setPageSize(value)
        elif (name == 'pageMargins' and isinstance(value, QMarginsF)):
            self.setPageMargins(value)
        elif (name == 'backgroundColor' and isinstance(value, QColor)):
            self.setBackgroundColor(value)
        elif (name == 'grid' and isinstance(value, float)):
            self.setGrid(value)
        elif (name == 'gridVisible' and isinstance(value, bool)):
            self.setGridVisible(value)
        elif (name == 'gridColor' and isinstance(value, QColor)):
            self.setGridColor(value)
        elif (name == 'gridSpacingMajor' and isinstance(value, int)):
            self.setGridSpacingMajor(value)
        elif (name == 'gridSpacingMinor' and isinstance(value, int)):
            self.setGridSpacingMinor(value)
        self.blockSignals(False)

    # ==================================================================================================================

    def _handleUnitsChange(self, units: OdgUnits) -> None:
        self.drawingPropertyChanged.emit('units', units)

    def _handlePageSizeChange(self, size: QSizeF) -> None:
        self.drawingPropertyChanged.emit('pageSize', size)

    def _handlePageMarginsChange(self, _: QSizeF) -> None:
        self.drawingPropertyChanged.emit('pageMargins', self.pageMargins())

    def _handleBackgroundColorChange(self, color: QColor) -> None:
        self.drawingPropertyChanged.emit('backgroundColor', color)

    def _handleGridChange(self, value: float) -> None:
        self.drawingPropertyChanged.emit('grid', value)

    def _handleGridVisibleChange(self, index: int) -> None:
        self.drawingPropertyChanged.emit('gridVisible', (index == 1))

    def _handleGridColorChange(self, color: QColor) -> None:
        self.drawingPropertyChanged.emit('gridColor', color)

    def _handleGridSpacingMajorChange(self) -> None:
        try:
            self.drawingPropertyChanged.emit('gridSpacingMajor', int(self._gridSpacingMajorWidget.text()))
            self.blockSignals(True)
            self._gridSpacingMajorWidget.clearFocus()
            self.blockSignals(False)
        except ValueError:
            self._gridSpacingMajorWidget.setText(str(self._cachedGridSpacingMajor))

    def _handleGridSpacingMinorChange(self) -> None:
        try:
            self.drawingPropertyChanged.emit('gridSpacingMinor', int(self._gridSpacingMinorWidget.text()))
            self.blockSignals(True)
            self._gridSpacingMinorWidget.clearFocus()
            self.blockSignals(False)
        except ValueError:
            self._gridSpacingMinorWidget.setText(str(self._cachedGridSpacingMinor))
