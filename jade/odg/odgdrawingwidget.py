# odgdrawingwidget.py
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

from enum import IntEnum
from typing import Any
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QColor, QCursor, QMouseEvent, QUndoCommand, QUndoStack
from .odgdrawingview import OdgDrawingView
from .odggroupitem import OdgGroupItem
from .odgitem import OdgItem
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgItemStyle
from .odgpage import OdgPage
from .odgwriter import OdgWriter


class OdgDrawingWidget(OdgDrawingView):
    cleanChanged = Signal(bool)
    cleanTextChanged = Signal(str)

    currentPagePropertyChanged = Signal(str, object)
    currentItemsPropertyChanged = Signal(list)

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._newPageCount: int = 0

        self._undoStack: QUndoStack = QUndoStack()
        self._undoStack.setUndoLimit(64)
        self._undoStack.cleanChanged.connect(self.cleanChanged)             # type: ignore
        self._undoStack.cleanChanged.connect(self._emitCleanTextChanged)    # type: ignore

        self._selectedItemsCenter: QPointF = QPointF()

        self._selectMoveItemsInitialPositions: dict[OdgItem, QPointF] = {}
        self._selectMoveItemsPreviousDeltaPosition: QPointF = QPointF()
        self._selectResizeItemInitialPosition: QPointF = QPointF()
        self._selectResizeItemPreviousPosition: QPointF = QPointF()

        self.currentItemsChanged.connect(self._updateSelectionCenter)
        self.currentItemsPropertyChanged.connect(self._updateSelectionCenter)
        self.modeChanged.connect(self._clearModeStateVariables)

    # ==================================================================================================================

    def addItems(self, page: OdgPage, items: list[OdgItem]) -> None:
        # Assumes each item in items is not already a member of page.items()
        for item in items:
            page.addItem(item)
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def insertItems(self, page: OdgPage, items: list[OdgItem], indices: dict[OdgItem, int]) -> None:
        # Assumes each item in items is not already a member of page.items() and has a corresponding index in indices
        for item in items:
            page.insertItem(indices[item], item)
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            self.setSelectedItems(items)
        self.viewport().update()

    def removeItems(self, page: OdgPage, items: list[OdgItem]) -> None:
        # Assumes each item in items is a member of page.items()
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            self.setSelectedItems([])
        for item in items:
            page.removeItem(item)
        self.viewport().update()

    def _reorderItems(self, page: OdgPage, items: list[OdgItem]) -> None:
        # Assumes that all members of page.items() are present in items with no extras
        # pylint: disable-next=W0212
        page._items = items
        self.viewport().update()

    def moveItems(self, items: list[OdgItem], positions: dict[OdgItem, QPointF]) -> None:
        # Assumes each item in items has a corresponding position in positions
        for item in items:
            item.move(positions[item])

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    def resizeItem(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        # Assume the point is a member of a valid item
        item = point.item()
        if (item is not None):
            item.resize(point, position, snapTo45Degrees)

            if (self._mode == OdgDrawingWidget.Mode.SelectMode and len(self._selectedItems) == 1 and
                    item in self._selectedItems):
                self.currentItemsPropertyChanged.emit(self._selectedItems)
            elif (self._mode == OdgDrawingWidget.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                    item in self._placeModeItems):
                self.currentItemsPropertyChanged.emit(self._placeModeItems)

            self.viewport().update()

    def rotateItems(self, items: list[OdgItem], position: QPointF) -> None:
        for item in items:
            item.rotate(position)

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a rotation event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def rotateBackItems(self, items: list[OdgItem], position: QPointF) -> None:
        for item in items:
            item.rotateBack(position)

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a rotation event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def flipItemsHorizontal(self, items: list[OdgItem], position: QPointF) -> None:
        for item in items:
            item.flipHorizontal(position)

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a flip event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def flipItemsVertical(self, items: list[OdgItem], position: QPointF) -> None:
        for item in items:
            item.flipVertical(position)

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            oldSelectionCenter = self._selectedItemsCenter
            self.currentItemsPropertyChanged.emit(items)
            # Don't change the selection center on a flip event
            self._selectedItemsCenter = oldSelectionCenter

        self.viewport().update()

    def insertItemPoint(self, item: OdgItem, position: QPointF) -> None:
        item.insertNewPoint(position)

        if (self._mode == OdgDrawingWidget.Mode.SelectMode and len(self._selectedItems) == 1 and
                item in self._selectedItems):
            self.currentItemsPropertyChanged.emit(self._selectedItems)
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                item in self._placeModeItems):
            self.currentItemsPropertyChanged.emit(self._placeModeItems)

        self.viewport().update()

    def removeItemPoint(self, item: OdgItem, position: QPointF) -> None:
        item.removeExistingPoint(position)

        if (self._mode == OdgDrawingWidget.Mode.SelectMode and len(self._selectedItems) == 1 and
                item in self._selectedItems):
            self.currentItemsPropertyChanged.emit(self._selectedItems)
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode and len(self._placeModeItems) == 1 and
                item in self._placeModeItems):
            self.currentItemsPropertyChanged.emit(self._placeModeItems)

        self.viewport().update()

    def setPageProperty(self, page: OdgPage, name: str, value: Any) -> None:
        page.setProperty(name, value)

        if (self._currentPage == page):
            self.currentPagePropertyChanged.emit(name, value)

        self.viewport().update()

    def setItemsProperty(self, items: list[OdgItem], name: str, value: Any) -> None:
        for item in items:
            item.setProperty(name, value)

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    def setItemsPropertyDict(self, items: list[OdgItem], name: str, values: dict[OdgItem, Any]) -> None:
        for item in items:
            item.setProperty(name, values[item])

        if ((self._mode == OdgDrawingWidget.Mode.SelectMode and items == self._selectedItems) or
                (self._mode == OdgDrawingWidget.Mode.PlaceMode and items == self._placeModeItems)):
            self.currentItemsPropertyChanged.emit(items)

        self.viewport().update()

    # ==================================================================================================================

    def createNew(self) -> None:
        self.insertNewPage()
        self._undoStack.clear()

    def save(self, path: str) -> bool:
        writer = OdgWriter(path, self._units, self._pageSize, self._pageMargins)
        self._write(writer)
        writer.commit()
        self._undoStack.setClean()
        return True

    def load(self, path: str) -> bool:
        self.clear()
        result = super().load(path)
        if (result):
            self._undoStack.setClean()
        return result

    def clear(self) -> None:
        super().clear()
        self._undoStack.clear()
        self._newPageCount = 0

    def _write(self, writer: OdgWriter) -> None:
        writer.startMetaDocument()
        writer.endDocument()

        writer.startSettingsDocument()
        self._writeSettings(writer)
        writer.endDocument()

        writer.startStylesDocument()
        self._writeStyles(writer)
        writer.endDocument()

        writer.startContentDocument()
        self._writeContent(writer)
        writer.endDocument()

    def _writeSettings(self, writer: OdgWriter) -> None:
        writer.writeStartElement('office:settings')

        writer.writeStartElement('config:config-item-set')
        writer.writeAttribute('config:name', 'jade:settings')

        # Units and grid settings
        writer.writeStartElement('config:config-item')
        writer.writeAttribute('config:name', 'units')
        writer.writeAttribute('config:type', 'string')
        writer.writeCharacters(str(self._units))
        writer.writeEndElement()

        writer.writeStartElement('config:config-item')
        writer.writeAttribute('config:name', 'grid')
        writer.writeAttribute('config:type', 'double')
        writer.writeCharacters(str(self._grid))
        writer.writeEndElement()

        writer.writeStartElement('config:config-item')
        writer.writeAttribute('config:name', 'gridVisible')
        writer.writeAttribute('config:type', 'boolean')
        writer.writeCharacters('true' if self._gridVisible else 'false')
        writer.writeEndElement()

        writer.writeStartElement('config:config-item')
        writer.writeAttribute('config:name', 'gridColor')
        writer.writeAttribute('config:type', 'string')
        writer.writeCharacters(self._gridColor.name(QColor.NameFormat.HexRgb))
        writer.writeEndElement()

        writer.writeStartElement('config:config-item')
        writer.writeAttribute('config:name', 'gridSpacingMajor')
        writer.writeAttribute('config:type', 'int')
        writer.writeCharacters(str(self._gridSpacingMajor))
        writer.writeEndElement()

        writer.writeStartElement('config:config-item')
        writer.writeAttribute('config:name', 'gridSpacingMinor')
        writer.writeAttribute('config:type', 'int')
        writer.writeCharacters(str(self._gridSpacingMinor))
        writer.writeEndElement()

        writer.writeEndElement()

        writer.writeEndElement()

    def _writeStyles(self, writer: OdgWriter) -> None:
        # Item styles
        writer.writeStartElement('office:styles')

        OdgItemStyle.writeDashStyles(writer)
        OdgItemStyle.writeMarkerStyles(writer)

        writer.writeStartElement('style:style')
        self._defaultItemStyle.write(writer)
        writer.writeEndElement()

        for style in self._itemStyles:
            writer.writeStartElement('style:style')
            style.write(writer)
            writer.writeEndElement()

        writer.writeEndElement()

        # Page styles
        writer.writeStartElement('office:automatic-styles')

        writer.writeStartElement('style:page-layout')
        writer.writeAttribute('style:name', 'DefaultPageLayout')

        writer.writeStartElement('style:page-layout-properties')
        writer.writeLengthAttribute('fo:page-width', self._pageSize.width())
        writer.writeLengthAttribute('fo:page-height', self._pageSize.height())
        writer.writeLengthAttribute('fo:margin-left', self._pageMargins.left())
        writer.writeLengthAttribute('fo:margin-top', self._pageMargins.top())
        writer.writeLengthAttribute('fo:margin-right', self._pageMargins.right())
        writer.writeLengthAttribute('fo:margin-bottom', self._pageMargins.bottom())
        writer.writeEndElement()

        writer.writeEndElement()
        writer.writeStartElement('style:style')
        writer.writeAttribute('style:name', 'DefaultPageStyle')
        writer.writeAttribute('style:family', 'drawing-page')

        writer.writeStartElement('style:drawing-page-properties')
        writer.writeFillAttributes(self._backgroundColor)
        writer.writeAttribute('draw:background-size', 'border')
        writer.writeEndElement()

        writer.writeEndElement()

        writer.writeEndElement()

        # Master page
        writer.writeStartElement('office:master-styles')

        writer.writeStartElement('style:master-page')
        writer.writeAttribute('style:name', 'Default')
        writer.writeAttribute('style:page-layout-name', 'DefaultPageLayout')
        writer.writeAttribute('draw:style-name', 'DefaultPageStyle')
        writer.writeEndElement()

        writer.writeEndElement()

    def _writeContent(self, writer: OdgWriter) -> None:
        # Automatic item styles
        writer.writeStartElement('office:automatic-styles')
        for page in self._pages:
            for item in page.items():
                style = item.style()
                if (isinstance(style, OdgItemStyle)):
                    writer.writeStartElement('style:style')
                    style.write(writer)
                    writer.writeEndElement()

        writer.writeEndElement()

        # Pages
        writer.writeStartElement('office:body')
        writer.writeStartElement('office:drawing')

        for page in self._pages:
            writer.writeStartElement('draw:page')
            page.write(writer)
            writer.writeEndElement()

        writer.writeEndElement()
        writer.writeEndElement()

    # ==================================================================================================================

    def undo(self) -> None:
        if (self.mode() == OdgDrawingWidget.Mode.SelectMode):
            # Get the command that will be undone by the call to self._undoStack.undo()
            command = self._undoStack.command(self._undoStack.index() - 1)

            if (isinstance(command, OdgDrawingUndoCommand)):
                self.setCurrentPage(command.viewPage())
                self.zoomToRect(command.viewRect())
                if (isinstance(command, OdgItemsUndoCommand)):
                    self.setSelectedItems(command.items())
                else:
                    self.setSelectedItems([])

            self._undoStack.undo()
        else:
            self.setSelectMode()

    def redo(self) -> None:
        if (self.mode() == OdgDrawingWidget.Mode.SelectMode):
            # Get the command that will be redone by the call to self._undoStack.redo()
            command = self._undoStack.command(self._undoStack.index())

            if (isinstance(command, OdgDrawingUndoCommand)):
                self.setCurrentPage(command.viewPage())
                self.zoomToRect(command.viewRect())
                if (isinstance(command, OdgItemsUndoCommand)):
                    self.setSelectedItems(command.items())
                else:
                    self.setSelectedItems([])

            self._undoStack.redo()
        else:
            self.setSelectMode()

    def isClean(self) -> bool:
        return self._undoStack.isClean()

    def _pushUndoCommand(self, command: QUndoCommand) -> None:
        self._undoStack.push(command)

    # ==================================================================================================================

    def cut(self) -> None:
        pass

    def copy(self) -> None:
        pass

    def paste(self) -> None:
        pass

    def delete(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._removeItemsCommand(self._currentPage, self._selectedItems))
        else:
            self.setSelectMode()

    # ==================================================================================================================

    def moveCurrentItemsDelta(self, delta: QPointF) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = item.position() + delta
                self._pushUndoCommand(self._moveItemsCommand(self._selectedItems, newPositions, finalMove=True,
                                                             place=True))

    def moveCurrentItem(self, position: QPointF) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                newPositions = {}
                for item in self._selectedItems:
                    newPositions[item] = position
                self._pushUndoCommand(self._moveItemsCommand(self._selectedItems, newPositions, finalMove=True,
                                                             place=True))

    def resizeCurrentItem(self, point: OdgItemPoint, position: QPointF) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                self._pushUndoCommand(self._resizeItemCommand(point, position, snapTo45Degrees=False, finalResize=True,
                                                              place=True, disconnect=False))

    def resizeCurrentItem2(self, point1: OdgItemPoint, position1: QPointF,
                           point2: OdgItemPoint, position2: QPointF) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) == 1):
                self._pushUndoCommand(self._resizeItemCommand2(point1, position1, point2, position2,
                                                               snapTo45Degrees=False, finalResize=True,
                                                               place=True, disconnect=False))

    # ==================================================================================================================

    def rotateCurrentItems(self) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._rotateItemsCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't rotate if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.rotateItems(self._placeModeItems,
                                     self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def rotateBackCurrentItems(self) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._rotateBackItemsCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't rotate if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.rotateBackItems(self._placeModeItems,
                                         self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def flipCurrentItemsHorizontal(self) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._flipItemsHorizontalCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't flip if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.flipItemsHorizontal(self._placeModeItems,
                                             self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    def flipCurrentItemsVertical(self) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(self._flipItemsVerticalCommand(
                    self._selectedItems, self.roundPointToGrid(self._selectedItemsCenter)))
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode):
            if (len(self._placeModeItems) > 0):
                # Don't flip if we're placing a single item using a mouse-press-and-release
                if (not self._placeByMousePressAndRelease):
                    self.flipItemsVertical(self._placeModeItems,
                                           self.roundPointToGrid(self.mapToScene(self.mapFromGlobal(QCursor.pos()))))

    # ==================================================================================================================

    def bringCurrentItemsForward(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode and
                len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._currentPage.items().copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemIndex = itemsOrdered.index(item)
                itemsOrdered.remove(item)
                itemsOrdered.insert(itemIndex + 1, item)

            self._pushUndoCommand(self._reorderItemsCommand(self._currentPage, itemsOrdered,
                                                            self._selectedItems.copy()))

    def sendCurrentItemsBackward(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode and
                len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._currentPage.items().copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemIndex = itemsOrdered.index(item)
                itemsOrdered.remove(item)
                itemsOrdered.insert(itemIndex - 1, item)

            self._pushUndoCommand(self._reorderItemsCommand(self._currentPage, itemsOrdered,
                                                            self._selectedItems.copy()))

    def bringCurrentItemsToFront(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode and
                len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._currentPage.items().copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemsOrdered.remove(item)
                itemsOrdered.append(item)

            self._pushUndoCommand(self._reorderItemsCommand(self._currentPage, itemsOrdered,
                                                            self._selectedItems.copy()))

    def sendCurrentItemsToBack(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode and
                len(self._selectedItems) > 0):
            itemsToReorder = self._selectedItems.copy()
            itemsOrdered = self._currentPage.items().copy()

            while (len(itemsToReorder) > 0):
                item = itemsToReorder.pop()
                itemsOrdered.remove(item)
                itemsOrdered.insert(0, item)

            self._pushUndoCommand(self._reorderItemsCommand(self._currentPage, itemsOrdered,
                                                            self._selectedItems.copy()))

    # ==================================================================================================================

    def groupCurrentItems(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode and
                len(self._selectedItems) > 1):
            itemsToRemove = self._selectedItems.copy()

            itemGroup = OdgItem.createItem('group', self.defaultItemStyle())
            if (isinstance(itemGroup, OdgGroupItem)):
                # Put the group position equal to the position of the last item and adjust each item's position
                # accordingly
                items = OdgItem.copyItems(itemsToRemove)
                itemGroup.setPosition(itemsToRemove[-1].position())
                for item in items:
                    item.setPosition(itemGroup.mapFromScene(item.position()))
                itemGroup.setItems(items)

                # Replace the selected items with the new group item
                self.setSelectedItems([])

                groupCommand = OdgDrawingUndoCommand(self, 'Group Items')
                groupCommand.addChild(self._removeItemsCommand(self._currentPage, itemsToRemove))
                groupCommand.addChild(self._addItemsCommand(self._currentPage, [itemGroup], False))
                self._pushUndoCommand(groupCommand)

    def ungroupCurrentItem(self) -> None:
        if (isinstance(self._currentPage, OdgPage) and self._mode == OdgDrawingWidget.Mode.SelectMode and
                len(self._selectedItems) == 1):
            itemGroup = self._selectedItems[0]
            if (isinstance(itemGroup, OdgGroupItem)):
                itemsToAdd = OdgItem.copyItems(itemGroup.items())
                for item in itemsToAdd:
                    # Apply the group's position/transform to each item
                    item.setPosition(itemGroup.mapToScene(item.position()))
                    item.setRotation(item.rotation() + itemGroup.rotation())
                    if (itemGroup.isFlipped()):
                        item.setFlipped(not item.isFlipped())

                # Replace the selected group item with copies of its constituent items
                self.setSelectedItems([])

                ungroupCommand = OdgDrawingUndoCommand(self, 'Group Items')
                ungroupCommand.addChild(self._removeItemsCommand(self._currentPage, [itemGroup]))
                ungroupCommand.addChild(self._addItemsCommand(self._currentPage, itemsToAdd, False))
                self._pushUndoCommand(ungroupCommand)

    # ==================================================================================================================

    def insertNewItemPoint(self) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode and len(self._selectedItems) == 1):
            item = self._selectedItems[0]
            if (item.canInsertPoints()):
                self._pushUndoCommand(self._insertPointCommand(
                    item, self.roundPointToGrid(self._mouseButtonDownScenePosition)))

    def removeCurrentItemPoint(self) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode and len(self._selectedItems) == 1):
            item = self._selectedItems[0]
            if (item.canRemovePoints()):
                self._pushUndoCommand(self._removePointCommand(
                    item, self.roundPointToGrid(self._mouseButtonDownScenePosition)))

    # ==================================================================================================================

    def insertNewPage(self) -> None:
        # Determine a unique name for the new page
        name = ''
        nameIsUnique = False
        while (not nameIsUnique):
            self._newPageCount = self._newPageCount + 1
            name = f'Page {self._newPageCount}'
            nameIsUnique = True
            for page in self._pages:
                if (name == page.name()):
                    nameIsUnique = False
                    break

        # Create the new page and add it to the view
        self._pushUndoCommand(OdgInsertPageCommand(self, OdgPage(name), self.currentPageIndex() + 1))
        self.zoomFit()

    def removeCurrentPage(self) -> None:
        if (isinstance(self._currentPage, OdgPage)):
            self._pushUndoCommand(OdgRemovePageCommand(self, self._currentPage))

    def moveCurrentPage(self, newIndex: int) -> None:
        if (isinstance(self._currentPage, OdgPage)):
            self._pushUndoCommand(OdgMovePageCommand(self, self._currentPage, newIndex))

    def renameCurrentPage(self, name: str) -> None:
        if (isinstance(self._currentPage, OdgPage)):
            self._pushUndoCommand(OdgSetPagePropertyCommand(self, self._currentPage, 'name', name))

    # ==================================================================================================================

    def updateProperty(self, name: str, value: Any) -> None:
        self._pushUndoCommand(OdgSetDrawingPropertyCommand(self, name, value))

    def updateCurrentItemsProperty(self, name: str, value: Any) -> None:
        if (self._mode == OdgDrawingWidget.Mode.SelectMode):
            if (len(self._selectedItems) > 0):
                self._pushUndoCommand(OdgSetItemsPropertyCommand(self, self._selectedItems, name, value))
        elif (self._mode == OdgDrawingWidget.Mode.PlaceMode):
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
        if (isinstance(self._currentPage, OdgPage) and (len(self._placeModeItems) > 0 or
                                                        (len(self._placeModeItems) == 1 and
                                                         self._placeModeItems[0].isValid()))):
            # Place the items within the scene
            self._pushUndoCommand(self._addItemsCommand(self._currentPage, self._placeModeItems, place=True))

            # Create a new set of place items
            newItems = OdgItem.copyItems(self._placeModeItems)
            if (not self._placeByMousePressAndRelease):
                for item in newItems:
                    item.placeCreateEvent(self.contentRect(), self._grid)

            self._placeModeItems = []
            self.setPlaceMode(newItems, self._placeByMousePressAndRelease)

    # ==================================================================================================================

    def _addItemsCommand(self, page: OdgPage, items: list[OdgItem], place: bool) -> 'OdgAddItemsCommand':
        # Assume items is not empty and that each item in items is not already a member of self.items()
        addCommand = OdgAddItemsCommand(self, page, items)
        if (place):
            addCommand.redo()
            self._placeItems(items, addCommand)
            addCommand.undo()
        return addCommand

    def _removeItemsCommand(self, page: OdgPage, items: list[OdgItem]) -> 'OdgRemoveItemsCommand':
        # Assume items is not empty and that each item in items is a member of self.items()
        removeCommand = OdgRemoveItemsCommand(self, page, items)
        removeCommand.redo()
        self._unplaceItems(items, removeCommand)
        removeCommand.undo()
        return removeCommand

    def _reorderItemsCommand(self, page: OdgPage, items: list[OdgItem],
                             selectedItems: list[OdgItem]) -> 'OdgReorderItemsCommand':
        # Assumes that all members of self.items() are present in items with no extras
        return OdgReorderItemsCommand(self, page, items, selectedItems)

    def _moveItemsCommand(self, items: list[OdgItem], positions: dict[OdgItem, QPointF], finalMove: bool,
                          place: bool) -> 'OdgMoveItemsCommand':
        # Assumes items is not empty and that each item in items has a corresponding position in positions
        moveCommand = OdgMoveItemsCommand(self, items, positions, finalMove)
        moveCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, moveCommand)
        if (place):
            self._placeItems(items, moveCommand)
        moveCommand.undo()
        return moveCommand

    def _resizeItemCommand(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool, finalResize: bool,
                           place: bool, disconnect: bool) -> 'OdgResizeItemCommand':
        # Assumes the point is a member of a valid item
        resizeCommand = OdgResizeItemCommand(self, point, position, snapTo45Degrees, finalResize)
        resizeCommand.redo()
        if (disconnect):
            self._disconnectAll(point, resizeCommand)
        self._tryToMaintainConnections([point.item()], True, not point.isFree(), point, resizeCommand)
        if (place):
            self._placeItems([point.item()], resizeCommand)
        resizeCommand.undo()
        return resizeCommand

    def _resizeItemCommand2(self, point1: OdgItemPoint, position1: QPointF,
                            point2: OdgItemPoint, position2: QPointF, snapTo45Degrees: bool, finalResize: bool,
                            place: bool, disconnect: bool) -> 'OdgItemsUndoCommand':
        # Assumes that point1 and point2 are members of the same valid item
        resizeCommand = OdgItemsUndoCommand(self, [point1.item()], 'Resize Item')

        resizeCommand1 = OdgResizeItemCommand(self, point1, position1, snapTo45Degrees, finalResize)
        resizeCommand2 = OdgResizeItemCommand(self, point2, position2, snapTo45Degrees, finalResize)
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

    def _rotateItemsCommand(self, items: list[OdgItem], position: QPointF) -> 'OdgRotateItemsCommand':
        # Assumes items is not empty
        rotateCommand = OdgRotateItemsCommand(self, items, position)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        return rotateCommand

    def _rotateBackItemsCommand(self, items: list[OdgItem], position: QPointF) -> 'OdgRotateBackItemsCommand':
        # Assumes items is not empty
        rotateCommand = OdgRotateBackItemsCommand(self, items, position)
        rotateCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, rotateCommand)
        rotateCommand.undo()
        return rotateCommand

    def _flipItemsHorizontalCommand(self, items: list[OdgItem], position: QPointF) -> 'OdgFlipItemsHorizontalCommand':
        # Assumes items is not empty
        flipCommand = OdgFlipItemsHorizontalCommand(self, items, position)
        flipCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, flipCommand)
        flipCommand.undo()
        return flipCommand

    def _flipItemsVerticalCommand(self, items: list[OdgItem], position: QPointF) -> 'OdgFlipItemsVerticalCommand':
        # Assumes items is not empty
        flipCommand = OdgFlipItemsVerticalCommand(self, items, position)
        flipCommand.redo()
        self._tryToMaintainConnections(items, True, True, None, flipCommand)
        flipCommand.undo()
        return flipCommand

    def _insertPointCommand(self, item: OdgItem, position: QPointF) -> 'OdgItemInsertPointCommand':
        return OdgItemInsertPointCommand(self, item, position)

    def _removePointCommand(self, item: OdgItem, position: QPointF) -> 'OdgItemRemovePointCommand':
        return OdgItemRemovePointCommand(self, item, position)

    def _connectPointsCommand(self, point1: OdgItemPoint,
                              point2: OdgItemPoint) -> 'OdgItemPointConnectCommand':
        # Assumes point1 and point2 are not already connected
        connectCommand = OdgItemPointConnectCommand(point1, point2)

        point1Item = point1.item()
        point2Item = point2.item()
        if (isinstance(point1Item, OdgItem) and isinstance(point2Item, OdgItem)):
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

    def _disconnectPointsCommand(self, point1: OdgItemPoint,
                                 point2: OdgItemPoint) -> 'OdgItemPointDisconnectCommand':
        # Assumes point1 and point2 are connected
        return OdgItemPointDisconnectCommand(point1, point2)

    # ==================================================================================================================

    def _placeItems(self, items: list[OdgItem], command: 'OdgUndoCommand') -> None:
        for widgetItem in self.currentPageItems():
            if (widgetItem not in items and widgetItem not in self._placeModeItems):
                for widgetItemPoint in widgetItem.points():
                    for item in items:
                        for point in item.points():
                            if (self._shouldConnect(point, widgetItemPoint)):
                                command.addChild(self._connectPointsCommand(point, widgetItemPoint))

    def _unplaceItems(self, items: list[OdgItem], command: 'OdgUndoCommand') -> None:
        for item in items:
            for point in item.points():
                for targetPoint in point.connections():
                    if (targetPoint.item() not in items):
                        command.addChild(self._disconnectPointsCommand(point, targetPoint))

    def _tryToMaintainConnections(self, items: list[OdgItem], allowResize: bool, checkControlPoints: bool,
                                  pointToSkip: OdgItemPoint | None, command: 'OdgUndoCommand') -> None:
        for item in items:
            for point in item.points():
                if (point != pointToSkip and (checkControlPoints or not point.isControlPoint())):
                    for targetPoint in point.connections():
                        targetItem = targetPoint.item()
                        if (isinstance(targetItem, OdgItem) and
                                item.mapToScene(point.position()) != targetItem.mapToScene(targetPoint.position())):
                            # Try to maintain the connection by resizing targetPoint if possible
                            if (allowResize and targetPoint.isFree() and not self._shouldDisconnect(point, targetPoint)):   # noqa
                                command.addChild(
                                    self._resizeItemCommand(targetPoint, item.mapToScene(point.position()), False,
                                                            finalResize=False, place=False, disconnect=False))
                            else:
                                command.addChild(self._disconnectPointsCommand(point, targetPoint))

    def _disconnectAll(self, point: OdgItemPoint, command: 'OdgUndoCommand') -> None:
        for targetPoint in point.connections():
            command.addChild(self._disconnectPointsCommand(point, targetPoint))

    # ==================================================================================================================

    def _emitCleanTextChanged(self, clean: bool) -> None:
        self.cleanTextChanged.emit('Modified' if (not clean) else '')

    def _updateSelectionCenter(self) -> None:
        self._selectedItemsCenter = self._itemsCenter(self._selectedItems)

    def _clearModeStateVariables(self, mode: OdgDrawingView.Mode) -> None:
        self._selectMoveItemsInitialPositions.clear()


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgUndoCommand(QUndoCommand):
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

