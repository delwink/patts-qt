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

from PyQt4.QtGui import QApplication
from .config import get
from .login import get_login
from .mainwindow import MainWindow

class PattsApp(QApplication):
    _user = ''
    _passwd = ''
    _host = ''
    _db = ''
    _mwin = None
    _argv = []

    def __init__(self, argv):
        self._argv = argv
        super(PattsApp, self).__init__(argv)

        try:
            if get('Login', 'autologin').lower() == 'true':
                self._user = get('Login', 'user')
                self._passwd = get('Login', 'passwd')
                self._host = get('Login', 'host')
                self._db = get('Login', 'database')
            else:
                self._user, self._passwd, self._host, self._db = get_login()
        except KeyError:
            self._user, self._passwd, self._host, self._db = get_login()

        _mwin = MainWindow(self._user, self._passwd, self._host, self._db)

    def exec_(self):
        if self._user and self._passwd and self._host and self._db:
            _mwin.show()
            return super(PattsApp, self).exec_(self._argv)
        else:
            raise LookupError('Application initialization did not get '
                              'credentials!')
