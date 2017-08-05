# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import time
import re
import os
import base64
import logging
logging = logging.getLogger('simpbot')

from six.moves import _thread
from six.moves import cPickle
from six import string_types
from six import PY3

from simpbot.envvars import cfg


class BaseError(Exception):
    string = "SCheduler '%(name)s': %(msg)s"

    def __init__(self, **kwargs):
        super(BaseError, self).__init__()
        self.kwargs = kwargs
        if not 'msg' in kwargs:
            self.kwargs['msg'] = self.msg

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(str(self)))

    def __str__(self):
        return self.string % self.kwargs


class DataError(BaseError):
    string = "File '%(name)s'; %(msg)s"

    def __init__(self, **kwargs):
        super(DataError, self).__init__(**kwargs)


class LockError(BaseError):
    msg = 'Cannot lock, already locked'

    def __init__(self, **kwargs):
        super(LockError, self).__init__(**kwargs)


class ReleaseError(BaseError):
    msg = 'Cannot release, already released'

    def __init__(self, **kwargs):
        super(LockError, self).__init__(**kwargs)

PENDING = 0
SUCCESS = 1
FAILED  = 2
ABORT   = 3
schedulers = {}
root_scheduler = '__root__'


class SCheduler(object):
    __header = re.compile('----- BEGIN (?P<content>.+) -----', re.IGNORECASE)
    __footer = re.compile('----- END (?P<content>.+) -----', re.IGNORECASE)
    __stop_all = False
    __lock_all = False

    def FLock(function):
        def argwrapper(self, *args, **kwargs):
            if self.__running:
                while self.__running:
                    time.sleep(0.1)

            self.__acquire += 1
            j_id = self.__acquire
            if self.__acquire == 1 and not self.__lock:
                self.lock()

            value = function(self, *args, **kwargs)
            if self.__acquire == j_id:
                if self.__lock:
                    self.release()
                self.__acquire = 0
            return value
        argwrapper.__name__ = function.__name__
        return argwrapper

    @classmethod
    def stop_all(cls):
        cls.__stop_all = True

    @classmethod
    def lock_all(cls):
        cls.__lock_all = True

    @classmethod
    def release_all(cls):
        cls.__lock_all = False

    @classmethod
    def job_name(cls, job):
        if isinstance(job.func, string_types):
            return job.func
        else:
            return job.func.__name__

    def __init__(self, name, check, max_date, max_attempts, filename=None):
        self.jobs = []
        self.name = name
        self.check = check
        self.max_date = max_date
        self.max_attempts = max_attempts
        self.filename = filename
        self.__stop = False
        self.__lock = False
        self.__loop = False
        self.__status = False
        self.__running = False
        self.__acquire = 0
        self.__loaded = False
        self.__to_sort = []
        self.__to_delete = []

    def __repr__(self):
        return '<SCheduler name="%s", total_jobs=%s, status="%s">' % \
        (self.name, len(self.jobs), 'started' if self.__status else 'stopped')

    def status(self):
        return self.__status and not self.__lock

    def lock(self):
        if self.__lock:
            raise LockError(name=self.name)
        self.__lock = True

    def release(self):
        if not self.__lock:
            raise ReleaseError(name=self.name)
        self.__lock = False

    def _sort(self):
        sorted_jobs = []
        epoch = time.time()
        for job in self.jobs:
            date = job.total_seconds(epoch)
            for s_job in sorted_jobs:
                if date < s_job.total_seconds(epoch):
                    sorted_jobs.insert(sorted_jobs.index(s_job), job)
                    break
            else:
                sorted_jobs.append(job)
        del self.jobs[:]
        self.jobs.extend(sorted_jobs)

    @FLock
    def sort(self):
        self._sort()

    @FLock
    def add_job(self, job, epoch=None):
        epoch = epoch or time.time()
        date = job.total_seconds(epoch)
        for s_job in self.jobs:
            if date < s_job.total_seconds(epoch):
                self.jobs.insert(self.jobs.index(s_job), job)
                break
        else:
            self.jobs.append(job)

    def new_job(self, func, exec_date, args, kwargs, thread=False, rerun=None, delay=None):
        if exec_date > self.max_date:
            exec_date = self.max_date

        epoch = time.time()
        job = Job(
            epoch,
            epoch + exec_date,
            self.max_attempts,
            delay or exec_date,
            rerun, func, args, kwargs)

        if thread:
            job.background()
        self.add_job(job, epoch)

    @FLock
    def del_job(self, job):
        self.jobs.remove(job)

    def write_file(self, fp):
        header = self.__header.pattern
        footer = self.__footer.pattern
        l_content = 'JOB: DATE=%s, EXEC=%s, RERUN=%s'
        for job in self.jobs:
            try:
                data = base64.b64encode(cPickle.dumps(job))
                if PY3:
                    data = data.decode()
            except:
                logging.warning('Cannot save job, skipping...')
                continue

            content = l_content % (job.date, job.exec_date, job.rerun)
            fp.write(header.replace('(?P<content>.+)', content) + '\n')
            t = len(data)
            I = 76
            i = 0
            n = 76

            while i < t:
                print((i, n, t))
                fp.write(data[i:n] + '\n')
                i += I
                n += I

            fp.write(footer.replace('(?P<content>.+)', content) + '\n')

    @FLock
    def write(self):
        if not self.filename:
            return

        with open(self.filename, 'w') as fp:
            self.write_file(fp)

    def load_file(self, fp):
        init = False
        end = False
        n_line = 0
        a_jobs = 0
        s_jobs = 0
        data = []

        for line in fp.read().splitlines():
            n_line = 0
            if self.__header.match(line):
                if init:
                    raise DataError(name=fp.name,
                        msg='Line #%s; Missing closing line' % n_line)

                init = True
                if end:
                    end = False
                continue
            elif self.__footer.match(line):
                if end:
                    raise DataError(name=fp.name,
                        msg='Line #%s; Already closed' % n_line)

                end = True
                if init:
                    init = False
                try:
                    self.jobs.append(cPickle.loads(base64.b64decode(''.join(data))))
                except Exception as error:
                    logging.warning('Cannot load job, skipping, error msg: %s', error)
                    s_jobs += 1
                    continue
                else:
                    a_jobs += 1
                    del data[:]
            elif init:
                data.append(line)
        if a_jobs > 0:
            self.sort()
        logging.debug('Total of added jobs %s, Skipped %s', a_jobs, s_jobs)

    @FLock
    def load(self):
        if self.__loaded or not self.filename:
            return

        if not os.path.exists(self.filename):
            return

        with open(self.filename, 'rb' if PY3 else 'r') as fp:
            self.load_file(fp)

    def mainloop(self):
        if self.__status:
            return
        else:
            self.__status = True

        obj = hasattr(self, 'obj')

        while not self.__stop and not self.__stop_all:
            try:
                time.sleep(self.check)
                if self.__lock or self.__lock_all or len(self.jobs) == 0:
                    continue

                epoch = time.time()
                if self.jobs[0].total_seconds(epoch) > 0:
                    # if the first is not within the time, the others are equal
                    # are sorted from the nearest time to the farthest...
                    continue

                self.__running = True
                for job in self.jobs:
                    if job.total_seconds(epoch) > 0:
                        break
                    if job.run_status():
                        continue
                    logging.debug('Running job "%s"...', self.job_name(job))
                    if obj:
                        job(self.__to_delete, self.__to_sort, epoch, self.obj)
                    else:
                        job(self.__to_delete, self.__to_sort, epoch)

                for job in self.__to_delete:
                    logging.debug('Removing job "%s"...', self.job_name(job))
                    self.jobs.remove(job)
                del self.__to_delete[:]

                if len(self.__to_sort) > 0:
                    del self.__to_sort[:]
                    logging.debug('Sorting jobs...')
                    self._sort()

                self.__running = False
            except KeyboardInterrupt:
                self.__status = False
                self.__running = False
                break
        else:
            self.__status = False

    def start(self):
        _thread.start_new(self.mainloop, (), {})

    def stop(self):
        self.__stop = True


