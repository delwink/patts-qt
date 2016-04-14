##
##  patts-qt - Qt GUI client for PATTS
##  Copyright (C) 2015-2016 Delwink, LLC
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

from patts import get_c_library_version, get_db_version
from PyQt4.QtGui import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget
from .lang import _

__copyright_year__ = '2015-2016'
__version__ = '0.0.0'

class AboutDialog(QDialog):
    def __init__(self, patts_version, parent=None):
        super().__init__(parent)

        okButton = QPushButton(_('OK'))
        okButton.clicked.connect(self.accept)

        layout = QVBoxLayout()

        title = QLabel('patts-qt v{}'.format(__version__))

        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        versions = (
            'patts module v{}'.format(patts_version),
            'libpatts v{}'.format(get_c_library_version()),
            'patts db v{}'.format(get_db_version())
        )

        layout.addWidget(title)
        layout.addWidget(QLabel('(' + ', '.join(versions) + ')'))

        copyright_text = _('About.copyright').format(__copyright_year__)
        layout.addWidget(QLabel(copyright_text.replace('\\n', '\n')))

        layout.addWidget(QLabel(_('About.license').replace('\\n', '\n')))

        layout.addWidget(okButton)

        self.setLayout(layout)
        self.setWindowTitle(_('About.title'))
