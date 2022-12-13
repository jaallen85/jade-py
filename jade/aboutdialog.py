# aboutdialog.py
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QTabWidget, QVBoxLayout, QWidget


class AboutDialog(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        imageLabel = QLabel()
        imageLabel.setPixmap(QPixmap('icons:jade.png'))

        nameLabel = QLabel('Jade 1.5.0')
        font = nameLabel.font()
        font.setBold(True)
        nameLabel.setFont(font)

        tabWidget = QTabWidget()
        tabWidget.addTab(self._createAboutTab(), 'About')
        tabWidget.setTabBarAutoHide(True)

        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        buttonBox.setCenterButtons(True)
        okButton = buttonBox.addButton('OK', QDialogButtonBox.ButtonRole.AcceptRole)
        okButton.setDefault(True)
        rect = QFontMetrics(okButton.font()).boundingRect('Cancel')
        okButton.setMinimumSize(rect.width() + 24, rect.height() + 16)
        okButton.clicked.connect(self.accept)       # type: ignore

        layout = QGridLayout()
        layout.addWidget(imageLabel, 0, 0)
        layout.addWidget(nameLabel, 0, 1)
        layout.addWidget(tabWidget, 1, 0, 1, 2)
        layout.addWidget(buttonBox, 2, 0, 1, 2)
        layout.setColumnStretch(1, 100)
        layout.setRowStretch(1, 100)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.setWindowTitle('About Jade')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(500, 200)

    def _createAboutTab(self) -> QWidget:
        nameLabel = QLabel('Jade')
        font = nameLabel.font()
        font.setBold(True)
        nameLabel.setFont(font)
        nameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        authorLabel = QLabel("written by Jason Allen")
        authorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copyrightLabel = QLabel("Copyright (c) 2014-")
        copyrightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(nameLabel)
        layout.addWidget(authorLabel)
        layout.addWidget(copyrightLabel)
        layout.addWidget(QWidget(), 100)
        widget.setLayout(layout)

        return widget
