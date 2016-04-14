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

from PyQt4.QtCore import QAbstractTableModel, QObject, Qt, SIGNAL
from PyQt4.QtGui import QAction, QComboBox, QDialog, QHBoxLayout, QIcon
from PyQt4.QtGui import QKeySequence, QLabel, QLineEdit, QMainWindow
from PyQt4.QtGui import QPushButton, QTableView, QVBoxLayout, QWidget
from .aboutdialog import AboutDialog
from .config import get, put, OptionsDialog
from .editor import TaskTypeTreeEditor, UserEditor
from .hostname import split_host
from .lang import _
from .exception import ExceptionDialog, format_exc
from .report import UserSummaryReportDialog, TaskSummaryReportDialog

def _panic():
    patts.cleanup()
    exit(0)

class VersionCheckDialog(QDialog):
    def __init__(self, diff, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        if abs(diff) == 1:
            version_word = _('VersionCheck.version')
        else:
            version_word = _('VersionCheck.versions')

        if diff < 0:
            if patts.get_db_version() == 0:
                text = _('VersionCheck.maintenance')
            else:
                text = _('VersionCheck.behind').format(-diff, version_word)
        elif diff > 0:
            text = _('VersionCheck.ahead').format(diff, version_word)
        else:
            text = _('VersionCheck.equal')

        layout.addWidget(QLabel(text))

        quitButton = QPushButton(_('VersionCheck.quit'))
        quitButton.clicked.connect(self.reject)

        continueButton = QPushButton(_('VersionCheck.continue'))
        continueButton.clicked.connect(self.accept)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(quitButton)
        buttonBox.addWidget(continueButton)

        layout.addLayout(buttonBox)
        self.setLayout(layout)
        self.setWindowTitle(_('VersionCheck.title'))

class TryAgainDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(_('ChangePasswd.tryAgain')))

        okButton = QPushButton(_('OK'))
        layout.addWidget(okButton)
        okButton.clicked.connect(self.accept)

        self.setLayout(layout)
        self.setWindowTitle(_('ChangePasswd.tryAgainTitle'))

class ChangePasswordDialog(QDialog):
    def __init__(self, old_pw, parent=None):
        super().__init__(parent)

        self._canceled = False
        self._pw = old_pw

        layout = QVBoxLayout()

        labelBox = QVBoxLayout()
        labelBox.addWidget(QLabel(_('ChangePasswd.current')))
        labelBox.addWidget(QLabel(_('ChangePasswd.new')))
        labelBox.addWidget(QLabel(_('ChangePasswd.confirm')))

        fieldBox = QVBoxLayout()

        self._cur_box = QLineEdit()
        self._cur_box.setEchoMode(QLineEdit.Password)
        fieldBox.addWidget(self._cur_box)

        self._new_box = QLineEdit()
        self._new_box.setEchoMode(QLineEdit.Password)
        fieldBox.addWidget(self._new_box)

        self._confirm_box = QLineEdit()
        self._confirm_box.setEchoMode(QLineEdit.Password)
        fieldBox.addWidget(self._confirm_box)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)

        cancelButton = QPushButton(_('cancel'))
        cancelButton.clicked.connect(self.reject)
        buttonBox.addWidget(cancelButton)

        okButton = QPushButton(_('OK'))
        okButton.setDefault(True)
        okButton.clicked.connect(self.accept)
        buttonBox.addWidget(okButton)

        labelFieldBox = QHBoxLayout()
        labelFieldBox.addLayout(labelBox)
        labelFieldBox.addLayout(fieldBox)
        layout.addLayout(labelFieldBox)
        layout.addLayout(buttonBox)

        self.rejected.connect(self._cancel)
        self.setLayout(layout)
        self.setWindowTitle(_('ChangePasswd.title'))

    def get_new_pw(self):
        self.exec_()
        while (not self._canceled
               and (self._cur_box.text() != self._pw
                    or not self._new_box.text()
                    or self._new_box.text() != self._confirm_box.text())):
            TryAgainDialog(self.parent()).exec_()
            self.exec_()

        return self._new_box.text()

    def _cancel(self):
        self._canceled = True

    @property
    def canceled(self):
        return self._canceled

class CurrentTaskModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._rows = [('', None, None)]

        tree = patts.get_tree()

        keys = list(tree.keys())
        keys.sort()
        for i in range(len(keys)):
            item = tree[keys[i]]
            self._rows.insert(1, (keys[i], item['typeID'], item['startTime']))

    def rowCount(self, parent=None):
        return len(self._rows)

    def columnCount(self, parent=None):
        return len(self._rows[0])

    def flags(self, index):
        flags = Qt.ItemIsEnabled
        if (index.row() == 1 and index.column() == 2) or index.row() == 0:
            flags |= Qt.ItemIsEditable

        return flags

    def data(self, index, role):
        if role in (Qt.DisplayRole, Qt.EditRole) and index.row() > 0:
            if index.column() == 0:
                type = patts.get_type_byid(self._rows[index.row()][1])
                return type['displayName']
            elif index.column() == 1:
                return self._rows[index.row()][2]
            else:
                return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return _('TaskTable.typeID')
                elif section == 1:
                    return _('TaskTable.startTime')
                else:
                    return None

            return self._rows[section][0]

