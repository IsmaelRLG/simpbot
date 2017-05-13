# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------
# configuration module

import random
from string import ascii_letters, digits, punctuation


def unsort(list):
    """Return a copy of unsorted list"""
    new_list = []
    for chance in range(len(list)):
        char = random.choice(list)
        list.remove(char)
        new_list.append(char)
    return new_list

entropy = 5
anti_flood = (20, 60)  # (lines, time in seconds)
full_block = ascii_letters + digits
slct_block = list(full_block + (punctuation * entropy))
slct_block = ''.join(unsort(unsort(unsort(unsort(unsort(slct_block))))))
min_len = 10  # minimum of chars in line
p_increase = 400  # Percentage to increase
init_level = 100  # First level
default_coins = 0  # coins awarded by default
default_ecoins = 1  # Default earned coins
default_chances = 0  # Default possibilities for obtaining a part of the block
default_bp_size = 10  # Default maximum number of items that can be saved
hash_function = 'md5'
bot_account = 'Simp Bank'
dateformat = '[%X] %x'
max_entries = 5
columns_name = ['id column', 'sender column', 'receiver column',
                'amount column', 'column date']
table_format = {
    #'vertical_char':   ' ',
    #'junction_char':   ' ',
    #'horizontal_char': ' ',
    'border':           False,
    'print_empty':      False,
    'header_style':     'upper'}