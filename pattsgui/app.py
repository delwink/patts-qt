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

from PyQt4.QtGui import QApplication
from .config import get, put
from .login import get_login
from .mainwindow import MainWindow
from .exception import ExceptionDialog, format_exc

class PattsApp(QApplication):
    def __init__(self, argv):
        super(PattsApp, self).__init__(argv)

        self._cancelled = False

        try:
            if get('Login', 'autologin').lower() == 'true':
                self._user = get('Login', 'user')
                self._passwd = get('Login', 'passwd')
                self._host = get('Login', 'host')
                self._db = get('Login', 'database')
            else:
                self._login()
        except KeyError:
            self._login()

        self._mwin = MainWindow(self._user, self._passwd, self._host, self._db)

    def _login(self, message=''):
        self._user, self._passwd, self._host, self._db = get_login(message)

        try:
            put('Login', 'user', self._user)
            put('Login', 'host', self._host)
            put('Login', 'database', self._db)

            if get('Login', 'autologin').lower() == 'true':
                put('Login', 'passwd', self._passwd)
        except TypeError:
            self._cancelled = True

    def exec_(self):
        if self._user and self._passwd and self._host and self._db:
            try:
                srv = self._host
                port = '0'

                if ':' in srv:
                    split = srv.split(':')
                    srv = split[0]
                    port = split[1]

                patts.init(host=srv, user=self._user, passwd=self._passwd,
                           database=self._db, port=port)

                self._mwin.show()
                return super(PattsApp, self).exec_()
            except Exception:
                ExceptionDialog(format_exc()).exec_()
                raise
        else:
            if self._cancelled:
                exit(0)
            elif not self._user:
                self._login('Login.badUser')
            elif not self._passwd:
                self._login('Login.badPass')
            elif not self._host:
                self._login('Login.badHost')
            elif not self._db:
                self._login('Login.badDatabase')
            else:
                try:
                    raise LookupError('Application initialization did not get '
                                      'credentials!')
                except:
                    ExceptionDialog(format_exc()).exec_()
                    raise

            return self.exec_()
