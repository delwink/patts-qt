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

from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import QDialog, QTableView, QVBoxLayout
from .lang import _

class UserTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        user_info = patts.get_users()

        self._keys = [k for k in user_info]
        self._keys.sort()

        self._fields = (
            'state', 'isAdmin', 'firstName', 'middleName', 'lastName'
        )

        self._users = []
        for k in self._keys:
            user = user_info[k]
            field_data = [user[field] for field in self._fields]
            self._users.append(field_data)

    def rowCount(self, parent):
        return len(self._users)

    def columnCount(self, parent):
        return len(self._fields)

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return self._users[row][col]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return _('User.' + self._fields[section])

            return self._keys[section]

    @property
    def table(self):
        return 'User'

class Editor(QDialog):
    def __init__(self, model):
        super().__init__()

        self._view = QTableView()
        self._view.setModel(model)

        layout = QVBoxLayout()
        layout.addWidget(self._view)

        self.setLayout(layout)

        self.setWindowTitle(_('Admin.edit' + model.table))
