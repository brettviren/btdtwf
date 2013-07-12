#!/usr/bin/env python

from distutils.core import setup

setup(
    name             = 'btdtwf',
    version          = '0.0.0',
    description      = 'Been There Done That Workflow',
    long_description = open('README.txt').read(),
    license          = 'GNU General Public License 2.0',
    url              = 'https://github.com/brettviren/btdtwf',
    author           = 'Brett Viren',
    author_email     = 'brett.viren@gmail.com',
    packages         = ['btdtwf'],
    data_files       = [
        ('doc', ['doc/*.org']),
        ],
    install_requires = ['bein>=1.1.0', 'pyutilib>4.5'],
    extras_require   = {
        'browser': ['bein-htminilims'],
        },
    )

    
