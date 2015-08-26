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

import patts

from PyQt4.QtGui import QAction, QMainWindow
from PyQt4.QtCore import QObject, SIGNAL
from .aboutdialog import AboutDialog
from .config import get, put
from .lang import _
from .exception import ExceptionDialog, format_exc

class MainWindow(QMainWindow):
    def __init__(self, user, passwd, host, database):
        srv = host
        port = '0'

        if ':' in srv:
            split = srv.split(':')
            srv = split[0]
            port = split[1]

        patts.init(host=srv, user=user, passwd=passwd, database=database,
                   port=port)

        super().__init__()

        aboutAction = QAction(_('Help.About'), self)
        aboutAction.triggered.connect(self._show_about)

        menuBar = self.menuBar()
        helpMenu = menuBar.addMenu(_('Help'))
        helpMenu.addAction(aboutAction)

        self.resize(int(get('MainWindow', 'width')),
                    int(get('MainWindow', 'height')))
        self.setWindowTitle(_('MainWindow.title').format(host, database, user))

    def closeEvent(self, event):
        self._save_dims()
        super().closeEvent(event)

    def _save_dims(self):
        put('MainWindow', 'width', str(self.width()))
        put('MainWindow', 'height', str(self.height()))

    def _show_about(self):
        AboutDialog(self).exec_()
