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

from patts import setup
from PyQt4.QtGui import QApplication, QComboBox, QDialog, QHBoxLayout, QLabel
from PyQt4.QtGui import QPushButton, QVBoxLayout
from .config import get, put
from .hostname import split_host
from .lang import _, get_langs, set_lang
from .login import get_login
from .mainwindow import MainWindow
from .exception import ExceptionDialog, format_exc

def value_to_index(dict, value):
    i = 0
    for key in dict:
        if dict[key] == value:
            return i
        i += 1

class LanguageDialog(QDialog):
    def __init__(self):
        super().__init__()

        text = QLabel('Choose a language: ') # intentionally English
        self._selection = QComboBox()
        okButton = QPushButton(_('OK'))
        layout = QVBoxLayout()
        inputBox = QHBoxLayout()
        buttonBox = QHBoxLayout()

        self._langs = get_langs()
        self._selection.addItems([lang for lang in self._langs])
        self._selection.currentIndexChanged.connect(self._set_lang)
        self._lang = value_to_index(self._langs, 'en_US')
        self._selection.setCurrentIndex(self._lang)
        okButton.clicked.connect(self.accept)

        inputBox.addWidget(text)
        inputBox.addWidget(self._selection)
        buttonBox.addStretch(2)
        buttonBox.addWidget(okButton)

        layout.addLayout(inputBox)
        layout.addLayout(buttonBox)

        self.setLayout(layout)

    def _set_lang(self, s):
        self._lang = s

    @property
    def lang(self):
        return self._langs[self._selection.itemText(self._lang)]

class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()

        question = QLabel(_('Setup.want'))
        yesButton = QPushButton(_('yes'))
        noButton = QPushButton(_('no'))
        layout = QVBoxLayout()
        buttonBox = QHBoxLayout()

        buttonBox.addStretch(1)
        buttonBox.addWidget(noButton)
        buttonBox.addWidget(yesButton)
        yesButton.setDefault(True)
        yesButton.clicked.connect(self.accept)
        noButton.clicked.connect(self.reject)

        layout.addWidget(question)
        layout.addLayout(buttonBox)
        self.setLayout(layout)

class PattsApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self._canceled = False
        self._mwin = None
        self._sd = SetupDialog()
        self._sd.accepted.connect(self._setup)
        self._sd.rejected.connect(self._bad_db)

        if get('Global', 'firstrun').lower() == 'true':
            ld = LanguageDialog()
            rc = ld.exec_()
            if rc != QDialog.Accepted:
                exit(0) # canceled

            set_lang(ld.lang)
            put('Global', 'firstrun', 'false')

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

                    if errno in (1044, 1049):
                        self._sd.exec_()
                    elif errno == 1045:
                        self._login('Login.accessDenied')
                    elif errno == 2005:
                        self._login('Login.badHost')
                    else:
                        self._login('Error {}'.format(errno))

                    if self._canceled:
                        exit(0)
                elif type(e) is KeyError:
                    self._login('Login.badUser')
                elif type(e) is TypeError:
                    exit(0) # canceled
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
            self._canceled = True

    def exec_(self):
        if self._user and self._passwd and self._host and self._db:
            self._mwin.show()
            return super().exec_()
        else:
            if self._canceled:
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

    def _setup(self):
        try:
            srv, port = split_host(self._host)
            setup(host=srv, user=self._user, passwd=self._passwd,
                  database=self._db, port=port)
            self._login()
        except:
            ExceptionDialog(format_exc()).exec_()
            raise

    def _bad_db(self):
        self._login('Login.badDatabase')
