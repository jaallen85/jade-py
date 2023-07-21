# stylesbrowser.py
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

from typing import Any, Callable, overload
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QPersistentModelIndex, QObject
from PySide6.QtGui import QAction, QContextMenuEvent, QIcon
from PySide6.QtWidgets import QMenu, QTreeView
from .odg.odgitemstyle import OdgItemStyle
from .drawingwidget import DrawingWidget


class StylesModel(QAbstractItemModel):
    def __init__(self, drawing: DrawingWidget) -> None:
        super().__init__()
        self._drawing: DrawingWidget = drawing

    def index(self, row: int, column: int, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> QModelIndex:
        if (parent.isValid()):
            parentStyle = self._getStyleFromIndex(parent)
            if (0 <= row < len(parentStyle.children())):
                return self.createIndex(row, column, parentStyle.children()[row])
        return self.createIndex(0, 0, self._drawing.defaultItemStyle())

    @overload
    def parent(self) -> QObject:
        ...

    @overload
    def parent(self, child: QModelIndex | QPersistentModelIndex) -> QModelIndex:
        ...

    def parent(self, child: QModelIndex | QPersistentModelIndex | None = None) -> QModelIndex | QObject:
        if (child is None):
            return super().parent()
        if (child.isValid()):
            childStyle = self._getStyleFromIndex(child)
            parentStyle = childStyle.parent()
            if (isinstance(parentStyle, OdgItemStyle)):
                return self.createIndex(parentStyle.children().index(childStyle), 0, parentStyle)
        return QModelIndex()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if (parent.isValid()):
            return len(self._getStyleFromIndex(parent).children())
        return 1

    def columnCount(self, _: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 1

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        if (index.isValid()):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.NoItemFlags

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if (index.isValid()):
            if (role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole)):
                return self._getStyleFromIndex(index).name()
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if (section == 0 and orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole):
            return 'Style Name'
        return None

    def sort(self, _: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self.beginResetModel()
        self._drawing.defaultItemStyle().sort(order)
        self.endResetModel()

    def _getStyleFromIndex(self, index: QModelIndex | QPersistentModelIndex) -> OdgItemStyle:
        if (index.isValid()):
            item = index.internalPointer()
            if (isinstance(item, OdgItemStyle)):
                return item
        return self._drawing.defaultItemStyle()


# ======================================================================================================================

class StylesBrowser(QTreeView):
    def __init__(self, drawing: DrawingWidget) -> None:
        super().__init__()
        self.setModel(StylesModel(drawing))
        self.setHeaderHidden(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.expandAll()
        self._createContextMenu()

    # ==================================================================================================================

    def _createContextMenu(self) -> None:
        self.applyStyleAction: QAction = self._addAction('Apply Style to Selection', self.applyStyleToSelection)
        self.newStyleAction: QAction = self._addAction('New Style...', self.newStyle)
        self.modifyStyleAction: QAction = self._addAction('Modify Style...', self.modifyStyle)
        self.removeStyleAction: QAction = self._addAction('Remove Style', self.removeStyle)

        self._contextMenu: QMenu = QMenu()
        self._contextMenu.addAction(self.applyStyleAction)
        self._contextMenu.addSeparator()
        self._contextMenu.addAction(self.newStyleAction)
        self._contextMenu.addAction(self.modifyStyleAction)
        self._contextMenu.addAction(self.removeStyleAction)

    def _addAction(self, text: str, slot: Callable, iconPath: str = '') -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)      # type: ignore
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        self.addAction(action)
        return action

    # ==================================================================================================================

    def applyStyleToSelection(self) -> None:
        pass

    # ==================================================================================================================

    def newStyle(self) -> None:
        pass

    def modifyStyle(self) -> None:
        pass

    def removeStyle(self) -> None:
        pass

    # ==================================================================================================================

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self._contextMenu.popup(event.globalPos())
