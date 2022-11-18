# drawing.py
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
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QBrush, QContextMenuEvent, QIcon, QKeySequence, QUndoStack
from PyQt6.QtWidgets import QMenu, QStackedWidget, QWidget
from .drawingpage import DrawingPage
from .drawingtypes import DrawingUnits


class Drawing(QWidget):
    scaleChanged = pyqtSignal(float)
    modeChanged = pyqtSignal(str)
    modifiedChanged = pyqtSignal(str)
    mouseInfoChanged = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self._stackedWidget: QStackedWidget = QStackedWidget()

        self._units: DrawingUnits = DrawingUnits.Millimeters

        self._grid: float = 0
        self._gridVisible: bool = False
        self._gridBrush: QBrush = QBrush()
        self._gridSpacingMajor: int = 0
        self._gridSpacingMinor: int = 0

        self._pages: list[DrawingPage] = []
        self._currentPage: DrawingPage | None = None
        self._newPageCount: int = 0

        self._undoStack: QUndoStack = QUndoStack()

        # Create actions and context menus
        self._createActions()
        self._createContextMenus()

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

        self.rotateAction: QAction = self._addNormalAction('Rotate', self.rotate,
                                                           'icons:object-rotate-right.png', 'R')
        self.rotateBackAction: QAction = self._addNormalAction('Rotate Back', self.rotateBack,
                                                               'icons:object-rotate-left.png', 'Shift+R')
        self.flipHorizontalAction: QAction = self._addNormalAction('Flip Horizontal', self.flipHorizontal,
                                                                   'icons:object-flip-horizontal.png', 'F')
        self.flipVerticalAction: QAction = self._addNormalAction('Flip Vertical', self.flipVertical,
                                                                 'icons:object-flip-vertical.png', 'Shift+F')

        self.bringForwardAction: QAction = self._addNormalAction('Bring Forward', self.bringForward,
                                                                 'icons:object-bring-forward.png')
        self.sendBackwardAction: QAction = self._addNormalAction('Send Backward', self.sendBackward,
                                                                 'icons:object-send-backward.png')
        self.bringToFrontAction: QAction = self._addNormalAction('Bring to Front', self.bringToFront,
                                                                 'icons:object-bring-to-front.png')
        self.sendToBackAction: QAction = self._addNormalAction('Send to Back', self.sendToBack,
                                                               'icons:object-send-to-back.png')

        self.groupAction: QAction = self._addNormalAction('Group', self.group, 'icons:merge.png', 'Ctrl+G')
        self.ungroupAction: QAction = self._addNormalAction('Ungroup', self.ungroup, 'icons:split.png', 'Ctrl+Shift+G')

        self.insertPointAction: QAction = self._addNormalAction('Insert Point', self.insertItemPoint)
        self.removePointAction: QAction = self._addNormalAction('Remove Point', self.removeItemPoint)

        self.insertPageAction: QAction = self._addNormalAction('Insert Page', self.insertNewPage)
        self.removePageAction: QAction = self._addNormalAction('Remove Page', self.removeCurrentPage)

        self.zoomInAction: QAction = self._addNormalAction('Zoom In', self.zoomIn, 'icons:zoom-in.png', '.')
        self.zoomOutAction: QAction = self._addNormalAction('Zoom Out', self.zoomOut, 'icons:zoom-out.png', ',')
        self.zoomFitAction: QAction = self._addNormalAction('Zoom Fit', self.zoomFit, 'icons:zoom-fit-best.png', '/')

        # Mode actions
        self._modeActionGroup: QActionGroup = QActionGroup(self)
        self._modeActionGroup.triggered.connect(self._setModeFromAction)    # type: ignore

        self.selectModeAction: QAction = self._addModeAction('Select Mode', '', 'icons:edit-select.png', 'Escape')
        self.scrollModeAction: QAction = self._addModeAction('Scroll Mode', '', 'icons:transform-move.png')
        self.zoomModeAction: QAction = self._addModeAction('Zoom Mode', '', 'icons:page-zoom.png')

        self.placeLineAction: QAction = self._addModeAction('Place Line', 'line', 'icons:draw-line.png')
        self.placeCurveAction: QAction = self._addModeAction('Place Curve', 'curve', 'icons:draw-curve.png')
        self.placePolylineAction: QAction = self._addModeAction('Place Polyline', 'polyline', 'icons:draw-polyline.png')
        self.placeRectAction: QAction = self._addModeAction('Place Rectangle', 'rect', 'icons:draw-rectangle.png')
        self.placeEllipseAction: QAction = self._addModeAction('Place Ellipse', 'ellipse', 'icons:draw-ellipse.png')
        self.placePolygonAction: QAction = self._addModeAction('Place Polygon', 'polygon', 'icons:draw-polygon.png')
        self.placeTextAction: QAction = self._addModeAction('Place Text', 'text', 'icons:draw-text.png')
        self.placeTextRectAction: QAction = self._addModeAction('Place Text Rectangle', 'textRect',
                                                                'icons:text-rect.png')
        self.placeTextEllipseAction: QAction = self._addModeAction('Place Text Ellipse', 'textEllipse',
                                                                   'icons:text-ellipse.png')

        self.selectModeAction.setChecked(True)

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

    def createNew(self) -> None:
        pass

    def clear(self) -> None:
        pass

    # ==================================================================================================================

    def undo(self) -> None:
        pass

    def redo(self) -> None:
        pass

    # ==================================================================================================================

    def cut(self) -> None:
        pass

    def copy(self) -> None:
        pass

    def paste(self) -> None:
        pass

    def delete(self) -> None:
        pass

    # ==================================================================================================================

    def selectAll(self) -> None:
        pass

    def selectNone(self) -> None:
        pass

    # ==================================================================================================================

    def rotate(self) -> None:
        pass

    def rotateBack(self) -> None:
        pass

    def flipHorizontal(self) -> None:
        pass

    def flipVertical(self) -> None:
        pass

    # ==================================================================================================================

    def bringForward(self) -> None:
        pass

    def sendBackward(self) -> None:
        pass

    def bringToFront(self) -> None:
        pass

    def sendToBack(self) -> None:
        pass

    # ==================================================================================================================

    def group(self) -> None:
        pass

    def ungroup(self) -> None:
        pass

    # ==================================================================================================================

    def insertItemPoint(self) -> None:
        pass

    def removeItemPoint(self) -> None:
        pass

    # ==================================================================================================================

    def insertNewPage(self) -> None:
        pass

    def removeCurrentPage(self) -> None:
        pass

    # ==================================================================================================================

    def zoomIn(self) -> None:
        pass

    def zoomOut(self) -> None:
        pass

    def zoomFit(self) -> None:
        pass

    # ==================================================================================================================

    def modeActions(self) -> list[QAction]:
        return self._modeActionGroup.actions()

    # ==================================================================================================================

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self._noItemContextMenu.popup(event.globalPos())

    # ==================================================================================================================

    def _setModeFromAction(self, action: QAction) -> None:
        pass

    # ==================================================================================================================

    def _addNormalAction(self, text: str, slot: typing.Callable, iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)      # type: ignore
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        self.addAction(action)
        return action

    def _addModeAction(self, text: str, itemKey: str = '', iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self._modeActionGroup)
        action.setProperty('key', itemKey)
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        action.setCheckable(True)
        action.setActionGroup(self._modeActionGroup)
        return action
