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

from os.path import join, realpath, dirname
from configparser import ConfigParser
from .config import get

_LANG = get('Global', 'lang')
_LDIR = join(dirname(realpath(__file__)), 'lang/')
_lfile = ConfigParser()

def _(s):
    _lfile.read(join(_LDIR, _LANG + '.lang'))
    try:
        return _lfile[_LANG][s]
    except KeyError:
        return s
        