class OdgDrawingUndoCommand(OdgUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, text: str) -> None:
        super().__init__(text)

        self._drawing: OdgDrawingWidget = drawing
        self._viewPage: OdgPage | None = drawing.currentPage()
        self._viewRect: QRectF = drawing.visibleRect()

    def drawing(self) -> OdgDrawingWidget:
        return self._drawing

    def viewPage(self) -> OdgPage | None:
        return self._viewPage

    def viewRect(self) -> QRectF:
        return self._viewRect


# ======================================================================================================================

class OdgItemsUndoCommand(OdgDrawingUndoCommand):
    class Id(IntEnum):
        MoveItemsId = 0
        ResizeItemId = 1
        SetItemsPropertyId = 2

    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], text: str) -> None:
        super().__init__(drawing, text)
        self._items: list[OdgItem] = items

    def items(self) -> list[OdgItem]:
        return self._items

    def mergeChildren(self, command: QUndoCommand) -> None:
        if (isinstance(command, OdgUndoCommand)):
            for commandChild in command.children():
                if (isinstance(commandChild, OdgResizeItemCommand)):
                    self.addChild(OdgResizeItemCommand(commandChild.drawing(),
                                                       commandChild.point(), commandChild.position(),
                                                       commandChild.shouldSnapTo45Degrees(),
                                                       commandChild.isFinalResize()))
                elif (isinstance(commandChild, OdgItemPointConnectCommand)):
                    self.addChild(OdgItemPointConnectCommand(commandChild.point1(), commandChild.point2()))
                elif (isinstance(commandChild, OdgItemPointDisconnectCommand)):
                    self.addChild(OdgItemPointDisconnectCommand(commandChild.point1(), commandChild.point2()))


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgInsertPageCommand(OdgUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage, index: int) -> None:
        super().__init__('Insert Page')

        # Assumes page is not already a member of drawing.pages()
        self._drawing: OdgDrawingWidget = drawing
        self._page: OdgPage = page
        self._index: int = index
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._page

    def redo(self) -> None:
        self._undone = False
        self._drawing.insertPage(self._index, self._page)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.removePage(self._page)
        self._undone = True


