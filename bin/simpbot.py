#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import sys
import simpbot


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        del args[0]

    if len(args) == 0 or args[0] not in simpbot.envvars.parsers:
        print(simpbot.cli.locale['available commands'])
        print('=' * len(simpbot.cli.locale['available commands']))
        print(', '.join(simpbot.envvars.parsers.keys()))
        exit(1)

    parser = simpbot.envvars.parsers[args[0]]()
    try:
        parser.process()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as error:
        errmsg = simpbot.cli.locale['unexpected error'] % repr(error) + '\n'
        sys.stderr.write(errmsg)
        sys.stderr.flush()
