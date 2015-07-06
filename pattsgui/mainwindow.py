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

from PyQt4.QtGui import QWidget
from .config import get

class MainWindow(QWidget):
    _user = ''
    _passwd = ''
    _host = ''
    _db = ''

    def __init__(self, user, passwd, host, database):
        super(MainWindow, self).__init__()

        self.resize(int(get('MainWindow', 'width')),
                    int(get('MainWindow', 'height')))
        self.setWindowTitle('PATTS')

        self._user = user
        self._passwd = passwd
        self._host = host
        self._db = database
