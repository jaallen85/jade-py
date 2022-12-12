# units.py
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


class Units(Enum):
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
            case Units.Millimeters:
                return 'mm'
            case Units.Centimeters:
                return 'cm'
            case Units.Meters:
                return 'm'
            case Units.Kilometers:
                return 'km'
            case Units.Mils:
                return 'mil'
            case Units.Inches:
                return 'in'
            case Units.Feet:
                return 'ft'
            case Units.Miles:
                return 'mi'
        return 'm'

    def conversionFactorToMeters(self) -> float:
        match (self):
            case Units.Millimeters:
                return 1E-3
            case Units.Centimeters:
                return 1E-2
            case Units.Meters:
                return 1
            case Units.Kilometers:
                return 1E3
            case Units.Mils:
                return 2.54E-5
            case Units.Inches:
                return 2.54E-2
            case Units.Feet:
                return 0.3048
            case Units.Miles:
                return 1609.344
        return 1.0

    def conversionFactorFromMeters(self) -> float:
        match (self):
            case Units.Millimeters:
                return 1E3
            case Units.Centimeters:
                return 1E2
            case Units.Meters:
                return 1
            case Units.Kilometers:
                return 1E-3
            case Units.Mils:
                return 1 / 2.54E-5
            case Units.Inches:
                return 1 / 2.54E-2
            case Units.Feet:
                return 1 / 0.3048
            case Units.Miles:
                return 1 / 1609.344
        return 1.0

    def conversionFactorToMetersSimple(self) -> float:
        match (self):
            case Units.Millimeters:
                return 1E-3
            case Units.Centimeters:
                return 1E-2
            case Units.Meters:
                return 1
            case Units.Kilometers:
                return 1E3
            case Units.Mils:
                return 2.5E-5
            case Units.Inches:
                return 2.5E-2
            case Units.Feet:
                return 0.3
            case Units.Miles:
                return 1584.0
        return 1.0

    def conversionFactorFromMetersSimple(self) -> float:
        match (self):
            case Units.Millimeters:
                return 1E3
            case Units.Centimeters:
                return 1E2
            case Units.Meters:
                return 1
            case Units.Kilometers:
                return 1E-3
            case Units.Mils:
                return 1 / 2.54E-5
            case Units.Inches:
                return 1 / 2.54E-2
            case Units.Feet:
                return 1 / 0.3
            case Units.Miles:
                return 1 / 1584.0
        return 1.0

    @staticmethod
    def fromString(text: str) -> 'Units':
        text = text.lower()
        if (text in ('mm', 'millimeter', 'millimeters')):
            return Units.Millimeters
        if (text in ('cm', 'centimeter', 'centimeters')):
            return Units.Centimeters
        if (text in ('m', 'meter', 'meters')):
            return Units.Meters
        if (text in ('km', 'kilometer', 'kilometers')):
            return Units.Kilometers
        if (text in ('mil', 'mils', 'thou')):
            return Units.Mils
        if (text in ('in', 'inch', 'inches', '"')):
            return Units.Inches
        if (text in ('ft', 'foot', 'feet', "'")):
            return Units.Feet
        if (text in ('mi', 'mile', 'miles')):
            return Units.Miles
        raise ValueError(f'Unable to convert {text} to Units')

    @staticmethod
    def convert(value: float, units: 'Units', newUnits: 'Units') -> float:
        return value * units.conversionFactorToMeters() * newUnits.conversionFactorFromMeters()

    @staticmethod
    def convertSimple(value: float, units: 'Units', newUnits: 'Units') -> float:
        return value * units.conversionFactorToMetersSimple() * newUnits.conversionFactorFromMetersSimple()
