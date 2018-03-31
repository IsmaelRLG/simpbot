# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2018, Ismael Lugo (kwargs)
from __future__ import unicode_literals

import time
import logging
from simpbot import settings as s
from six.moves import _thread
from six import string_types

logging = logging.getLogger(s.LOGGER_NAME)


class BaseError(Exception):
    string = "SCheduler '%(name)s': %(msg)s"

    def __init__(self, **kwargs):
        super(BaseError, self).__init__()
        self.kwargs = kwargs
        if 'msg' not in kwargs:
            self.kwargs['msg'] = self.msg

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(str(self)))

    def __str__(self):
        return self.string % self.kwargs


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
FAILED = 2
ABORT = 3
schedulers = {}
root_scheduler = '__root__'


class SCheduler(object):
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

    @staticmethod
    def job_name(job):
        if isinstance(job.func, string_types):
            return job.func
        else:
            return job.func.__name__

    def __init__(self, name, check, max_date, max_attempts):
        self.jobs = []
        self.name = name
        self.check = check
        self.max_date = max_date
        self.max_attempts = max_attempts
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

    def new_job(self, func, exec_date, args=None, kwargs=None, thread=False,
    rerun=None, delay=None, jobdb=None):
        if exec_date > self.max_date:
            exec_date = self.max_date
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        epoch = time.time()
        args = (
            #epoch,
            epoch + exec_date,
            self.max_attempts,
            delay or exec_date,
            rerun, func, args, kwargs)

        if jobdb:
            job = DBJob(*args)
        else:
            job = Job(*args)

        if thread:
            job.background()
        self.add_job(job, epoch)
        return job

    @FLock
    def del_job(self, job):
        self._del_job(job)

    def _del_job(self, job):
        if isinstance(job, list) and isinstance(job, tuple):
            job = (job,)

        for j in job:
            logging.debug('Removing job "%s"...', self.job_name(job))
            self.jobs.remove(job)

    def mainloop(self):
        if self.__status:
            return
        else:
            self.__status = True

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
                    job(self.__to_delete, self.__to_sort, epoch)

                self._del_job(self.__to_delete)
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


class DBSCheduler(SCheduler):

    def __init__(self, table, *args, **kwargs):
        super(DBSCheduler, self).__init__(*args, **kwargs)
        self.table = table

    def new_job(self, *args, **kwargs):
        kwargs['jobdb'] = True
        job = super(DBSCheduler, self).new_job(*args, **kwargs)
        job.setdb(job.record(self.table))

    def _del_job(self, job):
        if isinstance(job, list) and isinstance(job, tuple):
            job = (job,)

        for j in job:
            logging.debug('Removing job "%s"...', self.job_name(j))
            self.jobs.remove(j)
            j.delete()

    def load(self):
        if self.__loaded is True:
            return

        tload = 0
        for db in self.table.select():
            job = DBJob(
                db.exec_in,
                db.max_attempts,
                db.delay,
                db.p_rerun,
                db.function,
                db.args,
                db.kwargs
            )
            job.success(db.p_done)
            job.exec_status(db.p_exec)
            job.attempts(db.p_attempts)
            job.handlers.update(db.handlers)
            if db.p_thread:
                job.background()

            self.jobs.append(job)
        if tload > 0:
            self.sort()
        self.__loaded = True


