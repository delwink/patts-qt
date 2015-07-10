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

from os.path import expanduser, join, exists
from os import makedirs
from configparser import ConfigParser

CONFIG_DIR = join(expanduser('~'), '.patts')
CONFIG_PATH = join(CONFIG_DIR, 'config.ini')
config = ConfigParser()

DEFAULTS = {
    'Global': {
        'lang': 'en_US'
    },

    'Login': {
        'autologin': 'false',
        'user': '',
        'passwd': '',
        'host': '',
        'database': ''
    },

    'MainWindow': {
        'width': '800',
        'height': '600'
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
