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

import math
import typing
from enum import Enum
from xml.etree import ElementTree
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPainterPathStroker, QPen, QPolygonF, QTransform
from .drawingarrow import DrawingArrow
from .drawingitempoint import DrawingItemPoint


class DrawingItem:
    class PlaceType(Enum):
        PlaceByMouseRelease = 0
        PlaceByMousePressAndRelease = 1

    # ==================================================================================================================

    _factoryItems: list['DrawingItem'] = []
    _defaultProperties: dict[str, typing.Any] = {}

    def __init__(self) -> None:
        self._parent: typing.Any = None

        self._position: QPointF = QPointF()
        self._rotation: int = 0
        self._flipped: bool = False
        self._transform: QTransform = QTransform()
        self._transformInverse: QTransform = QTransform()

        self._points: list[DrawingItemPoint] = []

        self._placeType: DrawingItem.PlaceType = DrawingItem.PlaceType.PlaceByMouseRelease

        self._selected: bool = False

    def __del__(self) -> None:
        # Clear points
        while (len(self._points) > 0):
            point = self._points[-1]
            self.removePoint(point)
            del point

    # ==================================================================================================================

    def key(self) -> str:
        return ''

    def clone(self) -> 'DrawingItem':
        clonedItem = DrawingItem()
        clonedItem.copyBaseClassValues(self)
        return clonedItem

    def copyBaseClassValues(self, otherItem: 'DrawingItem'):
        self.setPosition(QPointF(otherItem.position()))
        self.setRotation(otherItem.rotation())
        self.setFlipped(otherItem.isFlipped())
        self.setPlaceType(otherItem.placeType())

    # ==================================================================================================================

    def parent(self) -> typing.Any:
        return self._parent

    # ==================================================================================================================

    def setPosition(self, position: QPointF) -> None:
        self._position = position

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

    def _updateTransform(self) -> None:
        self._transform.reset()
        if (self._flipped):
            self._transform.scale(-1, 1)
        self._transform.rotate(90 * self._rotation)

        self._transformInverse = self._transform.inverted()[0]

    def transform(self) -> QTransform:
        return self._transform

    def transformInverse(self) -> QTransform:
        return self._transformInverse

    def mapToScene(self, position: QPointF) -> QPointF:
        return self._transform.map(position) + self._position           # type: ignore

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
        return self._transformInverse.map(position - self._position)    # type: ignore

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
            point._item = self

    def removePoint(self, point: DrawingItemPoint) -> None:
        if (point in self._points):
            self._points.remove(point)
            point._item = None

    def points(self) -> list[DrawingItemPoint]:
        return self._points

    # ==================================================================================================================

    def setPlaceType(self, type: 'DrawingItem.PlaceType') -> None:
        self._placeType = type

    def placeType(self) -> 'DrawingItem.PlaceType':
        return self._placeType

    # ==================================================================================================================

    def setSelected(self, selected: bool) -> None:
        self._selected = selected

    def isSelected(self) -> bool:
        return self._selected

    # ==================================================================================================================

    def setProperty(self, name: str, value: typing.Any) -> None:
        pass

    def property(self, name: str) -> typing.Any:
        return None

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        return QRectF()

    def shape(self) -> QPainterPath:
        shape = QPainterPath()
        shape.addRect(self.boundingRect())
        return shape

    def centerPosition(self) -> QPointF:
        return self.boundingRect().center()

    def isValid(self) -> bool:
        return True

    # ==================================================================================================================

    def paint(self, painter: QPainter) -> None:
        pass

    # ==================================================================================================================

    def move(self, position: QPointF) -> None:
        self.setPosition(position)

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        point.setPosition(self.mapFromScene(position))

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        return None

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        return None

    # ==================================================================================================================

    def rotate(self, position: QPointF) -> None:
        # Calculate new position of item
        difference = QPointF(self._position - position)     # type: ignore
        self.setPosition(QPointF(position.x() - difference.y(), position.y() + difference.x()))

        # Update orientation
        self.setRotation(self._rotation + 1)

    def rotateBack(self, position: QPointF) -> None:
        # Calculate new position of item
        difference = QPointF(self._position - position)     # type: ignore
        self.setPosition(QPointF(position.x() + difference.y(), position.y() - difference.x()))

        # Update orientation
        self.setRotation(self._rotation - 1)

    def flipHorizontal(self, position: QPointF) -> None:
        # Calculate new position of item
        self.setPosition(QPointF(2 * position.x() - self._position.x(), self._position.y()))

        # Update orientation
        self.setFlipped(not self._flipped)

    def flipVertical(self, position: QPointF) -> None:
        self.rotate(position)
        self.rotate(position)
        self.flipHorizontal(position)

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        self._position = QPointF(self._position.x() * scale, self._position.y() * scale)

    # ==================================================================================================================

    def canInsertPoints(self) -> bool:
        return False

    def canRemovePoints(self) -> bool:
        return False

    def insertNewPoint(self, position: QPointF) -> DrawingItemPoint | None:
        return None

    def removeExistingPoint(self, position: QPointF) -> tuple[DrawingItemPoint | None, int]:
        return (None, -1)

    # ==================================================================================================================

    def writeToXml(self, element: ElementTree.Element) -> None:
        # Write position, rotation, and flipped
        self.writeFloatAttribute(element, 'translationX', self._position.x())
        self.writeFloatAttribute(element, 'translationY', self._position.y())
        self.writeIntAttribute(element, 'rotation', self._rotation, 0)
        self.writeBoolAttribute(element, 'flipped', self._flipped, False)

    def readFromXml(self, element: ElementTree.Element) -> None:
        # Read position, rotation, and flipped
        self.setPosition(QPointF(self.readFloatAttribute(element, 'translationX', 0),
                                 self.readFloatAttribute(element, 'translationY', 0)))
        self.setRotation(int(self.readIntAttribute(element, 'rotation', 0) / 90))
        self.setFlipped(self.readBoolAttribute(element, 'flipped', False))

    # ==================================================================================================================

    @staticmethod
    def writeBrushToXml(element: ElementTree.Element, name: str, brush: QBrush) -> None:
        DrawingItem.writeColorAttribute(element, f'{name}Color', brush.color())

    @staticmethod
    def writePenToXml(element: ElementTree.Element, name: str, pen: QPen) -> None:
        DrawingItem.writeBrushToXml(element, name, pen.brush())
        DrawingItem.writeFloatAttribute(element, f'{name}Width', pen.widthF())

        penStyle = 'solid'
        match (pen.style()):
            case Qt.PenStyle.NoPen:
                penStyle = 'none'
            case Qt.PenStyle.DashLine:
                penStyle = 'dash'
            case Qt.PenStyle.DotLine:
                penStyle = 'dot'
            case Qt.PenStyle.DashDotLine:
                penStyle = '"dash-dot'
            case Qt.PenStyle.DashDotDotLine:
                penStyle = 'dash-dot-dot'
        DrawingItem.writeStrAttribute(element, f'{name}Style', penStyle)

    @staticmethod
    def writeArrowToXml(element: ElementTree.Element, name: str, arrow: DrawingArrow) -> None:
        DrawingItem.writeStrAttribute(element, f'{name}Style', DrawingArrow.styleToString(arrow.style()), 'none')
        DrawingItem.writeFloatAttribute(element, f'{name}Size', arrow.size(), 0)

    @staticmethod
    def writeFontToXml(element: ElementTree.Element, name: str, font: QFont) -> None:
        DrawingItem.writeStrAttribute(element, f'{name}Name', font.family())
        DrawingItem.writeFloatAttribute(element, f'{name}Size', font.pointSizeF())
        DrawingItem.writeBoolAttribute(element, f'{name}Bold', font.bold(), False)
        DrawingItem.writeBoolAttribute(element, f'{name}Italic', font.italic(), False)
        DrawingItem.writeBoolAttribute(element, f'{name}Underline', font.underline(), False)
        DrawingItem.writeBoolAttribute(element, f'{name}StrikeThrough', font.strikeOut(), False)

    @staticmethod
    def writeAlignmentToXml(element: ElementTree.Element, name: str, alignment: Qt.AlignmentFlag) -> None:
        hAlignment = (alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
        hAlignmentStr = 'left'
        if (hAlignment & Qt.AlignmentFlag.AlignHCenter):
            hAlignmentStr = 'center'
        elif (hAlignment & Qt.AlignmentFlag.AlignRight):
            hAlignmentStr = 'right'
        DrawingItem.writeStrAttribute(element, f'{name}Horizontal', hAlignmentStr, 'left')

        vAlignment = (alignment & Qt.AlignmentFlag.AlignVertical_Mask)
        vAlignmentStr = 'top'
        if (vAlignment & Qt.AlignmentFlag.AlignVCenter):
            vAlignmentStr = 'center'
        elif (vAlignment & Qt.AlignmentFlag.AlignBottom):
            vAlignmentStr = 'bottom'
        DrawingItem.writeStrAttribute(element, f'{name}Vertical', vAlignmentStr, 'top')

    @staticmethod
    def readBrushFromXml(element: ElementTree.Element, name: str) -> QBrush:
        return QBrush(DrawingItem.readColorAttribute(element, f'{name}Color'))

    @staticmethod
    def readPenFromXml(element: ElementTree.Element, name: str) -> QPen:
        penStyle = Qt.PenStyle.SolidLine
        match (DrawingItem.readStrAttribute(element, f'{name}Style', 'solid').lower()):
            case 'none':
                penStyle = Qt.PenStyle.NoPen
            case 'dash':
                penStyle = Qt.PenStyle.DashLine
            case 'dot':
                penStyle = Qt.PenStyle.DotLine
            case 'dash-dot':
                penStyle = Qt.PenStyle.DashDotLine
            case 'dash-dot-dot':
                penStyle = Qt.PenStyle.DashDotDotLine

        return QPen(DrawingItem.readBrushFromXml(element, name),
                    DrawingItem.readFloatAttribute(element, f'{name}Width', 0),
                    penStyle, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    @staticmethod
    def readArrowFromXml(element: ElementTree.Element, name: str) -> DrawingArrow:
        return DrawingArrow(
            DrawingArrow.styleFromString(DrawingItem.readStrAttribute(element, f'{name}Style', 'none')),
            DrawingItem.readFloatAttribute(element, f'{name}Size', 0))

    @staticmethod
    def readFontFromXml(element: ElementTree.Element, name: str) -> QFont:
        font = QFont()
        font.setFamily(DrawingItem.readStrAttribute(element, f'{name}Name', font.family()))
        font.setPointSizeF(DrawingItem.readFloatAttribute(element, f'{name}Size', 0))
        font.setBold(DrawingItem.readBoolAttribute(element, f'{name}Bold', False))
        font.setItalic(DrawingItem.readBoolAttribute(element, f'{name}Italic', False))
        font.setUnderline(DrawingItem.readBoolAttribute(element, f'{name}Underline', False))
        font.setStrikeOut(DrawingItem.readBoolAttribute(element, f'{name}StrikeThrough', False))
        return font

    @staticmethod
    def readAlignmentFromXml(element: ElementTree.Element, name: str) -> Qt.AlignmentFlag:
        hAlignmentStr = DrawingItem.readStrAttribute(element, f'{name}Horizontal', '').lower()
        hAlignment = Qt.AlignmentFlag.AlignLeft
        if (hAlignmentStr == 'center'):
            hAlignment = Qt.AlignmentFlag.AlignHCenter
        elif (hAlignmentStr == 'right'):
            hAlignment = Qt.AlignmentFlag.AlignRight

        vAlignmentStr = DrawingItem.readStrAttribute(element, f'{name}Vertical', '').lower()
        vAlignment = Qt.AlignmentFlag.AlignTop
        if (vAlignmentStr == 'center'):
            vAlignment = Qt.AlignmentFlag.AlignVCenter
        elif (vAlignmentStr == 'bottom'):
            vAlignment = Qt.AlignmentFlag.AlignBottom

        return (hAlignment | vAlignment)

    # ==================================================================================================================

    @staticmethod
    def writeStrAttribute(element: ElementTree.Element, name: str, value: str, defaultValue: str | None = None) -> None:
        if (value != defaultValue):
            element.set(name, value)

    @staticmethod
    def writeFloatAttribute(element: ElementTree.Element, name: str, value: float,
                            defaultValue: float | None = None) -> None:
        if (value != defaultValue):
            element.set(name, f'{value}')

    @staticmethod
    def writeIntAttribute(element: ElementTree.Element, name: str, value: int, defaultValue: int | None = None) -> None:
        if (value != defaultValue):
            element.set(name, f'{value}')

    @staticmethod
    def writeBoolAttribute(element: ElementTree.Element, name: str, value: bool,
                           defaultValue: bool | None = None) -> None:
        if (value != defaultValue):
            element.set(name, 'true' if value else 'false')

    @staticmethod
    def writeColorAttribute(element: ElementTree.Element, name: str, color: QColor) -> None:
        if (color != QColor(0, 0, 0)):
            if (color.alpha() == 255):
                element.set(name, f'#{color.red():02X}{color.green():02X}{color.blue():02X}')
            else:
                element.set(name, f'#{color.red():02X}{color.green():02X}{color.blue():02X}{color.alpha():02X}')

    @staticmethod
    def writePointsAttribute(element: ElementTree.Element, name: str, points: QPolygonF) -> None:
        pointsStr = ''
        for index in range(points.size()):
            point = points[index]
            pointsStr = pointsStr + f'{point.x()},{point.y()} '
        element.set(name, pointsStr.strip())

    @staticmethod
    def readStrAttribute(element: ElementTree.Element, name: str, defaultValue: str) -> str:
        try:
            return element.attrib[name]
        except Exception:
            pass
        return defaultValue

    @staticmethod
    def readFloatAttribute(element: ElementTree.Element, name: str, defaultValue: float) -> float:
        try:
            return float(element.attrib[name])
        except Exception:
            pass
        return defaultValue

    @staticmethod
    def readIntAttribute(element: ElementTree.Element, name: str, defaultValue: int) -> int:
        try:
            return int(element.attrib[name])
        except Exception:
            pass
        return defaultValue

    @staticmethod
    def readBoolAttribute(element: ElementTree.Element, name: str, defaultValue: bool) -> bool:
        try:
            return (element.attrib[name].lower() == 'true')
        except Exception:
            pass
        return defaultValue

    @staticmethod
    def readColorAttribute(element: ElementTree.Element, name: str) -> QColor:
        try:
            colorStr = element.attrib[name]
            if (len(colorStr) == 9):
                return QColor(int(colorStr[1:3], 16), int(colorStr[3:5], 16), int(colorStr[5:7], 16),
                              int(colorStr[7:9], 16))
            return QColor(int(colorStr[1:3], 16), int(colorStr[3:5], 16), int(colorStr[5:7], 16))
        except Exception:
            pass
        return QColor(0, 0, 0)

    @staticmethod
    def readPointsAttribute(element: ElementTree.Element, name: str) -> QPolygonF:
        try:
            points = QPolygonF()
            for token in element.attrib[name].split(' '):
                coords = token.split(',')
                points.append(QPointF(float(coords[0]), float(coords[1])))
            return points
        except Exception:
            pass
        return QPolygonF()

    # ==================================================================================================================

    @staticmethod
    def strokePath(path: QPainterPath, pen: QPen) -> QPainterPath:
        if (path.isEmpty()):
            return path
        ps = QPainterPathStroker()
        ps.setWidth(1E-6 if (pen.widthF() <= 0.0) else pen.widthF())
        ps.setCapStyle(Qt.PenCapStyle.SquareCap)
        ps.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
        return ps.createStroke(path)

    # ==================================================================================================================

    @staticmethod
    def cloneItems(items: list['DrawingItem']) -> list['DrawingItem']:
        clonedItems = []

        # Clone items
        for item in items:
            clonedItems.append(item.clone())

        # Maintain connections to other items in this list
        for itemIndex, item in enumerate(items):
            for pointIndex, point in enumerate(item.points()):
                for targetPoint in point.connections():
                    targetItem = point.item()
                    if (targetItem in items):
                        # There is a connection here that must be maintained in the cloned items
                        clonedPoint = clonedItems[itemIndex].points()[pointIndex]
                        clonedTargetItem = clonedItems[items.index(targetItem)]
                        clonedTargetPoint = clonedTargetItem.points()[targetItem.points().index(targetPoint)]

                        clonedPoint.addConnection(clonedTargetPoint)
                        clonedTargetPoint.addConnection(clonedPoint)

        return clonedItems

    # ==================================================================================================================

    @staticmethod
    def register(item: 'DrawingItem') -> None:
        # Assumes that the item's key is unique and not already registered to DrawingItem
        DrawingItem._factoryItems.append(item)

    @staticmethod
    def create(key: str) -> 'DrawingItem | None':
        for item in DrawingItem._factoryItems:
            if (key == item.key()):
                clonedItem = item.clone()
                for name, value in DrawingItem._defaultProperties.items():
                    clonedItem.setProperty(name, value)
                return clonedItem
        return None

    # ==================================================================================================================

    @staticmethod
    def writeItemsToString(items: list['DrawingItem']) -> str:
        itemsElement = ElementTree.Element('items')
        DrawingItem.writeItemsToXml(itemsElement, items)
        return ElementTree.tostring(itemsElement, encoding='unicode')

    @staticmethod
    def readItemsFromString(text: str) -> list['DrawingItem']:
        rootElement = ElementTree.fromstring(text)
        if (rootElement.tag == 'items'):
            return DrawingItem.readItemsFromXml(rootElement)
        return []

    # ==================================================================================================================

    @staticmethod
    def writeItemsToXml(element: ElementTree.Element, items: list['DrawingItem']) -> None:
        for item in items:
            itemElement = ElementTree.SubElement(element, item.key())
            item.writeToXml(itemElement)

    @staticmethod
    def readItemsFromXml(element: ElementTree.Element) -> list['DrawingItem']:
        items = []

        # Read items from XML
        for itemElement in element:
            item = DrawingItem.create(itemElement.tag)
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
                            vec = vec - otherItem.mapToScene(otherPoint.position())     # type: ignore
                            distance = math.sqrt(vec.x() * vec.x() + vec.y() * vec.y())
                            if (distance <= 0.01):
                                point.addConnection(otherPoint)
                                otherPoint.addConnection(point)

        return items

    # ==================================================================================================================

    @staticmethod
    def setDefaultProperty(name: str, value: typing.Any) -> None:
        DrawingItem._defaultProperties[name] = value

    @staticmethod
    def defaultProperty(name: str) -> typing.Any:
        return DrawingItem._defaultProperties.get(name, None)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class DrawingRectResizeItem(DrawingItem):
    class PointIndex(Enum):
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

        self._rect: QRectF = QRectF()
        self._pen: QPen = QPen()

        self._cachedBoundingRect: QRectF = QRectF()

        for _ in range(8):
            self.addPoint(DrawingItemPoint(QPointF(), DrawingItemPoint.Type.ControlAndConnection))

    # ==================================================================================================================

    def setRect(self, rect: QRectF) -> None:
        points = self.points()
        if (len(points) >= 8):
            self._rect = rect

            center = rect.center()
            points[DrawingRectResizeItem.PointIndex.TopLeft.value].setPosition(QPointF(rect.left(), rect.top()))
            points[DrawingRectResizeItem.PointIndex.TopMiddle.value].setPosition(QPointF(center.x(), rect.top()))
            points[DrawingRectResizeItem.PointIndex.TopRight.value].setPosition(QPointF(rect.right(), rect.top()))
            points[DrawingRectResizeItem.PointIndex.MiddleRight.value].setPosition(QPointF(rect.right(), center.y()))
            points[DrawingRectResizeItem.PointIndex.BottomRight.value].setPosition(QPointF(rect.right(), rect.bottom()))
            points[DrawingRectResizeItem.PointIndex.BottomMiddle.value].setPosition(QPointF(center.x(), rect.bottom()))
            points[DrawingRectResizeItem.PointIndex.BottomLeft.value].setPosition(QPointF(rect.left(), rect.bottom()))
            points[DrawingRectResizeItem.PointIndex.MiddleLeft.value].setPosition(QPointF(rect.left(), center.y()))

            self._updateGeometry()

    def rect(self) -> QRectF:
        return self._rect

    # ==================================================================================================================

    def setPen(self, pen: QPen) -> None:
        self._pen = pen
        self._updateGeometry()

    def pen(self) -> QPen:
        return self._pen

    # ==================================================================================================================

    def boundingRect(self) -> QRectF:
        return self._cachedBoundingRect

    def isValid(self) -> bool:
        return (self._rect.width() != 0 and self._rect.height() != 0)

    # ==================================================================================================================

    def resize(self, point: DrawingItemPoint, position: QPointF, snapTo45Degrees: bool) -> None:
        points = self.points()
        if (len(points) >= 8):
            # Force the rect to be square if resizing a corner, if applicable
            if (snapTo45Degrees):
                otherCornerPoint = None
                if (point == points[DrawingRectResizeItem.PointIndex.TopLeft.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.BottomRight.value]
                elif (point == points[DrawingRectResizeItem.PointIndex.TopRight.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.BottomLeft.value]
                elif (point == points[DrawingRectResizeItem.PointIndex.BottomRight.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.TopLeft.value]
                elif (point == points[DrawingRectResizeItem.PointIndex.BottomLeft.value]):
                    otherCornerPoint = points[DrawingRectResizeItem.PointIndex.TopRight.value]

                if (otherCornerPoint is not None):
                    otherCornerPosition = self.mapToScene(otherCornerPoint.position())
                    delta = position - otherCornerPosition      # type: ignore

                    targetAngleDegrees = 0
                    if (delta.y() >= 0):
                        targetAngleDegrees = 45 if (delta.x() >= 0) else 135
                    else:
                        targetAngleDegrees = -45 if (delta.x() >= 0) else -135

                    if (targetAngleDegrees != 0):
                        targetAngle = targetAngleDegrees * math.pi / 180
                        length = max(abs(delta.x()), abs(delta.y())) * math.sqrt(2)
                        position.setX(otherCornerPosition.x() + length * math.cos(targetAngle))
                        position.setY(otherCornerPosition.y() + length * math.sin(targetAngle))

            # Move just the one point to its new position
            super().resize(point, position, False)

            # Adjust the other points as needed
            rect = QRectF(points[DrawingRectResizeItem.PointIndex.TopLeft.value].position(),
                          points[DrawingRectResizeItem.PointIndex.BottomRight.value].position())

            pointIndex = points.index(point)
            match (pointIndex):
                case DrawingRectResizeItem.PointIndex.TopLeft.value:
                    rect.setTopLeft(point.position())
                case DrawingRectResizeItem.PointIndex.TopMiddle.value:
                    rect.setTop(point.position().y())
                case DrawingRectResizeItem.PointIndex.TopRight.value:
                    rect.setTopRight(point.position())
                case DrawingRectResizeItem.PointIndex.MiddleRight.value:
                    rect.setRight(point.position().x())
                case DrawingRectResizeItem.PointIndex.BottomRight.value:
                    rect.setBottomRight(point.position())
                case DrawingRectResizeItem.PointIndex.BottomMiddle.value:
                    rect.setBottom(point.position().y())
                case DrawingRectResizeItem.PointIndex.BottomLeft.value:
                    rect.setBottomLeft(point.position())
                case DrawingRectResizeItem.PointIndex.MiddleLeft.value:
                    rect.setLeft(point.position().x())

            # Keep the item's position as the center of the rect
            center = rect.center()
            self.setPosition(self.mapToScene(center))
            rect.translate(-center)

            # Move all points to their final positions
            self.setRect(rect)

    def resizeStartPoint(self) -> DrawingItemPoint | None:
        points = self.points()
        if (len(points) >= 8):
            return self.points()[DrawingRectResizeItem.PointIndex.TopLeft.value]
        return None

    def resizeEndPoint(self) -> DrawingItemPoint | None:
        points = self.points()
        if (len(points) >= 8):
            return self.points()[DrawingRectResizeItem.PointIndex.BottomRight.value]
        return None

    # ==================================================================================================================

    def scale(self, scale: float) -> None:
        super().scale(scale)
        self._pen.setWidthF(self._pen.widthF() * scale)
        self.setRect(QRectF(QPointF(self._rect.left() * scale, self._rect.top() * scale),
                            QPointF(self._rect.right() * scale, self._rect.bottom() * scale)))

    # ==================================================================================================================

    def _updateGeometry(self):
        # Update bounding rect
        self._cachedBoundingRect = QRectF()
        if (self.isValid()):
            self._cachedBoundingRect = self._rect.normalized()
            if (self._pen.style() != Qt.PenStyle.NoPen):
                halfPenWidth = self._pen.widthF() / 2
                self._cachedBoundingRect.adjust(-halfPenWidth, -halfPenWidth, halfPenWidth, halfPenWidth)
