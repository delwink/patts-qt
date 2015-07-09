##
##  patts-qt - Qt GUI client for PATTS
##  Copyright (C) 2015 Delwink, LLC
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as published by
##  the Free Software Foundation, version 3 only.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from PyQt4.QtGui import QDialog, QPushButton, QTextEdit, QLabel, QGridLayout
from PyQt4.QtGui import QFont
from traceback import format_exc
from .lang import _

class ExceptionDialog(QDialog):
    def __init__(self, exc, parent=None):
        super(ExceptionDialog, self).__init__(parent)

        lbl = QLabel(_('Exception.label'))

        errorBox = QTextEdit(exc)
        errorBox.setReadOnly(True)
        errorBox.setFont(QFont('monospace', 9))

        okButton = QPushButton(_('OK'))
        okButton.clicked.connect(self.accept)

        layout = QGridLayout()
        layout.addWidget(lbl, 1, 0)
        layout.addWidget(errorBox, 2, 0, 5, 1)
        layout.addWidget(okButton, 7, 0)

        self.setLayout(layout)
        self.resize(400, 300)
