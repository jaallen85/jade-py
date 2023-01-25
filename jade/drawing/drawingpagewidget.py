# drawingpagewidget.py
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
from enum import IntEnum
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, Signal
from PySide6.QtGui import QCursor, QMouseEvent, QUndoCommand
from PySide6.QtWidgets import QApplication
from .drawinggroupitem import DrawingGroupItem
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint
from .drawingpageview import DrawingPageView


class DrawingPageWidget(DrawingPageView):
    undoCommandCreated = Signal(QUndoCommand)
    cleanChanged = Signal(bool)
    modifiedStringChanged = Signal(str)
    currentItemsPropertyChanged = Signal(list)
    contextMenuTriggered = Signal(QPoint)

    # ==================================================================================================================

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
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def insertItems(self, items: list[DrawingItem], indices: dict[DrawingItem, int]) -> None:
        # Assumes each item in items is not already a member of self.items() and has a corresponding index in indices
        for item in items:
            self.insertItem(indices[item], item)
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def removeItems(self, items: list[DrawingItem]) -> None:
        # Assumes each item in items is a member of self.items()
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            self.setSelectedItems([])
        for item in items:
            self.removeItem(item)
        self.viewport().update()

    def _reorderItems(self, items: list[DrawingItem]) -> None:
        # Assumes that all members of self.items() are present in items with no extras
        self._items = items
        self.viewport().update()

    def moveItems(self, items: list[DrawingItem], positions: dict[DrawingItem, QPointF]) -> None:
        # Assumes each item in items is a member of self.items() and has a corresponding position in positions
        for item in items:
            item.move(positions[item])

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    def resizeItem(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        # Assume the point is a member of a valid item which is in turn a member of self.items()
        item = point.item()
        if (item is not None):
            item.resize(point, position, snapTo45Degrees)

            if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) == 1 and
                    item in self._selectedItems):
                self.currentItemsPropertyChanged.emit(self._selectedItems)
            elif (self._mode == DrawingPageWidget.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                    item in self._placeModeItems):
                self.currentItemsPropertyChanged.emit(self._placeModeItems)

            self.viewport().update()

    def rotateItems(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.rotate(position)

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a rotation event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def rotateBackItems(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.rotateBack(position)

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a rotation event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def flipItemsHorizontal(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.flipHorizontal(position)

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a flip event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def flipItemsVertical(self, items: list[DrawingItem], position: QPointF) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.flipVertical(position)

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a flip event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def insertItemPoint(self, item: DrawingItem, position: QPointF) -> None:
        # Assumes the item is a member of self.items()
        item.insertNewPoint(position)

        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) == 1 and
                item in self._selectedItems):
            self.currentItemsPropertyChanged.emit(self._selectedItems)
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                item in self._placeModeItems):
            self.currentItemsPropertyChanged.emit(self._placeModeItems)

        self.viewport().update()

    def removeItemPoint(self, item: DrawingItem, position: QPointF) -> None:
        # Assumes the item is a member of self.items()
        item.removeExistingPoint(position)

        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) == 1 and
                item in self._selectedItems):
            self.currentItemsPropertyChanged.emit(self._selectedItems)
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                item in self._placeModeItems):
            self.currentItemsPropertyChanged.emit(self._placeModeItems)

        self.viewport().update()

    def setItemsProperty(self, items: list[DrawingItem], name: str, value: typing.Any) -> None:
        # Assumes each item in items is a member of self.items()
        for item in items:
            item.setProperty(name, value)

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    def setItemsPropertyDict(self, items: list[DrawingItem], name: str, values: dict[DrawingItem, typing.Any]) -> None:
        # Assumes each item in items is a member of self.items() and has a corresponding value in values
        for item in items:
            item.setProperty(name, values[item])

        if ((self._mode == DrawingPageWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == DrawingPageWidget.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    # ==================================================================================================================

    def cut(self) -> None:
        self.copy()
        self.delete()

    def copy(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsElement = ElementTree.Element('items')
            DrawingItem.writeItemsToXml(itemsElement, self._selectedItems)
            clipboardStr = ElementTree.tostring(itemsElement, encoding='unicode')
            QApplication.clipboard().setText(clipboardStr)

    def paste(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            newItems = []
            rootElement = ElementTree.fromstring(QApplication.clipboard().text())
            if (rootElement.tag == 'items'):
                newItems = DrawingItem.readItemsFromXml(rootElement)
            if (len(newItems) > 0):
                self.setPlaceMode(newItems, False)

    def delete(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._removeItemsCommand(self._selectedItems))
        else:
            self.setSelectMode()

    # ==================================================================================================================

    def moveCurrentItemsDelta(self, delta: QPointF) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = item.position() + delta
                self._pushUndoCommand(self._moveItemsCommand(self._selectedItems, newPositions, finalMove=True,
                                                             place=True))

    def moveCurrentItem(self, position: QPointF) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = position
                self._pushUndoCommand(self._moveItemsCommand(self._selectedItems, newPositions, finalMove=True,
                                                             place=True))

    def resizeCurrentItem(self, point: DrawingItemPoint, position: QPointF) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                self._pushUndoCommand(self._resizeItemCommand(point, position, snapTo45Degrees=False, finalResize=True,
                                                              place=True, disconnect=False))

    def resizeCurrentItem2(self, point1: DrawingItemPoint, position1: QPointF,
                           point2: DrawingItemPoint, position2: QPointF) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                self._pushUndoCommand(self._resizeItemCommand2(point1, position1, point2, position2,
                                                               snapTo45Degrees=False, finalResize=True,
                                                               place=True, disconnect=False))

    # ==================================================================================================================

    def rotateCurrentItems(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._rotateItemsCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't rotate if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.rotateItems(self._placeModeItems,
                                     self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def rotateBackCurrentItems(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._rotateBackItemsCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't rotate if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.rotateBackItems(self._placeModeItems,
                                         self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def flipCurrentItemsHorizontal(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._flipItemsHorizontalCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't flip if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.flipItemsHorizontal(self._placeModeItems,
                                             self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def flipCurrentItemsVertical(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._flipItemsVerticalCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't flip if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.flipItemsVertical(self._placeModeItems,
                                           self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    # ==================================================================================================================

    def bringCurrentItemsForward(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemIndex = itemsOrdered.index(item)
                itemsOrdered.remove(item)
                itemsOrdered.insert(itemIndex + 1, item)

            self._pushUndoCommand(self._reorderItemsCommand(itemsOrdered, self._selectedItems.copy()))

    def sendCurrentItemsBackward(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemIndex = itemsOrdered.index(item)
                itemsOrdered.remove(item)
                itemsOrdered.insert(itemIndex - 1, item)

            self._pushUndoCommand(self._reorderItemsCommand(itemsOrdered, self._selectedItems.copy()))

    def bringCurrentItemsToFront(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemsOrdered.remove(item)
                itemsOrdered.append(item)

            self._pushUndoCommand(self._reorderItemsCommand(itemsOrdered, self._selectedItems.copy()))

    def sendCurrentItemsToBack(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._items.copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemsOrdered.remove(item)
                itemsOrdered.insert(0, item)

            self._pushUndoCommand(self._reorderItemsCommand(itemsOrdered, self._selectedItems.copy()))

    # ==================================================================================================================

    def groupCurrentItems(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) > 1):
            itemsToRemove = self._selectedItems.copy()

            itemGroup = DrawingGroupItem()

            # Put the group position equal to the position of the last item and adjust each item's position accordingly
            items = DrawingItem.copyItems(itemsToRemove)
            itemGroup.setPosition(itemsToRemove[-1].position())
            for item in items:
                item.setPosition(itemGroup.mapFromScene(item.position()))
            itemGroup.setItems(items)

            # Replace the selected items with the new group item
            self.setSelectedItems([])

            groupCommand = DrawingPageUndoCommand(self, 'Group Items')
            groupCommand.addChild(self._removeItemsCommand(itemsToRemove))
            groupCommand.addChild(self._addItemsCommand([itemGroup], False))
            self._pushUndoCommand(groupCommand)

    def ungroupCurrentItem(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) == 1):
            itemGroup = self._selectedItems[0]
            if (isinstance(itemGroup, DrawingGroupItem)):
                itemsToAdd = DrawingItem.copyItems(itemGroup.items())
                for item in itemsToAdd:
                    # Apply the group's position/transform to each item
                    item.setPosition(itemGroup.mapToScene(item.position()))
                    item.setRotation(item.rotation() + itemGroup.rotation())
                    if (itemGroup.isFlipped()):
                        item.setFlipped(not item.isFlipped())

                # Replace the selected group item with copies of its constituent items
                self.setSelectedItems([])

                ungroupCommand = DrawingPageUndoCommand(self, 'Group Items')
                ungroupCommand.addChild(self._removeItemsCommand([itemGroup]))
                ungroupCommand.addChild(self._addItemsCommand(itemsToAdd, False))
                self._pushUndoCommand(ungroupCommand)

    # ==================================================================================================================

    def insertNewItemPoint(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) == 1):
            item = self._selectedItems[0]
            if (item.canInsertPoints()):
                self._pushUndoCommand(self._insertPointCommand(
                    item, self.roundPointToGrid(self._mouseButtonDownScenePosition)))

    def removeCurrentItemPoint(self) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode and len(self._selectedItems) == 1):
            item = self._selectedItems[0]
            if (item.canRemovePoints()):
                self._pushUndoCommand(self._removePointCommand(
                    item, self.roundPointToGrid(self._mouseButtonDownScenePosition)))

    # ==================================================================================================================

    def updateProperty(self, name: str, value: typing.Any) -> None:
        self._pushUndoCommand(DrawingSetPagePropertyCommand(self, name, value))

    def updateCurrentItemsProperty(self, name: str, value: typing.Any) -> None:
        if (self._mode == DrawingPageWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(DrawingSetItemsPropertyCommand(self, self._selectedItems, name, value))
        elif (self._mode == DrawingPageWidget.Mode.PlaceMode):
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
            deltaPosition = self.roundPointToGrid(mousePosition - self._mouseButtonDownScenePosition)
            if (finalMove or deltaPosition != self._selectMoveItemsPreviousDeltaPosition):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = self._selectMoveItemsInitialPositions[item] + deltaPosition

                self._pushUndoCommand(self._moveItemsCommand(self._selectedItems, newPositions, finalMove,
                                      place=placeItems))

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
                self._pushUndoCommand(self._resizeItemCommand(self._selectMouseDownPoint, newPosition, snapTo45Degrees,
                                                              finalResize, place=finalResize, disconnect=True))

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
        deltaPosition = self.roundPointToGrid(self.mapToScene(event.pos())) - centerPosition

        if (deltaPosition.x() != 0 or deltaPosition.y() != 0):
            newPositions = {}
            for item in self._placeModeItems:
                newPositions[item] = item.position() + deltaPosition
            self.moveItems(self._placeModeItems, newPositions)

            self.mouseInfoChanged.emit(self._createMouseInfo1(self.roundPointToGrid(self.mapToScene(event.pos()))))

    def _placeModeLeftMousePressEvent(self, event: QMouseEvent) -> None:
        # Nothing to do here.
        pass

    def _placeModeLeftMouseDragEvent(self, event: QMouseEvent) -> None:
        if (self._placeByMousePressAndRelease):
            # Resize the item's end point to the current mouse position
            placeItem = self._placeModeItems[0]
            placeItemResizeStartPoint = placeItem.placeResizeStartPoint()
            placeItemResizeEndPoint = placeItem.placeResizeEndPoint()

            if (placeItemResizeStartPoint is not None and placeItemResizeEndPoint is not None):
                startPosition = placeItem.mapToScene(placeItemResizeStartPoint.position())
                endPosition = self.roundPointToGrid(self.mapToScene(event.pos()))
                snapTo45Degrees = ((event.modifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier)    # noqa

                self.resizeItem(placeItemResizeEndPoint, endPosition, snapTo45Degrees)

                self.mouseInfoChanged.emit(self._createMouseInfo2(startPosition, endPosition))
            else:
                self._placeModeNoButtonMouseMoveEvent(event)
        else:
            self._placeModeNoButtonMouseMoveEvent(event)

    def _placeModeLeftMouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (len(self._placeModeItems) > 0 or (len(self._placeModeItems) == 1 and self._placeModeItems[0].isValid())):
            # Place the items within the scene.
            self._pushUndoCommand(self._addItemsCommand(self._placeModeItems, place=(len(self._placeModeItems) == 1)))

            # Create a new set of place items
            newItems = DrawingItem.copyItems(self._placeModeItems)
            if (self._placeByMousePressAndRelease):
                for item in newItems:
                    item.placeCreateEvent(self.contentRect(), self._grid)

            self._placeModeItems = []
            self.setPlaceMode(newItems, self._placeByMousePressAndRelease)

    # ==================================================================================================================

    def _addItemsCommand(self, items: list[DrawingItem], place: bool) -> 'DrawingAddItemsCommand':
        # Assume items is not empty and that each item in items is not already a member of self.items()
        addCommand = DrawingAddItemsCommand(self, items)
        if (place):
            addCommand.redo()
            self._placeItems(items, addCommand)
            addCommand.undo()
        return addCommand

    def _removeItemsCommand(self, items: list[DrawingItem]) -> 'DrawingRemoveItemsCommand':
        # Assume items is not empty and that each item in items is a member of self.items()
        removeCommand = DrawingRemoveItemsCommand(self, items)
        removeCommand.redo()
        self._unplaceItems(items, removeCommand)
        removeCommand.undo()
        return removeCommand

    def _reorderItemsCommand(self, items: list[DrawingItem],
                             selectedItems: list[DrawingItem]) -> 'DrawingReorderItemsCommand':
        # Assumes that all members of self.items() are present in items with no extras
        return DrawingReorderItemsCommand(self, items, selectedItems)

    def _moveItemsCommand(self, items: list[DrawingItem], positions: dict[DrawingItem, QPointF], finalMove: bool,
                          place: bool) -> 'DrawingMoveItemsCommand':
        # Assume items is not empty and that each item in items is a member of self.items() and has a corresponding
        # position in positions
        moveCommand = DrawingMoveItemsCommand(self, items, positions, finalMove)
        moveCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, moveCommand)
        if (place):
            self._placeItems(items, moveCommand)
        moveCommand.undo()
        return moveCommand

    def _resizeItemCommand(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool, finalResize: bool,
                           place: bool, disconnect: bool) -> 'DrawingResizeItemCommand':
        # Assume the point is a member of a valid item which is in turn a member of self.items()
        resizeCommand = DrawingResizeItemCommand(self, point, position, snapTo45Degrees, finalResize)
        resizeCommand.redo()
        if (disconnect):
            self._disconnectAll(point, resizeCommand)
        self._tryToMaintainConnections([point.item()], True, not point.isFree(), point, resizeCommand)
        if (place):
            self._placeItems([point.item()], resizeCommand)
        resizeCommand.undo()
        return resizeCommand

    def _resizeItemCommand2(self, point1: DrawingItemPoint, position1: QPointF,
                            point2: DrawingItemPoint, position2: QPointF, snapTo45Degrees: bool, finalResize: bool,
                            place: bool, disconnect: bool) -> 'DrawingItemsUndoCommand':
        # Assume that point1 and point2 are members of the same valid item which is in turn a member of self.items()
        resizeCommand = DrawingItemsUndoCommand(self, [point1.item()], 'Resize Item')

        resizeCommand1 = DrawingResizeItemCommand(self, point1, position1, snapTo45Degrees, finalResize)
        resizeCommand2 = DrawingResizeItemCommand(self, point2, position2, snapTo45Degrees, finalResize)
        resizeCommand.addChild(resizeCommand1)
        resizeCommand.addChild(resizeCommand2)

        resizeCommand1.redo()
        resizeCommand2.redo()
        if (disconnect):
            self._disconnectAll(point1, resizeCommand)
            self._disconnectAll(point2, resizeCommand)
        self._tryToMaintainConnections([point1.item()], True, not point1.isFree(), point1, resizeCommand)
        self._tryToMaintainConnections([point2.item()], True, not point2.isFree(), point2, resizeCommand)
        if (place):
            self._placeItems([point1.item()], resizeCommand)
        resizeCommand2.undo()
        resizeCommand1.undo()

        return resizeCommand

    def _rotateItemsCommand(self, items: list[DrawingItem],
                            position: QPointF) -> 'DrawingRotateItemsCommand':
        # Assume items is not empty and that each item in items is a member of self.items()
        rotateCommand = DrawingRotateItemsCommand(self, items, position)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        return rotateCommand

    def _rotateBackItemsCommand(self, items: list[DrawingItem],
                                position: QPointF) -> 'DrawingRotateBackItemsCommand':
        # Assume items is not empty and that each item in items is a member of self.items()
        rotateCommand = DrawingRotateBackItemsCommand(self, items, position)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        return rotateCommand

    def _flipItemsHorizontalCommand(self, items: list[DrawingItem],
                                    position: QPointF) -> 'DrawingFlipItemsHorizontalCommand':
        # Assume items is not empty and that each item in items is a member of self.items()
        flipCommand = DrawingFlipItemsHorizontalCommand(self, items, position)
        flipCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, flipCommand)
        flipCommand.undo()
        return flipCommand

    def _flipItemsVerticalCommand(self, items: list[DrawingItem],
                                  position: QPointF) -> 'DrawingFlipItemsVerticalCommand':
        # Assume items is not empty and that each item in items is a member of self.items()
        flipCommand = DrawingFlipItemsVerticalCommand(self, items, position)
        flipCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, flipCommand)
        flipCommand.undo()
        return flipCommand

    def _insertPointCommand(self, item: DrawingItem, position: QPointF) -> 'DrawingItemInsertPointCommand':
        # Assumes the item is a member of self.items()
        return DrawingItemInsertPointCommand(self, item, position)

    def _removePointCommand(self, item: DrawingItem, position: QPointF) -> 'DrawingItemRemovePointCommand':
        # Assumes the item is a member of self.items()
        return DrawingItemRemovePointCommand(self, item, position)

    def _connectPointsCommand(self, point1: DrawingItemPoint,
                              point2: DrawingItemPoint) -> 'DrawingItemPointConnectCommand':
        # Assumes point1 and point2 are not already connected
        connectCommand = DrawingItemPointConnectCommand(point1, point2)

        point1Item = point1.item()
        point2Item = point2.item()
        if (isinstance(point1Item, DrawingItem) and isinstance(point2Item, DrawingItem)):
            point1Position = point1Item.mapToScene(point1.position())
            point2Position = point2Item.mapToScene(point2.position())
            if (point1Position != point2Position):
                if (point2.isControlPoint()):
                    connectCommand.addChild(self._resizeItemCommand(point2, point1Position, False, finalResize=False,
                                            place=False, disconnect=True))
                elif (point1.isControlPoint()):
                    connectCommand.addChild(self._resizeItemCommand(point1, point2Position, False, finalResize=False,
                                            place=False, disconnect=True))

        return connectCommand

    def _disconnectPointsCommand(self, point1: DrawingItemPoint,
                                 point2: DrawingItemPoint) -> 'DrawingItemPointDisconnectCommand':
        # Assumes point1 and point2 are connected
        return DrawingItemPointDisconnectCommand(point1, point2)

    # ==================================================================================================================

    def _placeItems(self, items: list[DrawingItem], command: 'DrawingUndoCommand') -> None:
        # Assume each item in items already is or is about to become a member of self.items()
        for widgetItem in self._items:
            if (widgetItem not in items and widgetItem not in self._placeModeItems):
                for widgetItemPoint in widgetItem.points():
                    for item in items:
                        for point in item.points():
                            if (self._shouldConnect(point, widgetItemPoint)):
                                command.addChild(self._connectPointsCommand(point, widgetItemPoint))

    def _unplaceItems(self, items: list[DrawingItem], command: 'DrawingUndoCommand') -> None:
        # Assume each item in items is a member of self.items()
        for item in items:
            for point in item.points():
                for targetPoint in point.connections():
                    if (targetPoint.item() not in items):
                        command.addChild(self._disconnectPointsCommand(point, targetPoint))

    def _tryToMaintainConnections(self, items: list[DrawingItem], allowResize: bool, checkControlPoints: bool,
                                  pointToSkip: DrawingItemPoint | None, command: 'DrawingUndoCommand') -> None:
        # Assume each item in items is a member of self.items()
        for item in items:
            for point in item.points():
                if (point != pointToSkip and (checkControlPoints or not point.isControlPoint())):
                    for targetPoint in point.connections():
                        targetItem = targetPoint.item()
                        if (isinstance(targetItem, DrawingItem) and
                                item.mapToScene(point.position()) != targetItem.mapToScene(targetPoint.position())):
                            # Try to maintain the connection by resizing targetPoint if possible
                            if (allowResize and targetPoint.isFree() and not self._shouldDisconnect(point, targetPoint)):   # noqa
                                command.addChild(
                                    self._resizeItemCommand(targetPoint, item.mapToScene(point.position()), False,
                                                            finalResize=False, place=False, disconnect=False))
                            else:
                                command.addChild(self._disconnectPointsCommand(point, targetPoint))

    def _disconnectAll(self, point: DrawingItemPoint, command: 'DrawingUndoCommand') -> None:
        for targetPoint in point.connections():
            command.addChild(self._disconnectPointsCommand(point, targetPoint))

    # ==================================================================================================================

    def _pushUndoCommand(self, command: QUndoCommand) -> None:
        self.undoCommandCreated.emit(command)

    def _emitModifiedStringChanged(self, clean: bool) -> None:
        self.modifiedStringChanged.emit('Modified' if (not clean) else '')

    def _updateSelectionCenter(self) -> None:
        self._selectedItemsCenter = self._itemsCenter(self._selectedItems)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class DrawingUndoCommand(QUndoCommand):
    def __init__(self, text: str) -> None:
        super().__init__(text)

        self._children: list[QUndoCommand] = []

    def addChild(self, command: QUndoCommand) -> None:
        self._children.append(command)

    def children(self) -> list[QUndoCommand]:
        return self._children

    def redo(self) -> None:
        for child in self._children:
            child.redo()
        super().redo()

    def undo(self) -> None:
        super().undo()
        for child in reversed(self._children):
            child.undo()


# ======================================================================================================================

class DrawingPageUndoCommand(DrawingUndoCommand):
    def __init__(self, page: DrawingPageWidget, text: str) -> None:
        super().__init__(text)

        self._page: DrawingPageWidget = page
        self._viewRect: QRectF = self._page.visibleRect()

    def page(self) -> DrawingPageWidget:
        return self._page

    def viewRect(self) -> QRectF:
        return self._viewRect


# ======================================================================================================================

class DrawingItemsUndoCommand(DrawingPageUndoCommand):
    class Id(IntEnum):
        MoveItemsId = 0
        ResizeItemId = 1
        SetItemsPropertyId = 2

    # ==================================================================================================================

    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], text: str) -> None:
        super().__init__(page, text)
        self._items = items

    def items(self) -> list[DrawingItem]:
        return self._items

    # ==================================================================================================================

    def mergeChildren(self, command: QUndoCommand) -> None:
        if (isinstance(command, DrawingUndoCommand)):
            for commandChild in command.children():
                if (isinstance(commandChild, DrawingResizeItemCommand)):
                    self.addChild(DrawingResizeItemCommand(commandChild.page(), commandChild.point(),
                                                           commandChild.position(),
                                                           commandChild.shouldSnapTo45Degrees(),
                                                           commandChild.isFinalResize()))
                elif (isinstance(commandChild, DrawingItemPointConnectCommand)):
                    self.addChild(DrawingItemPointConnectCommand(commandChild.point1(), commandChild.point2()))
                elif (isinstance(commandChild, DrawingItemPointDisconnectCommand)):
                    self.addChild(DrawingItemPointDisconnectCommand(commandChild.point1(), commandChild.point2()))


# ======================================================================================================================

class DrawingAddItemsCommand(DrawingPageUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem]) -> None:
        super().__init__(page, 'Add Items')

        # Assumes each item in items is a not already a member of page.items()
        self._items: list[DrawingItem] = items
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._items[:]

    def redo(self) -> None:
        self._undone = False
        self.page().addItems(self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().removeItems(self._items)
        self._undone = True


# ======================================================================================================================

class DrawingRemoveItemsCommand(DrawingPageUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem]) -> None:
        super().__init__(page, 'Remove Items')

        # Assumes each item in items is a member of page.items()
        self._items: list[DrawingItem] = items
        self._undone: bool = True

        self._indices: dict[DrawingItem, int] = {}
        for item in self._items:
            self._indices[item] = self.page().items().index(item)

    def __del__(self) -> None:
        if (not self._undone):
            del self._items[:]

    def redo(self) -> None:
        self._undone = False
        self.page().removeItems(self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().insertItems(self._items, self._indices)
        self._undone = True


# ======================================================================================================================

class DrawingReorderItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], selectedItems: list[DrawingItem]) -> None:
        super().__init__(page, selectedItems, 'Reorder Items')

        # Assumes each item in items is a member of page.items() and no items have been added or removed
        self._itemOrder: list[DrawingItem] = items
        self._originalItemOrder: list[DrawingItem] = self.page().items()

    def redo(self) -> None:
        # pylint: disable-next=W0212
        self.page()._reorderItems(self._itemOrder)
        super().redo()

    def undo(self) -> None:
        super().undo()
        # pylint: disable-next=W0212
        self.page()._reorderItems(self._originalItemOrder)


# ======================================================================================================================

class DrawingMoveItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], positions: dict[DrawingItem, QPointF],
                 finalMove: bool) -> None:
        super().__init__(page, items, 'Move Items')

        # Assumes each item in items is a member of page.items() and has a corresponding position in positions
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
        return DrawingItemsUndoCommand.Id.MoveItemsId

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, DrawingMoveItemsCommand) and self.page() == command.page() and
                self.items() == command.items() and not self._finalMove):
            self._positions = command.positions()
            self._finalMove = command.isFinalMove()
            self.mergeChildren(command)
            return True
        return False

    def redo(self) -> None:
        self.page().moveItems(self._items, self._positions)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().moveItems(self._items, self._originalPositions)


