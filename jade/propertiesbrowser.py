# propertiesbrowser.py
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
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QScrollArea, QStackedWidget
from .items.odgitem import OdgItem
from .properties.drawingpropertieswidget import DrawingPropertiesWidget
from .properties.multipleitempropertieswidget import MultipleItemPropertiesWidget
from .properties.singleitempropertieswidget import SingleItemPropertiesWidget
from .drawingwidget import DrawingWidget


class PropertiesBrowser(QStackedWidget):
    def __init__(self, drawing: DrawingWidget) -> None:
        super().__init__()
        self._drawing: DrawingWidget = drawing

        self._drawingPropertiesWidget: DrawingPropertiesWidget = DrawingPropertiesWidget()
        self._drawingPropertiesScroll: QScrollArea = QScrollArea()
        self._drawingPropertiesScroll.setWidget(self._drawingPropertiesWidget)
        self._drawingPropertiesScroll.setWidgetResizable(True)
        self.addWidget(self._drawingPropertiesScroll)

        self._drawingPropertiesWidget.setUnits(self._drawing.units())
        self._drawingPropertiesWidget.setPageSize(self._drawing.pageSize())
        self._drawingPropertiesWidget.setPageMargins(self._drawing.pageMargins())
        self._drawingPropertiesWidget.setBackgroundColor(self._drawing.backgroundColor())
        self._drawingPropertiesWidget.setGrid(self._drawing.grid())
        self._drawingPropertiesWidget.setGridVisible(self._drawing.isGridVisible())
        self._drawingPropertiesWidget.setGridColor(self._drawing.gridColor())
        self._drawingPropertiesWidget.setGridSpacingMajor(self._drawing.gridSpacingMajor())
        self._drawingPropertiesWidget.setGridSpacingMinor(self._drawing.gridSpacingMinor())

        self._multipleItemsPropertiesWidget: MultipleItemPropertiesWidget = MultipleItemPropertiesWidget()
        self._multipleItemsPropertiesScroll: QScrollArea = QScrollArea()
        self._multipleItemsPropertiesScroll.setWidget(self._multipleItemsPropertiesWidget)
        self._multipleItemsPropertiesScroll.setWidgetResizable(True)
        self.addWidget(self._multipleItemsPropertiesScroll)

        self._multipleItemsPropertiesWidget.setUnits(self._drawing.units())

        self._singleItemsPropertiesWidget: SingleItemPropertiesWidget = SingleItemPropertiesWidget()
        self._singleItemsPropertiesScroll: QScrollArea = QScrollArea()
        self._singleItemsPropertiesScroll.setWidget(self._singleItemsPropertiesWidget)
        self._singleItemsPropertiesScroll.setWidgetResizable(True)
        self.addWidget(self._singleItemsPropertiesScroll)

        self._singleItemsPropertiesWidget.setUnits(self._drawing.units())

        self._drawing.propertyChanged.connect(self.setDrawingProperty)
        self._drawing.currentItemsChanged.connect(self.setItems)
        self._drawing.currentItemsPropertyChanged.connect(self.setItems)

        self._drawingPropertiesWidget.drawingPropertyChanged.connect(self._drawing.updateProperty)

        self._multipleItemsPropertiesWidget.itemsMovedDelta.connect(self._drawing.moveCurrentItemsDelta)
        self._multipleItemsPropertiesWidget.itemsPropertyChanged.connect(self._drawing.updateCurrentItemsProperty)

        self._singleItemsPropertiesWidget.itemMoved.connect(self._drawing.moveCurrentItem)
        self._singleItemsPropertiesWidget.itemResized.connect(self._drawing.resizeCurrentItem)
        self._singleItemsPropertiesWidget.itemResized2.connect(self._drawing.resizeCurrentItem2)
        self._singleItemsPropertiesWidget.itemPropertyChanged.connect(self._drawing.updateCurrentItemsProperty)

        self.setMinimumSize(300, 10)

        self._drawingPropertiesWidget.unitsChanged.connect(self._multipleItemsPropertiesWidget.setUnits)
        self._drawingPropertiesWidget.unitsChanged.connect(self._singleItemsPropertiesWidget.setUnits)

    # ==================================================================================================================

    def sizeHint(self) -> QSize:
        return QSize(320, -1)

    # ==================================================================================================================

    def setDrawingProperty(self, name: str, value: Any) -> None:
        self._drawingPropertiesWidget.setDrawingProperty(name, value)
        self.setCurrentIndex(0)

    def setItems(self, items: list[OdgItem]) -> None:
        if (len(items) > 1):
            self._multipleItemsPropertiesWidget.setItems(items)
            self.setCurrentIndex(1)
        elif (len(items) == 1):
            self._singleItemsPropertiesWidget.setItem(items[0])
            self.setCurrentIndex(2)
        else:
            self.setCurrentIndex(0)
