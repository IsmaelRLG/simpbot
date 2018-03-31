# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2018, Ismael Lugo (kwargs)
###############################################################################
# simpbot
###############################################################################
LANG = 'es'
#                          MM/DD/YYYY
DATE_DAY_FORMAT = '%d-%m-%Y'
HOUR_FORMAT = '%H:%M:%S'
DATE_FULL_FORMAT = '[%d-%m-%Y](%H:%M:%S)'
# Directory tree
MAIN_DIR = '.simpbot'
FILE_SETTINGS =     'settings.py'
MAIN_MODDATA_DIR =  'moddata'
MAIN_MODULES_DIR =  'modules'
MAIN_LOG_DIR =      'log'
SUB_LOG_DIR_BOT =       'simpbot'
SUB_LOG_DIR_IRC =       'scrollback'

###############################################################################
# logging
###############################################################################
DEFAULT_LEVEL = 'DEBUG'
LOG_FILENAME = 'simpbot.log'
IRC_FORMAT = '[%(asctime)s] %(message)s'
FIL_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s: %(message)s'
STD_FORMAT = '%(levelname)-8s | %(name)s: %(message)s'
MAX_BACKUP = 10

###############################################################################
# schedule
###############################################################################
CHECK_JOBS = 1
#          H    M    S    D        Y
MAX_DATE = 24 * 60 * 60 * 364.25 * 2
DELAY = 900
MAX_ATTEMPTS = 4

###############################################################################
# cache
###############################################################################
#                                   M    S
UP_TO_DATE_CACHE =                  2  * 60
CACHE_DURATION_USER =               30 * 60
CACHE_DURATION_USER_PROPERTIES =    10 * 60
CACHE_DURATION_CHANNEL =            60 * 60
CACHE_DURATION_CHANNEL_PROPERTIES = 25 * 60
NO_EXISTS = '1fc595904f5443eeb5fe013ccbc7be05'
NO_M_LINK = '3673eb4ccfb3498abceec402bc65f612'
NO_M_KEY = 'b30b1e00d3614b7384532024a19cb09a'

###############################################################################
# cache
###############################################################################
# Config vartypes values
STRING = 0
FLOAT  = 1
INT    = 2
BOOL   = 3
PICKLE = 4

###############################################################################
# user
###############################################################################
USER_LANG = LANG
USER_DATE_DAY_FORMAT = DATE_DAY_FORMAT
USER_DATE_HOUR_FORMAT = HOUR_FORMAT
USER_DATE_FULL_FORMAT = DATE_FULL_FORMAT
USER_UNIQ_STATUS = 'user_status'

###############################################################################
# channel
###############################################################################
CHANNEL_LANG = LANG
CHANNEL_DATE_DAY_FORMAT = DATE_DAY_FORMAT
CHANNEL_DATE_HOUR_FORMAT = HOUR_FORMAT
CHANNEL_DATE_FULL_FORMAT = DATE_FULL_FORMAT
CHANNEL_UNIQ_STATUS = 'channel_status'
FLAG_FOUNDER = 'F'
FLAG_SUCCESSOR = 'S'
FLAGS = []

###############################################################################
# trigger
###############################################################################
AFTER = 0
BEFORE = 1
MAX_RUNLEVEL = 100
TGR_CONTINUE = '5ab24da0'
TGR_BREAK = 'a5184a38'
TGR_STOP = 'da9d4413'
TGR_SKIP = None

###############################################################################
# network
###############################################################################
DEFAULT_PORT = 6667
DEFAULT_SSL = False

def get(name):
    return __dict__[name]
