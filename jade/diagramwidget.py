# diagramwidget.py
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
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QActionGroup, QBrush, QFont, QIcon, QKeySequence, QPen
from PySide6.QtWidgets import QMenu
from .drawing.drawingarrow import DrawingArrow
from .drawing.drawingitem import DrawingItem
from .drawing.drawingitemgroup import DrawingItemGroup
from .drawing.drawingpagewidget import DrawingPageWidget
from .drawing.drawingwidget import DrawingWidget
from .items.drawingcurveitem import DrawingCurveItem
from .items.drawingellipseitem import DrawingEllipseItem
from .items.drawinglineitem import DrawingLineItem
from .items.drawingpathitem import DrawingPathItem
from .items.drawingpolygonitem import DrawingPolygonItem
from .items.drawingpolylineitem import DrawingPolylineItem
from .items.drawingrectitem import DrawingRectItem
from .items.drawingtextellipseitem import DrawingTextEllipseItem
from .items.drawingtextitem import DrawingTextItem
from .items.drawingtextrectitem import DrawingTextRectItem
from .items.electricitems import ElectricItems
from .properties.units import Units
from .diagramtemplate import DiagramTemplate


class DiagramWidget(DrawingWidget):
    def __init__(self) -> None:
        super().__init__()

        self._units: Units = Units.Millimeters

        self._defaultPen: QPen = QPen(QBrush(Qt.GlobalColor.black), 0.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                      Qt.PenJoinStyle.RoundJoin)
        self._defaultBrush: QBrush = QBrush(Qt.GlobalColor.white)
        self._defaultStartArrow: DrawingArrow = DrawingArrow(DrawingArrow.Style.NoStyle, 4.0)
        self._defaultEndArrow: DrawingArrow = DrawingArrow(DrawingArrow.Style.NoStyle, 4.0)
        self._defaultFont: QFont = QFont('Arial')
        self._defaultFont.setPointSizeF(4)
        self._defaultTextAlignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
        self._defaultTextBrush: QBrush = QBrush(Qt.GlobalColor.black)

        self._createActions()
        self._createContextMenus()
        self.currentItemsChanged.connect(self._updateActionsFromSelection)
        self.currentItemsPropertyChanged.connect(self._updateActionsFromSelection)
        self.contextMenuTriggered.connect(self._contextMenuEvent)

    # ==================================================================================================================

    def setUnits(self, units: Units) -> None:
        scale = Units.convertSimple(1.0, self._units, units)

        self._units = units

        self._defaultPen.setWidthF(self._defaultPen.widthF() * scale)
        self._defaultStartArrow.setSize(self._defaultStartArrow.size() * scale)
        self._defaultEndArrow.setSize(self._defaultEndArrow.size() * scale)
        self._defaultFont.setPointSizeF(self._defaultFont.pointSizeF() * scale)

    def units(self) -> Units:
        return self._units

    # ==================================================================================================================

    def setDefaultPen(self, pen: QPen) -> None:
        self._defaultPen = QPen(pen)

    def setDefaultBrush(self, brush: QBrush) -> None:
        self._defaultBrush = QBrush(brush)

    def setDefaultStartArrow(self, arrow: DrawingArrow) -> None:
        self._defaultStartArrow = DrawingArrow(arrow.style(), arrow.size())

    def setDefaultEndArrow(self, arrow: DrawingArrow) -> None:
        self._defaultEndArrow = DrawingArrow(arrow.style(), arrow.size())

    def setDefaultFont(self, font: QFont) -> None:
        self._defaultFont = QFont(font)

    def setDefaultTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._defaultTextAlignment = alignment

    def setDefaultTextBrush(self, brush: QBrush) -> None:
        self._defaultTextBrush = QBrush(brush)

    def defaultPen(self) -> QPen:
        return self._defaultPen

    def defaultBrush(self) -> QBrush:
        return self._defaultBrush

    def defaultStartArrow(self) -> DrawingArrow:
        return self._defaultStartArrow

    def defaultEndArrow(self) -> DrawingArrow:
        return self._defaultEndArrow

    def defaultFont(self) -> QFont:
        return self._defaultFont

    def defaultTextAlignment(self) -> Qt.AlignmentFlag:
        return self._defaultTextAlignment

    def defaultTextBrush(self) -> QBrush:
        return self._defaultTextBrush

    def _setDefaultItemProperties(self, item: DrawingItem) -> None:
        item.setProperty('pen', QPen(self._defaultPen))
        item.setProperty('brush', QBrush(self._defaultBrush))
        item.setProperty('startArrow', DrawingArrow(self._defaultStartArrow.style(), self._defaultStartArrow.size()))
        item.setProperty('endArrow', DrawingArrow(self._defaultEndArrow.style(), self._defaultEndArrow.size()))
        item.setProperty('font', QFont(self._defaultFont))
        item.setProperty('textAlignment', Qt.AlignmentFlag(self._defaultTextAlignment))
        item.setProperty('textBrush', QBrush(self._defaultTextBrush))

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

        self.insertPointAction: QAction = self._addNormalAction('Insert Point', self.insertNewItemPoint)
        self.removePointAction: QAction = self._addNormalAction('Remove Point', self.removeCurrentItemPoint)

        self.insertPageAction: QAction = self._addNormalAction('Insert Page', self.insertNewPage)
        self.removePageAction: QAction = self._addNormalAction('Remove Page', self.removeCurrentPage)

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

        self.placeLineAction: QAction = self._addPlaceAction(DrawingLineItem(), 'icons:draw-line.png')
        self.placeCurveAction: QAction = self._addPlaceAction(DrawingCurveItem(), 'icons:draw-curve.png')
        self.placePolylineAction: QAction = self._addPlaceAction(DrawingPolylineItem(), 'icons:draw-polyline.png')
        self.placeRectAction: QAction = self._addPlaceAction(DrawingRectItem(), 'icons:draw-rectangle.png')
        self.placeEllipseAction: QAction = self._addPlaceAction(DrawingEllipseItem(), 'icons:draw-ellipse.png')
        self.placePolygonAction: QAction = self._addPlaceAction(DrawingPolygonItem(), 'icons:draw-polygon.png')
        self.placeTextAction: QAction = self._addPlaceAction(DrawingTextItem(), 'icons:draw-text.png')
        self.placeTextRectAction: QAction = self._addPlaceAction(DrawingTextRectItem(), 'icons:text-rect.png')
        self.placeTextEllipseAction: QAction = self._addPlaceAction(DrawingTextEllipseItem(), 'icons:text-ellipse.png')
        DrawingItem.registerFactoryItem(DrawingPathItem())
        DrawingItem.registerFactoryItem(DrawingItemGroup())

        self.electricActions: list[QAction] = self._addPathActions(ElectricItems.create())

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

    def _contextMenuEvent(self, position: QPoint) -> None:
        if (self._currentPage is not None and self.mode() == DrawingPageWidget.Mode.SelectMode):
            # Show context menu depending on whether or not the right-click occurred on a selected item
            # and if so, what kind of item it was.
            mouseDownItem = self._currentPage.mouseDownItem()
            selectedItems = self._currentPage.selectedItems()

            if (mouseDownItem is not None and mouseDownItem.isSelected()):
                if (len(selectedItems) == 1):
                    if (self.insertPointAction.isEnabled()):
                        self._singlePolyItemContextMenu.popup(self.mapToGlobal(position))
                    elif (self.groupAction.isEnabled() or self.ungroupAction.isEnabled()):
                        self._singleGroupItemContextMenu.popup(self.mapToGlobal(position))
                    else:
                        self._singleItemContextMenu.popup(self.mapToGlobal(position))
                else:
                    self._multipleItemContextMenu.popup(self.mapToGlobal(position))
            else:
                self.setSelectedItems([])
                self._noItemContextMenu.popup(self.mapToGlobal(position))

    # ==================================================================================================================

    def setActionsEnabled(self, enable: bool) -> None:
        for action in self.actions():
            action.setEnabled(enable)
        for action in self._modeActionGroup.actions():
            action.setEnabled(enable)

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

    def _addPlaceAction(self, item: DrawingItem, iconPath: str = '') -> QAction:
        DrawingItem.registerFactoryItem(item)
        return self._addModeAction(f'Place {item.prettyName()}', item.key(), iconPath)

    def _addPathActions(self, items: list[tuple[DrawingPathItem, str]]) -> list[QAction]:
        actions = []
        for pathItem, iconPath in items:
            DrawingItem.registerFactoryItem(pathItem)
            actions.append(self._addModeAction(f'Place {pathItem.prettyName()}', pathItem.pathName(), iconPath))
        return actions

    def _setModeFromAction(self, action: QAction) -> None:
        if (action == self.selectModeAction):
            self.setSelectMode()
        elif (action == self.scrollModeAction):
            self.setScrollMode()
        elif (action == self.zoomModeAction):
            self.setZoomMode()
        else:
            if (self._currentPage is not None):
                key = action.property('key')
                item = DrawingItem.createItemFromFactory(key)
                if (item is not None):
                    self._setDefaultItemProperties(item)
                    self.setPlaceMode([item])
                else:
                    self.setSelectMode()

    def _updateActionsFromMode(self, mode: int):
        if (mode == DrawingPageWidget.Mode.SelectMode.value and not self.selectModeAction.isChecked()):
            self.selectModeAction.setChecked(True)

    def _updateActionsFromSelection(self, items: list[DrawingItem]) -> None:
        canGroup = (len(items) > 1)
        canUngroup = False
        canInsertPoints = False
        canRemovePoints = False
        if (len(items) == 1):
            item = items[0]
            canUngroup = (item.key() == 'group')
            canInsertPoints = item.canInsertPoints()
            canRemovePoints = item.canRemovePoints()

        self.groupAction.setEnabled(canGroup)
        self.ungroupAction.setEnabled(canUngroup)
        self.insertPointAction.setEnabled(canInsertPoints)
        self.removePointAction.setEnabled(canRemovePoints)

    # ==================================================================================================================

    def createFromTemplate(self, template: DiagramTemplate) -> None:
        self.setUnits(template.units())
        self.setDefaultSceneRect(template.sceneRect())
        self.setDefaultBackgroundBrush(template.backgroundBrush())
        self.setGrid(template.grid())
        self.setGridVisible(template.isGridVisible())
        self.setGridBrush(template.gridBrush())
        self.setGridSpacingMajor(template.gridSpacingMajor())
        self.setGridSpacingMinor(template.gridSpacingMinor())

        self.insertNewPage()
        self._undoStack.clear()

    def saveToFile(self, path: str) -> bool:
        diagramElement = ElementTree.Element('jade-diagram')
        self.writeStr(diagramElement, 'units', self._units.toString())
        self.writeToXml(diagramElement)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(ElementTree.tostring(diagramElement, encoding='unicode', xml_declaration=True))

        self._undoStack.setClean()
        return True

    def loadFromFile(self, path: str) -> bool:
        self.clear()

        xml = ElementTree.parse(path)
        diagramElement = xml.getroot()
        if (diagramElement.tag == 'jade-diagram'):
            self.setUnits(Units.fromString(self.readStr(diagramElement, 'units')))
            self.readFromXml(diagramElement)

            self._undoStack.setClean()
            return True

        return False

    def clear(self) -> None:
        self._undoStack.clear()

        self.clearPages()
        self._newPageCount = 0