class Job(object):

    def __init__(self, date, exec_date, ma, dof, ru, func, args, kwargs, id=None):
        """
        Job object

        :param date: Fecha de creación de la tarea
        :param exec_date: Fecha de ejecución de la tarea
        :param ma: Máximo de reintentos
        :param dof: Tiempo de retraso para la próxima ejecución
        :param ru: Número de repeticiones
        :param func: Función para ejecutar (carga la util de la tarea)
        :param args: Argumentos posicionales para la función
        :param kwargs: Argumentos clave-valor para la función
        :param id: Identificador único para la tarea
        """

        self.last_epoch = None
        self.handlers = {'before': [], 'after': []}
        self.date = date
        self.exec_date = exec_date
        self._func = func
        self.args = tuple(args)
        self.kwargs = kwargs
        self.status = 0  # 0: pending, 1: success, 2: failed, 3:abort
        self.__done = False
        self.__exec = False
        self.__thread = False
        self.__attempts = 0
        self.max_attempts = ma
        self.__rerun = ru
        self.delay = dof
        self.id = id

    def __call__(self, delete_list, sort_list, epoch):
        return self.run(delete_list, sort_list, epoch)

    def __repr__(self):
        cmps = []
        cmps.append('run_date=%s' % int(self.total_seconds(time.time())))
        if self.rerun == 0:
            cmps.append("rerun=('endless',)")
        elif self.rerun > 0:
            cmps.append("rerun=(%s, %s)" % (self.__attempts, self.rerun))

        cmps.append('delay=%s' % self.delay)
        return '<job %s>' % ' '.join(cmps)

    @property
    def func(self):
        return self._func

    @property
    def rerun(self):
        if isinstance(self.__rerun, bool):
            # 0: Infinite
            return 0 if self.__rerun else -1
        if isinstance(self.__rerun, int):
            return -1 if self.__rerun < 0 else self.__rerun
        else:
            return -1

    def total_seconds(self, epoch):
        return (self.exec_date - epoch)

    def _run_function(self, obj=None):
        self.__exec = True
        self.__attempts += 1
        if len(self.handlers['before']) > 0:
            for handler in self.handlers['before']:
                status = handler(self, obj)
                if status == FAILED:
                    return FAILED
                elif status == ABORT:
                    self.__done = True
                    return SUCCESS

        try:
            if obj is None:
                status = self.func(*self.args, **self.kwargs)
            else:
                status = self.func(obj)(*self.args, **self.kwargs)
        except Exception as error:
            logging.error('Job "%s": %s', SCheduler.job_name(self), repr(error))
            self.__exec = False
            return FAILED
        else:
            if status == FAILED:
                self.__exec = False
                return FAILED
            elif status == ABORT:
                self.__done = True
                self.__exec = False
                return SUCCESS

        if len(self.handlers['after']) > 0:
            for handler in self.handlers['after']:
                status = handler(self, obj)
                if status == FAILED:
                    self.__exec = False
                    return FAILED

        self.__exec = False
        self.__done = True
        return SUCCESS

    def run_function(self):
        self._run_function()

    def run_status(self):
        return self.__exec

    def _run(self, delete_list, sort_list, epoch, obj=None):
        if self.__thread:
            _thread.start_new(self.run_function, (), {})
            status = SUCCESS
        else:
            status = self.run_function(obj)

        self.status = status
        if status == FAILED:
            if self.__attempts >= self.max_attempts:
                delete_list.append(self)
                return ABORT
            else:
                self.exec_date = epoch + self.delay
                sort_list.append(self)

        # <success>
        elif self.rerun != -1:
            if self.rerun != 0 and self.__attempts >= self.rerun:
                delete_list.append(self)
            else:
                self.exec_date = epoch + self.delay
                sort_list.append(self)
        else:
            delete_list.append(self)
        # </success>
        return status

    def run(self, delete_list, sort_list, epoch):
        self._run(delete_list, sort_list, epoch)


