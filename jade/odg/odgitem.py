# odgitem.py
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

import copy
import math
from abc import ABC, abstractmethod
from typing import Any
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPainterPathStroker, QPen, QPolygonF, QTransform
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgItemStyle, OdgItemAutomaticStyle
from .odgreader import OdgReader
from .odgwriter import OdgWriter


class OdgItem(ABC):
    def __init__(self, name: str) -> None:
        self._parent: Any = None

        self._name: str = name

        self._position: QPointF = QPointF()
        self._rotation: int = 0
        self._flipped: bool = False
        self._transform: QTransform = QTransform()
        self._transformInverse: QTransform = QTransform()

        self._points: list[OdgItemPoint] = []

        self._style: OdgItemAutomaticStyle = OdgItemAutomaticStyle(name)

        self._selected: bool = False

    def __del__(self) -> None:
        self.clearPoints()
        del self._style

    # ==================================================================================================================

    @abstractmethod
    def type(self) -> str:
        return ''

    @abstractmethod
    def prettyType(self) -> str:
        return ''

    @abstractmethod
    def qualifiedType(self) -> str:
        return ''

    # ==================================================================================================================

    def parent(self) -> Any:
        return self._parent

    # ==================================================================================================================

    def setName(self, name: str) -> None:
        self._name = name
        self._style.setName(name)

    def name(self) -> str:
        return self._name

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

    def addPoint(self, point: OdgItemPoint) -> None:
        self.insertPoint(len(self._points), point)

    def insertPoint(self, index: int, point: OdgItemPoint) -> None:
        if (point not in self._points):
            self._points.insert(index, point)
            # pylint: disable-next=W0212
            point._item = self

    def removePoint(self, point: OdgItemPoint) -> None:
        if (point in self._points):
            self._points.remove(point)
            # pylint: disable-next=W0212
            point._item = None

    def clearPoints(self) -> None:
        while (len(self._points) > 0):
            point = self._points[-1]
            self.removePoint(point)
            del point

    def points(self) -> list[OdgItemPoint]:
        return self._points

    # ==================================================================================================================

    def copyStyle(self, other: OdgItemAutomaticStyle) -> None:
        self._style.setParent(other.parent())

        self._style.setPenStyle(other.penStyle())
        self._style.setPenWidth(other.penWidth())
        self._style.setPenColor(other.penColor())
        self._style.setPenCapStyle(other.penCapStyle())
        self._style.setPenJoinStyle(other.penJoinStyle())
        self._style.setBrushColor(other.brushColor())

        self._style.setStartMarkerStyle(other.startMarkerStyle())
        self._style.setStartMarkerSize(other.startMarkerSize())
        self._style.setEndMarkerStyle(other.endMarkerStyle())
        self._style.setEndMarkerSize(other.endMarkerSize())

    def style(self) -> OdgItemAutomaticStyle:
        return self._style

    # ==================================================================================================================

    def setSelected(self, selected: bool) -> None:
        self._selected = selected

    def isSelected(self) -> bool:
        return self._selected

    # ==================================================================================================================

    def setProperty(self, name: str, value: Any) -> None:
        pass

    def property(self, name: str) -> Any:
        return None

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

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        point.setPosition(self.mapFromScene(position))

    def rotate(self, center: QPointF) -> None:
        self.setPosition(self._rotatePoint(self._position, center))
        self.setRotation(self._rotation + 1)

    def rotateBack(self, center: QPointF) -> None:
        self.setPosition(self._rotateBackPoint(self._position, center))
        self.setRotation(self._rotation - 1)

    def flipHorizontal(self, center: QPointF) -> None:
        self.setPosition(self._flipPointHorizontal(self._position, center))
        self.setFlipped(not self._flipped)

    def flipVertical(self, center: QPointF) -> None:
        self.rotate(center)
        self.rotate(center)
        self.flipHorizontal(center)

    def scale(self, scale: float) -> None:
        self._position = QPointF(self._position.x() * scale, self._position.y() * scale)
        for point in self._points:
            point.setPosition(QPointF(point.position().x() * scale, point.position().y() * scale))
        self._style.scale(scale)

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

    def placeResizeStartPoint(self) -> OdgItemPoint | None:
        return None

    def placeResizeEndPoint(self) -> OdgItemPoint | None:
        return None

    # ==================================================================================================================

    @abstractmethod
    def write(self, writer: OdgWriter) -> None:
        pass

    @abstractmethod
    def read(self, reader: OdgReader) -> None:
        pass

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

    def _snapResizeTo45Degrees(self, point: OdgItemPoint, position: QPointF, startPoint: OdgItemPoint,
                               endPoint: OdgItemPoint) -> QPointF:
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

    def _rotatePoint(self, point: QPointF, center: QPointF) -> QPointF:
        difference = point - center
        return QPointF(center.x() - difference.y(), center.y() + difference.x())

    def _rotateBackPoint(self, point: QPointF, center: QPointF) -> QPointF:
        difference = point - center
        return QPointF(center.x() + difference.y(), center.y() - difference.x())

    def _flipPointHorizontal(self, point: QPointF, center: QPointF) -> QPointF:
        return QPointF(2 * center.x() - point.x(), point.y())

    def _flipPointVertical(self, point: QPointF, center: QPointF) -> QPointF:
        return QPointF(point.x(), 2 * center.y() - point.y())

    # ==================================================================================================================

    def _distanceFromPointToLineSegment(self, point: QPointF, line: QLineF) -> float:
        # Let A = line.p1(), B = line.p2(), and C = point
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

    def _pointNearest(self, position: QPointF) -> OdgItemPoint | None:
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

    _factoryItems: 'list[OdgItem]' = []
    _factoryNewItemCount: 'dict[OdgItem, int]' = {}

    @staticmethod
    def registerFactoryItem(item: 'OdgItem') -> None:
        # Assumes that the item has a unique OdgItem.type when compared to all previously registered items
        OdgItem._factoryItems.append(item)
        OdgItem._factoryNewItemCount[item] = 0

    @staticmethod
    def resetFactoryCounts() -> None:
        for item in OdgItem._factoryItems:
            OdgItem._factoryNewItemCount[item] = 0

    @staticmethod
    def clearFactoryItems() -> None:
        OdgItem._factoryNewItemCount = {}
        del OdgItem._factoryItems[:]

    # ==================================================================================================================

    @staticmethod
    def createItem(typeKey: str, parentStyle: OdgItemStyle | None) -> 'OdgItem | None':
        for item in OdgItem._factoryItems:
            if (typeKey == item.type()):
                newItem = copy.copy(item)

                count = OdgItem._factoryNewItemCount[item] + 1
                newItem.setName(f'{item.prettyType()} {count}')
                OdgItem._factoryNewItemCount[item] = count

                newItem.style().setParent(parentStyle)

                return newItem
        return None

    @staticmethod
    def copyItems(items: 'list[OdgItem]') -> 'list[OdgItem]':
        copiedItems: list[OdgItem] = []

        # Copy items
        for item in items:
            newItem = OdgItem.createItem(item.type(), item.style().parent())
            if (isinstance(newItem, OdgItem)):
                copiedItems.append(newItem)

        # Maintain connections to other items in this list
        for itemIndex, item in enumerate(items):
            for pointIndex, point in enumerate(item.points()):
                for targetPoint in point.connections():
                    targetItem = targetPoint.item()
                    if (isinstance(targetItem, OdgItem) and targetItem in items):
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
