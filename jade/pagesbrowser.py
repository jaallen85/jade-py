# pagesbrowser.py
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

import typing
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QContextMenuEvent, QDropEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu
from .odg.odgpage import OdgPage
from .drawingwidget import DrawingWidget


class PagesBrowser(QListWidget):
    def __init__(self, drawing: DrawingWidget) -> None:
        super().__init__()

        self._drawing: DrawingWidget = drawing

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        # Signals and slots
        self._drawing.pageInserted.connect(self._insertItem)
        self._drawing.pageRemoved.connect(self._removeItem)
        self._drawing.currentPageIndexChanged.connect(self._updateCurrentItem)
        self._drawing.currentPagePropertyChanged.connect(self._updateCurrentItemText)

        self.currentRowChanged.connect(self._updateCurrentPage)     # type: ignore
        self.itemChanged.connect(self._updateCurrentPageName)       # type: ignore

        # Menus and actions
        renamePageAction = QAction('Rename Page', self)
        renamePageAction.triggered.connect(self._renamePage)        # type: ignore
        self.addAction(renamePageAction)

        self._contextMenu: QMenu = QMenu()
        self._contextMenu.addAction(self._drawing.insertPageAction)
        self._contextMenu.addAction(self._drawing.removePageAction)
        self._contextMenu.addAction(renamePageAction)

    # ==================================================================================================================

    def sizeHint(self) -> QSize:
        return QSize(200, -1)

    # ==================================================================================================================

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self._contextMenu.popup(event.globalPos())
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        eventItem = self.itemAt(event.position().toPoint())
        if (len(self.selectedItems()) > 0 and eventItem is not None):
            currentIndex = self.row(self.selectedItems()[0])
            newIndex = self.row(eventItem)
            if (currentIndex != newIndex):
                if (self.dropIndicatorPosition() == QListWidget.DropIndicatorPosition.BelowItem and currentIndex > newIndex):       # noqa
                    newIndex = newIndex + 1
                elif (self.dropIndicatorPosition() == QListWidget.DropIndicatorPosition.AboveItem and currentIndex < newIndex):     # noqa
                    newIndex = newIndex - 1
                if (currentIndex != newIndex):
                    self._drawing.moveCurrentPage(newIndex)

    # ==================================================================================================================

    def _renamePage(self) -> None:
        if (self.currentItem()):
            self.editItem(self.currentItem())

    # ==================================================================================================================

    def _insertItem(self, page: OdgPage, index: int) -> None:
        self.blockSignals(True)
        newItem = QListWidgetItem(page.name())
        newItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable |
                         Qt.ItemFlag.ItemIsDragEnabled)
        self.insertItem(index, newItem)
        self.blockSignals(False)

    def _removeItem(self, _: OdgPage, index: int) -> None:
        self.blockSignals(True)
        item = self.takeItem(index)
        del item
        self.blockSignals(False)

    def _updateCurrentItem(self, index: int) -> None:
        self.blockSignals(True)
        self.setCurrentRow(index)
        self.blockSignals(False)

    def _updateCurrentItemText(self, name: str, value: typing.Any) -> None:
        if (name == 'name' and isinstance(value, str) and self.currentItem() is not None):
            self.blockSignals(True)
            self.currentItem().setText(value)
            self.blockSignals(False)

    # ==================================================================================================================

    def _updateCurrentPage(self, row: int) -> None:
        self._drawing.setCurrentPageIndex(row)

    def _updateCurrentPageName(self, item: QListWidgetItem) -> None:
        if (item is not None):
            self._drawing.renameCurrentPage(item.text())
