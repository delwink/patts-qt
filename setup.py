import os
import re
import sys

from setuptools import setup

version = ''
with open('pattsgui/aboutdialog.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

data_files = []
if os.name == 'posix':
    usr_share = os.path.join(sys.prefix, 'share')
    data_files += [
        (os.path.join(usr_share, 'applications'), ['patts-qt.desktop'])
    ]

setup(
    name='patts-qt',
    version=version,
    description='Qt GUI client for PATTS',
    author='David McMackins II',
    author_email='david@delwink.com',
    url='http://delwink.com/software/patts.html',
    install_requires=['patts'],
    packages=['pattsgui'],

    package_data={
        '': ['COPYING'],
        'pattsgui': ['lang/*']
    },

    data_files=data_files,
    package_dir={'pattsgui': 'pattsgui'},
    scripts=['patts-qt'],
    include_package_data=True,
    license='AGPLv3'
)