# ======================================================================================================================

class DrawingResizeItemCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool,
                 finalResize: bool) -> None:
        super().__init__(page, [point.item()], 'Resize Item')

        # Assume the point is a member of a valid item which is in turn a member of page.items()
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
        return DrawingItemsUndoCommand.Id.ResizeItemId

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, DrawingResizeItemCommand) and self.page() == command.page() and
                self._point == command.point() and not self._finalResize):
            self._position = command.position()
            self._snapTo45Degrees = command.shouldSnapTo45Degrees()
            self._finalResize = command.isFinalResize()
            self.mergeChildren(command)
            return True
        return False

    def redo(self) -> None:
        self.page().resizeItem(self._point, self._position, self._snapTo45Degrees)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().resizeItem(self._point, self._originalPosition, False)


# ======================================================================================================================

class DrawingRotateItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], position: QPointF) -> None:
        super().__init__(page, items, 'Rotate Items')

        # Assumes each item in items is a member of page.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.page().rotateItems(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().rotateBackItems(self._items, self._position)


# ======================================================================================================================

class DrawingRotateBackItemsCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], position: QPointF) -> None:
        super().__init__(page, items, 'Rotate Back Items')

        # Assumes each item in items is a member of page.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.page().rotateBackItems(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().rotateItems(self._items, self._position)


