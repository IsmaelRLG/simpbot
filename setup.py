#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script de instalación para `simpbot'.
#
# Autor: Ismael Lugo <ismaelrlgv@gmail.com>
# Ultimo cambio: 29-12-2016
# URL: https://www.kwargs.net.ve/projects/simpbot
# GIT: https://github.com/IsmaelRLG/simpbot

try:
    from setuptools import setup
except ImportError:
    print("Please install the setuptools package")
    exit(0)

from os.path import join
import simpbot
import platform
import sys

kwargs = {}
if platform.system() == 'Windows' and 'py2exe' in sys.argv:
    try:
        import py2exe  # lint:ok
    except ImportError:
        print('Please install py2exe')

    kwargs = {
        'console': [{
            'script': 'nombrescript.py',
            'description': 'Descripcion del programa.',
            'icon_resources': [(0, join('icons', 'simpbot-48x48.png'))]
            }],
        'zipfile': None,
        'options': {'py2exe': {
            'dll_excludes': ['w9xpopen.exe'],
            'bundle_files': 1,
            'compressed': True,
            'optimize': 2
            }},
     }

setup(
    name='simpbot',
    version=simpbot.__version__,
    author=simpbot.__author__,
    author_email="ismaelrlgv@gmail.com",
    description="Simple Bot (SimpBot) - IRC (Internet Relay Chat) Bot",
    url="https://github.com/IsmaelRLG/simpbot",
    packages=[
        'simpbot',
        'simpbot.request',
        'simpbot.admins',
        'simpbot.dbstore',
        'simpbot.bottools',
        'simpbot.moduletools',
        'simpbot.samples',
        'simpbot.commands',
        'simpmods',
        'simpmods.admin'
        ],

    package_data={'simpbot': [join('localedata', '*.dat')]},
    scripts=[
        join('bin', 'simpbot')
    ],
    requires=[
        'six'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Spanish",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        "Topic :: Communications :: Chat :: Internet Relay Chat"
    ]
)
