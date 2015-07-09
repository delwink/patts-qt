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

from PyQt4.QtGui import QDialog, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt4.QtGui import QLineEdit, QDesktopWidget, QLabel, QPalette, QCheckBox
from PyQt4.QtCore import SIGNAL, QObject, Qt

from .lang import _
from .config import get, put

class LoginWindow(QDialog):
    def __init__(self, message='', logInText='LoginWindow.logIn',
                 cancelText='LoginWindow.cancel'):
        super(LoginWindow, self).__init__()

        self._cancelled = False
        self._ready = False

        logInButton = QPushButton(_(logInText))
        logInButton.clicked.connect(self._store_results)
        logInButton.setDefault(True)

        cancelButton = QPushButton(_(cancelText))
        cancelButton.clicked.connect(self._cancel)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(cancelButton)
        buttonBox.addWidget(logInButton)

        self.serverInput = QLineEdit()
        self.serverInput.setPlaceholderText(_('LoginWindow.server'))
        try:
            self.serverInput.setText(get('Login', 'host'))
        except KeyError:
            pass

        self.dbInput = QLineEdit()
        self.dbInput.setPlaceholderText(_('LoginWindow.database'))
        try:
            self.dbInput.setText(get('Login', 'database'))
        except KeyError:
            pass

        self.userInput = QLineEdit()
        self.userInput.setPlaceholderText(_('LoginWindow.user'))
        try:
            self.userInput.setText(get('Login', 'user'))
        except KeyError:
            pass

        self.passInput = QLineEdit()
        self.passInput.setPlaceholderText(_('LoginWindow.password'))
        self.passInput.setEchoMode(QLineEdit.Password)

        self.autoLogin = QCheckBox()
        self.autoLogin.setText(_('LoginWindow.autoLogin'))
        self.autoLogin.toggled.connect(self._set_auto)

        if message:
            self.errorLabel = QLabel(_(message))
            palette = QPalette()
            palette.setColor(QPalette.Foreground, Qt.red)
            self.errorLabel.setPalette(palette)

        inputBox = QVBoxLayout()
        if message:
            inputBox.addWidget(self.errorLabel)
        inputBox.addWidget(self.serverInput)
        inputBox.addWidget(self.dbInput)
        inputBox.addWidget(self.userInput)
        inputBox.addWidget(self.passInput)
        inputBox.addWidget(self.autoLogin)

        winLayout = QVBoxLayout()
        winLayout.addLayout(inputBox)
        winLayout.addLayout(buttonBox)

        self.setLayout(winLayout)
        self.setWindowTitle(_('LoginWindow.title'))
        self.resize(250, 200)
        self._center()

    def _store_results(self):
        self.hide()
        self.deleteLater()
        self._server = self.serverInput.text()
        self._db = self.dbInput.text()
        self._user = self.userInput.text()
        self._pass = self.passInput.text()
        self._ready = True

    def _cancel(self):
        self.hide()
        self.deleteLater()
        self._cancelled = True
        self._ready = True

    def _set_auto(self):
        if self.autoLogin.isChecked():
            put('Login', 'autologin', 'true')
        else:
            put('Login', 'autologin', 'false')

    def _center(self):
        geom = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        geom.moveCenter(centerPoint)
        self.move(geom.topLeft())

    def get_info(self):
        self.exec_()

        if not self._cancelled:
            return (self._user, self._pass, self._server, self._db)
        else:
            return (None, None, None, None)

def get_login(message=''):
    l = LoginWindow(message)
    return l.get_info()