# ======================================================================================================================

class OdgRemovePageCommand(OdgUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage) -> None:
        super().__init__('Remove Page')

        # Assumes page is a member of drawing.pages()
        self._drawing: OdgDrawingWidget = drawing
        self._page: OdgPage = page
        self._index: int = self._drawing.pages().index(self._page)
        self._undone: bool = True

    def __del__(self) -> None:
        if (not self._undone):
            del self._page

    def redo(self) -> None:
        self._undone = False
        self._drawing.removePage(self._page)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.insertPage(self._index, self._page)
        self._undone = True


# ======================================================================================================================

class OdgMovePageCommand(OdgUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage, newIndex: int) -> None:
        super().__init__('Move Page')

        # Assumes page is a member of drawing.pages()
        self._drawing: OdgDrawingWidget = drawing
        self._page: OdgPage = page
        self._newIndex: int = newIndex
        self._originalIndex: int = self._drawing.pages().index(self._page)

    def redo(self) -> None:
        self._drawing.movePage(self._page, self._newIndex)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.movePage(self._page, self._originalIndex)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgAddItemsCommand(OdgDrawingUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage, items: list[OdgItem]) -> None:
        super().__init__(drawing, 'Add Items')

        # Assumes each item in items is a not already a member of page.items()
        self._page: OdgPage = page
        self._items: list[OdgItem] = items
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._items[:]

    def redo(self) -> None:
        self._undone = False
        self._drawing.addItems(self._page, self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.removeItems(self._page, self._items)
        self._undone = True


# ======================================================================================================================

class OdgRemoveItemsCommand(OdgDrawingUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage, items: list[OdgItem]) -> None:
        super().__init__(drawing, 'Remove Items')

        # Assumes each item in items is a member of page.items()
        self._page: OdgPage = page
        self._items: list[OdgItem] = items
        self._undone: bool = True

        self._indices: dict[OdgItem, int] = {}
        for item in self._items:
            self._indices[item] = self._page.items().index(item)

    def __del__(self) -> None:
        if (not self._undone):
            del self._items[:]

    def redo(self) -> None:
        self._undone = False
        self._drawing.removeItems(self._page, self._items)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.insertItems(self._page, self._items, self._indices)
        self._undone = True


# ======================================================================================================================

class OdgReorderItemsCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage, items: list[OdgItem],
                 selectedItems: list[OdgItem]) -> None:
        super().__init__(drawing, selectedItems, 'Reorder Items')

        # Assumes each item in items is a member of page.items() and no items have been added or removed
        self._page: OdgPage = page
        self._itemOrder: list[OdgItem] = items
        self._originalItemOrder: list[OdgItem] = self._page.items()

    def redo(self) -> None:
        # pylint: disable-next=W0212
        self._drawing._reorderItems(self._page, self._itemOrder)
        super().redo()

    def undo(self) -> None:
        super().undo()
        # pylint: disable-next=W0212
        self._drawing._reorderItems(self._page, self._originalItemOrder)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgMoveItemsCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], positions: dict[OdgItem, QPointF],
                 finalMove: bool) -> None:
        super().__init__(drawing, items, 'Move Items')

        # Assumes each item has a corresponding position in positions
        self._positions: dict[OdgItem, QPointF] = positions
        self._finalMove: bool = finalMove

        self._originalPositions: dict[OdgItem, QPointF] = {}
        for item in self._items:
            self._originalPositions[item] = item.position()

    def positions(self) -> dict[OdgItem, QPointF]:
        return self._positions

    def isFinalMove(self) -> bool:
        return self._finalMove

    def id(self) -> int:
        return OdgItemsUndoCommand.Id.MoveItemsId

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, OdgMoveItemsCommand) and self._drawing == command.drawing() and
                self._items == command.items() and not self._finalMove):
            self._positions = command.positions()
            self._finalMove = command.isFinalMove()
            self.mergeChildren(command)
            return True
        return False

    def redo(self) -> None:
        self._drawing.moveItems(self._items, self._positions)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.moveItems(self._items, self._originalPositions)


