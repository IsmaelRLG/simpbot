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
full_block = ascii_letters + digits
slct_block = list(full_block + (punctuation * entropy))
slct_block = ''.join(unsort(unsort(unsort(unsort(unsort(slct_block))))))
min_len = 10  # minimum of chars in line
p_increase = 400  # Percentage to increase
init_level = 100  # First level
default_coins = 0  # coins awarded by default
default_ecoins = 1  # Default earned coins
default_chances = 1  # Default possibilities for obtaining a part of the block
bot_account = 'bot account'
