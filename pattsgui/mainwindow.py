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

import patts

from PyQt4.QtCore import QObject, Qt, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QKeySequence, QMainWindow
from .aboutdialog import AboutDialog
from .config import get, put
from .editor import TaskTypeEditor, UserEditor
from .hostname import split_host
from .lang import _
from .exception import ExceptionDialog, format_exc

class MainWindow(QMainWindow):
    def __init__(self, user, passwd, host, database):
        srv, port = split_host(host)

        patts.init(host=srv, user=user, passwd=passwd, database=database,
                   port=port)

        super().__init__()

        menuBar = self.menuBar()

        sessionMenu = menuBar.addMenu(_('Session'))

        logoutAction = QAction(_('Session.LogOut'), self)
        logoutAction.triggered.connect(self._log_out)
        sessionMenu.addAction(logoutAction)

        quitAction = QAction(_('Session.Quit'), self)
        quitAction.setIcon(QIcon.fromTheme('application-exit'))
        quitAction.setShortcut(QKeySequence.Quit)
        quitAction.triggered.connect(self.close)
        sessionMenu.addAction(quitAction)

        if patts.have_admin():
            adminMenu = menuBar.addMenu(_('Admin'))

            tasksAction = QAction(_('Admin.TaskTypes'), self)
            tasksAction.triggered.connect(self._show_tasks)
            adminMenu.addAction(tasksAction)

            usersAction = QAction(_('Admin.Users'), self)
            usersAction.triggered.connect(self._show_users)
            adminMenu.addAction(usersAction)

        helpMenu = menuBar.addMenu(_('Help'))
        aboutAction = QAction(_('Help.About'), self)
        aboutAction.setIcon(QIcon.fromTheme('help-about'))
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

    def _log_out(self):
        put('Login', 'autologin', 'false')
        put('Login', 'passwd', '')
        self.close()

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
            UserEditor().exec_()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()

    def _show_tasks(self):
        try:
            TaskTypeEditor().exec_()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()