# ======================================================================================================================

class OdgResizeItemCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool,
                 finalResize: bool) -> None:
        super().__init__(drawing, [point.item()], 'Resize Item')

        # Assumes the point is a member of a valid item
        self._point: OdgItemPoint = point
        self._position: QPointF = position
        self._snapTo45Degrees: bool = snapTo45Degrees
        self._finalResize: bool = finalResize
        self._originalPosition: QPointF = QPointF()

        item = point.item()
        if (isinstance(item, OdgItem)):
            self._originalPosition = item.mapToScene(point.position())

    def point(self) -> OdgItemPoint:
        return self._point

    def position(self) -> QPointF:
        return self._position

    def shouldSnapTo45Degrees(self) -> bool:
        return self._snapTo45Degrees

    def isFinalResize(self) -> bool:
        return self._finalResize

    def id(self) -> int:
        return OdgItemsUndoCommand.Id.ResizeItemId

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, OdgResizeItemCommand) and self._drawing == command.drawing() and
                self._point == command.point() and not self._finalResize):
            self._position = command.position()
            self._snapTo45Degrees = command.shouldSnapTo45Degrees()
            self._finalResize = command.isFinalResize()
            self.mergeChildren(command)
            return True
        return False

    def redo(self) -> None:
        self._drawing.resizeItem(self._point, self._position, self._snapTo45Degrees)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.resizeItem(self._point, self._originalPosition, False)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgRotateItemsCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], position: QPointF) -> None:
        super().__init__(drawing, items, 'Rotate Items')
        self._position: QPointF = position

    def redo(self) -> None:
        self._drawing.rotateItems(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.rotateBackItems(self._items, self._position)


# ======================================================================================================================

class OdgRotateBackItemsCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], position: QPointF) -> None:
        super().__init__(drawing, items, 'Rotate Back Items')
        self._position: QPointF = position

    def redo(self) -> None:
        self._drawing.rotateBackItems(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.rotateItems(self._items, self._position)


# ======================================================================================================================

class OdgFlipItemsHorizontalCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], position: QPointF) -> None:
        super().__init__(drawing, items, 'Flip Items Horizontal')
        self._position: QPointF = position

    def redo(self) -> None:
        self._drawing.flipItemsHorizontal(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.flipItemsHorizontal(self._items, self._position)


# ======================================================================================================================

class OdgFlipItemsVerticalCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], position: QPointF) -> None:
        super().__init__(drawing, items, 'Flip Items Vertical')
        self._position: QPointF = position

    def redo(self) -> None:
        self._drawing.flipItemsVertical(self._items, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.flipItemsVertical(self._items, self._position)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgItemInsertPointCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, item: OdgItem, position: QPointF) -> None:
        super().__init__(drawing, [item], 'Insert Point')

        self._item: OdgItem = item
        self._position: QPointF = position

    def redo(self) -> None:
        self._drawing.insertItemPoint(self._item, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.removeItemPoint(self._item, self._position)


# ======================================================================================================================

class OdgItemRemovePointCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, item: OdgItem, position: QPointF) -> None:
        super().__init__(drawing, [item], 'Remove Point')

        self._item: OdgItem = item
        self._position: QPointF = position
        self._undone: bool = True

    def redo(self) -> None:
        self._drawing.removeItemPoint(self._item, self._position)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.insertItemPoint(self._item, self._position)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgItemPointConnectCommand(OdgUndoCommand):
    def __init__(self, point1: OdgItemPoint, point2: OdgItemPoint) -> None:
        super().__init__('Connect Points')

        # Assumes point1 and point2 are not already connected
        self._point1: OdgItemPoint = point1
        self._point2: OdgItemPoint = point2

    def point1(self) -> OdgItemPoint:
        return self._point1

    def point2(self) -> OdgItemPoint:
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

