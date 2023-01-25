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
        copiedItem.setPosition(self.position())
        copiedItem.setRotation(self.rotation())
        copiedItem.setFlipped(self.isFlipped())
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
        self._updateTransformedPath()

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
        if (rect.width() >= 0 and rect.height() >= 0):
            self._rect = QRectF(rect)

            # Put the item's position at the path origin
            offset = self.mapFromPath(QPointF(0, 0))
            self.setPosition(self.mapToScene(offset))
            self._rect.translate(-offset)

            # Set point positions to match self._rect
            if (len(self._points) >= 8):
                center = self._rect.center()
                self._points[DrawingPathItem.PointIndex.TopLeft].setPosition(QPointF(self._rect.left(), self._rect.top()))          # noqa
                self._points[DrawingPathItem.PointIndex.TopMiddle].setPosition(QPointF(center.x(), self._rect.top()))
                self._points[DrawingPathItem.PointIndex.TopRight].setPosition(QPointF(self._rect.right(), self._rect.top()))        # noqa
                self._points[DrawingPathItem.PointIndex.MiddleRight].setPosition(QPointF(self._rect.right(), center.y()))           # noqa
                self._points[DrawingPathItem.PointIndex.BottomRight].setPosition(QPointF(self._rect.right(), self._rect.bottom()))  # noqa
                self._points[DrawingPathItem.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), self._rect.bottom()))         # noqa
                self._points[DrawingPathItem.PointIndex.BottomLeft].setPosition(QPointF(self._rect.left(), self._rect.bottom()))    # noqa
                self._points[DrawingPathItem.PointIndex.MiddleLeft].setPosition(QPointF(self._rect.left(), center.y()))

            # Set connection point positions based on self._rect
            for connectionPoint, pathPosition in self._additionalPathConnectionPoints.items():
                connectionPoint.setPosition(self.mapFromPath(pathPosition))

            # Update the transformed path based on self._rect
            self._updateTransformedPath()

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
            return self.rect()
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
        if (self._rect.width() != 0 and self._rect.height() != 0):
            return QPointF((position.x() - self._rect.left()) / self._rect.width() * self._pathRect.width() + self._pathRect.left(),    # noqa
                           (position.y() - self._rect.top()) / self._rect.height() * self._pathRect.height() + self._pathRect.top())    # noqa
        return QPointF(position)

    def mapRectToPath(self, rect: QRectF) -> QRectF:
        return QRectF(self.mapToPath(rect.topLeft()), self.mapToPath(rect.bottomRight()))

    def mapFromPath(self, position: QPointF) -> QPointF:
        if (self._pathRect.width() != 0 and self._pathRect.height() != 0):
            return QPointF((position.x() - self._pathRect.left()) / self._pathRect.width() * self._rect.width() + self._rect.left(),    # noqa
                           (position.y() - self._pathRect.top()) / self._pathRect.height() * self._rect.height() + self._rect.top())    # noqa
        return QPointF(position)

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
            pointIndex = self._points.index(point)

            # Ensure that rect.width() >= 0
            if (pointIndex in (DrawingPathItem.PointIndex.TopLeft, DrawingPathItem.PointIndex.MiddleLeft,
                               DrawingPathItem.PointIndex.BottomLeft)):
                if (position.x() > rect.right()):
                    rect.setLeft(rect.right())
                else:
                    rect.setLeft(position.x())
            elif (pointIndex in (DrawingPathItem.PointIndex.TopRight, DrawingPathItem.PointIndex.MiddleRight,
                                 DrawingPathItem.PointIndex.BottomRight)):
                if (position.x() < rect.left()):
                    rect.setRight(rect.left())
                else:
                    rect.setRight(position.x())

            # Ensure that rect.height() >= 0
            if (pointIndex in (DrawingPathItem.PointIndex.TopLeft, DrawingPathItem.PointIndex.TopMiddle,
                               DrawingPathItem.PointIndex.TopRight)):
                if (position.y() > rect.bottom()):
                    rect.setTop(rect.bottom())
                else:
                    rect.setTop(position.y())
            elif (pointIndex in (DrawingPathItem.PointIndex.BottomLeft, DrawingPathItem.PointIndex.BottomMiddle,
                                 DrawingPathItem.PointIndex.BottomRight)):
                if (position.y() < rect.top()):
                    rect.setBottom(rect.top())
                else:
                    rect.setBottom(position.y())

            self.setRect(rect)

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = grid
        if (size <= 0):
            size = sceneRect.width() / 320
        self.setRect(QRectF(self._rect.left() * size, self._rect.top() * size,
                            self._rect.width() * size, self._rect.height() * size))

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        element.set('pathName', self._pathName)

        if (self.rotation() == 0 and not self.isFlipped()):
            rect = self.mapRectToScene(self._rect)
            element.set('x', self._toPositionStr(rect.left()))
            element.set('y', self._toPositionStr(rect.top()))
            element.set('width', self._toSizeStr(rect.width()))
            element.set('height', self._toSizeStr(rect.height()))
        else:
            self._writeTransform(element)
            element.set('x', self._toPositionStr(self._rect.left()))
            element.set('y', self._toPositionStr(self._rect.top()))
            element.set('width', self._toSizeStr(self._rect.width()))
            element.set('height', self._toSizeStr(self._rect.height()))

        self._writePen(element, 'pen', self._pen)

        element.set('viewBox', self._toViewBoxStr(self._pathRect))
        element.set('d', self._toPathStr(self._path))

        element.set('connectionPoints', self._toPointsStr(self.connectionPoints()))

    def readFromXml(self, element: ElementTree.Element) -> None:
        self._readTransform(element)

        self.setPathName(element.get('pathName', ''))

        self.setPen(self._readPen(element, 'pen'))

        self.setPath(self._fromPathStr(element.get('d', '')),
                     self._fromViewBoxStr(element.get('viewBox', '0 0 0 0')))

        connectionPoints = self._fromPointsStr(element.get('connectionPoints', ''))
        for index in range(connectionPoints.size()):
            self.addConnectionPoint(connectionPoints.at(index))

        self.setRect(QRectF(self._fromPositionStr(element.get('x', '0')),
                            self._fromPositionStr(element.get('y', '0')),
                            self._fromSizeStr(element.get('width', '0')),
                            self._fromSizeStr(element.get('height', '0'))))

    # ==================================================================================================================

    def _updateTransformedPath(self) -> None:
        self._transformedPath.clear()

        curveDataPoints = []
        for index in range(self._path.elementCount()):
            element = self._path.elementAt(index)
            match (element.type):   # type: ignore
                case QPainterPath.ElementType.MoveToElement:
                    self._transformedPath.moveTo(self.mapFromPath(QPointF(element.x, element.y)))   # type: ignore
                case QPainterPath.ElementType.LineToElement:
                    self._transformedPath.lineTo(self.mapFromPath(QPointF(element.x, element.y)))   # type: ignore
                case QPainterPath.ElementType.CurveToElement:
                    curveDataPoints.append(self.mapFromPath(QPointF(element.x, element.y)))         # type: ignore
                case QPainterPath.ElementType.CurveToDataElement:
                    if (len(curveDataPoints) < 2):
                        curveDataPoints.append(self.mapFromPath(QPointF(element.x, element.y)))     # type: ignore
                    else:
                        self._transformedPath.cubicTo(curveDataPoints[0], curveDataPoints[1],
                                                      self.mapFromPath(QPointF(element.x, element.y)))  # type: ignore
                        curveDataPoints = []
