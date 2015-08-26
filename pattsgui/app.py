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
        super().__init__(argv)

        self._cancelled = False
        self._mwin = None

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

        while self._mwin is None:
            try:
                self._mwin = MainWindow(self._user, self._passwd, self._host,
                                        self._db)
            except Exception as e:
                if type(e) is Exception:
                    errno = int(str(e))

                    if errno == 1044:
                        self._login('Login.badDatabase')
                    elif errno == 1045:
                        self._login('Login.accessDenied')
                    elif errno == 2005:
                        self._login('Login.badHost')
                    else:
                        self._login('Error {}'.format(errno))

                    if self._cancelled:
                        exit(0)
                elif type(e) is TypeError:
                    exit(0) # cancelled
                else:
                    ExceptionDialog(format_exc()).exec_()
                    raise

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
            self._mwin.show()
            return super().exec_()
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
