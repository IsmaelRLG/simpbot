# coding=utf8
"""
trigger.py - trigger utilities.

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

import inspect
from simpbot.envvars import TriggerIns
from simpbot.logger import getLogger
from simpbot.settings import AFTER, BEFORE, MAX_RUNLEVEL
from simpbot.settings import TGR_CONTINUE, TGR_SKIP, TGR_STOP, TGR_BREAK

logger = getLogger(__name__)


class trigger(object):
    __universal_before = {}
    __universal_after = {}
    __empty_list = []

    def __init__(self, name):
        self.module_name = name
        self.tggr_before = {}
        self.tggr_after = {}
        self.tggr_funcs = {}

    def _check(self, routine):
        if routine == BEFORE:
            return self.tggr_before
        elif routine == AFTER:
            return self.tggr_after
        else:
            raise ValueError('Routine unknown: %s' % routine)

    def _check_universal(self, routine):
        if routine == BEFORE:
            return self.__universal_before
        elif routine == AFTER:
            return self.__universal_after
        else:
            raise ValueError('Routine unknown: %s' % routine)

    def get_id(self, name):
        return self.module_name + '.' + name

    def add_universal(self, routine, runlevel, handler):
        routine = self._check_universal(routine)
        if runlevel not in routine:
            routine[runlevel] = []
        routine[runlevel].append(handler)
        logger.debug('Universal trigger added: %s', handler.__name__)

    def add(self, id, handler, runlevel, routine):
        if runlevel >= MAX_RUNLEVEL:
            raise ValueError('runlevel limit exceeded: %s/%s' %
            (runlevel, MAX_RUNLEVEL))

        id = self.get_id(id)
        if id not in routine:
            routine[id] = {}

        if runlevel not in routine:
            routine[id][runlevel] = []

        routine[id][runlevel].append(handler)
        logger.debug("Trigger '%s' added to '%s'", handler.__name__, id)

    def routine(self, status, _routine, end):
        runlevel = list(_routine.keys())
        runlevel.sort()
        for lvl in runlevel:
            for handler in _routine[runlevel]:
                logger.debug('running handler: %s.%s', status.id, handler.__name__ )
                try:
                    handler(status)
                except Exception as e:
                    logger.error('handler exception: %s', status.id, exc_info=e)
                    status.status = False
                    return status

                if status.status == TGR_SKIP or status.status == TGR_CONTINUE:
                    continue
                elif status.status == TGR_STOP:
                    status.status = False
                    return status
                elif status.status == TGR_BREAK:
                    break
        status.status = end

    def process(self, id, routine, status):
        # Universal
        r = self.routine(status, self._check_universal(routine), None)
        if r is status:
            return False

        routine = self._check(routine)
        if id in routine:
            self.routine(status, routine, True)
        return True

    def trigger(self, name):
        id = self.get_id(name)
        def function(func):
            def wrap(*args, **kwargs):
                status = exec_status(
                    id=id,
                    status=None,
                    value=None,
                    func=func,
                    args=args,
                    kwargs=kwargs)

                if not self.process(id, BEFORE, status):
                    return
                status.value = status.func(*status.args, **status.kwargs)
                self.process(id, AFTER, status)
                return status.value
            wrap.__name__ = name
            return wrap
        function.__name__ = name
        return function


class exec_status:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def return_continue(self):
        self.status = TGR_CONTINUE

    def return_skip(self):
        self.status = TGR_SKIP

    def return_stop(self):
        self.status = TGR_STOP

    def return_break(self):
        self.status = TGR_BREAK

    def get(self, **kwargs):
        result = []
        reverse_kwargs = {}
        for k, i in kwargs.items():
            reverse_kwargs[i] = k

        index = list(reverse_kwargs.keys())
        index.sort()
        for i in index:
            try:
                result.append(self.args[i])
            except IndexError:
                pass
            else:
                continue

            try:
                result.append(self.kwargs[reverse_kwargs[i]])
            except KeyError:
                result.append(None)
        return result


def getTrigger(name=None):
    if name is None:
        name = inspect.getmodule(inspect.stack()[1])
    if name in TriggerIns:
        return TriggerIns[name]
    TriggerIns[name] = trigger(name)
    return TriggerIns[name]
