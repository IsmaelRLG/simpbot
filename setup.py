#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script de instalación para `simpbot'.
#
# Autor: Ismael Lugo <ismaelrlgv@gmail.com>
# Ultimo cambio: 10-09-2016
# URL: https://www.kwargs.net.ve/projects/simpbot
# GIT: https://github.com/IsmaelRLG/simpbot

from setuptools import setup

setup(
    name='simpbot',
    author="Ismael Lugo",
    author_email="ismaelrlgv@gmail.com",
    description="Simple Bot (SimpBot) - IRC (Internet Relay Chat) Bot",
    url="https://www.kwargs.net.ve/projects/SimpBot",
    packages=['simpbot'],
    scripts=['bin/simpbot'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Spanish",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications :: Chat"
    ]
)



