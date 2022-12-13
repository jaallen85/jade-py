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
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF, Signal
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QIntValidator
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLineEdit, QVBoxLayout, QWidget
from ..drawing.drawingpagewidget import DrawingPageWidget
from .helperwidgets import ColorWidget, PositionWidget, SizeEdit, SizeWidget


class PagePropertiesWidget(QWidget):
    drawingPropertyChanged = Signal(str, object)
    pagePropertyChanged = Signal(str, object)

    def __init__(self) -> None:
        super().__init__()

        self._cachedGridSpacingMajor: int = 0
        self._cachedGridSpacingMinor: int = 0

        labelWidth = QFontMetrics(self.font()).boundingRect("Minor Grid Spacing:").width() + 8

        layout = QVBoxLayout()
        layout.addWidget(self._createPageGroup(labelWidth))
        layout.addWidget(self._createGridGroup(labelWidth))
        layout.addWidget(QWidget(), 100)
        self.setLayout(layout)

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
        self._gridEdit.sizeChanged.connect(self._handleGridChange)

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

    def setSceneRect(self, rect: QRectF) -> None:
        self._sceneRectTopLeftWidget.setPosition(rect.topLeft())
        self._sceneRectSizeWidget.setSize(rect.size())

    def setBackgroundBrush(self, brush: QBrush) -> None:
        self._backgroundColorWidget.setColor(brush.color())

    def setGrid(self, grid: float) -> None:
        self._gridEdit.setSize(grid)

    def setGridVisible(self, visible: bool) -> None:
        self._gridVisibleCombo.setCurrentIndex(1 if visible else 0)

    def setGridBrush(self, brush: QBrush) -> None:
        self._gridColorWidget.setColor(brush.color())

    def setGridSpacingMajor(self, spacing: int) -> None:
        self._gridSpacingMajorWidget.setText(str(spacing))
        self._cachedGridSpacingMajor = spacing

    def setGridSpacingMinor(self, spacing: int) -> None:
        self._gridSpacingMinorWidget.setText(str(spacing))
        self._cachedGridSpacingMinor = spacing

    def sceneRect(self) -> QRectF:
        return QRectF(self._sceneRectTopLeftWidget.position(), self._sceneRectSizeWidget.size()).normalized()

    def backgroundBrush(self) -> QBrush:
        return QBrush(self._backgroundColorWidget.color())

    def grid(self) -> float:
        return self._gridEdit.size()

    def isGridVisible(self) -> bool:
        return (self._gridVisibleCombo.currentIndex() == 1)

    def gridBrush(self) -> QBrush:
        return QBrush(self._gridColorWidget.color())

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

    def setDrawingProperty(self, name: str, value: typing.Any) -> None:
        self.blockSignals(True)
        if (name == 'grid' and isinstance(value, float)):
            self.setGrid(value)
        elif (name == 'gridVisible' and isinstance(value, bool)):
            self.setGridVisible(value)
        elif (name == 'gridBrush' and isinstance(value, QBrush)):
            self.setGridBrush(value)
        elif (name == 'gridSpacingMajor' and isinstance(value, int)):
            self.setGridSpacingMajor(value)
        elif (name == 'gridSpacingMinor' and isinstance(value, int)):
            self.setGridSpacingMinor(value)
        self.blockSignals(False)

    def setPage(self, page: DrawingPageWidget | None) -> None:
        if (page is not None):
            self.blockSignals(True)
            self.setSceneRect(page.sceneRect())
            self.setBackgroundBrush(page.backgroundBrush())
            self.blockSignals(False)

    def setPageProperty(self, name: str, value: typing.Any) -> None:
        self.blockSignals(True)
        if (name == 'sceneRect' and isinstance(value, QRectF)):
            self.setSceneRect(value)
        elif (name == 'backgroundBrush' and isinstance(value, QBrush)):
            self.setBackgroundBrush(value)
        self.blockSignals(False)

    # ==================================================================================================================

    def _handleSceneRectTopLeftChange(self, position: QPointF) -> None:
        self.pagePropertyChanged.emit('sceneRect', QRectF(position, self._sceneRectSizeWidget.size()).normalized())

    def _handleSceneRectSizeChange(self, size: QSizeF) -> None:
        self.pagePropertyChanged.emit('sceneRect', QRectF(self._sceneRectTopLeftWidget.position(), size).normalized())

    def _handleBackgroundColorChange(self, color: QColor) -> None:
        self.pagePropertyChanged.emit('backgroundBrush', QBrush(color))

    # ==================================================================================================================

    def _handleGridChange(self, value: float) -> None:
        self.drawingPropertyChanged.emit('grid', value)

    def _handleGridVisibleChange(self, index: int) -> None:
        self.drawingPropertyChanged.emit('gridVisible', (index == 1))

    def _handleGridColorChange(self, color: QColor) -> None:
        self.drawingPropertyChanged.emit('gridBrush', QBrush(color))

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
