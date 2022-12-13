# propertiesbrowser.py
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
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QScrollArea, QStackedWidget
from .drawing.drawingitem import DrawingItem
from .drawing.drawingpagewidget import DrawingPageWidget
from .properties.multipleitempropertieswidget import MultipleItemPropertiesWidget
from .properties.pagepropertieswidget import PagePropertiesWidget
from .properties.singleitempropertieswidget import SingleItemPropertiesWidget
from .diagramwidget import DiagramWidget


class PropertiesBrowser(QStackedWidget):
    def __init__(self, diagram: DiagramWidget) -> None:
        super().__init__()

        self._diagram: DiagramWidget = diagram

        self._pagePropertiesWidget: PagePropertiesWidget = PagePropertiesWidget()
        self._pagePropertiesScroll: QScrollArea = QScrollArea()
        self._pagePropertiesScroll.setWidget(self._pagePropertiesWidget)
        self._pagePropertiesScroll.setWidgetResizable(True)
        self.addWidget(self._pagePropertiesScroll)

        self._multipleItemsPropertiesWidget: MultipleItemPropertiesWidget = MultipleItemPropertiesWidget()
        self._multipleItemsPropertiesScroll: QScrollArea = QScrollArea()
        self._multipleItemsPropertiesScroll.setWidget(self._multipleItemsPropertiesWidget)
        self._multipleItemsPropertiesScroll.setWidgetResizable(True)
        self.addWidget(self._multipleItemsPropertiesScroll)

        self._singleItemsPropertiesWidget: SingleItemPropertiesWidget = SingleItemPropertiesWidget()
        self._singleItemsPropertiesScroll: QScrollArea = QScrollArea()
        self._singleItemsPropertiesScroll.setWidget(self._singleItemsPropertiesWidget)
        self._singleItemsPropertiesScroll.setWidgetResizable(True)
        self.addWidget(self._singleItemsPropertiesScroll)

        self._diagram.propertyChanged.connect(self.setDrawingProperty)
        self._diagram.currentPageChanged.connect(self.setPage)
        self._diagram.currentPagePropertyChanged.connect(self.setPageProperty)
        self._diagram.currentItemsChanged.connect(self.setItems)
        self._diagram.currentItemsPropertyChanged.connect(self.setItems)

        self._pagePropertiesWidget.drawingPropertyChanged.connect(self._diagram.updateProperty)
        self._pagePropertiesWidget.pagePropertyChanged.connect(self._diagram.updateCurrentPageProperty)

        self._multipleItemsPropertiesWidget.itemsMovedDelta.connect(self._diagram.moveCurrentItemsDelta)
        self._multipleItemsPropertiesWidget.itemsPropertyChanged.connect(self._diagram.updateCurrentItemsProperty)

        self._singleItemsPropertiesWidget.itemMoved.connect(self._diagram.moveCurrentItem)
        self._singleItemsPropertiesWidget.itemResized.connect(self._diagram.resizeCurrentItem)
        self._singleItemsPropertiesWidget.itemPropertyChanged.connect(self._diagram.updateCurrentItemsProperty)

        self._pagePropertiesWidget.setDrawingProperty('grid', self._diagram.grid())
        self._pagePropertiesWidget.setDrawingProperty('gridVisible', self._diagram.isGridVisible())
        self._pagePropertiesWidget.setDrawingProperty('gridBrush', self._diagram.gridBrush())
        self._pagePropertiesWidget.setDrawingProperty('gridSpacingMajor', self._diagram.gridSpacingMajor())
        self._pagePropertiesWidget.setDrawingProperty('gridSpacingMinor', self._diagram.gridSpacingMinor())

    # ==================================================================================================================

    def sizeHint(self) -> QSize:
        return QSize(320, -1)

    # ==================================================================================================================

    def setDrawingProperty(self, name: str, value: typing.Any) -> None:
        self._pagePropertiesWidget.setDrawingProperty(name, value)
        self.setCurrentIndex(0)

    def setPage(self, page: DrawingPageWidget | None) -> None:
        self._pagePropertiesWidget.setPage(page)
        self.setCurrentIndex(0)

    def setPageProperty(self, name: str, value: typing.Any) -> None:
        self._pagePropertiesWidget.setPageProperty(name, value)
        self.setCurrentIndex(0)

    def setItems(self, items: list[DrawingItem]) -> None:
        if (len(items) > 1):
            self._multipleItemsPropertiesWidget.setItems(items)
            self.setCurrentIndex(1)
        elif (len(items) == 1):
            self._singleItemsPropertiesWidget.setItem(items[0])
            self.setCurrentIndex(2)
        else:
            self.setCurrentIndex(0)
