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
from PyQt4.QtGui import QKeySequence, QLabel, QMainWindow, QPushButton
from PyQt4.QtGui import QTableView, QVBoxLayout, QWidget
from .aboutdialog import AboutDialog
from .config import get, put
from .editor import TaskTypeEditor, UserEditor
from .hostname import split_host
from .lang import _
from .exception import ExceptionDialog, format_exc
from .report import UserSummaryReportDialog, TaskSummaryReportDialog

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
                text = _('VersionCheck.ahead').format(-diff, version_word)
        elif diff > 0:
            text = _('VersionCheck.behind').format(diff, version_word)
        else:
            text = _('VersionCheck.equal')

        layout.addWidget(QLabel(text.replace('\\n', '\n')))

        quitButton = QPushButton(_('VersionCheck.quit'))
        quitButton.clicked.connect(self.reject)

        continueButton = QPushButton(_('VersionCheck.continue'))
        continueButton.clicked.connect(self.accept)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(quitButton)
        buttonBox.addWidget(continueButton)

        layout.addLayout(buttonBox)
        self.setWindowTitle(_('VersionCheck.title'))

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
        srv, port = split_host(host)

        patts.init(host=srv, user=user, passwd=passwd, database=database,
                   port=port)

        super().__init__()

        version_diff = patts.version_check()
        if version_diff:
            d = VersionCheckDialog()
            d.rejected.connect(self.close)
            d.exec_()

        menuBar = self.menuBar()

        sessionMenu = menuBar.addMenu(_('Session'))

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
            TaskTypeEditor(self).exec_()
        except Exception as e:
            ExceptionDialog(format_exc()).exec_()

    def _user_summary_report(self):
        UserSummaryReportDialog(self).exec_()

    def _task_summary_report(self):
        TaskSummaryReportDialog(self).exec_()