# ======================================================================================================================

class DrawingFlipItemsHorizontalCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], position: QPointF) -> None:
        super().__init__(page, items, 'Flip Items Horizontal')

        # Assumes each item in items is a member of page.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.page().flipItemsHorizontal(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().flipItemsHorizontal(self._items, self._position)


# ======================================================================================================================

class DrawingFlipItemsVerticalCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], position: QPointF) -> None:
        super().__init__(page, items, 'Flip Items Vertical')

        # Assumes each item in items is a member of page.items()
        self._position: QPointF = position

    def redo(self) -> None:
        self.page().flipItemsVertical(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().flipItemsVertical(self._items, self._position)


# ======================================================================================================================

class DrawingItemInsertPointCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, item: DrawingItem, position: QPointF) -> None:
        super().__init__(page, [item], 'Insert Point')

        # Assumes the item is a member of page.items()
        self._item: DrawingItem = item
        self._position: QPointF = position

    def redo(self) -> None:
        self.page().insertItemPoint(self._item, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().removeItemPoint(self._item, self._position)


# ======================================================================================================================

class DrawingItemRemovePointCommand(DrawingItemsUndoCommand):
    def __init__(self, page: DrawingPageWidget, item: DrawingItem, position: QPointF) -> None:
        super().__init__(page, [item], 'Remove Point')

        # Assumes the item is a member of page.items()
        self._item: DrawingItem = item
        self._position: QPointF = position
        self._undone: bool = True

    def redo(self) -> None:
        self.page().removeItemPoint(self._item, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().insertItemPoint(self._item, self._position)


# ======================================================================================================================

class DrawingItemPointConnectCommand(DrawingUndoCommand):
    def __init__(self, point1: DrawingItemPoint, point2: DrawingItemPoint) -> None:
        super().__init__('Connect Points')

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

class DrawingItemPointDisconnectCommand(DrawingUndoCommand):
    def __init__(self, point1: DrawingItemPoint, point2: DrawingItemPoint) -> None:
        super().__init__('Disconnect Points')

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
    def __init__(self, page: DrawingPageWidget, items: list[DrawingItem], name: str, value: typing.Any) -> None:
        super().__init__(page, items, 'Set Items Property')

        # Assumes each item in items is a member of page.items()
        self._name: str = name
        self._value: typing.Any = value

        self._originalValues: dict[DrawingItem, typing.Any] = {}
        for item in self._items:
            self._originalValues[item] = item.property(name)

    def name(self) -> str:
        return self._name

    def value(self) -> typing.Any:
        return self._value

    def id(self) -> int:
        return DrawingItemsUndoCommand.Id.SetItemsPropertyId

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, DrawingSetItemsPropertyCommand) and self.page() == command.page()):
            if (len(self.items()) == 1 and len(command.items()) == 1 and self.items()[0] == command.items()[0] and
                    self.name() == 'caption' and command.name() == 'caption'):
                self._value = command.value()
                self.mergeChildren(command)
                return True
        return False

    def redo(self) -> None:
        self.page().setItemsProperty(self._items, self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().setItemsPropertyDict(self._items, self._name, self._originalValues)


# ======================================================================================================================

class DrawingSetPagePropertyCommand(DrawingPageUndoCommand):
    def __init__(self, page: DrawingPageWidget, name: str, value: typing.Any) -> None:
        super().__init__(page, 'Set Property')

        self._name: str = name
        self._value: typing.Any = value

        self._originalValue: typing.Any = self.page().property(self._name)

        if (self._name == 'sceneRect'):
            self._viewRect = QRectF()

    def redo(self) -> None:
        self.page().setProperty(self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self.page().setProperty(self._name, self._originalValue)
