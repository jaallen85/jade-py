# odgunits.py
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

from enum import IntEnum


class OdgUnits(IntEnum):
    Millimeters = 0
    Inches = 1

    # ==================================================================================================================

    def __str__(self) -> str:
        if (self == OdgUnits.Inches):
            return 'in'
        return 'mm'

    @staticmethod
    def fromStr(text: str) -> 'OdgUnits':
        lowerText = text.lower()
        if (lowerText == 'mm'):
            return OdgUnits.Millimeters
        if (lowerText == 'in'):
            return OdgUnits.Inches
        raise ValueError(f'Unknown value provided to OdgUnits.fromStr: {text}')

    # ==================================================================================================================

    def conversionFactorToMeters(self) -> float:
        if (self == OdgUnits.Inches):
            return 0.0254
        return 0.001

    def conversionFactorFromMeters(self) -> float:
        if (self == OdgUnits.Inches):
            return 1 / 0.0254
        return 1000

    @staticmethod
    def convert(position: float, oldUnits: 'OdgUnits', newUnits: 'OdgUnits') -> float:
        return position * oldUnits.conversionFactorToMeters() * newUnits.conversionFactorFromMeters()
