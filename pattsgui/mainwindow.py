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
from PyQt4.QtCore import QObject, Qt, SIGNAL
from .aboutdialog import AboutDialog
from .config import get, put
from .editor import Editor, UserTableModel
from .hostname import split_host
from .lang import _
from .exception import ExceptionDialog, format_exc

def new_user():
    pass

class MainWindow(QMainWindow):
    def __init__(self, user, passwd, host, database):
        srv, port = split_host(host)

        patts.init(host=srv, user=user, passwd=passwd, database=database,
                   port=port)

        super().__init__()

        menuBar = self.menuBar()

        if patts.have_admin():
            adminMenu = menuBar.addMenu(_('Admin'))
            usersAction = QAction(_('Admin.Users'), self)
            usersAction.triggered.connect(self._show_users)
            adminMenu.addAction(usersAction)

        helpMenu = menuBar.addMenu(_('Help'))
        aboutAction = QAction(_('Help.About'), self)
        aboutAction.triggered.connect(self._show_about)
        helpMenu.addAction(aboutAction)

        self.resize(int(get('MainWindow', 'width')),
                    int(get('MainWindow', 'height')))
        if get('MainWindow', 'max').lower() == 'true':
            self.showMaximized()
        self.setWindowTitle(_('MainWindow.title').format(host, database, user))

    def closeEvent(self, event):
        self._save_dims()
        patts.cleanup()
        super().closeEvent(event)

    def _save_dims(self):
        if self.windowState() & Qt.WindowMaximized:
            put('MainWindow', 'max', 'true')
        else:
            put('MainWindow', 'max', 'false')
            put('MainWindow', 'width', str(self.width()))
            put('MainWindow', 'height', str(self.height()))

    def _show_about(self):
        AboutDialog(patts.__version__, self).exec_()

    def _show_users(self):
        try:
            Editor(UserTableModel()).exec_()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()
