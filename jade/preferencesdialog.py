# preferencesdialog.py
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

from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QBrush, QFont, QFontMetrics, QIcon, QPen
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout, QListWidget,
                               QListWidgetItem, QStackedWidget, QVBoxLayout, QWidget)
from .drawing.drawingarrow import DrawingArrow
from .properties.pagepropertieswidget import PagePropertiesWidget
from .properties.singleitempropertieswidget import SingleItemPropertiesWidget


class PreferencesDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        rect = QFontMetrics(self.font()).boundingRect('Diagram Defaults')
        width = rect.width() + 24
        height = rect.height()

        self._listWidget: QListWidget = QListWidget()
        self._stackedWidget: QStackedWidget = QStackedWidget()

        self._listWidget.setIconSize(QSize(2 * height, 2 * height))
        self._listWidget.setGridSize(QSize(width, 4 * height))
        self._listWidget.setViewMode(QListWidget.ViewMode.IconMode)
        self._listWidget.setMovement(QListWidget.Movement.Static)
        self._listWidget.setFixedWidth(width + 4)
        self._listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._listWidget.currentRowChanged.connect(self._stackedWidget.setCurrentIndex)     # type: ignore

        self._setupGeneralWidget()
        self._setupDiagramDefaultsWidget()
        self._setupItemDefaultsWidget()

        widget = QWidget()
        hLayout = QHBoxLayout()
        hLayout.addWidget(self._listWidget)
        hLayout.addWidget(self._stackedWidget, 100)
        hLayout.setSpacing(8)
        hLayout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(hLayout)

        vLayout = QVBoxLayout()
        vLayout.addWidget(widget, 100)
        vLayout.addWidget(self._createButtonBox())
        self.setLayout(vLayout)

        self.setWindowTitle('Preferences')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(460, 580)

    def _setupGeneralWidget(self) -> None:
        self._promptOverwriteCheck: QCheckBox = QCheckBox('Prompt when overwriting existing files')
        self._promptCloseUnsavedCheck: QCheckBox = QCheckBox('Prompt when closing unsaved files')

        promptGroup = QGroupBox('Prompt')
        promptLayout = QVBoxLayout()
        promptLayout.addWidget(self._promptOverwriteCheck)
        promptLayout.addWidget(self._promptCloseUnsavedCheck)
        promptGroup.setLayout(promptLayout)

        generalWidget = QWidget()
        generalLayout = QVBoxLayout()
        generalLayout.addWidget(promptGroup)
        generalLayout.addWidget(QWidget(), 100)
        generalWidget.setLayout(generalLayout)

        listWidgetItem = QListWidgetItem('General')
        listWidgetItem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        listWidgetItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        listWidgetItem.setIcon(QIcon("icons:configure.png"))
        self._listWidget.addItem(listWidgetItem)
        self._stackedWidget.addWidget(generalWidget)

    def _setupDiagramDefaultsWidget(self) -> None:
        self._diagramDefaultPropertiesWidget: PagePropertiesWidget = PagePropertiesWidget()

        listWidgetItem = QListWidgetItem('Diagram Defaults')
        listWidgetItem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        listWidgetItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        listWidgetItem.setIcon(QIcon("icons:jade.png"))
        self._listWidget.addItem(listWidgetItem)
        self._stackedWidget.addWidget(self._diagramDefaultPropertiesWidget)

    def _setupItemDefaultsWidget(self) -> None:
        self._itemDefaultPropertiesWidget: SingleItemPropertiesWidget = SingleItemPropertiesWidget()

        listWidgetItem = QListWidgetItem('Item Defaults')
        listWidgetItem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        listWidgetItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        listWidgetItem.setIcon(QIcon("icons:text-rect.png"))
        self._listWidget.addItem(listWidgetItem)
        self._stackedWidget.addWidget(self._itemDefaultPropertiesWidget)

    def _createButtonBox(self) -> QWidget:
        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        buttonBox.setCenterButtons(True)

        okButton = buttonBox.addButton('OK', QDialogButtonBox.ButtonRole.AcceptRole)
        cancelButton = buttonBox.addButton('Cancel', QDialogButtonBox.ButtonRole.RejectRole)

        rect = QFontMetrics(cancelButton.font()).boundingRect('Cancel')
        okButton.setMinimumSize(rect.width() + 24, rect.height() + 16)
        cancelButton.setMinimumSize(rect.width() + 24, rect.height() + 16)

        okButton.clicked.connect(self.accept)       # type: ignore
        cancelButton.clicked.connect(self.reject)   # type: ignore

        return buttonBox

    # ==================================================================================================================

    def setPromptWhenOverwriting(self, prompt: bool) -> None:
        self._promptOverwriteCheck.setChecked(prompt)

    def setPromptWhenClosingUnsaved(self, prompt: bool) -> None:
        self._promptCloseUnsavedCheck.setChecked(prompt)

    def shouldPromptWhenOverwriting(self) -> bool:
        return self._promptOverwriteCheck.isChecked()

    def shouldPromptWhenClosingUnsaved(self) -> bool:
        return self._promptCloseUnsavedCheck.isChecked()

    # ==================================================================================================================

    def setDefaultSceneRect(self, rect: QRectF) -> None:
        self._diagramDefaultPropertiesWidget.setSceneRect(rect)

    def setDefaultBackgroundBrush(self, brush: QBrush) -> None:
        self._diagramDefaultPropertiesWidget.setBackgroundBrush(brush)

    def setDefaultGrid(self, grid: float) -> None:
        self._diagramDefaultPropertiesWidget.setGrid(grid)

    def setDefaultGridVisible(self, visible: bool) -> None:
        self._diagramDefaultPropertiesWidget.setGridVisible(visible)

    def setDefaultGridBrush(self, brush: QBrush) -> None:
        self._diagramDefaultPropertiesWidget.setGridBrush(brush)

    def setDefaultGridSpacingMajor(self, spacing: int) -> None:
        self._diagramDefaultPropertiesWidget.setGridSpacingMajor(spacing)

    def setDefaultGridSpacingMinor(self, spacing: int) -> None:
        self._diagramDefaultPropertiesWidget.setGridSpacingMinor(spacing)

    def defaultSceneRect(self) -> QRectF:
        return self._diagramDefaultPropertiesWidget.sceneRect()

    def defaultBackgroundBrush(self) -> QBrush:
        return self._diagramDefaultPropertiesWidget.backgroundBrush()

    def defaultGrid(self) -> float:
        return self._diagramDefaultPropertiesWidget.grid()

    def isDefaultGridVisible(self) -> bool:
        return self._diagramDefaultPropertiesWidget.isGridVisible()

    def defaultGridBrush(self) -> QBrush:
        return self._diagramDefaultPropertiesWidget.gridBrush()

    def defaultGridSpacingMajor(self) -> int:
        return self._diagramDefaultPropertiesWidget.gridSpacingMajor()

    def defaultGridSpacingMinor(self) -> int:
        return self._diagramDefaultPropertiesWidget.gridSpacingMinor()

    # ==================================================================================================================

    def setDefaultPen(self, pen: QPen) -> None:
        self._itemDefaultPropertiesWidget.setPen(pen)

    def setDefaultBrush(self, brush: QBrush) -> None:
        self._itemDefaultPropertiesWidget.setBrush(brush)

    def setDefaultStartArrow(self, arrow: DrawingArrow) -> None:
        self._itemDefaultPropertiesWidget.setStartArrow(arrow)

    def setDefaultEndArrow(self, arrow: DrawingArrow) -> None:
        self._itemDefaultPropertiesWidget.setEndArrow(arrow)

    def setDefaultFont(self, font: QFont) -> None:
        self._itemDefaultPropertiesWidget.setFont(font)

    def setDefaultTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._itemDefaultPropertiesWidget.setTextAlignment(alignment)

    def setDefaultTextBrush(self, brush: QBrush) -> None:
        self._itemDefaultPropertiesWidget.setTextBrush(brush)

    def defaultPen(self) -> QPen:
        return self._itemDefaultPropertiesWidget.pen()

    def defaultBrush(self) -> QBrush:
        return self._itemDefaultPropertiesWidget.brush()

    def defaultStartArrow(self) -> DrawingArrow:
        return self._itemDefaultPropertiesWidget.startArrow()

    def defaultEndArrow(self) -> DrawingArrow:
        return self._itemDefaultPropertiesWidget.endArrow()

    def defaultFont(self) -> QFont:
        return self._itemDefaultPropertiesWidget.font()

    def defaultTextAlignment(self) -> Qt.AlignmentFlag:
        return self._itemDefaultPropertiesWidget.textAlignment()

    def defaultTextBrush(self) -> QBrush:
        return self._itemDefaultPropertiesWidget.textBrush()
