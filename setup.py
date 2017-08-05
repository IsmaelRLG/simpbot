#!/usr/bin/env python
# SimpBot - Simple IRC Bot
#
# Author: Ismael Lugo <ismaelrlgv@gmail.com>
# GIT: https://github.com/IsmaelRLG/simpbot

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install the setuptools package")
    exit(1)

from os import walk
from os.path import join
from os.path import dirname as dir
import simpbot

requirements_file = 'requirements.txt'
currentdir = dir(__file__)
requires = open(join(currentdir, requirements_file), 'r').read().splitlines()

# searching plugins requirements...
for path, dirnames, filenames in walk(join(currentdir, 'simpmods')):
    if requirements_file in filenames:
        for req in open(join(path, requirements_file), 'r').read().splitlines():

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
    license='MIT',
    packages=find_packages(exclude=['extra']),
    package_data=dict(simpbot=[join('localedata', '*.dat')]),
    install_requires=requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Chat :: Internet Relay Chat"
    ],
    entry_points=dict(console_scripts=['simpbot = simpbot.cli:main'])
)
