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
from enum import IntEnum
from typing import Any
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPainterPathStroker, QPen, QPolygonF, QTransform
from .odgitempoint import OdgItemPoint
from .odgitemstyle import OdgItemStyle
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

        self._style: OdgItemStyle = OdgItemStyle(name)

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

    def style(self) -> OdgItemStyle:
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

    def writeStyles(self, writer: OdgWriter) -> None:
        if (isinstance(self._style, OdgItemStyle)):
            writer.writeStartElement('style:style')
            self._style.write(writer)
            writer.writeEndElement()

    def write(self, writer: OdgWriter) -> None:
        if (self._name != ''):
            writer.writeAttribute('draw:name', self._name)
        writer.writeAttribute('draw:style-name', self._style.name())

        transformStr = ''
        if (self._rotation != 0):
            transformStr = f'{transformStr} rotate({self._rotation * (-math.pi / 2)})'
        if (self._flipped):
            transformStr = f'{transformStr} scale(-1, 1)'
        if (self._position.x() != 0 or self._position.y() != 0):
            xStr = writer.xCoordinateToString(self._position.x())
            yStr = writer.yCoordinateToString(self._position.y())
            transformStr = f'{transformStr} translate({xStr}, {yStr})'
        transformStr = transformStr.strip()
        if (transformStr != ''):
            writer.writeAttribute('draw:transform', transformStr)

    def read(self, reader: OdgReader, automaticItemStyles: list[OdgItemStyle]) -> None:
        self._name = ''
        self._position = QPointF()
        self._rotation = 0
        self._flipped = False
        self._transform = QTransform()
        self._transformInverse = QTransform()
        self._style.clear()
        self._selected = False

        attributes = reader.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'draw:name':
                    self.setName(attr.value())
                case 'draw:style-name':
                    styleName = attr.value()
                    for style in automaticItemStyles:
                        if (style.name() == styleName):
                            self.style().copyFromStyle(style)
                            break
                case 'draw:transform':
                    try:
                        transformStr = attr.value()
                        for token in transformStr.split(')'):
                            strippedToken = token.strip()
                            if (strippedToken.startswith('translate(')):
                                coords = strippedToken[10:].split(',')
                                self.setPosition(QPointF(self.position().x() + reader.xCoordinateFromString(coords[0]),
                                                         self.position().y() + reader.yCoordinateFromString(coords[1])))
                            elif (strippedToken.startswith('scale(')):
                                self.setFlipped(not self.isFlipped())
                            elif (strippedToken.startswith('rotate(')):
                                self.setRotation(self.rotation() + int(float(strippedToken[7:]) / (-math.pi / 2)))
                    except (KeyError, ValueError):
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
                copiedItem = copy.copy(item)
                copiedItem.setName(newItem.name())
                copiedItems.append(copiedItem)

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

    # ==================================================================================================================

    @staticmethod
    def writeItems(writer: OdgWriter, items: 'list[OdgItem]') -> None:
        for item in items:
            writer.writeStartElement(item.qualifiedType())
            item.write(writer)
            writer.writeEndElement()

    @staticmethod
    def readItems(reader: OdgReader, automaticItemStyles: list[OdgItemStyle]) -> 'list[OdgItem]':
        items: list[OdgItem] = []
        newItem: OdgItem | None = None

        # Read items from XML
        while (reader.readNextStartElement()):
            qualifiedName = reader.qualifiedName()
            newItem = None
            for item in OdgItem._factoryItems:
                if (qualifiedName == item.qualifiedType()):
                    newItem = OdgItem.createItem(item.type(), None)
                    break

            if (isinstance(newItem, OdgItem)):
                newItem.read(reader, automaticItemStyles)
                items.append(newItem)
            else:
                reader.skipCurrentElement()

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


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgRectItemBase(OdgItem):
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

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._rect: QRectF = QRectF()

        for _ in range(8):
            self.addPoint(OdgItemPoint(QPointF(0, 0), OdgItemPoint.Type.Control))

    # ==================================================================================================================

    def setRect(self, rect: QRectF) -> None:
        if (rect.width() >= 0 and rect.height() >= 0):
            self._rect = QRectF(rect)

            # Put the item's position at the center of the rect
            offset = rect.center()
            self.setPosition(self.mapToScene(offset))
            self._rect.translate(-offset)

            # Set point positions to match self._rect
            if (len(self._points) >= 8):
                topLeft = self._rect.topLeft()
                center = self._rect.center()
                bottomRight = self._rect.bottomRight()

                self._points[OdgRectItemBase.PointIndex.TopLeft].setPosition(topLeft)
                self._points[OdgRectItemBase.PointIndex.TopMiddle].setPosition(QPointF(center.x(), topLeft.y()))
                self._points[OdgRectItemBase.PointIndex.TopRight].setPosition(QPointF(bottomRight.x(), topLeft.y()))
                self._points[OdgRectItemBase.PointIndex.MiddleRight].setPosition(QPointF(bottomRight.x(), center.y()))
                self._points[OdgRectItemBase.PointIndex.BottomRight].setPosition(bottomRight)
                self._points[OdgRectItemBase.PointIndex.BottomMiddle].setPosition(QPointF(center.x(), bottomRight.y()))
                self._points[OdgRectItemBase.PointIndex.BottomLeft].setPosition(QPointF(topLeft.x(), bottomRight.y()))
                self._points[OdgRectItemBase.PointIndex.MiddleLeft].setPosition(QPointF(topLeft.x(), center.y()))

    def rect(self) -> QRectF:
        return self._rect

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        rect = QRectF(self._rect.normalized())

        # Adjust for pen width
        if (self.style().lookupPenStyle() != Qt.PenStyle.NoPen):
            halfPenWidth = self.style().lookupPenWidth() / 2
            rect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)

        return rect

    def isValid(self) -> bool:
        return (self._rect.width() != 0 or self._rect.height() != 0)

    # ==================================================================================================================

    def resize(self, point: OdgItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        if (point in self._points):
            if (snapTo45Degrees and len(self._points) >= 8):
                position = self._snapResizeTo45Degrees(point, position,
                                                       self._points[OdgRectItemBase.PointIndex.TopLeft],
                                                       self._points[OdgRectItemBase.PointIndex.BottomRight])
            position = self.mapFromScene(position)

            rect = QRectF(self._rect)
            pointIndex = self._points.index(point)

            # Ensure that rect.width() >= 0
            if (pointIndex in (OdgRectItemBase.PointIndex.TopLeft, OdgRectItemBase.PointIndex.MiddleLeft,
                               OdgRectItemBase.PointIndex.BottomLeft)):
                if (position.x() > rect.right()):
                    rect.setLeft(rect.right())
                else:
                    rect.setLeft(position.x())
            elif (pointIndex in (OdgRectItemBase.PointIndex.TopRight, OdgRectItemBase.PointIndex.MiddleRight,
                                 OdgRectItemBase.PointIndex.BottomRight)):
                if (position.x() < rect.left()):
                    rect.setRight(rect.left())
                else:
                    rect.setRight(position.x())

            # Ensure that rect.height() >= 0
            if (pointIndex in (OdgRectItemBase.PointIndex.TopLeft, OdgRectItemBase.PointIndex.TopMiddle,
                               OdgRectItemBase.PointIndex.TopRight)):
                if (position.y() > rect.bottom()):
                    rect.setTop(rect.bottom())
                else:
                    rect.setTop(position.y())
            elif (pointIndex in (OdgRectItemBase.PointIndex.BottomLeft, OdgRectItemBase.PointIndex.BottomMiddle,
                                 OdgRectItemBase.PointIndex.BottomRight)):
                if (position.y() < rect.top()):
                    rect.setBottom(rect.top())
                else:
                    rect.setBottom(position.y())

            self.setRect(rect)

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self.setRect(QRectF(self._rect.left() * scale, self._rect.top() * scale,
                            self._rect.width() * scale, self._rect.height() * scale))

    # ==================================================================================================================

    def placeCreateEvent(self, sceneRect: QRectF, grid: float) -> None:
        size = 8 * grid
        if (size <= 0):
            size = sceneRect.width() / 40
        self.setRect(QRectF(-size, -size / 2, 2 * size, size))

    def placeResizeStartPoint(self) -> OdgItemPoint | None:
        return self._points[OdgRectItemBase.PointIndex.TopLeft] if (len(self._points) >= 8) else None

    def placeResizeEndPoint(self) -> OdgItemPoint | None:
        return self._points[OdgRectItemBase.PointIndex.BottomRight] if (len(self._points) >= 8) else None

    # ==================================================================================================================

    def write(self, writer: OdgWriter) -> None:
        super().write(writer)

        writer.writeLengthAttribute('svg:x', self._rect.left())
        writer.writeLengthAttribute('svg:y', self._rect.top())
        writer.writeLengthAttribute('svg:width', self._rect.width())
        writer.writeLengthAttribute('svg:height', self._rect.height())

    def read(self, reader: OdgReader, automaticItemStyles: list[OdgItemStyle]) -> None:
        super().read(reader, automaticItemStyles)

        left, top, width, height = (0.0, 0.0, 0.0, 0.0)
        attributes = reader.attributes()
        for i in range(attributes.count()):
            attr = attributes.at(i)
            match (attr.qualifiedName()):
                case 'svg:x':
                    left = reader.lengthFromString(attr.value())
                case 'svg:y':
                    top = reader.lengthFromString(attr.value())
                case 'svg:width':
                    width = reader.lengthFromString(attr.value())
                case 'svg:height':
                    height = reader.lengthFromString(attr.value())
        self.setRect(QRectF(left, top, width, height))
