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

from configparser import ConfigParser
from os.path import expanduser, join, exists
from os import makedirs
from PyQt4.QtGui import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton
from PyQt4.QtGui import QVBoxLayout

CONFIG_DIR = join(expanduser('~'), '.patts')
CONFIG_PATH = join(CONFIG_DIR, 'config.ini')
config = ConfigParser()

DEFAULTS = {
    'Global': {
        'lang': 'en_US',
        'firstrun': 'true'
    },

    'Login': {
        'autologin': 'false',
        'user': '',
        'passwd': '',
        'host': '',
        'database': ''
    },

    'MainWindow': {
        'width': '450',
        'height': '500',
        'max': 'false'
    }
}

if not exists(CONFIG_PATH):
    if not exists(CONFIG_DIR):
        makedirs(CONFIG_DIR)

    with open(CONFIG_PATH, 'w') as f:
        config.write(f)
else:
    config.read(CONFIG_PATH)

def get(section, key):
    try:
        return config[section][key]
    except KeyError:
        return DEFAULTS[section][key]

def put(section, key, value):
    if get(section, key) != value:
        try:
            config[section][key] = value
        except KeyError:
            config[section] = {}
            config[section][key] = value

        with open(CONFIG_PATH, 'w') as f:
            config.write(f)

# down here against standards because of mutual dependency
from .lang import _, get_langs, set_lang

class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._langs = get_langs()
        self._lang_selection = QComboBox()

        i = 0
        lang_index = None
        for lang in self._langs:
            self._lang_selection.addItem(lang)
            if self._langs[lang] == get('Global', 'lang'):
                lang_index = i

            i += 1

        try:
            self._lang_selection.setCurrentIndex(lang_index)
        except TypeError:
            pass

        langBox = QHBoxLayout()
        langBox.addWidget(QLabel(_('OptionsDialog.lang')))
        langBox.addStretch(1)
        langBox.addWidget(self._lang_selection)

        cancelButton = QPushButton(_('cancel'))
        cancelButton.clicked.connect(self.reject)

        okButton = QPushButton(_('OK'))
        okButton.clicked.connect(self.accept)

        buttonBox = QHBoxLayout()
        buttonBox.addStretch(1)
        buttonBox.addWidget(cancelButton)
        buttonBox.addWidget(okButton)

        layout = QVBoxLayout()
        layout.addLayout(langBox)
        layout.addLayout(buttonBox)

        self.accepted.connect(self._save)

        self.setLayout(layout)
        self.setWindowTitle(_('OptionsDialog.title'))

    def _save(self):
        set_lang(self._langs[self._lang_selection.currentText()])
