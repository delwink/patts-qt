##
##  patts-qt - Qt GUI client for PATTS
##  Copyright (C) 2016 Delwink, LLC
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

from datetime import datetime
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QCalendarWidget, QComboBox, QDialog, QHBoxLayout
from PyQt4.QtGui import QLabel, QPushButton, QVBoxLayout
from .exception import ExceptionDialog, format_exc
from .lang import _

_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def sort_types(keys, already_used):
    keys.sort()
    for key in keys:
        if key not in already_used:
            already_used.append(key)
            child_types = list(patts.get_child_types(key).keys())
            sort_types(child_types, already_used)

def task_time_sum(result_set):
    summary = {}
    for item in result_set:
        type = item['typeID']
        startTime = datetime.strptime(item['startTime'], _TIME_FORMAT)
        stopTime = datetime.strptime(item['stopTime'], _TIME_FORMAT)
        diff = stopTime - startTime

        try:
            summary[type] += diff
        except KeyError:
            summary[type] = diff

    return summary

def result_stamp(delta):
    minutes = (delta.seconds // 60) % 60
    hours = (delta.seconds // 3600) + (delta.days * 24)

    return _('Reports.timeSpentFormat').format(hours, format(minutes, '2d'))

class SummaryReportResultsDialog(QDialog):
    def __init__(self, data, summary, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        types = []
        patts.connect()
        try:
            info = self._title_info(data)
            self._title_string = _('Reports.summaryFor').format(info)

            titleLabel = QLabel(self._title_string)
            titleLabelFont = titleLabel.font()
            titleLabelFont.setBold(True)
            titleLabel.setFont(titleLabelFont)
            layout.addWidget(titleLabel)

            sort_types(list(summary.keys()), types)
            for type in types:
                if type not in summary:
                    continue

                type_info = patts.get_type_byid(type)

                resultBox = QHBoxLayout()
                resultBox.addWidget(QLabel(type_info['displayName'] + ':'))
                resultBox.addStretch(1)
                resultBox.addWidget(QLabel(result_stamp(summary[type])))

                layout.addLayout(resultBox)
        finally:
            patts.close()

        self.setWindowTitle(_('Reports.summaryResults'))
        self.setLayout(layout)

    def _title_info(self):
        raise NotImplementedError()

class SummaryReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._query = None
        self._query_format = None
        self._header = None
        self._result_dialog_type = None

        self._selection_box = QComboBox()
        self._init_selection_box()

        self._start_date = QCalendarWidget()
        self._end_date = QCalendarWidget()

        startDateBox = QHBoxLayout()
        startDateBox.addWidget(QLabel(_('Reports.startDate')))
        startDateBox.addWidget(self._start_date)

        endDateBox = QHBoxLayout()
        endDateBox.addWidget(QLabel(_('Reports.endDate')))
        endDateBox.addWidget(self._end_date)

        closeButton = QPushButton(_('close'))
        closeButton.clicked.connect(self.reject)

        runButton = QPushButton(_('Reports.run'))
        runButton.clicked.connect(self.accept)
        runButton.setDefault(True)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(closeButton)
        buttonBox.addWidget(runButton)

        layout = QVBoxLayout()
        layout.addWidget(self._selection_box)
        layout.addLayout(startDateBox)
        layout.addLayout(endDateBox)
        layout.addLayout(buttonBox)

        self.accepted.connect(self._run_report)
        self.setLayout(layout)

    def _run_report(self):
        if None in (self._query, self._query_format, self._header,
                    self._result_dialog_type):
            raise NotImplementedError('No query for report')

        try:
            query = self._query.format(*self._query_format)
            results = task_time_sum(patts.query(query))
            self._result_dialog_type(self._header, results, self.parent()).exec_()
        except Exception:
            ExceptionDialog(format_exc()).exec_()

    def _init_selection_box(self):
        raise NotImplementedError()

class UserSummaryReportResultsDialog(SummaryReportResultsDialog):
    def __init__(self, user, summary, parent=None):
        super().__init__(user, summary, parent)

    def _title_info(self, user):
        user = patts.get_user_byid(user)
        return '{} {} {}'.format(user['firstName'], user['middleName'],
                                 user['lastName'])

class UserSummaryReportDialog(SummaryReportDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._result_dialog_type = UserSummaryReportResultsDialog
        self._query = ('SELECT typeID,startTime,stopTime FROM TaskItem '
                       "WHERE state=1 AND userID='{}' AND stopTime IS NOT NULL "
                       "AND startTime>='{}' AND startTime<='{} 23:59:59'")

        self.setWindowTitle(_('Reports.userSummary'))

    def _init_selection_box(self):
        i = 0
        for user in patts.get_users():
            self._selection_box.addItem(user)
            if user == patts.get_user():
                user_index = i

            i += 1

        self._selection_box.setCurrentIndex(user_index)

    def _run_report(self):
        self._header = self._selection_box.currentText()
        start_date = self._start_date.selectedDate().toString(Qt.ISODate)
        end_date = self._end_date.selectedDate().toString(Qt.ISODate)
        self._query_format = (self._header, start_date, end_date)

        super()._run_report()

class TaskSummaryReportResultsDialog(SummaryReportResultsDialog):
    def __init__(self, type, summary, parent=None):
        super().__init__(type, summary, parent)

    def _title_info(self, type):
        type = patts.get_type_byid(type)
        return type['displayName']

class TaskSummaryReportDialog(SummaryReportDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._result_dialog_type = TaskSummaryReportResultsDialog
        self._query = ('SELECT typeID,startTime,stopTime FROM TaskItem '
                       "WHERE state=1 AND typeID={} AND stopTime IS NOT NULL "
                       "AND startTime>='{}' AND startTime<='{} 23:59:59'")

        self.setWindowTitle(_('Reports.taskSummary'))

    def _init_selection_box(self):
        types = patts.get_types()
        keys = [int(k) for k in types]
        keys.sort()

        for key in keys:
            type = str(key)
            text = '({}) {}'.format(type, types[type]['displayName'])
            self._selection_box.addItem(text)

    def _run_report(self):
        index = self._selection_box.currentText().index(')')
        self._header = self._selection_box.currentText()[1:index]
        start_date = self._start_date.selectedDate().toString(Qt.ISODate)
        end_date = self._end_date.selectedDate().toString(Qt.ISODate)
        self._query_format = (self._header, start_date, end_date)

        super()._run_report()
