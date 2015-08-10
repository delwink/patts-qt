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

from patts import PATTS_COPYRIGHT
from PyQt4.QtGui import QDialog, QLabel, QPushButton, QVBoxLayout
from .lang import _

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        okButton = QPushButton(_('OK'))
        okButton.clicked.connect(self.accept)

        layout = QVBoxLayout()

        for line in PATTS_COPYRIGHT.split('\n'):
            layout.addWidget(QLabel(line))

        layout.addWidget(okButton)

        self.setLayout(layout)
        self.resize(600, 400)
