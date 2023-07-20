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
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence
from .odg.odgdrawingwidget import OdgDrawingWidget


class DrawingWidget(OdgDrawingWidget):
    def __init__(self) -> None:
        super().__init__()
        self._createActions()

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

        self.selectModeAction: QAction = self._addModeAction('Select Mode', 'icons:edit-select.png', 'Escape')
        self.scrollModeAction: QAction = self._addModeAction('Scroll Mode', 'icons:transform-move.png')
        self.zoomModeAction: QAction = self._addModeAction('Zoom Mode', 'icons:page-zoom.png')

        self.placeLineAction: QAction = self._addModeAction('Draw Line', 'icons:draw-line.png')
        self.placeCurveAction: QAction = self._addModeAction('Draw Curve', 'icons:draw-curve.png')
        self.placePolylineAction: QAction = self._addModeAction('Draw Polyline', 'icons:draw-polyline.png')
        self.placeRectAction: QAction = self._addModeAction('Draw Rectangle', 'icons:draw-rectangle.png')
        self.placeEllipseAction: QAction = self._addModeAction('Draw Ellipse', 'icons:draw-ellipse.png')
        self.placePolygonAction: QAction = self._addModeAction('Draw Polygon', 'icons:draw-polygon.png')
        self.placeTextAction: QAction = self._addModeAction('Draw Text', 'icons:draw-text.png')
        self.placeTextRectAction: QAction = self._addModeAction('Draw Text Rect', 'icons:text-rect.png')
        self.placeTextEllipseAction: QAction = self._addModeAction('Draw Text Ellipse', 'icons:text-ellipse.png')

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

    def _addModeAction(self, text: str, iconPath: str = '', shortcut: str = '') -> QAction:
        action = QAction(text, self._modeActionGroup)
        if (iconPath != ''):
            action.setIcon(QIcon(iconPath))
        if (shortcut != ''):
            action.setShortcut(QKeySequence(shortcut))
        action.setCheckable(True)
        action.setActionGroup(self._modeActionGroup)
        return action

    # ==================================================================================================================

    def _setModeFromAction(self, action: QAction) -> None:
        if (action == self.selectModeAction):
            self.setSelectMode()
        elif (action == self.scrollModeAction):
            self.setScrollMode()
        elif (action == self.zoomModeAction):
            self.setZoomMode()
        else:
            self.setSelectMode()

    def _updateActionsFromMode(self, mode: int) -> None:
        pass
