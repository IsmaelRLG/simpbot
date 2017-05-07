#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script de instalación para `simpbot'.
#
# Author: Ismael Lugo <ismaelrlgv@gmail.com>
# Last change: 07-05-2017
# GIT: https://github.com/IsmaelRLG/simpbot

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install the setuptools package")
    exit(0)

from os import walk
from os.path import join, exists
from os.path import dirname as dir
import simpbot
import platform
import shutil

requirements_file = 'requirements.txt'
currentdir = dir(__file__)
bindir = join(currentdir, 'bin')
script = 'simpbot.py'
if platform.system() == 'Linux':
    if exists(join(bindir, script)):
        shutil.move(join(bindir, script), join(bindir, 'simpbot'))
    script = 'simpbot'

requires = file(join(currentdir, requirements_file), 'r').read().splitlines()

# searching plugins requirements...
for path, dirnames, filenames in walk(join(currentdir, 'simpmods')):
    if requirements_file in filenames:
        for req in file(join(path, requirements_file), 'r').read().splitlines():

            if req in requires:
                continue
            else:
                requires.append(req)


setup(
    name='simpbot',
    version=simpbot.__version__,
    author=simpbot.__author__,
    author_email="ismaelrlgv@gmail.com",
    description="Simple Bot (SimpBot) - IRC (Internet Relay Chat) Bot",
    url="https://github.com/IsmaelRLG/simpbot",
    packages=find_packages(exclude=['extra']),
    package_data={'simpbot': [join('localedata', '*.dat')]},
    scripts=[
        join('bin', script)
    ],
    install_requires=requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Chat :: Internet Relay Chat"
    ]
)