class CurrentTaskView(QTableView):
    def __init__(self):
        super().__init__()
        self._triggers = []

    def setModel(self, model):
        super().setModel(model)

        current_task = patts.get_active_task()
        if current_task:
            parent_id = current_task[list(current_task.keys())[0]]['typeID']
        else:
            parent_id = '0'

        child_tasks = patts.get_child_types(parent_id)
        self._select_box = QComboBox()

        i = 0
        self._task_map = {}
        for task in child_tasks:
            self._select_box.addItem(child_tasks[task]['displayName'])
            self._task_map[i] = task
            i += 1

        self.setIndexWidget(model.createIndex(0, 0), self._select_box)

        clockInButton = QPushButton(_('TaskTable.clockIn'))
        clockInButton.clicked.connect(self._clock_in)
        self.setIndexWidget(model.createIndex(0, 1), clockInButton)

        if parent_id != '0':
            clockOutButton = QPushButton(_('TaskTable.clockOut'))
            clockOutButton.clicked.connect(self._clock_out)
            self.setIndexWidget(model.createIndex(1, 2), clockOutButton)

        self.resizeColumnsToContents()

    def add_trigger(self, f):
        self._triggers.append(f)

    def _clock_in(self):
        try:
            patts.clockin(self._task_map[self._select_box.currentIndex()])
            for trigger in self._triggers:
                trigger()
        except Exception as e:
            if not (type(e) is KeyError and str(e) == '-1'):
                ExceptionDialog(format_exc()).exec_()

    def _clock_out(self):
        try:
            patts.clockout(list(patts.get_active_task().keys())[0])
            for trigger in self._triggers:
                trigger()
        except:
            ExceptionDialog(format_exc()).exec_()

class MainWindowCentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        self._view = CurrentTaskView()
        self._view.setModel(CurrentTaskModel())
        self._view.add_trigger(self._load_tree)
        layout.addWidget(self._view)

        refreshButton = QPushButton(_('MainWindow.refresh'))
        refreshButton.setShortcut(QKeySequence.Refresh)
        refreshButton.clicked.connect(self._load_tree)
        layout.addWidget(refreshButton)

        self.setLayout(layout)

    def _load_tree(self):
        self._view.setModel(CurrentTaskModel())

class MainWindow(QMainWindow):
    def __init__(self, user, passwd, host, database):
        self._srv, self._port = split_host(host)
        self._user = user
        self._pw = passwd
        self._db = database

        super().__init__()

        self._log_in()

        version_diff = patts.version_check()
        if version_diff:
            d = VersionCheckDialog(version_diff)
            d.rejected.connect(_panic)
            d.exec_()

        menuBar = self.menuBar()

        sessionMenu = menuBar.addMenu(_('Session'))

        optionsAction = QAction(_('OptionsDialog.title'), self)
        optionsAction.triggered.connect(self._open_options)
        sessionMenu.addAction(optionsAction)

        sessionMenu.addSeparator()

        passwdAction = QAction(_('ChangePasswd.title'), self)
        passwdAction.triggered.connect(self._change_pw)
        sessionMenu.addAction(passwdAction)

        logoutAction = QAction(_('Session.LogOut'), self)
        logoutAction.triggered.connect(self._log_out)
        sessionMenu.addAction(logoutAction)

        quitAction = QAction(_('Session.Quit'), self)
        quitAction.setIcon(QIcon.fromTheme('application-exit'))
        quitAction.setShortcut(QKeySequence.Quit)
        quitAction.triggered.connect(self.close)
        sessionMenu.addAction(quitAction)

        reportsMenu = menuBar.addMenu(_('Reports'))

        userReportAction = QAction(_('Reports.userSummary'), self)
        userReportAction.triggered.connect(self._user_summary_report)
        reportsMenu.addAction(userReportAction)

        taskReportAction = QAction(_('Reports.taskSummary'), self)
        taskReportAction.triggered.connect(self._task_summary_report)
        reportsMenu.addAction(taskReportAction)

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

        self.setCentralWidget(MainWindowCentralWidget())

        self.resize(int(get('MainWindow', 'width')),
                    int(get('MainWindow', 'height')))
        if get('MainWindow', 'max').lower() == 'true':
            self.showMaximized()
        self.setWindowTitle(_('MainWindow.title').format(host, database, user))

    def closeEvent(self, event):
        self._save_dims()
        patts.cleanup()
        super().closeEvent(event)

    def _log_in(self):
        patts.init(host=self._srv, user=self._user, passwd=self._pw,
                   database=self._db, port=self._port)

    def _open_options(self):
        OptionsDialog(self).exec_()

    def _change_pw(self):
        d = ChangePasswordDialog(self._pw, self)
        pw = d.get_new_pw()

        if not d.canceled:
            try:
                pw = patts.escape_string(pw)
                patts.query("SET PASSWORD=PASSWORD('{}')".format(pw))
            except Exception as e:
                ExceptionDialog(format_exc()).exec_()

            self._pw = pw
            patts.cleanup()
            self._log_in()

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
            UserEditor(self).exec_()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()

    def _show_tasks(self):
        try:
            TaskTypeTreeEditor(self).exec_()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()

    def _user_summary_report(self):
        UserSummaryReportDialog(self).exec_()

    def _task_summary_report(self):
        TaskSummaryReportDialog(self).exec_()
