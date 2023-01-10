# run_linters.py
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

import subprocess

# flake8
print('-' * 80)
print('flake8')
print('-' * 80)
subprocess.run(['flake8', '--max-line-length=120', 'jade'])
print('flake8 run complete.')

# mypy
print(' ')
print('-' * 80)
print('mypy')
print('-' * 80)
subprocess.run(['mypy', '--disallow-untyped-defs', '--disallow-incomplete-defs', 'jade'])
print('mypy run complete.')

# pylint
# Ignore snake_case naming style check (C0103)
# Ignore docstring checks for modules (C0114), classes (C0115), and functions (C0116)
# Ignore line too long checks as we're covered by flake8 (C0301)
# Ignore modules with too many lines of code (C0302)
# Ignore unnecessary parenthesis after 'if' keyword (C0325)
# Ignore components not found in modules, as this is returning false positives for all PyQt6 components (E0611)
# Ignore similar code in multiple files (R0801)
# Ignore classes with too many member variables (R0902)
# Ignore classes with too few public functions (R0903)
# Ignore classes with too many public functions (R0904)
# Ignore classes with too many return statements (R0911)
# Ignore if statements with too many branches (R0912)
# Ignore functions with too many arguments (R0913)
# Ignore functions with too many local variables (R0914)
# Ignore functions with too many lines of code (R0915)
# Ignore if statements with too many clauses (R0916)
# Ignore functions with too many nested blocks (R1702)
# Ignore unused arguments (W0613)
print(' ')
print('-' * 80)
print('pylint')
print('-' * 80)
subprocess.run(['pylint', '--disable=C0103,C0114,C0115,C0116,C0301,C0302,C0325,E0611,R0801,R0902,R0903,R0904,R0911,'
                          'R0912,R0913,R0914,R0915,R0916,R1702,W0613', 'jade'])
print('pylint run complete.')
