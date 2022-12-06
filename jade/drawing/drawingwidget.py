# drawingwidget.py
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
from enum import Enum
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QPointF, QRectF
from PyQt6.QtGui import QCursor, QMouseEvent, QUndoCommand
from PyQt6.QtWidgets import QApplication
from .drawingitem import DrawingItem
from .drawingitemgroup import DrawingItemGroup
from .drawingitempoint import DrawingItemPoint
from .drawingview import DrawingView


class DrawingWidget(DrawingView):
    undoCommandCreated = pyqtSignal(QUndoCommand)
    cleanChanged = pyqtSignal(bool)
    modifiedStringChanged = pyqtSignal(str)
    currentItemsPropertyChanged = pyqtSignal(list)
    contextMenuTriggered = pyqtSignal(QPoint)

    def __init__(self) -> None:
        super().__init__()

        self._selectedItemsCenter: QPointF = QPointF()
        self.currentItemsChanged.connect(self._updateSelectionCenter)
        self.currentItemsPropertyChanged.connect(self._updateSelectionCenter)

        self._selectMoveItemsInitialPositions: dict[DrawingItem, QPointF] = {}
        self._selectMoveItemsPreviousDeltaPosition: QPointF = QPointF()
        self._selectResizeItemInitialPosition: QPointF = QPointF()
        self._selectResizeItemPreviousPosition: QPointF = QPointF()

    # ==================================================================================================================

    def addItems(self, items: list[DrawingItem]) -> None:
        # Assumes each item in items is not already a member of self.items()
        for item in items:
            self.addItem(item)
        if (self._mode == DrawingView.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def insertItems(self, items: list[DrawingItem], indices: dict[DrawingItem, int]) -> None:
        # Assumes each item in items is not already a member of self.items() and has a corresponding index in indices
        for item in items:
            self.insertItem(indices[item], item)
        if (self._mode == DrawingView.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def removeItems(self, items: list[DrawingItem]) -> None:
        # Assumes each item in items is a member of self.items()
        if (self._mode == DrawingView.Mode.SelectMode):
            self.setSelectedItems([])
        for item in items:
            self.removeItem(item)
        self.viewport().update()

    def _reorderItems(self, items: list[DrawingItem]) -> None:
        # Assumes that all members of self.items() are present in items with no extras
        self._items = items
        if (self._mode == DrawingView.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def moveItems(self, items: list[DrawingItem], positions: dict[DrawingItem, QPointF]) -> None:
        # Assumes each item in items is a member of self.items() and has a corresponding position in positions
        for item in items:
            item.move(positions[item])

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    def resizeItem(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        # Assume the point is a member of a valid item which is in turn a member of self.items()
        item = point.item()
        if (item is not None):
            item.resize(point, position, snapTo45Degrees)

            if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) == 1 and
                    item in self._selectedItems):
                self.currentItemsPropertyChanged.emit(self._selectedItems)
            elif (self._mode == DrawingView.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                    item in self._placeModeItems):
                self.currentItemsPropertyChanged.emit(self._placeModeItems)

            self.viewport().update()

    def rotateItems(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.rotate(position)

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a rotation event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def rotateBackItems(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.rotateBack(position)

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a rotation event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def flipItemsHorizontal(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.flipHorizontal(position)

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a flip event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def flipItemsVertical(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.flipVertical(position)

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a flip event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def insertItemPoint(self, item: DrawingItem, point: DrawingItemPoint, index: int) -> None:
        # Assumes the item is a member of self.items() and that point is not already a member of item.points()
        item.insertPoint(index, point)
        item.resize(point, item.mapToScene(point.position()), False)

        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) == 1 and
                item in self._selectedItems):
            self.currentItemsPropertyChanged.emit(self._selectedItems)
        elif (self._mode == DrawingView.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                item in self._placeModeItems):
            self.currentItemsPropertyChanged.emit(self._placeModeItems)

        self.viewport().update()

    def removeItemPoint(self, item: DrawingItem, point: DrawingItemPoint) -> None:
        # Assumes the item is a member of self.items() and that point is a member of item.points()
        item.removePoint(point)

        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) == 1 and
                item in self._selectedItems):
            self.currentItemsPropertyChanged.emit(self._selectedItems)
        elif (self._mode == DrawingView.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                item in self._placeModeItems):
            self.currentItemsPropertyChanged.emit(self._placeModeItems)

        self.viewport().update()

    def setItemsProperty(self, items: list[DrawingItem], name: str, value: typing.Any) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.setProperty(name, value)

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    def setItemsPropertyDict(self, items: list[DrawingItem], name: str, values: dict[DrawingItem, typing.Any]) -> None:
        # Assumes each item in items is a member of self.items() and has a corresponding value in values
        for item in items:
            item.setProperty(name, values[item])

        if ((self._mode == DrawingView.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingView.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    # ==================================================================================================================

    def cut(self) -> None:
        self.copy()
        self.delete()

    def copy(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) > 0):
            QApplication.clipboard().setText(DrawingItem.writeItemsToString(self._selectedItems))

    def paste(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            newItems = DrawingItem.readItemsFromString(QApplication.clipboard().text())
            if (len(newItems) > 0):
                # Center the items under the mouse cursor
                centerPosition = self.roundPointToGrid(self._itemsCenter(newItems))
                deltaPosition = self.roundPointToGrid(self.mapToScene(
                    self.mapFromGlobal(QCursor.pos())) - centerPosition)    # type: ignore

                for item in newItems:
                    item.setPosition(item.position() + deltaPosition)       # type: ignore
                    item.setPlaceType(DrawingItem.PlaceType.PlaceByMouseRelease)

                # Start placing the items in the scene
                self.setPlaceMode(newItems)

    def delete(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._removeItemsCommand(self._selectedItems)
        else:
            self.setSelectMode()

    # ==================================================================================================================

    def moveCurrentItemsDelta(self, delta: QPointF) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = item.position() + delta    # type: ignore
                self._moveItemsCommand(self._selectedItems, newPositions, finalMove=True, place=True)

    def moveCurrentItem(self, position: QPointF) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = position
                self._moveItemsCommand(self._selectedItems, newPositions, finalMove=True, place=True)

    def resizeCurrentItem(self, point: DrawingItemPoint, position: QPointF) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                self._resizeItemCommand(point, position, snapTo45Degrees=False, finalResize=True, place=True,
                                        disconnect=False)

    # ==================================================================================================================

    def rotate(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._rotateItemsCommand(self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter))
        elif (self._mode == DrawingView.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't rotate a single PlaceByMousePressAndRelease item
                dontRotate = (len(self._placeModeItems) == 1 and
                              self._placeModeItems[0].placeType() == DrawingItem.PlaceType.PlaceByMousePressAndRelease)
                if (not dontRotate):
                    self.rotateItems(self._placeModeItems,
                                     self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def rotateBack(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._rotateBackItemsCommand(self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter))
        elif (self._mode == DrawingView.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't rotate a single PlaceByMousePressAndRelease item
                dontRotate = (len(self._placeModeItems) == 1 and
                              self._placeModeItems[0].placeType() == DrawingItem.PlaceType.PlaceByMousePressAndRelease)
                if (not dontRotate):
                    self.rotateBackItems(self._placeModeItems,
                                         self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def flipHorizontal(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._flipItemsHorizontalCommand(self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter))
        elif (self._mode == DrawingView.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't flip a single PlaceByMousePressAndRelease item
                dontFlip = (len(self._placeModeItems) == 1 and
                            self._placeModeItems[0].placeType() == DrawingItem.PlaceType.PlaceByMousePressAndRelease)
                if (not dontFlip):
                    self.flipItemsHorizontal(self._placeModeItems,
                                             self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def flipVertical(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._flipItemsVerticalCommand(self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter))
        elif (self._mode == DrawingView.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't flip a single PlaceByMousePressAndRelease item
                dontFlip = (len(self._placeModeItems) == 1 and
                            self._placeModeItems[0].placeType() == DrawingItem.PlaceType.PlaceByMousePressAndRelease)
                if (not dontFlip):
                    self.flipItemsVertical(self._placeModeItems,
                                           self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    # ==================================================================================================================

    def bringForward(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemIndex = itemsOrdered.index(item)
                itemsOrdered.remove(item)
                itemsOrdered.insert(itemIndex + 1, item)

            self._reorderItemsCommand(itemsOrdered)

    def sendBackward(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemIndex = itemsOrdered.index(item)
                itemsOrdered.remove(item)
                itemsOrdered.insert(itemIndex - 1, item)

            self._reorderItemsCommand(itemsOrdered)

    def bringToFront(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemsOrdered.remove(item)
                itemsOrdered.append(item)

            self._reorderItemsCommand(itemsOrdered)

    def sendToBack(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemsOrdered.remove(item)
                itemsOrdered.insert(0, item)

            self._reorderItemsCommand(itemsOrdered)

    # ==================================================================================================================

    def group(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) > 1):
            itemsToRemove = self._selectedItems.copy()

            itemGroup = DrawingItemGroup()

            # Put the group position in the center of the selected items and adjust each item's position accordingly
            items = DrawingItem.cloneItems(itemsToRemove)
            itemGroup.setPosition(self._itemsCenter(items))
            for item in items:
                item.setPosition(itemGroup.mapFromScene(item.position()))
            itemGroup.setItems(items)

            # Replace the selected items with the new group item
            self.setSelectedItems([])

            groupCommand = QUndoCommand('Group Items')
            self._removeItemsCommand(itemsToRemove, groupCommand)
            self._addItemsCommand([itemGroup], False, groupCommand)
            self._pushUndoCommand(groupCommand)

    def ungroup(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) == 1):
            itemGroup = self._selectedItems[0]
            if (isinstance(itemGroup, DrawingItemGroup)):
                itemsToAdd = DrawingItem.cloneItems(itemGroup.items())
                for item in itemsToAdd:
                    # Apply the group's position/transform to each item
                    item.setPosition(itemGroup.mapToScene(item.position()))
                    item.setRotation(item.rotation() + itemGroup.rotation())
                    if (itemGroup.isFlipped()):
                        item.setFlipped(not item.isFlipped())

                # Replace the selected group item with clones of its constituent items
                self.setSelectedItems([])

                ungroupCommand = QUndoCommand('Group Items')
                self._removeItemsCommand([itemGroup], ungroupCommand)
                self._addItemsCommand(itemsToAdd, False, ungroupCommand)
                self._pushUndoCommand(ungroupCommand)

    # ==================================================================================================================

    def insertNewItemPoint(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) == 1):
            item = self._selectedItems[0]
            if (item.canInsertPoints()):
                point = item.insertNewPoint(self.roundPointToGrid(self._mouseButtonDownScenePosition))
                if (point is not None):
                    # Undo the insertNewPoint behavior and reapply is as an undo command
                    index = item.points().index(point)
                    item.removePoint(point)
                    self._insertPointCommand(item, point, index)

    def removeCurrentItemPoint(self) -> None:
        if (self._mode == DrawingView.Mode.SelectMode and len(self._selectedItems) == 1):
            item = self._selectedItems[0]
            if (item.canRemovePoints()):
                (point, index) = item.removeExistingPoint(self.roundPointToGrid(self._mouseButtonDownScenePosition))
                if (point is not None):
                    # Undo the removeExistingPoint behavior and reapply is as an undo command
                    item.insertPoint(index, point)

                    removeCommand = QUndoCommand('Remove Point')
                    self._disconnectAll(point, removeCommand)
                    self._removePointCommand(item, point, removeCommand)
                    self._pushUndoCommand(removeCommand)

    # ==================================================================================================================

    def updateProperty(self, name: str, value: typing.Any) -> None:
        self._pushUndoCommand(DrawingSetWidgetPropertyCommand(self, name, value))

    def updateCurrentItemsProperty(self, name: str, value: typing.Any) -> None:
        if (self._mode == DrawingView.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(DrawingSetItemsPropertyCommand(self, self._selectedItems, name, value))
        elif (self._mode == DrawingView.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                self.setItemsProperty(self._placeModeItems, name, value)

    # ==================================================================================================================

    def _selectModeMoveItemsStartEvent(self, event: QMouseEvent) -> None:
        for item in self._selectedItems:
            self._selectMoveItemsInitialPositions[item] = item.position()
        self._selectMoveItemsPreviousDeltaPosition = QPointF()

    def _selectModeMoveItemsUpdateEvent(self, event: QMouseEvent) -> None:
        # Move items within the scene
        self._selectModeMoveItems(self.mapToScene(event.pos()), finalMove=False, placeItems=False)

    def _selectModeMoveItemsEndEvent(self, event: QMouseEvent) -> None:
        # Move items within the scene
        self._selectModeMoveItems(self.mapToScene(event.pos()),
                                  finalMove=True, placeItems=(len(self._selectedItems) == 1))

        # Reset select mode move items event variables
        self._selectMoveItemsInitialPositions = {}
        self._selectMoveItemsPreviousDeltaPosition = QPointF()

    def _selectModeMoveItems(self, mousePosition: QPointF, finalMove: bool, placeItems: bool) -> None:
        if (len(self._selectedItems) > 0):
            deltaPosition = self.roundPointToGrid(mousePosition - self._mouseButtonDownScenePosition)   # type: ignore
            if (finalMove or deltaPosition != self._selectMoveItemsPreviousDeltaPosition):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = self._selectMoveItemsInitialPositions[item] + deltaPosition    # type: ignore

                self._moveItemsCommand(self._selectedItems, newPositions, finalMove, place=placeItems)

                if (not finalMove):
                    position1 = self._selectMoveItemsInitialPositions[self._selectedItems[0]]
                    position2 = newPositions[self._selectedItems[0]]
                    self.mouseInfoChanged.emit(self._createMouseInfo2(position1, position2))
                else:
                    self.mouseInfoChanged.emit('')

                self._selectMoveItemsPreviousDeltaPosition = deltaPosition

    # ==================================================================================================================

    def _selectModeResizeItemStartEvent(self, event: QMouseEvent) -> None:
        if (self._selectMouseDownItem is not None and self._selectMouseDownPoint is not None):
            self._selectResizeItemInitialPosition = self._selectMouseDownItem.mapToScene(
                self._selectMouseDownPoint.position())
        self._selectResizeItemPreviousPosition = QPointF()

    def _selectModeResizeItemUpdateEvent(self, event: QMouseEvent) -> None:
        shiftDown = ((event.modifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier)
        self._selectModeResizeItem(self.mapToScene(event.pos()), snapTo45Degrees=shiftDown, finalResize=False)

    def _selectModeResizeItemEndEvent(self, event: QMouseEvent) -> None:
        shiftDown = ((event.modifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier)
        self._selectModeResizeItem(self.mapToScene(event.pos()), snapTo45Degrees=shiftDown, finalResize=True)

        # Reset select mode resize item event variables
        self._selectResizeItemInitialPosition = QPointF()
        self._selectResizeItemPreviousPosition = QPointF()

    def _selectModeResizeItem(self, mousePosition: QPointF, snapTo45Degrees: bool, finalResize: bool) -> None:
        if (self._selectMouseDownItem is not None and self._selectMouseDownPoint is not None):
            newPosition = self.roundPointToGrid(mousePosition)
            if (finalResize or newPosition != self._selectResizeItemPreviousPosition):
                self._resizeItemCommand(self._selectMouseDownPoint, newPosition, snapTo45Degrees, finalResize,
                                        place=finalResize, disconnect=True)

                if (not finalResize):
                    self.mouseInfoChanged.emit(self._createMouseInfo2(self._selectResizeItemInitialPosition,
                                                                      newPosition))
                else:
                    self.mouseInfoChanged.emit('')

                self._selectResizeItemPreviousPosition = newPosition

    # ==================================================================================================================

    def _selectModeRightMouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.contextMenuTriggered.emit(event.pos())
        super()._selectModeRightMouseReleaseEvent(event)

    # ==================================================================================================================

    def _placeModeNoButtonMouseMoveEvent(self, event: QMouseEvent) -> None:
        # Move the place items within the scene relative to the center of those items.
        centerPosition = self.roundPointToGrid(self._itemsCenter(self._placeModeItems))
        deltaPosition = self.roundPointToGrid(self.mapToScene(event.pos()) - centerPosition)    # type: ignore

        if (deltaPosition.x() != 0 or deltaPosition.y() != 0):
            newPositions = {}
            for item in self._placeModeItems:
                newPositions[item] = item.position() + deltaPosition    # type: ignore
            self.moveItems(self._placeModeItems, newPositions)

            self.mouseInfoChanged.emit(self._createMouseInfo1(self.roundPointToGrid(self.mapToScene(event.pos()))))

    def _placeModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        # Nothing to do here.
        pass

    def _placeModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        if (len(self._placeModeItems) == 1):
            placeItem = self._placeModeItems[0]
            placeItemResizeStartPoint = placeItem.resizeStartPoint()
            placeItemResizeEndPoint = placeItem.resizeEndPoint()
            if (placeItem.placeType() == DrawingItem.PlaceType.PlaceByMousePressAndRelease and
                    placeItemResizeStartPoint is not None and placeItemResizeEndPoint is not None):
                # Resize the item's end point to the current mouse position
                startPosition = placeItem.mapToScene(placeItemResizeStartPoint.position())
                endPosition = self.roundPointToGrid(self.mapToScene(event.pos()))
                snapTo45Degrees = ((event.modifiers() & Qt.KeyboardModifier.ShiftModifier) ==
                                   Qt.KeyboardModifier.ShiftModifier)
                self.resizeItem(placeItemResizeEndPoint, endPosition, snapTo45Degrees)

                self.mouseInfoChanged.emit(self._createMouseInfo2(startPosition, endPosition))
            else:
                self._placeModeNoButtonMouseMoveEvent(event)
        else:
            self._placeModeNoButtonMouseMoveEvent(event)

    def _placeModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (len(self._placeModeItems) > 0 or (len(self._placeModeItems) == 1 and self._placeModeItems[0].isValid())):
            # Place the items within the scene.
            self._addItemsCommand(self._placeModeItems, place=(len(self._placeModeItems) == 1))

            # Create a new set of place items
            newItems = DrawingItem.cloneItems(self._placeModeItems)
            if (len(newItems) == 1):
                newItem = newItems[0]
                newItemResizeStartPoint = newItem.resizeStartPoint()
                newItemResizeEndPoint = newItem.resizeEndPoint()
                if (newItem.placeType() == DrawingItem.PlaceType.PlaceByMousePressAndRelease and
                        newItemResizeStartPoint is not None and newItemResizeEndPoint is not None):
                    # Reset the item size to prepare for the next left mouse drag event
                    position = newItem.mapToScene(QPointF(0, 0))
                    newItem.resize(newItemResizeStartPoint, position, False)
                    newItem.resize(newItemResizeEndPoint, position, False)

            self._placeModeItems = []
            self.setPlaceMode(newItems)

    # ==================================================================================================================

    def _addItemsCommand(self, items: list[DrawingItem], place: bool, command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is not already a member of self.items()
        addCommand = DrawingAddItemsCommand(self, items, command)
        if (place):
            addCommand.redo()
            self._placeItems(items, addCommand)
            addCommand.undo()
        if (command is None):
            self._pushUndoCommand(addCommand)

    def _removeItemsCommand(self, items: list[DrawingItem], command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is a member of self.items()
        removeCommand = DrawingRemoveItemsCommand(self, items, command)
        removeCommand.redo()
        self._unplaceItems(items, removeCommand)
        removeCommand.undo()
        if (command is None):
            self._pushUndoCommand(removeCommand)

    def _reorderItemsCommand(self, items: list[DrawingItem], command: QUndoCommand | None = None) -> None:
        # Assumes that all members of self.items() are present in items with no extras
        reorderCommand = DrawingReorderItemsCommand(self, items, command)
        if (command is None):
            self._pushUndoCommand(reorderCommand)

    def _moveItemsCommand(self, items: list[DrawingItem], positions: dict[DrawingItem, QPointF], finalMove: bool,
                          place: bool, command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is a member of self.items() and has a corresponding
        # position in positions
        moveCommand = DrawingMoveItemsCommand(self, items, positions, finalMove, command)
        moveCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, moveCommand)
        if (place):
            self._placeItems(items, moveCommand)
        moveCommand.undo()
        if (command is None):
            self._pushUndoCommand(moveCommand)

    def _resizeItemCommand(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool, finalResize: bool,
                           place: bool, disconnect: bool, command: QUndoCommand | None = None) -> None:
        # Assume the point is a member of a valid item which is in turn a member of self.items()
        resizeCommand = DrawingResizeItemCommand(self, point, position, snapTo45Degrees, finalResize, command)
        resizeCommand.redo()
        if (disconnect):
            self._disconnectAll(point, resizeCommand)
        self._tryToMaintainConnections([point.item()], True, not point.isFree(), point, resizeCommand)
        if (place):
            self._placeItems([point.item()], resizeCommand)
        resizeCommand.undo()
        if (command is None):
            self._pushUndoCommand(resizeCommand)

    def _rotateItemsCommand(self, items: list[DrawingItem], position: QPointF,
                            command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is a member of self.items()
        rotateCommand = DrawingRotateItemsCommand(self, items, position, command)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        if (command is None):
            self._pushUndoCommand(rotateCommand)

    def _rotateBackItemsCommand(self, items: list[DrawingItem], position: QPointF,
                                command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is a member of self.items()
        rotateCommand = DrawingRotateBackItemsCommand(self, items, position, command)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        if (command is None):
            self._pushUndoCommand(rotateCommand)

    def _flipItemsHorizontalCommand(self, items: list[DrawingItem], position: QPointF,
                                    command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is a member of self.items()
        rotateCommand = DrawingFlipItemsHorizontalCommand(self, items, position, command)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        if (command is None):
            self._pushUndoCommand(rotateCommand)

    def _flipItemsVerticalCommand(self, items: list[DrawingItem], position: QPointF,
                                  command: QUndoCommand | None = None) -> None:
        # Assume items is not empty and that each item in items is a member of self.items()
        rotateCommand = DrawingFlipItemsVerticalCommand(self, items, position, command)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        if (command is None):
            self._pushUndoCommand(rotateCommand)

    def _insertPointCommand(self, item: DrawingItem, point: DrawingItemPoint, index: int,
                            command: QUndoCommand | None = None) -> None:
        # Assumes the item is a member of self.items() and that point is not already a member of item.points()
        insertCommand = DrawingItemInsertPointCommand(self, item, point, index, command)
        if (command is None):
            self._pushUndoCommand(insertCommand)

    def _removePointCommand(self, item: DrawingItem, point: DrawingItemPoint,
                            command: QUndoCommand | None = None) -> None:
        # Assumes the item is a member of self.items() and that point is a member of item.points()
        removeCommand = DrawingItemRemovePointCommand(self, item, point, command)
        if (command is None):
            self._pushUndoCommand(removeCommand)

    def _connectPointsCommand(self, point1: DrawingItemPoint, point2: DrawingItemPoint,
                              command: QUndoCommand | None = None) -> None:
        # Assumes point1 and point2 are not already connected
        connectCommand = DrawingItemPointConnectCommand(point1, point2, command)

        point1Position = point1.item().mapToScene(point1.position())
        point2Position = point2.item().mapToScene(point2.position())
        if (point1Position != point2Position):
            if (point2.isControlPoint()):
                self._resizeItemCommand(point2, point1Position, False, finalResize=False, place=False, disconnect=True,
                                        command=connectCommand)
            elif (point1.isControlPoint()):
                self._resizeItemCommand(point1, point2Position, False, finalResize=False, place=False, disconnect=True,
                                        command=connectCommand)

        if (command is None):
            self._pushUndoCommand(connectCommand)

    def _disconnectPointsCommand(self, point1: DrawingItemPoint, point2: DrawingItemPoint,
                                 command: QUndoCommand | None = None) -> None:
        # Assumes point1 and point2 are connected
        disconnectCommand = DrawingItemPointDisconnectCommand(point1, point2, command)
        if (command is None):
            self._pushUndoCommand(disconnectCommand)

    # ==================================================================================================================

    def _placeItems(self, items: list[DrawingItem], command: QUndoCommand | None = None) -> None:
        # Assume each item in items already is or is about to become a member of self.items()
        for widgetItem in self._items:
            if (widgetItem not in items and widgetItem not in self._placeModeItems):
                for widgetItemPoint in widgetItem.points():
                    for item in items:
                        for point in item.points():
                            if (self._shouldConnect(point, widgetItemPoint)):
                                self._connectPointsCommand(point, widgetItemPoint, command)

    def _unplaceItems(self, items: list[DrawingItem], command: QUndoCommand | None = None) -> None:
        # Assume each item in items is a member of self.items()
        for item in items:
            for point in item.points():
                for targetPoint in point.connections():
                    if (targetPoint.item() not in items):
                        self._disconnectPointsCommand(point, targetPoint, command)

    def _tryToMaintainConnections(self, items: list[DrawingItem], allowResize: bool, checkControlPoints: bool,
                                  pointToSkip: DrawingItemPoint | None, command: QUndoCommand | None = None) -> None:
        # Assume each item in items is a member of self.items()
        for item in items:
            for point in item.points():
                if (point != pointToSkip and (checkControlPoints or not point.isControlPoint())):
                    for targetPoint in point.connections():
                        if (item.mapToScene(point.position()) != targetPoint.item().mapToScene(targetPoint.position())):
                            # Try to maintain the connection by resizing targetPoint if possible
                            if (allowResize and targetPoint.isFree() and not self._shouldDisconnect(point, targetPoint)):   # noqa
                                self._resizeItemCommand(targetPoint, item.mapToScene(point.position()), False,
                                                        finalResize=False, place=False, disconnect=False,
                                                        command=command)
                            else:
                                self._disconnectPointsCommand(point, targetPoint, command)

    def _disconnectAll(self, point: DrawingItemPoint, command: QUndoCommand | None = None) -> None:
        for targetPoint in point.connections():
            self._disconnectPointsCommand(point, targetPoint, command)

    # ==================================================================================================================

    def _pushUndoCommand(self, command: QUndoCommand) -> None:
        self.undoCommandCreated.emit(command)

    # ==================================================================================================================

    def _emitModifiedStringChanged(self, clean: bool) -> None:
        self.modifiedStringChanged.emit('Modified' if (not clean) else '')

    # ==================================================================================================================

    def _updateSelectionCenter(self) -> None:
        self._selectedItemsCenter = self._itemsCenter(self._selectedItems)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class DrawingUndoCommand(QUndoCommand):
    def __init__(self, widget: DrawingWidget, text: str, parent: QUndoCommand | None = None) -> None:
        super().__init__(text, parent)

        self._widget: DrawingWidget = widget
        self._viewRect: QRectF = self._widget.visibleRect()

    def widget(self) -> DrawingWidget:
        return self._widget

    def viewRect(self) -> QRectF:
        return self._viewRect


# ======================================================================================================================

class DrawingItemsUndoCommand(DrawingUndoCommand):
    class Id(Enum):
        MoveItemsId = 0
        ResizeItemId = 1

    # ==================================================================================================================

    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], text: str,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, text, parent)

        self._items = items

    def items(self) -> list[DrawingItem]:
        return self._items

    # ==================================================================================================================

    def mergeChildren(self, command: QUndoCommand) -> None:
        for commandChildIndex in range(command.childCount()):
            commandChild = command.child(commandChildIndex)
            if (isinstance(commandChild, DrawingResizeItemCommand)):
                DrawingResizeItemCommand(commandChild.widget(), commandChild.point(), commandChild.position(),
                                         commandChild.shouldSnapTo45Degrees(), commandChild.isFinalResize(), self)
            elif (isinstance(commandChild, DrawingItemPointConnectCommand)):
                DrawingItemPointConnectCommand(commandChild.point1(), commandChild.point2(), self)
            elif (isinstance(commandChild, DrawingItemPointDisconnectCommand)):
                DrawingItemPointDisconnectCommand(commandChild.point1(), commandChild.point2(), self)


# ======================================================================================================================

class DrawingAddItemsCommand(DrawingUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, 'Add Items', parent)

        # Assumes each item in items is a not already a member of widget.items()
        self._items: list[DrawingItem] = items
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._items[:]

    def redo(self) -> None:
        self._undone = False
        self.widget().addItems(self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().removeItems(self._items)
        self._undone = True


# ======================================================================================================================

class DrawingRemoveItemsCommand(DrawingUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, 'Remove Items', parent)

        # Assumes each item in items is a member of widget.items()
        self._items: list[DrawingItem] = items
        self._undone: bool = True

        self._indices: dict[DrawingItem, int] = {}
        for item in self._items:
            self._indices[item] = self.widget().items().index(item)

    def __del__(self) -> None:
        if (not self._undone):
            del self._items[:]

    def redo(self) -> None:
        self._undone = False
        self.widget().removeItems(self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().insertItems(self._items, self._indices)
        self._undone = True


# ======================================================================================================================

class DrawingReorderItemsCommand(DrawingUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, 'Reorder Items', parent)

        # Assumes each item in items is a member of widget.items() and no items have been added or removed
        self._items: list[DrawingItem] = items
        self._originalItems: list[DrawingItem] = self.widget().items()

    def redo(self) -> None:
        # pylint: disable-next=W0212
        self.widget()._reorderItems(self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        # pylint: disable-next=W0212
        self.widget()._reorderItems(self._originalItems)


# ======================================================================================================================

class DrawingMoveItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], positions: dict[DrawingItem, QPointF],
                 finalMove: bool, parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, items, 'Move Items', parent)

        # Assumes each item in items is a member of widget.items() and has a corresponding position in positions
        self._positions: dict[DrawingItem, QPointF] = positions
        self._finalMove: bool = finalMove

        self._originalPositions: dict[DrawingItem, QPointF] = {}
        for item in self._items:
            self._originalPositions[item] = item.position()

    def positions(self) -> dict[DrawingItem, QPointF]:
        return self._positions

    def isFinalMove(self) -> bool:
        return self._finalMove

    def id(self) -> int:
        return DrawingItemsUndoCommand.Id.MoveItemsId.value

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, DrawingMoveItemsCommand) and self.widget() == command.widget() and
                self.items() == command.items() and not self._finalMove):
            self._positions = command.positions()
            self._finalMove = command.isFinalMove()
            self.mergeChildren(command)
            return True
        return False

    def redo(self) -> None:
        self.widget().moveItems(self._items, self._positions)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().moveItems(self._items, self._originalPositions)


# ======================================================================================================================

class DrawingResizeItemCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool,
                 finalResize: bool, parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, [point.item()], 'Resize Item', parent)

        # Assume the point is a member of a valid item which is in turn a member of widget.items()
        self._point: DrawingItemPoint = point
        self._position: QPointF = position
        self._snapTo45Degrees: bool = snapTo45Degrees
        self._finalResize: bool = finalResize
        self._originalPosition: QPointF = QPointF()

        item = point.item()
        if (isinstance(item, DrawingItem)):
            self._originalPosition = item.mapToScene(point.position())

    def point(self) -> DrawingItemPoint:
        return self._point

    def position(self) -> QPointF:
        return self._position

    def shouldSnapTo45Degrees(self) -> bool:
        return self._snapTo45Degrees

    def isFinalResize(self) -> bool:
        return self._finalResize

    def id(self) -> int:
        return DrawingItemsUndoCommand.Id.ResizeItemId.value

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, DrawingResizeItemCommand) and self.widget() == command.widget() and
                self._point == command.point() and not self._finalResize):
            self._position = command.position()
            self._snapTo45Degrees = command.shouldSnapTo45Degrees()
            self._finalResize = command.isFinalResize()
            self.mergeChildren(command)
            return True
        return False

    def redo(self) -> None:
        self.widget().resizeItem(self._point, self._position, self._snapTo45Degrees)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().resizeItem(self._point, self._originalPosition, False)


# ======================================================================================================================

class DrawingRotateItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], position: QPointF,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, items, 'Rotate Items', parent)

        # Assumes each item in items is a member of widget.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.widget().rotateItems(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().rotateBackItems(self._items, self._position)


# ======================================================================================================================

class DrawingRotateBackItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], position: QPointF,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, items, 'Rotate Back Items', parent)

        # Assumes each item in items is a member of widget.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.widget().rotateBackItems(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().rotateItems(self._items, self._position)


# ======================================================================================================================

class DrawingFlipItemsHorizontalCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], position: QPointF,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, items, 'Flip Items Horizontal', parent)

        # Assumes each item in items is a member of widget.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.widget().flipItemsHorizontal(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().flipItemsHorizontal(self._items, self._position)


# ======================================================================================================================

class DrawingFlipItemsVerticalCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], position: QPointF,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, items, 'Flip Items Vertical', parent)

        # Assumes each item in items is a member of widget.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.widget().flipItemsVertical(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().flipItemsVertical(self._items, self._position)


# ======================================================================================================================

class DrawingItemInsertPointCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, item: DrawingItem, point: DrawingItemPoint, index: int,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, [item], 'Insert Point', parent)

        # Assumes the item is a member of widget.items() and that point is not already a member of item.points()
        self._item: DrawingItem = item
        self._point: DrawingItemPoint = point
        self._index: int = index
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._point

    def redo(self) -> None:
        self._undone = False
        self.widget().insertItemPoint(self._item, self._point, self._index)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().removeItemPoint(self._item, self._point)
        self._undone = True


# ======================================================================================================================

class DrawingItemRemovePointCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, item: DrawingItem, point: DrawingItemPoint,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, [item], 'Remove Point', parent)

        # Assumes the item is a member of widget.items() and that point is a member of item.points()
        self._item: DrawingItem = item
        self._point: DrawingItemPoint = point
        self._index: int = item.points().index(point)
        self._undone: bool = True

    def __del__(self) -> None:
        if (not self._undone):
            del self._point

    def redo(self) -> None:
        self._undone = False
        self.widget().removeItemPoint(self._item, self._point)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().insertItemPoint(self._item, self._point, self._index)
        self._undone = True


# ======================================================================================================================

class DrawingItemPointConnectCommand(QUndoCommand):
    def __init__(self, point1: DrawingItemPoint, point2: DrawingItemPoint, parent: QUndoCommand | None = None) -> None:
        super().__init__('Connect Points', parent)

        # Assumes point1 and point2 are not already connected
        self._point1: DrawingItemPoint = point1
        self._point2: DrawingItemPoint = point2

    def point1(self) -> DrawingItemPoint:
        return self._point1

    def point2(self) -> DrawingItemPoint:
        return self._point2

    def redo(self) -> None:
        self._point1.addConnection(self._point2)
        self._point2.addConnection(self._point1)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._point1.removeConnection(self._point2)
        self._point2.removeConnection(self._point1)


# ======================================================================================================================

class DrawingItemPointDisconnectCommand(QUndoCommand):
    def __init__(self, point1: DrawingItemPoint, point2: DrawingItemPoint, parent: QUndoCommand | None = None) -> None:
        super().__init__('Disconnect Points', parent)

        # Assumes point1 and point2 are connected
        self._point1: DrawingItemPoint = point1
        self._point2: DrawingItemPoint = point2

    def point1(self) -> DrawingItemPoint:
        return self._point1

    def point2(self) -> DrawingItemPoint:
        return self._point2

    def redo(self) -> None:
        self._point1.removeConnection(self._point2)
        self._point2.removeConnection(self._point1)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._point1.addConnection(self._point2)
        self._point2.addConnection(self._point1)


# ======================================================================================================================

class DrawingSetItemsPropertyCommand(DrawingItemsUndoCommand):
    def __init__(self, widget: DrawingWidget, items: list[DrawingItem], name: str, value: typing.Any,
                 parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, items, 'Set Items Property', parent)

        # Assumes each item in items is a member of widget.items()
        self._name: str = name
        self._value: typing.Any = value

        self._originalValues: dict[DrawingItem, typing.Any] = {}
        for item in self._items:
            self._originalValues[item] = item.property(name)

    def redo(self) -> None:
        self.widget().setItemsProperty(self._items, self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().setItemsPropertyDict(self._items, self._name, self._originalValues)


# ======================================================================================================================

class DrawingSetWidgetPropertyCommand(DrawingUndoCommand):
    def __init__(self, widget: DrawingWidget, name: str, value: typing.Any, parent: QUndoCommand | None = None) -> None:
        super().__init__(widget, 'Set Property', parent)

        self._name: str = name
        self._value: typing.Any = value

        self._originalValue: typing.Any = self.widget().property(self._name)

        if (self._name == 'sceneRect'):
            self._viewRect = QRectF()

    def redo(self) -> None:
        self.widget().setProperty(self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.widget().setProperty(self._name, self._originalValue)
