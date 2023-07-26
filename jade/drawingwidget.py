# drawingwidget.py
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

from typing import Callable
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence, QMouseEvent
from PySide6.QtWidgets import QMenu
from .odg.odgdrawingwidget import OdgDrawingWidget
from .odg.odggroupitem import OdgGroupItem
from .odg.odgitem import OdgItem
from .odg.odgpage import OdgPage
from .items.odglineitem import OdgLineItem
from .items.odgrectitem import OdgRectItem


class DrawingWidget(OdgDrawingWidget):
    def __init__(self) -> None:
        super().__init__()

        OdgItem.registerFactoryItem(OdgLineItem('Line'))
        OdgItem.registerFactoryItem(OdgRectItem('Rect'))
        OdgItem.registerFactoryItem(OdgGroupItem('Group'))

        self._createActions()
        self._createContextMenus()

        self.currentItemsChanged.connect(self._updateActionsFromSelection)
        self.currentItemsPropertyChanged.connect(self._updateActionsFromSelection)

    def __del__(self) -> None:
        OdgItem.clearFactoryItems()
        super().__del__()

    # ==================================================================================================================

    def _createActions(self) -> None:
        # Normal actions
        self.undoAction: QAction = self._addNormalAction('Undo', self.undo, 'icons:edit-undo.png', 'Ctrl+Z')
        self.redoAction: QAction = self._addNormalAction('Redo', self.redo, 'icons:edit-redo.png', 'Ctrl+Shift+Z')

        self.cutAction: QAction = self._addNormalAction('Cut', self.cut, 'icons:edit-cut.png', 'Ctrl+X')
        self.copyAction: QAction = self._addNormalAction('Copy', self.copy, 'icons:edit-copy.png', 'Ctrl+C')
        self.pasteAction: QAction = self._addNormalAction('Paste', self.paste, 'icons:edit-paste.png', 'Ctrl+V')
        self.deleteAction: QAction = self._addNormalAction('Delete', self.delete, 'icons:edit-delete.png', 'Delete')

        self.selectAllAction: QAction = self._addNormalAction('Select All', self.selectAll,
                                                              'icons:edit-select-all.png', 'Ctrl+A')
        self.selectNoneAction: QAction = self._addNormalAction('Select None', self.selectNone, '', 'Ctrl+Shift+A')

        self.rotateAction: QAction = self._addNormalAction('Rotate', self.rotateCurrentItems,
                                                           'icons:object-rotate-right.png', 'R')
        self.rotateBackAction: QAction = self._addNormalAction('Rotate Back', self.rotateBackCurrentItems,
                                                               'icons:object-rotate-left.png', 'Shift+R')
        self.flipHorizontalAction: QAction = self._addNormalAction('Flip Horizontal', self.flipCurrentItemsHorizontal,
                                                                   'icons:object-flip-horizontal.png', 'F')
        self.flipVerticalAction: QAction = self._addNormalAction('Flip Vertical', self.flipCurrentItemsVertical,
                                                                 'icons:object-flip-vertical.png', 'Shift+F')

        self.bringForwardAction: QAction = self._addNormalAction('Bring Forward', self.bringCurrentItemsForward,
                                                                 'icons:object-bring-forward.png')
        self.sendBackwardAction: QAction = self._addNormalAction('Send Backward', self.sendCurrentItemsBackward,
                                                                 'icons:object-send-backward.png')
        self.bringToFrontAction: QAction = self._addNormalAction('Bring to Front', self.bringCurrentItemsToFront,
                                                                 'icons:object-bring-to-front.png')
        self.sendToBackAction: QAction = self._addNormalAction('Send to Back', self.sendCurrentItemsToBack,
                                                               'icons:object-send-to-back.png')

        self.groupAction: QAction = self._addNormalAction('Group', self.groupCurrentItems, 'icons:merge.png', 'Ctrl+G')
        self.ungroupAction: QAction = self._addNormalAction('Ungroup', self.ungroupCurrentItem, 'icons:split.png',
                                                            'Ctrl+Shift+G')

        self.insertPointAction: QAction = self._addNormalAction('Insert Point', self.insertNewItemPoint,
                                                                'icons:format-add-node.png')
        self.removePointAction: QAction = self._addNormalAction('Remove Point', self.removeCurrentItemPoint,
                                                                'icons:format-remove-node.png')

        self.insertPageAction: QAction = self._addNormalAction('Insert Page', self.insertNewPage,
                                                               'icons:archive-insert.png')
        self.removePageAction: QAction = self._addNormalAction('Remove Page', self.removeCurrentPage,
                                                               'icons:archive-remove.png')

        self.zoomInAction: QAction = self._addNormalAction('Zoom In', self.zoomIn, 'icons:zoom-in.png', '.')
        self.zoomOutAction: QAction = self._addNormalAction('Zoom Out', self.zoomOut, 'icons:zoom-out.png', ',')
        self.zoomFitAction: QAction = self._addNormalAction('Zoom Fit', self.zoomFit, 'icons:zoom-fit-best.png', '/')

        # Mode actions
        self._modeActionGroup: QActionGroup = QActionGroup(self)
        self._modeActionGroup.triggered.connect(self._setModeFromAction)    # type: ignore
        self.modeChanged.connect(self._updateActionsFromMode)

        self.selectModeAction: QAction = self._addModeAction('Select Mode', '', 'icons:edit-select.png', 'Escape')
        self.scrollModeAction: QAction = self._addModeAction('Scroll Mode', '', 'icons:transform-move.png')
        self.zoomModeAction: QAction = self._addModeAction('Zoom Mode', '', 'icons:page-zoom.png')

        self.placeLineAction: QAction = self._addModeAction('Draw Line', 'line', 'icons:draw-line.png')
        self.placeCurveAction: QAction = self._addModeAction('Draw Curve', 'curve', 'icons:draw-curve.png')
        self.placePolylineAction: QAction = self._addModeAction('Draw Polyline', 'polyline', 'icons:draw-polyline.png')
        self.placeRectAction: QAction = self._addModeAction('Draw Rectangle', 'rect', 'icons:draw-rectangle.png')
        self.placeEllipseAction: QAction = self._addModeAction('Draw Ellipse', 'ellipse', 'icons:draw-ellipse.png')
        self.placePolygonAction: QAction = self._addModeAction('Draw Polygon', 'polygon', 'icons:draw-polygon.png')
        self.placeTextAction: QAction = self._addModeAction('Draw Text', 'text', 'icons:draw-text.png')
        self.placeTextRectAction: QAction = self._addModeAction('Draw Text Rect', 'textRect', 'icons:text-rect.png')
        self.placeTextEllipseAction: QAction = self._addModeAction('Draw Text Ellipse', 'textEllipse',
                                                                   'icons:text-ellipse.png')

        self.selectModeAction.setChecked(True)

    def _addNormalAction(self, text: str, slot: Callable, iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)      # type: ignore
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        self.addAction(action)
        return action

    def _addModeAction(self, text: str, typeKey: str = '', iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self._modeActionGroup)
        if (typeKey != ''):
            action.setProperty('type', typeKey)
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        action.setCheckable(True)
        action.setActionGroup(self._modeActionGroup)
        return action

    # ==================================================================================================================

    def _createContextMenus(self) -> None:
        self._noItemContextMenu: QMenu = QMenu()
        self._noItemContextMenu.addAction(self.undoAction)
        self._noItemContextMenu.addAction(self.redoAction)
        self._noItemContextMenu.addSeparator()
        self._noItemContextMenu.addAction(self.cutAction)
        self._noItemContextMenu.addAction(self.copyAction)
        self._noItemContextMenu.addAction(self.pasteAction)
        self._noItemContextMenu.addSeparator()
        self._noItemContextMenu.addAction(self.zoomInAction)
        self._noItemContextMenu.addAction(self.zoomOutAction)
        self._noItemContextMenu.addAction(self.zoomFitAction)

        self._singleItemContextMenu: QMenu = QMenu()
        self._singleItemContextMenu.addAction(self.cutAction)
        self._singleItemContextMenu.addAction(self.copyAction)
        self._singleItemContextMenu.addAction(self.pasteAction)
        self._singleItemContextMenu.addAction(self.deleteAction)
        self._singleItemContextMenu.addSeparator()
        self._singleItemContextMenu.addAction(self.rotateAction)
        self._singleItemContextMenu.addAction(self.rotateBackAction)
        self._singleItemContextMenu.addAction(self.flipHorizontalAction)
        self._singleItemContextMenu.addAction(self.flipVerticalAction)
        self._singleItemContextMenu.addSeparator()
        self._singleItemContextMenu.addAction(self.bringForwardAction)
        self._singleItemContextMenu.addAction(self.sendBackwardAction)
        self._singleItemContextMenu.addAction(self.bringToFrontAction)
        self._singleItemContextMenu.addAction(self.sendToBackAction)

        self._singlePolyItemContextMenu: QMenu = QMenu()
        self._singlePolyItemContextMenu.addAction(self.cutAction)
        self._singlePolyItemContextMenu.addAction(self.copyAction)
        self._singlePolyItemContextMenu.addAction(self.pasteAction)
        self._singlePolyItemContextMenu.addAction(self.deleteAction)
        self._singlePolyItemContextMenu.addSeparator()
        self._singlePolyItemContextMenu.addAction(self.insertPointAction)
        self._singlePolyItemContextMenu.addAction(self.removePointAction)
        self._singlePolyItemContextMenu.addSeparator()
        self._singlePolyItemContextMenu.addAction(self.rotateAction)
        self._singlePolyItemContextMenu.addAction(self.rotateBackAction)
        self._singlePolyItemContextMenu.addAction(self.flipHorizontalAction)
        self._singlePolyItemContextMenu.addAction(self.flipVerticalAction)
        self._singlePolyItemContextMenu.addSeparator()
        self._singlePolyItemContextMenu.addAction(self.bringForwardAction)
        self._singlePolyItemContextMenu.addAction(self.sendBackwardAction)
        self._singlePolyItemContextMenu.addAction(self.bringToFrontAction)
        self._singlePolyItemContextMenu.addAction(self.sendToBackAction)

        self._singleGroupItemContextMenu: QMenu = QMenu()
        self._singleGroupItemContextMenu.addAction(self.cutAction)
        self._singleGroupItemContextMenu.addAction(self.copyAction)
        self._singleGroupItemContextMenu.addAction(self.pasteAction)
        self._singleGroupItemContextMenu.addAction(self.deleteAction)
        self._singleGroupItemContextMenu.addSeparator()
        self._singleGroupItemContextMenu.addAction(self.rotateAction)
        self._singleGroupItemContextMenu.addAction(self.rotateBackAction)
        self._singleGroupItemContextMenu.addAction(self.flipHorizontalAction)
        self._singleGroupItemContextMenu.addAction(self.flipVerticalAction)
        self._singleGroupItemContextMenu.addSeparator()
        self._singleGroupItemContextMenu.addAction(self.bringForwardAction)
        self._singleGroupItemContextMenu.addAction(self.sendBackwardAction)
        self._singleGroupItemContextMenu.addAction(self.bringToFrontAction)
        self._singleGroupItemContextMenu.addAction(self.sendToBackAction)
        self._singleGroupItemContextMenu.addSeparator()
        self._singleGroupItemContextMenu.addAction(self.groupAction)
        self._singleGroupItemContextMenu.addAction(self.ungroupAction)

        self._multipleItemContextMenu: QMenu = QMenu()
        self._multipleItemContextMenu.addAction(self.cutAction)
        self._multipleItemContextMenu.addAction(self.copyAction)
        self._multipleItemContextMenu.addAction(self.pasteAction)
        self._multipleItemContextMenu.addAction(self.deleteAction)
        self._multipleItemContextMenu.addSeparator()
        self._multipleItemContextMenu.addAction(self.rotateAction)
        self._multipleItemContextMenu.addAction(self.rotateBackAction)
        self._multipleItemContextMenu.addAction(self.flipHorizontalAction)
        self._multipleItemContextMenu.addAction(self.flipVerticalAction)
        self._multipleItemContextMenu.addSeparator()
        self._multipleItemContextMenu.addAction(self.bringForwardAction)
        self._multipleItemContextMenu.addAction(self.sendBackwardAction)
        self._multipleItemContextMenu.addAction(self.bringToFrontAction)
        self._multipleItemContextMenu.addAction(self.sendToBackAction)
        self._multipleItemContextMenu.addSeparator()
        self._multipleItemContextMenu.addAction(self.groupAction)
        self._multipleItemContextMenu.addAction(self.ungroupAction)

    # ==================================================================================================================

    def _selectModeRightMouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (isinstance(self._currentPage, OdgPage) and self.mode() == OdgDrawingWidget.Mode.SelectMode):
            # Show context menu depending on whether or not the right-click occurred on a selected item
            # and if so, what kind of item it was.
            if (self._selectMouseDownItem is not None and self._selectMouseDownItem.isSelected()):
                if (len(self._selectedItems) == 1):
                    if (self.insertPointAction.isEnabled()):
                        self._singlePolyItemContextMenu.popup(self.mapToGlobal(event.pos()))
                    elif (self.groupAction.isEnabled() or self.ungroupAction.isEnabled()):
                        self._singleGroupItemContextMenu.popup(self.mapToGlobal(event.pos()))
                    else:
                        self._singleItemContextMenu.popup(self.mapToGlobal(event.pos()))
                else:
                    self._multipleItemContextMenu.popup(self.mapToGlobal(event.pos()))
            else:
                self.setSelectedItems([])
                self._noItemContextMenu.popup(self.mapToGlobal(event.pos()))

        super()._selectModeRightMouseReleaseEvent(event)

    # ==================================================================================================================

    def setActionsEnabled(self, enable: bool) -> None:
        for action in self.actions():
            action.setEnabled(enable)
        for action in self._modeActionGroup.actions():
            action.setEnabled(enable)

    def _setModeFromAction(self, action: QAction) -> None:
        if (action == self.selectModeAction):
            self.setSelectMode()
        elif (action == self.scrollModeAction):
            self.setScrollMode()
        elif (action == self.zoomModeAction):
            self.setZoomMode()
        else:
            item = OdgItem.createItem(action.property('type'), self.defaultItemStyle())
            if (isinstance(item, OdgItem)):
                # Send the item a placeCreateEvent so it can set its initial geometry as needed
                item.placeCreateEvent(self.contentRect(), self._grid)
                placeByMousePressAndRelease = (not item.isValid() and item.placeResizeStartPoint() is not None and
                                               item.placeResizeEndPoint() is not None)

                self.setPlaceMode([item], placeByMousePressAndRelease)
            else:
                self.setSelectMode()

    def _updateActionsFromMode(self, mode: int) -> None:
        if (mode == DrawingWidget.Mode.SelectMode and not self.selectModeAction.isChecked()):
            self.selectModeAction.setChecked(True)

    # ==================================================================================================================

    def _updateActionsFromSelection(self, items: list[OdgItem]) -> None:
        canGroup = (len(items) > 1)
        canUngroup = False
        canInsertPoints = False
        canRemovePoints = False
        if (len(items) == 1):
            item = items[0]
            canUngroup = isinstance(item, OdgGroupItem)
            canInsertPoints = item.canInsertPoints()
            canRemovePoints = item.canRemovePoints()

        self.groupAction.setEnabled(canGroup)
        self.ungroupAction.setEnabled(canUngroup)
        self.insertPointAction.setEnabled(canInsertPoints)
        self.removePointAction.setEnabled(canRemovePoints)
