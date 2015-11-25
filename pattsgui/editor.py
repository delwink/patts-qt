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

from PyQt4.QtGui import QDialog, QTableWidget
from .lang import _

class Editor(QDialog):
    def __init__(self, get, byid, add, rem, table):
        super().__init__()

        self._get = get
        self._byid = byid
        self._add = add
        self._del = rem
        self._table = table
        self._changes = {}

        self.setWindowTitle(_('Admin.edit' + table))
