# main.py
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

import os
import sys
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication
from jade.mainwindow import MainWindow

app = QApplication(sys.argv)
QDir.addSearchPath('icons', os.path.join(sys.path[0], 'icons'))

window = MainWindow()
window.show()

app.exec()