class Job(object):

    def __init__(self, exec_date, ma, dof, ru, func, args, kwargs):
        self.handlers = {'before': [], 'after': []}
        #self.date = date
        self.exec_date = exec_date
        self._func = func
        self.args = args
        self.kwargs = kwargs
        #self.kwargs['__job__'] = self
        self.status = 0  # 0: pending, 1: success, 2: failed, 3:abort
        self.__done = False
        self.__exec = False
        self.__thread = False
        self.__attempts = 0
        self.max_attempts = ma
        self.__rerun = ru
        self.delay = dof

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
        if self.__rerun is None:
            # 0: Infinite
            return 0
        if isinstance(self.__rerun, int):
            return -1 if self.__rerun < 0 else self.__rerun
        else:
            return -1

    def total_seconds(self, epoch):
        return (self.exec_date - epoch)

    def attempts(self, n):
        self.__attempts = n

    def exec_status(self, s):
        self.__exec = s

    def run_function(self):
        self.exec_status(True)
        self.__attempts += 1
        if len(self.handlers['before']) > 0:
            for handler in self.handlers['before']:
                status = handler(self)
                if status == FAILED:
                    return FAILED
                elif status == ABORT:
                    self.success()
                    return SUCCESS

        try:
            status = self.func(*self.args, **self.kwargs)
        except Exception as error:
            logging.error('Job "%s": %s', SCheduler.job_name(self), repr(error))
            self.exec_status(False)
            return FAILED
        else:
            if status == FAILED:
                self.exec_status(False)
                return FAILED
            elif status == ABORT:
                self.success()
                self.exec_status(False)
                return SUCCESS

        if len(self.handlers['after']) > 0:
            for handler in self.handlers['after']:
                status = handler(self)
                if status == FAILED:
                    self.exec_status(False)
                    return FAILED

        self.exec_status(False)
        self.success()
        return SUCCESS

    def status(self):
        return self.__done

    def success(self, status=True):
        self.__done = status

    def run_status(self):
        return self.__exec

    def run(self, delete_list, sort_list, epoch):
        if self.__thread:
            _thread.start_new(self.run_function, (), {})
            status = SUCCESS
        else:
            status = self.run_function()

        self.status = status
        if status == FAILED:
            if self.__attempts >= self.max_attempts:
                delete_list.append(self)
                self.save()
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
        self.save()
        return status

    def background(self):
        self.__thread = True

    def foreground(self):
        self.__thread = False

    def add_handler(self, m, function):
        self.handlers[m].append(function)

    def del_handler(self, m, function):
        self.handlers[m].remove(function)


class DBJob(Job):
    MAP_ATTR = {
        'handlers': 'handlers', '_func': 'function',
        'args': 'args',         'kwargs': 'kwargs',
        'status': 'status',     'exec_date': 'exec_in',
        'delay': 'delay',       'max_attempts': 'max_attempts',
        '__done': 'p_done',     '__exec': 'p_exec',
        '__thread': 'p_thread', '__attempts': 'p_attempts',
        '__rerun': 'p_rerun'}

    def __setattr__(self, attr, value):
        if attr in self.MAP_ATTR:
            if '__job' in self.__dict__:
                setattr(self._job, self.MAP_ATTR[attr], value)
                #self._job.save()
        self.__dict__[attr] = value

    def record(self, table):
        return table.create(
            handlers=self.handlers,
            function=self._func,
            args=self.args,
            kwargs=self.kwargs,
            #status=0,  # default in model
            #date=self.date,
            exec_in=self.exec_date,
            delay=self.delay,
            max_attempts=self.max_attempts,
            p_done=self.__done,
            p_exec=self.__exec,
            p_thread=self.__thread,
            p_attempts=self.__attempts,
            p_rerun=self.__rerun)

    def setdb(self, jobdb):
        self._job = jobdb

    @property
    def uuid(self):
        return self._job.uuid

    def save(self):
        if '_job' in self.__dict__:
            self._job.save()

    def delete(self):
        if '_job' in self.__dict__:
            self._job.delete_instance()

    def add_handler(self, *args, **kwargs):
        super(DBJob, self).add_handler(*args, **kwargs)
        self.save()

    def del_handler(self, *args, **kwargs):
        super(DBJob, self).del_handler(*args, **kwargs)
        self.save()


def remove(name):
    return schedulers[name]


def insert(name, scheduler):
    schedulers[name] = scheduler


def basic(name, check=s.CHECK_JOBS, md=s.MAX_DATE, ma=s.MAX_ATTEMPTS):
    if name in schedulers:
        return schedulers[name]

    schedulers[name] = SCheduler(name, check, md, ma)
    return schedulers[name]


def getroot():
    return basic(root_scheduler)


getroot()
