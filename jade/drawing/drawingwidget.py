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
from xml.etree import ElementTree
from PySide6.QtCore import QPoint, QPointF, QRectF, QSizeF, Signal
from PySide6.QtGui import QBrush, QUndoCommand, QUndoStack
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from .drawingitem import DrawingItem
from .drawingitempoint import DrawingItemPoint
from .drawingpagewidget import DrawingItemsUndoCommand, DrawingPageUndoCommand, DrawingPageWidget
from .drawingxmlinterface import DrawingXmlInterface


class DrawingWidget(QWidget, DrawingXmlInterface):
    propertyChanged = Signal(str, object)

    pageInserted = Signal(DrawingPageWidget, int)
    pageRemoved = Signal(DrawingPageWidget, int)
    currentPageChanged = Signal(DrawingPageWidget)
    currentPageIndexChanged = Signal(int)
    currentPagePropertyChanged = Signal(str, object)

    scaleChanged = Signal(float)
    modeChanged = Signal(int)
    modeStringChanged = Signal(str)
    mouseInfoChanged = Signal(str)
    currentItemsChanged = Signal(list)
    currentItemsPropertyChanged = Signal(list)

    cleanChanged = Signal(bool)
    modifiedStringChanged = Signal(str)

    contextMenuTriggered = Signal(QPoint)

    def __init__(self) -> None:
        super().__init__()

        self._defaultPageSize: QSizeF = QSizeF()
        self._defaultPageMargin: float = 0.0
        self._defaultBackgroundBrush: QBrush = QBrush()

        self._grid: float = 0.0
        self._gridVisible: bool = False
        self._gridBrush: QBrush = QBrush()
        self._gridSpacingMajor: int = 0
        self._gridSpacingMinor: int = 0

        self._pages: list[DrawingPageWidget] = []
        self._currentPage: DrawingPageWidget | None = None
        self._newPageCount: int = 0

        self._stackedWidget: QStackedWidget = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self._stackedWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._undoStack: QUndoStack = QUndoStack()
        self._undoStack.setUndoLimit(64)
        self._undoStack.cleanChanged.connect(self.cleanChanged)                 # type: ignore
        self._undoStack.cleanChanged.connect(self._emitModifiedStringChanged)   # type: ignore

    def __del__(self) -> None:
        self.clearPages()

    # ==================================================================================================================

    def setDefaultPageSize(self, size: QSizeF) -> None:
        if (size.width() > 0 and size.height() > 0):
            self._defaultPageSize = QSizeF(size)

    def setDefaultPageMargin(self, margin: float) -> None:
        if (margin >= 0):
            self._defaultPageMargin = margin

    def setDefaultBackgroundBrush(self, brush: QBrush) -> None:
        self._defaultBackgroundBrush = QBrush(brush)

    def defaultPageSize(self) -> QSizeF:
        return self._defaultPageSize

    def defaultPageMargin(self) -> float:
        return self._defaultPageMargin

    def defaultBackgroundBrush(self) -> QBrush:
        return self._defaultBackgroundBrush

    # ==================================================================================================================

    def setGrid(self, grid: float) -> None:
        if (self._grid != grid and grid >= 0):
            self._grid = grid

            self.blockSignals(True)
            for page in self._pages:
                page.setGrid(self._grid)
            self.blockSignals(False)

            self.propertyChanged.emit('grid', self._grid)

    def setGridVisible(self, visible: bool) -> None:
        if (self._gridVisible != visible):
            self._gridVisible = visible

            self.blockSignals(True)
            for page in self._pages:
                page.setGridVisible(self._gridVisible)
            self.blockSignals(False)

            self.propertyChanged.emit('gridVisible', self._gridVisible)

    def setGridBrush(self, brush: QBrush) -> None:
        if (self._gridBrush != brush):
            self._gridBrush = QBrush(brush)

            self.blockSignals(True)
            for page in self._pages:
                page.setGridBrush(self._gridBrush)
            self.blockSignals(False)

            self.propertyChanged.emit('gridBrush', self._gridBrush)

    def setGridSpacingMajor(self, spacing: int) -> None:
        if (self._gridSpacingMajor != spacing and spacing >= 0):
            self._gridSpacingMajor = spacing

            self.blockSignals(True)
            for page in self._pages:
                page.setGridSpacingMajor(self._gridSpacingMajor)
            self.blockSignals(False)

            self.propertyChanged.emit('gridSpacingMajor', self._gridSpacingMajor)

    def setGridSpacingMinor(self, spacing: int) -> None:
        if (self._gridSpacingMinor != spacing and spacing >= 0):
            self._gridSpacingMinor = spacing

            self.blockSignals(True)
            for page in self._pages:
                page.setGridSpacingMinor(self._gridSpacingMinor)
            self.blockSignals(False)

            self.propertyChanged.emit('gridSpacingMinor', self._gridSpacingMinor)

    def grid(self) -> float:
        return self._grid

    def isGridVisible(self) -> bool:
        return self._gridVisible

    def gridBrush(self) -> QBrush:
        return self._gridBrush

    def gridSpacingMajor(self) -> int:
        return self._gridSpacingMajor

    def gridSpacingMinor(self) -> int:
        return self._gridSpacingMinor

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> bool:
        match (name):
            case 'grid':
                if (isinstance(value, float)):
                    self.setGrid(value)
            case 'gridVisible':
                if (isinstance(value, bool)):
                    self.setGridVisible(value)
            case 'gridBrush':
                if (isinstance(value, QBrush)):
                    self.setGridBrush(value)
            case 'gridSpacingMajor':
                if (isinstance(value, int)):
                    self.setGridSpacingMajor(value)
            case 'gridSpacingMinor':
                if (isinstance(value, int)):
                    self.setGridSpacingMinor(value)
        return True

    def property(self, name: str) -> typing.Any:
        match (name):
            case 'grid':
                return self.grid()
            case 'gridVisible':
                return self.isGridVisible()
            case 'gridBrush':
                return self.gridBrush()
            case 'gridSpacingMajor':
                return self.gridSpacingMajor()
            case 'gridSpacingMinor':
                return self.gridSpacingMinor()
        return None

    # ==================================================================================================================

    def addPage(self, page: DrawingPageWidget) -> None:
        self.insertPage(len(self._pages), page)

    def insertPage(self, index: int, page: DrawingPageWidget) -> None:
        if (page not in self._pages):
            self._pages.insert(index, page)
            self._stackedWidget.insertWidget(index, page)

            self.pageInserted.emit(page, index)

            page.undoCommandCreated.connect(self._pushUndoCommand)
            page.scaleChanged.connect(self._emitScaleChanged)
            page.modeChanged.connect(self._emitModeChanged)
            page.modeStringChanged.connect(self._emitModeStringChanged)
            page.mouseInfoChanged.connect(self._emitMouseInfoChanged)
            page.currentItemsChanged.connect(self._emitCurrentItemsChanged)
            page.currentItemsPropertyChanged.connect(self._emitCurrentItemsPropertyChanged)
            page.propertyChanged.connect(self._emitCurrentPagePropertyChanged)
            page.contextMenuTriggered.connect(self._emitContextMenuTriggered)

            self.setCurrentPage(page)

    def removePage(self, page: DrawingPageWidget) -> None:
        if (page in self._pages):
            index = self._pages.index(page)

            newCurrentPageIndex = -1
            if (index > 0):
                newCurrentPageIndex = index - 1
            elif (index < len(self._pages) - 1):
                newCurrentPageIndex = index + 1

            self._pages.remove(page)
            self._stackedWidget.removeWidget(page)
            page.setParent(None)    # type: ignore

            page.undoCommandCreated.disconnect(self._pushUndoCommand)
            page.scaleChanged.disconnect(self._emitScaleChanged)
            page.modeChanged.disconnect(self._emitModeChanged)
            page.modeStringChanged.disconnect(self._emitModeStringChanged)
            page.mouseInfoChanged.disconnect(self._emitMouseInfoChanged)
            page.currentItemsChanged.disconnect(self._emitCurrentItemsChanged)
            page.currentItemsPropertyChanged.disconnect(self._emitCurrentItemsPropertyChanged)
            page.propertyChanged.disconnect(self._emitCurrentPagePropertyChanged)
            page.contextMenuTriggered.disconnect(self._emitContextMenuTriggered)

            self.pageRemoved.emit(page, index)

            self.setCurrentPageIndex(newCurrentPageIndex)

    def movePage(self, page: DrawingPageWidget, newIndex: int) -> None:
        if (page in self._pages):
            index = self._pages.index(page)

            self._pages.remove(page)
            self._stackedWidget.removeWidget(page)
            page.setParent(None)    # type: ignore

            self.pageRemoved.emit(page, index)

            self._pages.insert(newIndex, page)
            self._stackedWidget.insertWidget(newIndex, page)

            self.pageInserted.emit(page, newIndex)

            self.setCurrentPage(page)

    def clearPages(self) -> None:
        while (len(self._pages) > 0):
            page = self._pages[-1]
            self.removePage(page)
            del page

    def pages(self) -> list[DrawingPageWidget]:
        return self._pages

    # ==================================================================================================================

    def setCurrentPage(self, page: DrawingPageWidget | None) -> None:
        # Only allow us to use a page that is part of the view as the current page, but also allow None
        if (page is None or page in self._pages):
            self.setSelectMode()
            self.setSelectedItems([])

            self._currentPage = page
            if (self._currentPage is not None):
                self._stackedWidget.setCurrentWidget(self._currentPage)
            else:
                self._stackedWidget.setCurrentIndex(-1)

            self.currentPageChanged.emit(self._currentPage)
            self.currentPageIndexChanged.emit(self.currentPageIndex())

            self.scaleChanged.emit(self.scale())
            self.mouseInfoChanged.emit('')

    def setCurrentPageIndex(self, index: int) -> None:
        if (0 <= index < len(self._pages)):
            self.setCurrentPage(self._pages[index])
        else:
            self.setCurrentPage(None)

    def currentPage(self) -> DrawingPageWidget | None:
        return self._currentPage

    def currentPageIndex(self) -> int:
        if (self._currentPage is not None and self._currentPage in self._pages):
            return self._pages.index(self._currentPage)
        return -1

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        element.set('grid', self._toSizeStr(self.grid()))
        element.set('gridVisible', 'true' if (self.isGridVisible()) else 'false')
        element.set('gridColor', self._toColorStr(self.gridBrush().color()))
        element.set('gridSpacingMajor', f'{self.gridSpacingMajor()}')
        element.set('gridSpacingMinor', f'{self.gridSpacingMinor()}')

        for page in self._pages:
            pageElement = ElementTree.SubElement(element, 'page')
            page.writeToXml(pageElement)

    def readFromXml(self, element: ElementTree.Element) -> None:
        self.clearPages()

        self.setGrid(self._fromSizeStr(element.get('grid', '0')))
        self.setGridVisible(element.get('gridVisible', 'false').lower() == 'true')
        self.setGridBrush(QBrush(self._fromColorStr(element.get('gridColor', '0'))))
        self.setGridSpacingMajor(int(element.get('gridSpacingMajor', '0')))
        self.setGridSpacingMinor(int(element.get('gridSpacingMinor', '0')))

        for pageElement in element.findall('page'):
            newPage = DrawingPageWidget()

            newPage.setGrid(self._grid)
            newPage.setGridVisible(self._gridVisible)
            newPage.setGridBrush(self._gridBrush)
            newPage.setGridSpacingMajor(self._gridSpacingMajor)
            newPage.setGridSpacingMinor(self._gridSpacingMinor)

            newPage.readFromXml(pageElement)

            self.addPage(newPage)
            self.zoomFit()

    # ==================================================================================================================

    def undo(self) -> None:
        if (self.mode() == DrawingPageWidget.Mode.SelectMode):
            # Get the command that will be undone by the call to self._undoStack.undo()
            command = self._undoStack.command(self._undoStack.index() - 1)

            if (isinstance(command, DrawingPageUndoCommand)):
                self.setCurrentPage(command.page())
                if (command.viewRect().width() > 0 and command.viewRect().height() > 0):
                    self.zoomToRect(command.viewRect())
                if (isinstance(command, DrawingItemsUndoCommand)):
                    self.setSelectedItems(command.items())
                else:
                    self.setSelectedItems([])
            else:
                self.setSelectedItems([])

            self._undoStack.undo()
        else:
            self.setSelectMode()

    def redo(self) -> None:
        if (self.mode() == DrawingPageWidget.Mode.SelectMode):
            # Get the command that will be redone by the call to self._undoStack.redo()
            command = self._undoStack.command(self._undoStack.index())

            if (isinstance(command, DrawingPageUndoCommand)):
                self.setCurrentPage(command.page())
                if (command.viewRect().width() > 0 and command.viewRect().height() > 0):
                    self.zoomToRect(command.viewRect())
                if (isinstance(command, DrawingItemsUndoCommand)):
                    self.setSelectedItems(command.items())
                else:
                    self.setSelectedItems([])
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
        if (self._currentPage is not None):
            self._currentPage.cut()

    def copy(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.copy()

    def paste(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.paste()

    def delete(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.delete()

    # ==================================================================================================================

    def setSelectedItems(self, items: list[DrawingItem]):
        if (self._currentPage is not None):
            self._currentPage.setSelectedItems(items)

    def selectAll(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.selectAll()

    def selectNone(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.selectNone()

    def selectedItems(self) -> list[DrawingItem]:
        if (self._currentPage is not None):
            return self._currentPage.selectedItems()
        return []

    # ==================================================================================================================

    def moveCurrentItemsDelta(self, delta: QPointF) -> None:
        if (self._currentPage is not None):
            self._currentPage.moveCurrentItemsDelta(delta)

    def moveCurrentItem(self, position: QPointF) -> None:
        if (self._currentPage is not None):
            self._currentPage.moveCurrentItem(position)

    def resizeCurrentItem(self, point: DrawingItemPoint, position: QPointF) -> None:
        if (self._currentPage is not None):
            self._currentPage.resizeCurrentItem(point, position)

    # ==================================================================================================================

    def rotateCurrentItems(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.rotateCurrentItems()

    def rotateBackCurrentItems(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.rotateBackCurrentItems()

    def flipCurrentItemsHorizontal(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.flipCurrentItemsHorizontal()

    def flipCurrentItemsVertical(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.flipCurrentItemsVertical()

    # ==================================================================================================================

    def bringCurrentItemsForward(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.bringCurrentItemsForward()

    def sendCurrentItemsBackward(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.sendCurrentItemsBackward()

    def bringCurrentItemsToFront(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.bringCurrentItemsToFront()

    def sendCurrentItemsToBack(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.sendCurrentItemsToBack()

    # ==================================================================================================================

    def groupCurrentItems(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.groupCurrentItems()

    def ungroupCurrentItem(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.ungroupCurrentItem()

    # ==================================================================================================================

    def insertNewItemPoint(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.insertNewItemPoint()

    def removeCurrentItemPoint(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.removeCurrentItemPoint()

    # ==================================================================================================================

    def insertNewPage(self) -> None:
        # Determine a unique name for the new page
        name = ''
        nameIsUnique = False
        while (not nameIsUnique):
            self._newPageCount = self._newPageCount + 1
            name = f'Page{self._newPageCount}'
            nameIsUnique = True
            for page in self._pages:
                if (name == page.name()):
                    nameIsUnique = False
                    break

        # Create the new page and add it to the view
        newPage = DrawingPageWidget()
        newPage.setName(name)
        newPage.setPageSize(self._defaultPageSize)
        newPage.setPageMargin(self._defaultPageMargin)
        newPage.setBackgroundBrush(self._defaultBackgroundBrush)
        newPage.setGrid(self._grid)
        newPage.setGridVisible(self._gridVisible)
        newPage.setGridBrush(self._gridBrush)
        newPage.setGridSpacingMajor(self._gridSpacingMajor)
        newPage.setGridSpacingMinor(self._gridSpacingMinor)
        self._pushUndoCommand(DrawingInsertPageCommand(self, newPage, self.currentPageIndex() + 1))
        self.zoomFit()

    def removeCurrentPage(self) -> None:
        if (self._currentPage is not None):
            self._pushUndoCommand(DrawingRemovePageCommand(self, self._currentPage))

    def moveCurrentPage(self, newIndex: int) -> None:
        if (self._currentPage is not None):
            self._pushUndoCommand(DrawingMovePageCommand(self, self._currentPage, newIndex))

    def renameCurrentPage(self, name: str) -> None:
        if (self._currentPage is not None):
            self._currentPage.updateProperty('name', name)

    # ==================================================================================================================

    def setScale(self, scale: float) -> None:
        if (self._currentPage is not None):
            self._currentPage.setScale(scale)

    def zoomToRect(self, rect: QRectF = QRectF()) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomToRect(rect)

    def zoomIn(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomIn()

    def zoomOut(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomOut()

    def zoomFit(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.zoomFit()

    def scale(self) -> float:
        if (self._currentPage is not None):
            return self._currentPage.scale()
        return 1.0

    # ==================================================================================================================

    def setSelectMode(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.setSelectMode()

    def setScrollMode(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.setScrollMode()

    def setZoomMode(self) -> None:
        if (self._currentPage is not None):
            self._currentPage.setZoomMode()

    def setPlaceMode(self, items: list[DrawingItem], placeByMousePressAndRelease: bool) -> None:
        if (self._currentPage is not None):
            self._currentPage.setPlaceMode(items, placeByMousePressAndRelease)

    def mode(self) -> DrawingPageWidget.Mode:
        if (self._currentPage is not None):
            return self._currentPage.mode()
        return DrawingPageWidget.Mode.SelectMode

    # ==================================================================================================================

    def updateProperty(self, name: str, value: typing.Any) -> None:
        self._pushUndoCommand(DrawingSetPropertyCommand(self, name, value))

    def updateCurrentPageProperty(self, name: str, value: typing.Any) -> None:
        if (self._currentPage is not None):
            self._currentPage.updateProperty(name, value)

    def updateCurrentItemsProperty(self, name: str, value: typing.Any) -> None:
        if (self._currentPage is not None):
            self._currentPage.updateCurrentItemsProperty(name, value)

    # ==================================================================================================================

    def _emitScaleChanged(self, scale: float) -> None:
        self.scaleChanged.emit(scale)

    def _emitModeChanged(self, mode: DrawingPageWidget.Mode) -> None:
        self.modeChanged.emit(mode)

    def _emitModeStringChanged(self, modeStr: str) -> None:
        self.modeStringChanged.emit(modeStr)

    def _emitMouseInfoChanged(self, mouseInfo: str) -> None:
        self.mouseInfoChanged.emit(mouseInfo)

    def _emitCurrentItemsChanged(self, items: list[DrawingItem]) -> None:
        self.currentItemsChanged.emit(items)

    def _emitCurrentItemsPropertyChanged(self, items: list[DrawingItem]) -> None:
        self.currentItemsPropertyChanged.emit(items)

    def _emitCurrentPagePropertyChanged(self, name: str, value: typing.Any) -> None:
        self.currentPagePropertyChanged.emit(name, value)

    def _emitModifiedStringChanged(self, clean: bool) -> None:
        self.modifiedStringChanged.emit('Modified' if (not clean) else '')

    def _emitContextMenuTriggered(self, position: QPoint) -> None:
        self.contextMenuTriggered.emit(position)


# ======================================================================================================================

class DrawingInsertPageCommand(QUndoCommand):
    def __init__(self, widget: DrawingWidget, page: DrawingPageWidget, index: int) -> None:
        super().__init__('Insert Page')

        # Assumes page is not already a member of widget.pages()
        self._widget: DrawingWidget = widget
        self._page: DrawingPageWidget = page
        self._index: int = index
        self._undone: bool = True

    def __del__(self) -> None:
        if (self._undone):
            del self._page

    def redo(self) -> None:
        self._undone = False
        self._widget.insertPage(self._index, self._page)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.removePage(self._page)
        self._undone = True


# ======================================================================================================================

class DrawingRemovePageCommand(QUndoCommand):
    def __init__(self, widget: DrawingWidget, page: DrawingPageWidget) -> None:
        super().__init__('Remove Page')

        # Assumes page is a member of widget.pages()
        self._widget: DrawingWidget = widget
        self._page: DrawingPageWidget = page
        self._index: int = self._widget.pages().index(self._page)
        self._undone: bool = True

    def __del__(self) -> None:
        if (not self._undone):
            del self._page

    def redo(self) -> None:
        self._undone = False
        self._widget.removePage(self._page)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.insertPage(self._index, self._page)
        self._undone = True


# ======================================================================================================================

class DrawingMovePageCommand(QUndoCommand):
    def __init__(self, widget: DrawingWidget, page: DrawingPageWidget, newIndex: int) -> None:
        super().__init__('Remove Page')

        # Assumes page is a member of widget.pages()
        self._widget: DrawingWidget = widget
        self._page: DrawingPageWidget = page
        self._newIndex: int = newIndex
        self._originalIndex: int = self._widget.pages().index(self._page)

    def redo(self) -> None:
        self._widget.movePage(self._page, self._newIndex)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.movePage(self._page, self._originalIndex)


# ======================================================================================================================

class DrawingSetPropertyCommand(QUndoCommand):
    def __init__(self, widget: DrawingWidget, name: str, value: typing.Any) -> None:
        super().__init__('Set Property')

        self._widget: DrawingWidget = widget
        self._name: str = name
        self._value: typing.Any = value

        self._originalValue: typing.Any = self._widget.property(self._name)

    def redo(self) -> None:
        self._widget.setProperty(self._name, self._value)
        super().redo()

    def undo(self) -> None:
        super().undo()
        self._widget.setProperty(self._name, self._originalValue)
