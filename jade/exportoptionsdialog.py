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

from PySide6.QtCore import Qt, QSizeF
from PySide6.QtGui import QDoubleValidator, QFontMetrics, QIcon, QIntValidator
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QLineEdit, QVBoxLayout,
                               QWidget)
from .diagramwidget import DiagramWidget
from .properties.helperwidgets import SizeEdit


class PngSvgExportOptionsDialog(QDialog):
    def __init__(self, scale: float, pageSize: QSizeF, parent: QWidget) -> None:
        super().__init__(parent)

        self._pageSize: QSizeF = QSizeF(pageSize)

        layout = QVBoxLayout()
        layout.addWidget(self._createSizeGroup())
        layout.addWidget(self._createButtonBox())
        self.setLayout(layout)

        self.setWindowTitle('Export Options')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(200, 10)

        self._scaleEdit.setText(f'{scale}')
        self._updateWidthAndHeightFromScale(self._scaleEdit.text())

    def _createSizeGroup(self) -> QGroupBox:
        self._widthEdit: QLineEdit = QLineEdit()
        self._widthEdit.setValidator(QIntValidator(0, 10000000))
        self._widthEdit.textEdited.connect(self._updateHeightAndScaleFromWidth)     # type: ignore

        self._heightEdit: QLineEdit = QLineEdit()
        self._heightEdit.setValidator(QIntValidator(0, 10000000))
        self._heightEdit.textEdited.connect(self._updateWidthAndScaleFromHeight)    # type: ignore

        self._scaleEdit: QLineEdit = QLineEdit()
        self._scaleEdit.setValidator(QDoubleValidator(1E-9, 1E9, -1))
        self._scaleEdit.textEdited.connect(self._updateWidthAndHeightFromScale)     # type: ignore

        sizeGroup = QGroupBox('Size')
        labelWidth = QFontMetrics(sizeGroup.font()).boundingRect('Height:').width() + 24
        sizeLayout = QFormLayout()
        sizeLayout.addRow('Width:', self._widthEdit)
        sizeLayout.addRow('Height:', self._heightEdit)
        sizeLayout.addRow('Scale:', self._scaleEdit)
        sizeLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        sizeLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        sizeLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        sizeLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        sizeGroup.setLayout(sizeLayout)

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

    def scale(self) -> float:
        try:
            return float(self._scaleEdit.text())
        except ValueError:
            pass
        return 1.0

    # ==================================================================================================================

    def _updateHeightAndScaleFromWidth(self, text: str) -> None:
        try:
            width = int(text)
            scale = width / self._pageSize.width()
            height = round(scale * self._pageSize.height())
            self._heightEdit.setText(f'{height}')
            self._scaleEdit.setText(f'{scale}')
        except ValueError:
            pass

    def _updateWidthAndScaleFromHeight(self, text: str) -> None:
        try:
            height = int(text)
            scale = height / self._pageSize.height()
            width = round(scale * self._pageSize.width())
            self._widthEdit.setText(f'{width}')
            self._scaleEdit.setText(f'{scale}')
        except ValueError:
            pass

    def _updateWidthAndHeightFromScale(self, text: str) -> None:
        try:
            scale = float(text)
            self._widthEdit.setText(f'{round(self._pageSize.width() * scale)}')
            self._heightEdit.setText(f'{round(self._pageSize.height() * scale)}')
        except ValueError:
            pass


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================

class OdgVsdxExportOptionsDialog(QDialog):
    def __init__(self, drawing: DiagramWidget, exportEntireDocument: bool, scale: float, units: str,
                 parent: QWidget) -> None:
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(self._createExportGroup())
        layout.addWidget(self._createButtonBox())
        self.setLayout(layout)

        self.setWindowTitle('Export Options')
        self.setWindowIcon(QIcon('icons:jade.png'))
        self.resize(280, 10)

        self._pagesCombo.setCurrentIndex(0 if (exportEntireDocument) else 1)
        self._scaleCombo.setSize(scale)
        self._unitsCombo.setCurrentIndex(1 if (units.lower() == 'in') else 0)

    def _createExportGroup(self) -> QWidget:
        self._pagesCombo: QComboBox = QComboBox()
        self._pagesCombo.addItems(['Entire Document', 'Current Page Only'])

        self._scaleCombo: SizeEdit = SizeEdit()

        self._unitsCombo: QComboBox = QComboBox()
        self._unitsCombo.addItems(['Millimeters (mm)', 'Inches (in)'])

        exportGroup = QGroupBox('Export')
        labelWidth = QFontMetrics(exportGroup.font()).boundingRect('Target Units:').width() + 16
        exportLayout = QFormLayout()
        exportLayout.addRow('Pages:', self._pagesCombo)
        exportLayout.addRow('Scale:', self._scaleCombo)
        exportLayout.addRow('Target Units:', self._unitsCombo)
        exportLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        exportLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        exportLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        exportLayout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().setMinimumWidth(labelWidth)
        exportGroup.setLayout(exportLayout)

        return exportGroup

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

    def shouldExportEntireDocument(self) -> bool:
        return (self._pagesCombo.currentIndex() == 0)

    def scale(self) -> float:
        return self._scaleCombo.size()

    def units(self) -> str:
        return 'in' if (self._unitsCombo.currentIndex() == 1) else 'mm'
