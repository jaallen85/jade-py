# exportoptionsdialog.py
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

from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QFontMetrics, QIcon, QIntValidator
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QLineEdit, QVBoxLayout,
                               QWidget)


class ExportOptionsDialog(QDialog):
    def __init__(self, sceneRect: QRectF, exportSize: QSize, maintainAspectRatio: bool, parent: QWidget) -> None:
        super().__init__()

        self._sceneRect: QRectF = QRectF(sceneRect)

        layout = QVBoxLayout()
        layout.addWidget(self._createSizeGroup(exportSize, maintainAspectRatio))
        layout.addWidget(self._createButtonBox())
        self.setLayout(layout)

        self.setWindowTitle('Export Options')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(240, 10)

    def _createSizeGroup(self, exportSize: QSize, maintainAspectRatio: bool) -> QWidget:
        self._widthEdit: QLineEdit = QLineEdit()
        self._heightEdit: QLineEdit = QLineEdit()
        self._widthEdit.setValidator(QIntValidator(0, 10000000))
        self._heightEdit.setValidator(QIntValidator(0, 10000000))
        self._widthEdit.textEdited.connect(self._updateHeightFromWidth)      # type: ignore
        self._heightEdit.textEdited.connect(self._updateWidthFromHeight)     # type: ignore

        self._maintainAspectRatioCheck = QCheckBox('Maintain Aspect Ratio')
        self._maintainAspectRatioCheck.setChecked(maintainAspectRatio)

        widthHeightWidget: QWidget = QWidget()
        widthHeightLayout: QFormLayout = QFormLayout()
        widthHeightLayout.addRow('Width:', self._widthEdit)
        widthHeightLayout.addRow('Height:', self._heightEdit)
        widthHeightLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        widthHeightLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        widthHeightLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        labelWidth = QFontMetrics(widthHeightWidget.font()).boundingRect('Height:').width() + 24
        widthHeightLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        widthHeightWidget.setLayout(widthHeightLayout)

        maintainWidget = QWidget()
        maintainLayout = QVBoxLayout()
        maintainLayout.addWidget(self._maintainAspectRatioCheck)
        maintainLayout.setContentsMargins(0, 0, 0, 0)
        maintainWidget.setLayout(maintainLayout)

        sizeGroup = QGroupBox('Size')
        sizeLayout = QVBoxLayout()
        sizeLayout.addWidget(widthHeightWidget)
        sizeLayout.addWidget(maintainWidget)
        sizeLayout.setSpacing(8)
        sizeGroup.setLayout(sizeLayout)

        if (maintainAspectRatio):
            if (exportSize.height() > 0):
                self._heightEdit.setText(f'{exportSize.height()}')
                self._updateWidthFromHeight()
            elif (exportSize.width() > 0):
                self._widthEdit.setText(f'{exportSize.width()}')
                self._updateHeightFromWidth()
            else:
                self._widthEdit.setText(f'{exportSize.width()}')
                self._heightEdit.setText(f'{exportSize.height()}')
        else:
            self._widthEdit.setText(f'{exportSize.width()}')
            self._heightEdit.setText(f'{exportSize.height()}')

        return sizeGroup

    def _createButtonBox(self) -> QWidget:
        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        buttonBox.setCenterButtons(True)

        okButton = buttonBox.addButton('OK', QDialogButtonBox.ButtonRole.AcceptRole)
        cancelButton = buttonBox.addButton('Cancel', QDialogButtonBox.ButtonRole.RejectRole)

        rect = QFontMetrics(cancelButton.font()).boundingRect('Cancel')
        okButton.setMinimumSize(rect.width() + 24, rect.height() + 16)
        cancelButton.setMinimumSize(rect.width() + 24, rect.height() + 16)

        okButton.clicked.connect(self.accept)       # type: ignore
        cancelButton.clicked.connect(self.reject)   # type: ignore

        return buttonBox

    # ==================================================================================================================

    def _updateWidthFromHeight(self) -> None:
        pass

    def _updateHeightFromWidth(self) -> None:
        pass
