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

from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt4.QtGui import QApplication, QDialog, QGraphicsWidget, QHBoxLayout
from PyQt4.QtGui import QLabel, QLineEdit, QPushButton, QStyle
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionButton, QTableView
from PyQt4.QtGui import QTableWidgetItem, QValidator, QVBoxLayout
from .exception import ExceptionDialog, format_exc
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
        return self._quoted

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

    def rowCount(self, parent=None):
        return len(self._rows)

    def columnCount(self, parent=None):
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

    def insertRows(self, position, rows, parent):
        return False

    def removeRows(self, position, rows, parent):
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return _('.'.join((self.table, self._fields[section].name)))

            return self._keys[section]

    def primary_key_value(self, i):
        return self._keys[i]

    def add_change(self, queries, changes, row, i, j):
        field = self._fields[j]
        changes.append(field.name + '=' + field.format(row[j]))

    def save_row_query(self, i):
        row = self._rows[i]
        pkval = self.primary_key_value(i)
        changes = []
        queries = []

        orig_row = self._orig[i]
        for j in range(len(row)):
            if row[j] != orig_row[j]:
                self.add_change(queries, changes, row, i, j)

        if changes:
            changes = ','.join(changes)
            query = 'UPDATE {} SET {} WHERE {}={}'.format(self.table, changes,
                                                          self.primary_key,
                                                          pkval)
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

    def add_change(self, queries, changes, row, i, j):
        field = self._fields[j]

        if field.name == 'state':
            if not row[j]:
                queries.append((patts.delete_user, (self._keys[i],)))
        elif field.name == 'isAdmin':
            val = field.format(row[j])

            if val == '0':
                queries.append((patts.revoke_admin, (self._keys[i], '%')))
            elif val == '1':
                queries.append((patts.grant_admin, (self._keys[i], '%')))
            else:
                raise ValueError('Illegal boolean value')
        else:
            super().add_change(queries, changes, row, i, j)

class TaskTypeTableModel(PattsTableModel):
    def __init__(self, parent=None):
        fields = (
            Field('state', boolean=True),
            Field('parentID'),
            Field('displayName', quoted=True)
        )
        super().__init__('TaskType', patts.get_types, fields, parent)

    def init_rows(self, table_info):
        keys = [int(k) for k in self._keys]
        keys.sort()
        for i in range(len(keys)):
            self._keys[i] = str(keys[i])

        super().init_rows(table_info)

    @property
    def parent_column(self):
        return 1

class TryAgainDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(_('NewUser.tryAgain')))

        okButton = QPushButton(_('OK'))
        layout.addWidget(okButton)
        okButton.clicked.connect(self.accept)

        self.setLayout(layout)
        self.setWindowTitle(_('NewUser.tryAgainTitle'))

class UsernameValidator(QValidator):
    def __init__(self):
        super().__init__()

    def validate(self, input, pos):
        if len(input) > 8:
            return (QValidator.Invalid, input, pos - 1)

        out = ''
        for c in input:
            if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                c = c.lower()

            if c not in 'abcdefghijklmnopqrstuvwxyz0123456789':
                return (QValidator.Invalid, input, pos - 1)

            out += c

        return (QValidator.Acceptable, out, pos)