class OBJ_SCheduler(SCheduler):

    def __init__(self, name, check, max_date, max_attempts, obj, filename=None):
        super(OBJ_SCheduler, self).\
        __init__(name, check, max_date, max_attempts, filename)
        self.obj = obj


class IRCJob(Job):

    def __call__(self, delete_list, sort_list, epoch, irc):
        return self.run(delete_list, sort_list, epoch, irc)

    def run(self, delete_list, sort_list, epoch, irc):
        self._run(delete_list, sort_list, epoch, irc)

    def func(self, irc):
        return getattr(irc, self._func.split(' ', 1)[1])

    def run_function(self, irc):
        self._run_function(irc)


def remove(name):
    return schedulers[name]


def insert(name, scheduler):
    schedulers[name] = scheduler


def basic_scheduler(name, obj=None, filename=None):
    if name in schedulers:
        return schedulers[name]

    if obj:
        schedulers[name] = OBJ_SCheduler(
            name,
            cfg.getint('CHECK_JOBS', 1),
            cfg.getint('MAX_DATE', 62942400),
            #cfg.getint('DELAY', 900),
            cfg.getint('MAX_ATTEMPTS', 4), obj, filename=filename)
    else:
        schedulers[name] = SCheduler(
            name,
            cfg.getint('CHECK_JOBS', 1),
            cfg.getint('MAX_DATE', 62942400),
            #cfg.getint('DELAY', 900),
            cfg.getint('MAX_ATTEMPTS', 4), filename=filename)

    return schedulers[name]


def getroot():
    return basic_scheduler(root_scheduler)
getroot()