class OdgItemPointDisconnectCommand(OdgUndoCommand):
    def __init__(self, point1: OdgItemPoint, point2: OdgItemPoint) -> None:
        super().__init__('Disconnect Points')

        # Assumes point1 and point2 are connected
        self._point1: OdgItemPoint = point1
        self._point2: OdgItemPoint = point2

    def point1(self) -> OdgItemPoint:
        return self._point1

    def point2(self) -> OdgItemPoint:
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

class OdgSetItemsPropertyCommand(OdgItemsUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, items: list[OdgItem], name: str, value: Any) -> None:
        super().__init__(drawing, items, 'Set Items Property')

        self._name: str = name
        self._value: Any = value

        self._originalValues: dict[OdgItem, Any] = {}
        for item in self._items:
            self._originalValues[item] = item.property(name)

    def name(self) -> str:
        return self._name

    def value(self) -> Any:
        return self._value

    def id(self) -> int:
        return OdgItemsUndoCommand.Id.SetItemsPropertyId

    def mergeWith(self, command: QUndoCommand) -> bool:
        if (isinstance(command, OdgSetItemsPropertyCommand) and self.drawing() == command.drawing()):
            if (len(self.items()) == 1 and len(command.items()) == 1 and self.items()[0] == command.items()[0] and
                    self.name() == 'caption' and command.name() == 'caption'):
                self._value = command.value()
                self.mergeChildren(command)
                return True
        return False

    def redo(self) -> None:
        self._drawing.setItemsProperty(self._items, self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.setItemsPropertyDict(self._items, self._name, self._originalValues)


# ======================================================================================================================

class OdgSetPagePropertyCommand(OdgDrawingUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, page: OdgPage, name: str, value: Any) -> None:
        super().__init__(drawing, 'Set Page Property')

        self._page: OdgPage = page
        self._name: str = name
        self._value: Any = value

        self._originalValue: Any = self._page.property(self._name)

    def redo(self) -> None:
        self._drawing.setPageProperty(self._page, self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.setPageProperty(self._page, self._name, self._originalValue)


# ======================================================================================================================

class OdgSetDrawingPropertyCommand(OdgDrawingUndoCommand):
    def __init__(self, drawing: OdgDrawingWidget, name: str, value: Any) -> None:
        super().__init__(drawing, 'Set Property')

        self._name: str = name
        self._value: Any = value

        self._originalValue: Any = self._drawing.property(self._name)

        if (self._name == 'sceneRect'):
            self._viewRect = QRectF()

    def redo(self) -> None:
        self._drawing.setProperty(self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._drawing.setProperty(self._name, self._originalValue)