class NewUserDialog(QDialog):
    def __init__(self):
        super().__init__()

        self._name = ''
        self._passwd = ''
        self._cancelled = False

        labelBox = QVBoxLayout()
        labelBox.addWidget(QLabel(_('NewUser.name')))
        labelBox.addWidget(QLabel(_('NewUser.passwd')))
        labelBox.addWidget(QLabel(_('NewUser.confirm')))

        fieldBox = QVBoxLayout()

        self._name_box = QLineEdit()
        self._name_box.setValidator(UsernameValidator())
        fieldBox.addWidget(self._name_box)

        self._pw_box = QLineEdit()
        self._pw_box.setEchoMode(QLineEdit.Password)
        fieldBox.addWidget(self._pw_box)

        self._confirm_box = QLineEdit()
        self._confirm_box.setEchoMode(QLineEdit.Password)
        fieldBox.addWidget(self._confirm_box)

        labelFieldBox = QHBoxLayout()
        labelFieldBox.addLayout(labelBox)
        labelFieldBox.addLayout(fieldBox)

        cancelButton = QPushButton(_('cancel'))
        cancelButton.clicked.connect(self.reject)
        self.rejected.connect(self._set_cancelled)

        okButton = QPushButton(_('OK'))
        okButton.setDefault(True)
        okButton.clicked.connect(self.accept)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(cancelButton)
        buttonBox.addWidget(okButton)

        layout = QVBoxLayout()
        layout.addLayout(labelFieldBox)
        layout.addLayout(buttonBox)
        self.setLayout(layout)

        self.setWindowTitle(_('NewUser.title'))

    def get_info(self):
        self.exec_()
        while (not self._cancelled
               and (not (self._name_box.text() and self._pw_box.text())
                    or self._pw_box.text() != self._confirm_box.text())):
            TryAgainDialog().exec_()
            self.exec_()

        return (self._name_box.text(), self._pw_box.text())

    def _set_cancelled(self):
        self._cancelled = True

    @property
    def cancelled(self):
        return self._cancelled

class Editor(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)

        self._view = QTableView()
        self._view.setModel(model)

        cancelButton = QPushButton(_('cancel'))
        cancelButton.clicked.connect(self.reject)

        okButton = QPushButton(_('OK'))
        okButton.setDefault(True)
        okButton.clicked.connect(self.accept)

        addButton = QPushButton('+')
        addButton.clicked.connect(self.add)

        buttonBox = QHBoxLayout()
        buttonBox.addWidget(addButton)
        buttonBox.addStretch(1)
        buttonBox.addWidget(cancelButton)
        buttonBox.addWidget(okButton)

        layout = QVBoxLayout()
        layout.addWidget(self._view)
        layout.addLayout(buttonBox)

        self.setLayout(layout)

        self.accepted.connect(self.save)

        self.setWindowTitle(_('Admin.edit' + model.table))
        self.resize(600, 300)
        self._view.resizeColumnsToContents()

    def save(self):
        self._view.model().save()

    def add(self):
        raise NotImplementedError()

class UserEditor(Editor):
    def __init__(self, parent=None):
        super().__init__(UserTableModel(), parent)

    def add(self):
        try:
            dialog = NewUserDialog()
            name, passwd = dialog.get_info()

            if not dialog.cancelled:
                patts.create_user(name, '%', passwd)
                self._view.setModel(UserTableModel())
                self._view.resizeColumnsToContents()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()

class ParentTaskValidator(QValidator):
    def __init__(self, row, get_num_rows):
        super().__init__()
        self._id = row + 1
        self._nr = get_num_rows

    def validate(self, input, pos):
        if len(input) == 0:
            return (QValidator.Intermediate, input, pos)

        try:
            n = int(input)

            if n < 0 or n > self._nr():
                return (QValidator.Invalid, input, pos - 1)

            if n == self._id:
                return (QValidator.Intermediate, input, pos)

            return (QValidator.Acceptable, input, pos)
        except ValueError:
            return (QValidator.Invalid, input, pos - 1)

class TaskTypeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent_column, get_num_rows):
        super().__init__()
        self._pc = parent_column
        self._nr = get_num_rows

    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0

        if index.column() == self._pc:
            editor = QLineEdit(widget)
            editor.setValidator(ParentTaskValidator(index.row(), self._nr))
            return editor

        return super().createEditor(widget, option, index)

class TaskTypeEditor(Editor):
    def __init__(self, parent=None):
        model = TaskTypeTableModel()
        super().__init__(model, parent)
        self._view.setItemDelegate(TaskTypeItemDelegate(model.parent_column,
                                                        self._row_count))

    def add(self):
        try:
            patts.create_task('0', '')
            self._view.setModel(TaskTypeTableModel())
            self._view.resizeColumnsToContents()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()

    def _row_count(self):
        return self._view.model().rowCount()
