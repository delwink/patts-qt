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

def split_host(host):
    srv = host
    port = '0'

    if '[' in host and ']' in host:
        if host[0] != '[' or host.count('[') > 1 or host.count(']') > 1:
            raise ValueError('Invalid brackets in IPv6 address')

        bracket_index = host.index(']')
        srv = host[1:bracket_index]

        post = host[bracket_index + 1:]
        if post and post[0] == ':':
            port = str(int(post[1:]))
    elif ':' in host:
        if host.count(':') > 1:
            raise ValueError('Invalid colon in IPv4 address')

        split = host.split(':')
        srv = split[0]
        port = split[1]

    return (srv, port)
