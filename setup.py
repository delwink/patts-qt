from setuptools import setup
import re

version = ''
with open('patts-qt', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='patts-qt',
    version=version,
    description='Qt GUI client for PATTS',
    author='David McMackins II',
    author_email='david@delwink.com',
    url='http://delwink.com/software/patts.html',
    install_requires=['patts', 'sqon', 'PyQt4'],
    packages=['patts_gui'],
    package_data={'': ['COPYING']},
    package_dir={'patts_gui': 'gui'},
    scripts=['patts-qt'],
    include_package_data=True,
    license='AGPLv3'
)
