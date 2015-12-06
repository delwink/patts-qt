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
from PyQt4.QtGui import QApplication, QDialog, QGraphicsWidget, QStyle
from PyQt4.QtGui import QStyleOptionButton, QTableView, QTableWidgetItem
from PyQt4.QtGui import QVBoxLayout
from .lang import _

class PattsTableModel(QAbstractTableModel):
    def __init__(self, table_name, get_table_info, fields, bool_fields,
                 parent=None):
        super().__init__(parent)

        table_info = get_table_info()
        self._table_name = table_name

        self._keys = [k for k in table_info]
        self._keys.sort()

        self._fields = fields
        self._bool_fields = bool_fields

        self.init_rows(table_info)
        self._orig = [row for row in self._rows]

    def init_rows(self, table_info):
        self._rows = []
        for k in self._keys:
            row = table_info[k]
            field_data = [row[field] for field in self._fields]
            self._rows.append(field_data)

    def rowCount(self, parent):
        return len(self._rows)

    def columnCount(self, parent):
        return len(self._fields)

    def flags(self, index):
        flags = Qt.ItemIsEditable | Qt.ItemIsEnabled
        if self._fields[index.column()] in self._bool_fields:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def _raw_data(self, index, role):
        row = index.row()
        col = index.column()

        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._rows[row][col]

    def data(self, index, role):
        if self._fields[index.column()] in self._bool_fields:
            if role == Qt.CheckStateRole:
                if self._raw_data(index, Qt.DisplayRole):
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return None

        return self._raw_data(index, role)

    def _set(self, index, value):
        self._rows[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        col = index.column()

        if self._fields[index.column()] in self._bool_fields:
            if role == Qt.CheckStateRole:
                return self._set(index, value)
            return False

        if role == Qt.EditRole:
            return self._set(index, value)
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return _('.'.join((self.table, self._fields[section])))

            return self._keys[section]

    @property
    def table(self):
        return self._table_name

class UserTableModel(PattsTableModel):
    def __init__(self, parent=None):
        fields = ('state', 'isAdmin', 'firstName', 'middleName', 'lastName')
        bool_fields = ('state', 'isAdmin')
        super().__init__('User', patts.get_users, fields, bool_fields, parent)

class Editor(QDialog):
    def __init__(self, model):
        super().__init__()

        self._view = QTableView()
        self._view.setModel(model)

        layout = QVBoxLayout()
        layout.addWidget(self._view)

        self.setLayout(layout)

        self.setWindowTitle(_('Admin.edit' + model.table))
        self.resize(600, 300)
