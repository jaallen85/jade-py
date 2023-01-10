# drawingrectitem.py
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
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from ..drawing.drawingitem import DrawingItem
from ..drawing.drawingitempoint import DrawingItemPoint


class DrawingPathItem(DrawingItem):
    class PointIndex(IntEnum):
        TopLeft = 0
        TopMiddle = 1
        TopRight = 2
        MiddleRight = 3
        BottomRight = 4
        BottomMiddle = 5
        BottomLeft = 6
        MiddleLeft = 7

    # ==================================================================================================================

    def __init__(self) -> None:
        super().__init__()

        self._pathName: str = ''
        self._path: QPainterPath = QPainterPath()
        self._pathRect: QRectF = QRectF()
        self._additionalPathConnectionPoints: dict[DrawingItemPoint, QPointF] = {}

        self._rect: QRectF = QRectF()

        self._pen: QPen = QPen()

        self._transformedPath: QPainterPath = QPainterPath()

        for _ in range(8):
            self.addPoint(DrawingItemPoint(QPointF(0, 0), DrawingItemPoint.Type.Control))

    def __copy__(self) -> 'DrawingPathItem':
        copiedItem = DrawingPathItem()
        copiedItem._copyBaseClassValues(self)
        copiedItem.setPathName(self.pathName())
        copiedItem.setPath(self.path(), self.pathRect())

        copiedItem.setRect(self.rect())
        copiedItem.setPen(self.pen())

        connectionPoints = self.connectionPoints()
        for index in range(connectionPoints.size()):
            copiedItem.addConnectionPoint(connectionPoints.at(index))

        return copiedItem

    # ==================================================================================================================

    def key(self) -> str:
        return 'path'

    def prettyName(self) -> str:
        return self._pathName

    # ==================================================================================================================

    def setPathName(self, name: str) -> None:
        self._pathName = str(name)

    def setPath(self, path: QPainterPath, pathRect: QRectF) -> None:
        self._path = QPainterPath(path)
        self._pathRect = QRectF(pathRect)
        self._updatePathTransforms()

    def pathName(self) -> str:
        return self._pathName

    def path(self) -> QPainterPath:
        return self._path

    def pathRect(self) -> QRectF:
        return self._pathRect

    def transformedPath(self) -> QPainterPath:
        return self._transformedPath

    # ==================================================================================================================

    def addConnectionPoint(self, position: QPointF) -> None:
        itemPosition = self.mapFromPath(position)

        # Determine if the provided pathPosition refers to one of the item's existing points
        existingPoint = None
        for point in self._points:
            if (point.position() == itemPosition):
                existingPoint = point
                break

        if (existingPoint is not None):
            # If so, simply set that point as a connection point
            existingPoint.setType(DrawingItemPoint.Type.ControlAndConnection)
        else:
            # If not, create a new point and add it to the item
            newPoint = DrawingItemPoint(itemPosition, DrawingItemPoint.Type.Connection)
            self._additionalPathConnectionPoints[newPoint] = QPointF(position)
            self.addPoint(newPoint)

    def connectionPoints(self) -> QPolygonF:
        connectionPoints = QPolygonF()
        for point in self._points:
            if (point.isConnectionPoint()):
                connectionPoints.append(self.mapToPath(point.position()))
        return connectionPoints

    # ==================================================================================================================

    def setRect(self, rect: QRectF) -> None:
        self._rect = QRectF(rect)

        # Set point positions to match self._rect
        if (len(self._points) >= 8):
            center = self._rect.center()
            self._points[DrawingPathItem.PointIndex.TopLeft].setPosition(QPointF(rect.left(), rect.top()))
            self._points[DrawingPathItem.PointIndex.TopMiddle].setPosition(QPointF(center.x(), rect.top()))
            self._points[DrawingPathItem.PointIndex.TopRight].setPosition(QPointF(rect.right(), rect.top()))
            self._points[DrawingPathItem.PointIndex.MiddleRight].setPosition(QPointF(rect.right(), center.y()))
            self._points[DrawingPathItem.PointIndex.BottomRight].setPosition(QPointF(rect.right(), rect.bottom()))
            self._points[DrawingPathItem.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), rect.bottom()))
            self._points[DrawingPathItem.PointIndex.BottomLeft].setPosition(QPointF(rect.left(), rect.bottom()))
            self._points[DrawingPathItem.PointIndex.MiddleLeft].setPosition(QPointF(rect.left(), center.y()))

            self._updatePathTransforms()

            for connectionPoint, pathPosition in self._additionalPathConnectionPoints.items():
                connectionPoint.setPosition(self.mapFromPath(pathPosition))

    def rect(self) -> QRectF:
        return self._rect

    # ==================================================================================================================

    def setPen(self, pen: QPen) -> None:
        self._pen = QPen(pen)

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
        if (name == 'pen' and isinstance(value, QPen)):
            self.setPen(value)
        elif (name == 'penStyle' and isinstance(value, int)):
            pen = self.pen()
            pen.setStyle(Qt.PenStyle(value))
            self.setPen(pen)
        elif (name == 'penWidth' and isinstance(value, float)):
            pen = self.pen()
            pen.setWidthF(value)
            self.setPen(pen)
        elif (name == 'penColor' and isinstance(value, QColor)):
            pen = self.pen()
            pen.setBrush(QBrush(QColor(value)))
            self.setPen(pen)

    def property(self, name: str) -> typing.Any:
        if (name == 'rect'):
            return self.mapRectToScene(self.rect())
        if (name == 'pen'):
            return self.pen()
        if (name == 'penStyle'):
            return self.pen().style().value
        if (name == 'penWidth'):
            return self.pen().widthF()
        if (name == 'penColor'):
            return self.pen().brush().color()
        return None

    # ==================================================================================================================

    def mapToPath(self, position: QPointF) -> QPointF:
        return QPointF((position.x() - self._rect.left()) / self._rect.width() * self._pathRect.width() + self._pathRect.left(),    # noqa
	                   (position.y() - self._rect.top()) / self._rect.height() * self._pathRect.height() + self._pathRect.top())    # noqa

    def mapRectToPath(self, rect: QRectF) -> QRectF:
        return QRectF(self.mapToPath(rect.topLeft()), self.mapToPath(rect.bottomRight()))

    def mapFromPath(self, position: QPointF) -> QPointF:
        return QPointF((position.x() - self._pathRect.left()) / self._pathRect.width() * self._rect.width() + self._rect.left(),    # noqa
	                   (position.y() - self._pathRect.top()) / self._pathRect.height() * self._rect.height() + self._rect.top())    # noqa

    def mapRectFromPath(self, rect: QRectF) -> QRectF:
        return QRectF(self.mapFromPath(rect.topLeft()), self.mapFromPath(rect.bottomRight()))

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = QRectF(self._rect.normalized())

        # Adjust for pen width
        if (self._pen.style() != Qt.PenStyle.NoPen):
            halfPenWidth = self._pen.widthF() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def shape(self) -> QPainterPath:
        shape = QPainterPath()
        shape.addRect(self._rect.normalized())
        return shape

    def centerPosition(self) -> QPointF:
        return QPointF(0.0, 0.0)

    def isValid(self) -> bool:
        return (self._rect.width() != 0 and self._rect.height() != 0 and not self._path.isEmpty() and
                self._pathRect.width() != 0 and self._pathRect.height() != 0)

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(self._pen)
        painter.drawPath(self._transformedPath)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            position = self.mapFromScene(position)
            rect = QRectF(self._rect)
            match (self._points.index(point)):
                case DrawingPathItem.PointIndex.TopLeft:
                    rect.setTopLeft(position)
                case DrawingPathItem.PointIndex.TopMiddle:
                    rect.setTop(position.y())
                case DrawingPathItem.PointIndex.TopRight:
                    rect.setTopRight(position)
                case DrawingPathItem.PointIndex.MiddleRight:
                    rect.setRight(position.x())
                case DrawingPathItem.PointIndex.BottomRight:
                    rect.setBottomRight(position)
                case DrawingPathItem.PointIndex.BottomMiddle:
                    rect.setBottom(position.y())
                case DrawingPathItem.PointIndex.BottomLeft:
                    rect.setBottomLeft(position)
                case DrawingPathItem.PointIndex.MiddleLeft:
                    rect.setLeft(position.x())

            # Keep the item's position as the center of the rect
            center = rect.center()
            self.setPosition(self.mapToScene(center))
            rect.translate(-center)

            self.setRect(rect)

    # ==================================================================================================================

    def placeStartEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = grid
        if (size <= 0):
            size = sceneRect.width() / 320
        self.setRect(QRectF(self._rect.left() * size, self._rect.top() * size,
                            self._rect.width() * size, self._rect.height() * size))

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        super().writeToXml(element)

        element.set('pathName', self._pathName)

        element.set('x', self._toPositionStr(self._rect.left()))
        element.set('y', self._toPositionStr(self._rect.top()))
        element.set('width', self._toSizeStr(self._rect.width()))
        element.set('height', self._toSizeStr(self._rect.height()))

        self._writePen(element, 'pen', self._pen)

        element.set('pathLeft', self._toPositionStr(self._pathRect.left()))
        element.set('pathTop', self._toPositionStr(self._pathRect.top()))
        element.set('pathWidth', self._toSizeStr(self._pathRect.width()))
        element.set('pathHeight', self._toSizeStr(self._pathRect.height()))

        element.set('d', self._toPathStr(self._path))

        element.set('connectionPoints', self._toPointsStr(self.connectionPoints()))

    def readFromXml(self, element: ElementTree.Element) -> None:
        super().readFromXml(element)

        self.setPathName(element.get('pathName', ''))

        self.setRect(QRectF(self._fromPositionStr(element.get('x', '0')),
                            self._fromPositionStr(element.get('y', '0')),
                            self._fromSizeStr(element.get('width', '0')),
                            self._fromSizeStr(element.get('height', '0'))))

        self.setPen(self._readPen(element, 'pen'))

        self.setPath(self._fromPathStr(element.get('d', '')),
                     QRectF(self._fromPositionStr(element.get('pathLeft', '0')),
                            self._fromPositionStr(element.get('pathTop', '0')),
                            self._fromSizeStr(element.get('pathWidth', '0')),
                            self._fromSizeStr(element.get('pathHeight', '0'))))

        connectionPoints = self._fromPointsStr(element.get('connectionPoints', ''))
        for index in range(connectionPoints.size()):
            self.addConnectionPoint(connectionPoints.at(index))

    # ==================================================================================================================

    def _updatePathTransforms(self):
        self._transformedPath.clear()

        curveDataPoints = []
        for index in range(self._path.elementCount()):
            element = self._path.elementAt(index)
            match (element.type):
                case QPainterPath.ElementType.MoveToElement:
                    self._transformedPath.moveTo(self.mapFromPath(QPointF(element.x, element.y)))
                case QPainterPath.ElementType.LineToElement:
                    self._transformedPath.lineTo(self.mapFromPath(QPointF(element.x, element.y)))
                case QPainterPath.ElementType.CurveToElement:
                    curveDataPoints.append(self.mapFromPath(QPointF(element.x, element.y)))
                case QPainterPath.ElementType.CurveToDataElement:
                    if (len(curveDataPoints) < 2):
                        curveDataPoints.append(self.mapFromPath(QPointF(element.x, element.y)))
                    else:
                        self._transformedPath.cubicTo(curveDataPoints[0], curveDataPoints[1],
                                                      self.mapFromPath(QPointF(element.x, element.y)))
                        curveDataPoints = []
