#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script de instalación para `simpbot'.
#
# Autor: Ismael Lugo <ismaelrlgv@gmail.com>
# Ultimo cambio: 19-03-2017
# URL: https://www.kwargs.net.ve/projects/simpbot
# GIT: https://github.com/IsmaelRLG/simpbot

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install the setuptools package")
    exit(0)

from os.path import join, exists
from os.path import dirname as dir
import simpbot
import platform
import shutil

currentdir = dir(__file__)
bindir = join(currentdir, 'bin')
script = 'simpbot.py'
if platform.system() == 'Linux':
    if exists(join(bindir, script)):
        shutil.move(join(bindir, script), join(bindir, 'simpbot'))
    script = 'simpbot'

requires = file(join(currentdir, 'requires.txt'), 'r').read().splitlines()

setup(
    name='simpbot',
    version=simpbot.__version__,
    author=simpbot.__author__,
    author_email="ismaelrlgv@gmail.com",
    description="Simple Bot (SimpBot) - IRC (Internet Relay Chat) Bot",
    url="https://github.com/IsmaelRLG/simpbot",
    packages=find_packages(),
    package_data={'simpbot': [join('localedata', '*.dat')]},
    scripts=[
        join('bin', script)
    ],
    requires=[

    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        "Topic :: Communications :: Chat :: Internet Relay Chat"
    ]
)
