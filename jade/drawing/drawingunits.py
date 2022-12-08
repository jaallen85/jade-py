# drawingunits.py
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

from enum import Enum


class DrawingUnits(Enum):
    Millimeters = 0
    Centimeters = 1
    Meters = 2
    Kilometers = 3
    Mils = 4
    Inches = 5
    Feet = 6
    Miles = 7

    def toString(self) -> str:
        match (self):
            case DrawingUnits.Millimeters:
                return 'mm'
            case DrawingUnits.Centimeters:
                return 'cm'
            case DrawingUnits.Meters:
                return 'm'
            case DrawingUnits.Kilometers:
                return 'km'
            case DrawingUnits.Mils:
                return 'mil'
            case DrawingUnits.Inches:
                return 'in'
            case DrawingUnits.Feet:
                return 'ft'
            case DrawingUnits.Miles:
                return 'mi'
        return 'm'

    def conversionFactorToMeters(self) -> float:
        match (self):
            case DrawingUnits.Millimeters:
                return 1E-3
            case DrawingUnits.Centimeters:
                return 1E-2
            case DrawingUnits.Meters:
                return 1
            case DrawingUnits.Kilometers:
                return 1E3
            case DrawingUnits.Mils:
                return 2.54E-5
            case DrawingUnits.Inches:
                return 2.54E-2
            case DrawingUnits.Feet:
                return 0.3048
            case DrawingUnits.Miles:
                return 1609.34
        return 1.0

    def conversionFactorFromMeters(self) -> float:
        match (self):
            case DrawingUnits.Millimeters:
                return 1E3
            case DrawingUnits.Centimeters:
                return 1E2
            case DrawingUnits.Meters:
                return 1
            case DrawingUnits.Kilometers:
                return 1E-3
            case DrawingUnits.Mils:
                return 1 / 2.54E-5
            case DrawingUnits.Inches:
                return 1 / 2.54E-2
            case DrawingUnits.Feet:
                return 1 / 0.3048
            case DrawingUnits.Miles:
                return 1 / 1609.34
        return 1.0

    @staticmethod
    def fromString(text: str) -> 'DrawingUnits':
        text = text.lower()
        if (text in ('mm', 'millimeter', 'millimeters')):
            return DrawingUnits.Millimeters
        if (text in ('cm', 'centimeter', 'centimeters')):
            return DrawingUnits.Centimeters
        if (text in ('m', 'meter', 'meters')):
            return DrawingUnits.Meters
        if (text in ('km', 'kilometer', 'kilometers')):
            return DrawingUnits.Kilometers
        if (text in ('mil', 'mils', 'thou')):
            return DrawingUnits.Mils
        if (text in ('in', 'inch', 'inches', '"')):
            return DrawingUnits.Inches
        if (text in ('ft', 'foot', 'feet', "'")):
            return DrawingUnits.Feet
        if (text in ('mi', 'mile', 'miles')):
            return DrawingUnits.Miles
        raise ValueError(f'Unable to convert {text} to DrawingUnits')

    @staticmethod
    def convert(value: float, units: 'DrawingUnits', newUnits: 'DrawingUnits') -> float:
        return value * units.conversionFactorToMeters() * newUnits.conversionFactorFromMeters()
