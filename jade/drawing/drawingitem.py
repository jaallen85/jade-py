# drawingitem.py
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

import copy
import math
import typing
from abc import ABC, abstractmethod
from xml.etree import ElementTree
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPainterPathStroker, QPen, QPolygonF, QTransform
from .drawingitempoint import DrawingItemPoint
from .drawingxmlinterface import DrawingXmlInterface


class DrawingItem(ABC, DrawingXmlInterface):
    _factoryItems: list['DrawingItem'] = []

    # ==================================================================================================================

    def __init__(self) -> None:
        self._parent: typing.Any = None

        self._position: QPointF = QPointF()
        self._rotation: int = 0
        self._flipped: bool = False
        self._transform: QTransform = QTransform()
        self._transformInverse: QTransform = QTransform()

        self._points: list[DrawingItemPoint] = []

        self._selected: bool = False

    def __del__(self) -> None:
        self.clearPoints()

    # ==================================================================================================================

    def _copyBaseClassValues(self, otherItem: 'DrawingItem') -> None:
        self.setPosition(otherItem.position())
        self.setRotation(otherItem.rotation())
        self.setFlipped(otherItem.isFlipped())

    # ==================================================================================================================

    @abstractmethod
    def key(self) -> str:
        return ''

    @abstractmethod
    def prettyName(self) -> str:
        return ''

    # ==================================================================================================================

    def parent(self) -> typing.Any:
        return self._parent

    # ==================================================================================================================

    def setPosition(self, position: QPointF) -> None:
        self._position = QPointF(position)

    def setRotation(self, rotation: int) -> None:
        self._rotation = (rotation % 4)
        self._updateTransform()

    def setFlipped(self, flipped: bool) -> None:
        self._flipped = flipped
        self._updateTransform()

    def position(self) -> QPointF:
        return self._position

    def rotation(self) -> int:
        return self._rotation

    def isFlipped(self) -> bool:
        return self._flipped

    def transform(self) -> QTransform:
        return self._transform

    def transformInverse(self) -> QTransform:
        return self._transformInverse

    def mapToScene(self, position: QPointF) -> QPointF:
        return self._transform.map(position) + self._position

    def mapRectToScene(self, rect: QRectF) -> QRectF:
        return QRectF(self.mapToScene(rect.topLeft()), self.mapToScene(rect.bottomRight()))

    def mapPolygonToScene(self, polygon: QPolygonF) -> QPolygonF:
        scenePolygon = self._transform.map(polygon)
        scenePolygon.translate(self._position)
        return scenePolygon

    def mapPathToScene(self, path: QPainterPath) -> QPainterPath:
        scenePath = self._transform.map(path)
        scenePath.translate(self._position)
        return scenePath

    def mapFromScene(self, position: QPointF) -> QPointF:
        return self._transformInverse.map(position - self._position)

    def mapRectFromScene(self, rect: QRectF) -> QRectF:
        return QRectF(self.mapFromScene(rect.topLeft()), self.mapFromScene(rect.bottomRight()))

    def mapPolygonFromScene(self, polygon: QPolygonF) -> QPolygonF:
        itemPolygon = QPolygonF(polygon)
        itemPolygon.translate(-self._position)
        return self._transformInverse.map(itemPolygon)

    def mapPathFromScene(self, path: QPainterPath) -> QPainterPath:
        itemPath = QPainterPath(path)
        itemPath.translate(-self._position)
        return self._transformInverse.map(itemPath)

    # ==================================================================================================================

    def addPoint(self, point: DrawingItemPoint) -> None:
        self.insertPoint(len(self._points), point)

    def insertPoint(self, index: int, point: DrawingItemPoint) -> None:
        if (point not in self._points):
            self._points.insert(index, point)
            # pylint: disable-next=W0212
            point._item = self

    def removePoint(self, point: DrawingItemPoint) -> None:
        if (point in self._points):
            self._points.remove(point)
            # pylint: disable-next=W0212
            point._item = None

    def clearPoints(self) -> None:
        while (len(self._points) > 0):
            point = self._points[-1]
            self.removePoint(point)
            del point

    def points(self) -> list[DrawingItemPoint]:
        return self._points

    # ==================================================================================================================

    def setSelected(self, selected: bool) -> None:
        self._selected = selected

    def isSelected(self) -> bool:
        return self._selected

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
        pass

    def property(self, name: str) -> typing.Any:
        pass

    # ==================================================================================================================

    @abstractmethod
    def boundingRect(self) -> QRectF:
        return QRectF()

    def shape(self) -> QPainterPath:
        shape = QPainterPath()
        shape.addRect(self.boundingRect())
        return shape

    def isValid(self) -> bool:
        return True

    # ==================================================================================================================

    @abstractmethod
    def paint(self, painter: QPainter) -> None:
        pass

    # ==================================================================================================================

    def move(self, position: QPointF) -> None:
        self.setPosition(position)

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        point.setPosition(self.mapFromScene(position))

    def rotate(self, center: QPointF) -> None:
        # Calculate new position of item
        difference = self._position - center
        self.setPosition(QPointF(center.x() - difference.y(), center.y() + difference.x()))

        # Update orientation
        self.setRotation(self._rotation + 1)

    def rotateBack(self, center: QPointF) -> None:
        # Calculate new position of item
        difference = self._position - center
        self.setPosition(QPointF(center.x() + difference.y(), center.y() - difference.x()))

        # Update orientation
        self.setRotation(self._rotation - 1)

    def flipHorizontal(self, center: QPointF) -> None:
        # Calculate new position of item
        self.setPosition(QPointF(2 * center.x() - self._position.x(), self._position.y()))

        # Update orientation
        self.setFlipped(not self._flipped)

    def flipVertical(self, center: QPointF) -> None:
        self.rotate(center)
        self.rotate(center)
        self.flipHorizontal(center)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return False

    def canRemovePoints(self) -> bool:
        return False

    def insertNewPoint(self, position: QPointF) -> None:
        pass

    def removeExistingPoint(self, position: QPointF) -> None:
        pass

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        pass

    def placeResizeStartPoint(self) -> DrawingItemPoint | None:
        return None

    def placeResizeEndPoint(self) -> DrawingItemPoint | None:
        return None

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        element.set('translationX', self._toPositionStr(self._position.x()))
        element.set('translationY', self._toPositionStr(self._position.y()))
        if (self.rotation() != 0):
            element.set('rotation', f'{self._rotation}')
        if (self.isFlipped()):
            element.set('flipped', 'true' if (self._flipped) else 'false')

    def readFromXml(self, element: ElementTree.Element) -> None:
        self.setPosition(QPointF(self._fromPositionStr(element.get('translationX', '0')),
                                 self._fromPositionStr(element.get('translationY', '0'))))
        self.setRotation(int(element.get('rotation', '0')))
        self.setFlipped(element.get('flipped', 'false').lower() == 'true')

    # ==================================================================================================================

    def _updateTransform(self) -> None:
        self._transform.reset()
        if (self._flipped):
            self._transform.scale(-1, 1)
        self._transform.rotate(90 * self._rotation)

        self._transformInverse = self._transform.inverted()[0]

    # ==================================================================================================================

    def _strokePath(self, path: QPainterPath, pen: QPen) -> QPainterPath:
        if (path.isEmpty()):
            return path
        ps = QPainterPathStroker()
        ps.setWidth(1E-6 if (pen.widthF() <= 0.0) else pen.widthF())
        ps.setCapStyle(Qt.PenCapStyle.SquareCap)
        ps.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
        return ps.createStroke(path)

    # ==================================================================================================================

    def _snapResizeTo45Degrees(self, point: DrawingItemPoint, position: QPointF, startPoint: DrawingItemPoint,
                               endPoint: DrawingItemPoint) -> QPointF:
        otherPoint = None
        if (point == startPoint):
            otherPoint = endPoint
        elif (point == endPoint):
            otherPoint = startPoint

        if (otherPoint is not None):
            otherPosition = self.mapToScene(otherPoint.position())
            delta = position - otherPosition

            angle = math.atan2(position.y() - otherPosition.y(), position.x() - otherPosition.x())
            targetAngleDegrees = round(angle * 180 / math.pi / 45) * 45
            targetAngleRadians = targetAngleDegrees * math.pi / 180

            length = max(abs(delta.x()), abs(delta.y()))
            if (abs(targetAngleDegrees % 90) == 45):
                length = length * math.sqrt(2)

            return QPointF(otherPosition.x() + length * math.cos(targetAngleRadians),
                           otherPosition.y() + length * math.sin(targetAngleRadians))

        return QPointF(position)

    # ==================================================================================================================

    def _distanceFromPointToLineSegment(self, point: QPointF, line: QLineF) -> float:
        # Let A = line point 0, B = line point 1, and C = point
        dotAbBc = (line.x2() - line.x1()) * (point.x() - line.x2()) + (line.y2() - line.y1()) * (point.y() - line.y2())
        dotBaAc = (line.x1() - line.x2()) * (point.x() - line.x1()) + (line.y1() - line.y2()) * (point.y() - line.y1())
        crossABC = (line.x2() - line.x1()) * (point.y() - line.y1()) - (line.y2() - line.y1()) * (point.x() - line.x1())
        distanceAB = math.sqrt((line.x2() - line.x1()) * (line.x2() - line.x1()) + (line.y2() - line.y1()) * (line.y2() - line.y1()))   # noqa
        distanceAC = math.sqrt((point.x() - line.x1()) * (point.x() - line.x1()) + (point.y() - line.y1()) * (point.y() - line.y1()))   # noqa
        distanceBC = math.sqrt((point.x() - line.x2()) * (point.x() - line.x2()) + (point.y() - line.y2()) * (point.y() - line.y2()))   # noqa

        if (distanceAB != 0):
            if (dotAbBc > 0):
                return distanceBC
            if (dotBaAc > 0):
                return distanceAC
            return abs(crossABC) / distanceAB
        return 1.0E12

    def _pointNearest(self, position: QPointF) -> DrawingItemPoint | None:
        if (len(self._points) > 0):
            nearestPoint = self._points[0]

            vec = nearestPoint.position() - position
            minimumDistanceSquared = vec.x() * vec.x() + vec.y() * vec.y()

            for point in self._points[1:]:
                vec = point.position() - position
                distanceSquared = vec.x() * vec.x() + vec.y() * vec.y()
                if (distanceSquared < minimumDistanceSquared):
                    nearestPoint = point
                    minimumDistanceSquared = distanceSquared

            return nearestPoint
        return None

    # ==================================================================================================================

    @staticmethod
    def copyItems(items: list['DrawingItem']) -> list['DrawingItem']:
        copiedItems: list[DrawingItem] = []

        # Copy items
        for item in items:
            copiedItems.append(copy.copy(item))

        # Maintain connections to other items in this list
        for itemIndex, item in enumerate(items):
            for pointIndex, point in enumerate(item.points()):
                for targetPoint in point.connections():
                    targetItem = targetPoint.item()
                    if (isinstance(targetItem, DrawingItem) and targetItem in items):
                        # There is a connection here that must be maintained in the copied items
                        targetItemIndex = items.index(targetItem)
                        targetItemPointIndex = targetItem.points().index(targetPoint)

                        copiedItem = copiedItems[itemIndex]
                        copiedItemPoint = copiedItem.points()[pointIndex]

                        copiedTargetItem = copiedItems[targetItemIndex]
                        copiedTargetItemPoint = copiedTargetItem.points()[targetItemPointIndex]

                        # Create connection
                        copiedItemPoint.addConnection(copiedTargetItemPoint)
                        copiedTargetItemPoint.addConnection(copiedItemPoint)

        return copiedItems

    # ==================================================================================================================

    @staticmethod
    def registerFactoryItem(item: 'DrawingItem') -> None:
        # Assumes that the item's key is unique and not already registered
        DrawingItem._factoryItems.append(item)

    @staticmethod
    def createItemFromFactory(key: str) -> 'DrawingItem | None':
        for item in DrawingItem._factoryItems:
            if (key == item.key()):
                return copy.copy(item)
        for item in DrawingItem._factoryItems:
            if (key == item.prettyName()):
                return copy.copy(item)
        return None

    # ==================================================================================================================

    @staticmethod
    def writeItemsToXml(element: ElementTree.Element, items: list['DrawingItem']) -> None:
        for item in items:
            itemElement = ElementTree.SubElement(element, item.key())
            item.writeToXml(itemElement)

    @staticmethod
    def readItemsFromXml(element: ElementTree.Element) -> list['DrawingItem']:
        items: list[DrawingItem] = []

        # Read items from XML
        for itemElement in element:
            item = DrawingItem.createItemFromFactory(itemElement.tag)
            if (item is not None):
                item.readFromXml(itemElement)
                items.append(item)

        # Connect items together
        for itemIndex, item in enumerate(items):
            for otherItem in items[itemIndex+1:]:
                for point in item.points():
                    for otherPoint in otherItem.points():
                        shouldConnect = (point.isConnectionPoint() and otherPoint.isConnectionPoint() and
                                         (point.isFree() or otherPoint.isFree()))
                        if (shouldConnect):
                            vec = item.mapToScene(point.position())
                            vec = vec - otherItem.mapToScene(otherPoint.position())
                            distance = math.sqrt(vec.x() * vec.x() + vec.y() * vec.y())
                            if (distance <= 0.01):
                                point.addConnection(otherPoint)
                                otherPoint.addConnection(point)

        return items
