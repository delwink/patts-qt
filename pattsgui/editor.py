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
from PyQt4.QtGui import QApplication, QDialog, QGraphicsWidget, QHBoxLayout
from PyQt4.QtGui import QPushButton, QStyle, QStyleOptionButton, QTableView
from PyQt4.QtGui import QTableWidgetItem, QVBoxLayout
from .lang import _

class Field:
    def __init__(self, name, boolean=False, quoted=False):
        self._name = name
        self._bool = boolean
        self._quoted = quoted

    @property
    def name(self):
        return self._name

    @property
    def is_bool(self):
        return self._bool

    @property
    def quoted(self):
        return self.quoted

    def format(self, val):
        if self._bool:
            return str(int(bool(val)))

        return patts.escape_string(str(val), self._quoted)

class PattsTableModel(QAbstractTableModel):
    def __init__(self, table_name, get_table_info, fields, parent=None):
        super().__init__(parent)

        table_info = get_table_info()
        self._table_name = table_name
        self._primary_key = patts.get_primary_key(table_name)

        self._keys = [k for k in table_info]
        self._keys.sort()

        self._fields = fields

        self.init_rows(table_info)
        self._orig = []
        for row in self._rows:
            self._orig.append([col for col in row])

    def init_rows(self, table_info):
        self._rows = []
        for k in self._keys:
            row = table_info[k]
            field_data = [row[field.name] for field in self._fields]
            self._rows.append(field_data)

    def rowCount(self, parent):
        return len(self._rows)

    def columnCount(self, parent):
        return len(self._fields)

    def flags(self, index):
        flags = Qt.ItemIsEditable | Qt.ItemIsEnabled
        if self._fields[index.column()].is_bool:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def _raw_data(self, index, role):
        row = index.row()
        col = index.column()

        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._rows[row][col]

    def data(self, index, role):
        if self._fields[index.column()].is_bool:
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

        if self._fields[index.column()].is_bool:
            if role == Qt.CheckStateRole:
                return self._set(index, value)
            return False

        if role == Qt.EditRole:
            return self._set(index, value)
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return _('.'.join((self.table, self._fields[section].name)))

            return self._keys[section]

    def primary_key_value(self, i):
        return self._keys[i]

    def add_change(self, queries, changes, row, i):
        field = self._fields[i]
        changes.append(field.name + '=' + field.format(row[i]))

    def save_row_query(self, i):
        row = self._rows[i]
        pkval = self.primary_key_value(i)
        changes = []
        queries = []

        try:
            orig_row = self._orig[i]
        except IndexError:
            orig_row = None

        for j in range(len(row)):
            if not orig_row or row[j] != orig_row[j]:
                self.add_change(queries, changes, row, j)

        if not changes:
            return None

        changes = ','.join(changes)
        query = 'UPDATE {} SET {} WHERE {}={}'.format(self.table, changes,
                                                      self.primary_key, pkval)
        queries.append((patts.query, (query,)))

        return queries

    def save(self):
        queries = []
        for i in range(len(self._rows)):
            query = self.save_row_query(i)
            if query:
                queries += query

        for query in queries:
            # each item here is a tuple whose first element is a function and
            # whose second element is another tuple of the arguments
            query[0](*query[1])

    @property
    def table(self):
        return self._table_name

    @property
    def primary_key(self):
        return self._primary_key

class UserTableModel(PattsTableModel):
    def __init__(self, parent=None):
        fields = (
            Field('state', boolean=True),
            Field('isAdmin', boolean=True),
            Field('firstName', quoted=True),
            Field('middleName', quoted=True),
            Field('lastName', quoted=True)
        )
        super().__init__('User', patts.get_users, fields, parent)

    def primary_key_value(self, i):
        return patts.escape_string(super().primary_key_value(i), quote=True)

class Editor(QDialog):
    def __init__(self, model):
        super().__init__()

        tableView = QTableView()
        tableView.setModel(model)

        okButton = QPushButton(_('OK'))
        okButton.clicked.connect(self.accept)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(okButton)

        layout = QVBoxLayout()
        layout.addWidget(tableView)
        layout.addLayout(buttonBox)

        self.setLayout(layout)

        self.accepted.connect(model.save)

        self.setWindowTitle(_('Admin.edit' + model.table))
        self.resize(600, 300)
