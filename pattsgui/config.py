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
from configparser import ConfigParser

CONFIG_PATH = join(expanduser('~'), '.patts', 'config.ini')
config = ConfigParser()

if not exists(CONFIG_PATH): # need to write default settings
    config['Global']['lang'] = 'en_US'

    with open(CONFIG_PATH, 'w') as f:
        config.write(f)
else:
    config.read(CONFIG_PATH)

def get(section, key):
    return config[section][key]

def put(section, key, value):
    config[section][key] = value
    with open(CONFIG_PATH, 'w') as f:
        config.write(f)
