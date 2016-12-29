#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script de instalación para `simpbot'.
#
# Autor: Ismael Lugo <ismaelrlgv@gmail.com>
# Ultimo cambio: 29-12-2016
# URL: https://www.kwargs.net.ve/projects/simpbot
# GIT: https://github.com/IsmaelRLG/simpbot

from setuptools import setup
import simpbot

setup(
    name='simpbot',
    version=simpbot.__version__,
    author=simpbot.__author__,
    author_email="ismaelrlgv@gmail.com",
    description="Simple Bot (SimpBot) - IRC (Internet Relay Chat) Bot",
    url="https://kwargs.net.ve/projects/SimpBot",
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
    scripts=['bin/simpbot'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Spanish",
        "Operating System :: POSIX :: Linux",
        #"Operating System :: Microsoft :: Windows",  # Proximamente...
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications :: Chat :: Internet Relay Chat"
    ]
)
