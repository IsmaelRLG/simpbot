# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import argparse, socket, os, platform, json, sys, simpbot, time, datetime, re
from . import envvars, localedata, connections, samples, api
from .bottools import dummy, text
from getpass import getpass
from prettytable import PrettyTable
from six.moves import input
from six.moves import _thread

refile = re.compile('(?P<name>.+)\.(?P<ext>py[co]?$)', re.IGNORECASE)
parsers = envvars.parsers
locale = localedata.get(package='simpbot.cli')
table_kwargs = {
    #'vertical_char':   ' ',
    #'junction_char':   ' ',
    #'horizontal_char': ' ',
    'border':           False,
    'print_empty':      False,
    'header_style':     'upper'}
testing = False


def error(text, e=True):
    sys.stdout.write('[!] ' + text + '\n')
    if e:
        exit(1)


def echo(text):
    print('[+]  ' + text)


class SimpParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(SimpParser, self).__init__(*args, **kwargs)
        self.add_argument("-v", "--version",
            help=locale['version help'],
            action="store_true")

        self.add_argument("-d", "--debug",
            help=locale['debug help'],
            type=int, metavar='level')

        self.add_argument("--root",
            action='store_true', dest='root',
            help=locale['help root'])

        self.user = api.config.DEFAULT_USER
        self.host = api.config.CONNECT_HOST
        self.port = api.config.CONNECT_PORT

    def debug(self, level=40):
        if not level in (10, 20, 30, 40, 50):
            error(locale['invalid debug level'])
        dummy.debug(level)

    def edit(self, abspath):
        if not os.path.exists(abspath) or os.path.isdir(abspath):
            error(locale['invalid network name'])

        if platform.system() == 'Linux':
            editor = 'editor'
        elif platform.system() == 'Windows':
            editor = 'notepad'

        os.system('%s %s' % (editor, abspath))

    def running_api(self):
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            sock.close()
        except Exception:
            return False
        else:
            return True

    def request(self):
        if self.user is None:
            error(locale['id needed'])

        host = self.host
        port = self.port
        user = self.user
        try:
            network = input(locale['enter network'])
            passwdl = locale['passwd'] % (user, host, network)
            while 1:
                password = getpass(passwdl)
                if password != '':
                    break
        except KeyboardInterrupt:
            print('\n')
            exit(1)

        if network == '':
            network = None

        return api.client.request(host, port, network, user, password)

    def check_root(self, root):
        if os.geteuid() == 0 and root:
            error('no root!')


class ServerParser(SimpParser):

    def __init__(self, *args, **kwargs):
        super(ServerParser, self).__init__(*args, **kwargs)
        if testing:
            return

        self.add_argument("-u", "--username", type=str,
            help=locale['username help'],
            metavar=locale['<username>'])

        self.add_argument("-R", "--remote-host", type=str,
            help=locale['remote host help'],
            metavar=locale['<remote host>'])

        server = self.add_argument_group(locale['options for'] % 'server')
        server.add_argument("-l", "--list",
            action='store_true',
            help=locale['help server list'])

        server.add_argument("-e", "--edit", type=str,
            metavar=(locale['<server name>'],),
            help=locale['help edit server'])

        server.add_argument("-a", "--add", type=str,
            metavar=(locale['<server name>'],),
            help=locale['help add server'])

        server.add_argument("-r", "--remove", type=str,
            metavar=(locale['<server name>'],),
            help=locale['help remove server'])

        login = self.add_argument_group(locale['required login'])
        login.add_argument("-s", "--status",
            action='store_true',
            help=locale['help server status'])

        login.add_argument("-cc", "--connect", type=str,
            metavar=(locale['<server name>'],),
            help=locale['help connect server'])

        login.add_argument("-dc", "--disconnect", type=str,
            metavar=(locale['<server name>'],),
            help=locale['help disconnect server'])

        login.add_argument("-rc", "--reconnect", type=str,
            metavar=(locale['<server name>'],),
            help=locale['help reconnect server'])

    def get_servers(self):
        tmp_core = {}
        connections.load_servers(core=tmp_core, connect=False)
        return tmp_core

    def gen_request(self, attr, *args, **kwargs):
        if not self.running_api():
            error(locale['api is not running'] % (self.host, self.port))
        request = getattr(self.request(), attr)(*args, **kwargs)
        if request[0]['status'] == '401':
            error(locale['invalid password'])
        elif request[0]['status'] != '201':
            error(locale['unknown response'])
        return json.loads(request[1])

    def print_response(self, response):
        response = {'status': None, 'errors': [], 'messages': []}
        print(locale[response['status']])

        if len(response['errors']) > 0:
            print('\n' + locale[response['error']])
            for line in response['errors']:
                print(line)

        if len(response['messages']) > 0:
            print('\n' + locale[response['messages']])
            for line in response['messages']:
                print(line)

    @text.lower
    def add(self, server_name):
        tmp_core = {}
        connections.load_servers(core=tmp_core, connect=False)
        if server_name in tmp_core:
            tmp_core.clear()
            return

        with open(envvars.servers.join(server_name + '.ini'), 'w') as server:
            server.write(dummy.ascii(start=';'))
            server.write(samples.server.sample.format(server_name=server_name))
        return

    @text.lower
    def remove(self, server_name):
        tmp_core = {}
        connections.load_servers(core=tmp_core, connect=False)
        if not server_name in tmp_core:
            tmp_core.clear()
            return

        server = tmp_core[server_name]
        os.remove(server.conf_path)

    def server_list(self):
        parsebol = lambda bool: locale['true'] if bool else locale['false']
        basicrows = [
            locale['row name'],
            locale['row host'],
            locale['row port'],
            'ssl', 'sasl',
            locale['row pass']
        ]

        servers = self.get_servers()
        if len(servers) == 0:
            error(locale['no servers'], False)
            return

        tablecfg = PrettyTable(basicrows, **table_kwargs)
        tablecfg._set_align('l')
        for server in servers.values():
            tablecfg.add_row([
            server.servname,
            server.addr,
            server.port,
            parsebol(server.ssl),
            parsebol(server.sasl),
            parsebol(server.servpass)])
        print(tablecfg)

    def server_status(self):
        request = self.gen_request('connections')
        basicrows = [
            locale['row name'],
            locale['row host'],
            locale['row port'],
            'ssl', 'sasl',
            locale['row pass'],
            locale['row status']
        ]
        tableapi = PrettyTable(basicrows, **table_kwargs)
        tableapi._set_align('l')
        for server in request['servers']:
            server.append(locale[server.pop()])
            tableapi.add_row(server)
        print(tableapi)

    def connect(self, server_name):
        self.print_response(self.gen_request('connect', server_name))

    def disconnect(self, server_name):
        self.print_response(self.gen_request('connect', server_name))

    def reconnect(self, server_name):
        self.print_response(self.gen_request('connect', server_name))

    def process(self):
        args = self.parse_args()
        #print(dummy.ascii(start=''))

        if args.username:
            self.user = args.username

        if args.remote_host:
            try:
                host, port = args.remote_host.split(':')
                if not port.isdigit() or int(port) == 0:
                    raise ValueError('Invalid port number: ' + port)
            except ValueError:
                error(locale['invalid syntax'])
            else:
                self.host, self.port = host, int(port)

        if args.debug:
            if not args.debug in (10, 20, 30, 40, 50):
                error(locale['invalid debug level'])
            dummy.debug(args.debug)
        else:
            self.debug(40)

        if args.add:
            self.add(args.add)
        elif args.remove:
            self.remove(args.remove)
        elif args.edit:
            self.edit(envvars.servers.join(args.edit.lower() + '.ini'))
        elif args.list:
            self.server_list()
        elif args.status:
            self.server_status()
        elif args.connect:
            self.connect(args.connect)
        elif args.connect:
            self.connect(args.connect)
        elif args.connect:
            self.connect(args.connect)
        else:
            self.print_help()


class ConfigParser(SimpParser):

    def __init__(self, *args, **kwargs):
        super(ConfigParser, self).__init__(*args, **kwargs)
        if testing:
            return

        self.add_argument("-u", "--username", type=str,
            help=locale['username help'],
            metavar=locale['<username>'])

        self.add_argument("-R", "--remote-host", type=str,
            help=locale['remote host help'],
            metavar=locale['<remote host>'])

        config = self.add_argument_group(locale['options for'] % 'conf')
        config.add_argument("-l", "--langs",
            action='store_true',
            help=locale['help lang list'])

        config.add_argument("-e", "--edit",
            action='store_true',
            help=locale['help edit config'])

        config.add_argument("-a", "--admins",
            action='store_true',
            help=locale['help make admins'])

        config.add_argument("-c", "--conf",
            action='store_true',
            help=locale['help make conf'])

        login = self.add_argument_group(locale['required login'])

        login.add_argument("-r", "--reconfigure",
            action='store_true',
            help=locale['help reconfigure'])

    def langs(self):
        basicrows = [locale['row langcode'], locale['row langname']]
        langtable = PrettyTable(basicrows, **table_kwargs)
        langtable._set_align('l')
        for lang, package in localedata.simplocales.langs('fullsuport'):
            langtable.add_row([lang, localedata.get(lang, package)['lang']])
        print(langtable)

    def reconnect(self, server_name):
        self.print_response(self.gen_request('connect', server_name))

    def process(self):
        args = self.parse_args()
        #print(dummy.ascii(start=''))

        if args.debug:
            if not args.debug in (10, 20, 30, 40, 50):
                error(locale['invalid debug level'])
            dummy.debug(args.debug)
        else:
            self.debug(40)
        self.check_root(args.root)

        if args.langs:
            return self.langs()

        if args.username:
            self.user = args.username

        if args.remote_host:
            try:
                host, port = args.listen.split(':')
                if not port.isdigit() or int(port) == 0:
                    raise ValueError('Invalid port number: ' + port)
            except ValueError:
                error(locale['invalid syntax'])
            else:
                self.host, self.port = host, int(port)

        if args.admins:
            if args.edit:
                self.edit(envvars.adminspath)
            else:
                if os.path.exists(envvars.adminspath):
                    error(locale['admin conf already exists'])
                with open(envvars.adminspath, 'w') as fp:
                    fp.write(dummy.ascii(start=';'))
                    fp.write(samples.admins.sample)
            if not args.conf:
                return

        if args.conf:
            if args.edit:
                self.edit(envvars.simpbotcfg)
            else:
                if os.path.exists(envvars.simpbotcfg):
                    error(locale['simpbot conf already exists'])
                with open(envvars.simpbotcfg, 'w') as fp:
                    fp.write(dummy.ascii(start='#'))
                    fp.write(samples.simpconf.sample)
        else:
            self.print_help()


class StatusParser(SimpParser):

    def __init__(self, *args, **kwargs):
        super(StatusParser, self).__init__(*args, **kwargs)
        if testing:
            return

        status = self.add_argument_group(locale['options for'] % 'status')
        status.add_argument("-s", "--start",
            action='store_true',
            help=locale['help start'])

        status.add_argument("-S", "--stop",
            action='store_true',
            help=locale['help stop'])

        status.add_argument("-r", "--restart",
            action='store_true',
            help=locale['help restart'])

        status.add_argument("-nd", "--no-daemon",
            action='store_true', dest='daemon',
            help=locale['help no daemon'])

        status.add_argument("-i", "--info",
            action='store_true',
            help=locale['help info'])

        gr_api = status.add_mutually_exclusive_group()

        gr_api.add_argument("-l", "--listen", type=str,
            help=locale['help listen host'],
            metavar=locale['<remote host>'])

        gr_api.add_argument("-na", "--no-api",
            action='store_true', dest='no_api',
            help=locale['help no api'])

        filename = 'simpbot-%s.pid'
        if platform.system() == 'Windows':
            base = os.environ['TEMP']
            filename = filename % os.environ['USERNAME']
        elif platform.system() == 'Linux':
            base = '/tmp'
            filename = filename % os.environ['USER']

        self.pid_path = os.path.join(base, filename)

    def _check_pid(self, pid):
        if platform.system() == 'Windows':
            return False

        if pid > 0:
            import errno
            try:
                os.kill(pid, 0)
            except OSError as err:
                if err.errno == errno.EPERM:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    def check_pid(self, path):
        if not os.path.exists(path) or not os.path.isfile(path):
            return False

        with open(path, 'r') as fp:
            pid = fp.read()
        if not pid.isdigit():
            return False
        else:
            pid = int(pid)

        return self._check_pid(pid)

    def demonize(self, startmsg=None):
        if platform.system() == 'Windows':
            print(locale['use linux!'])
        elif platform.system() == 'Linux':

            if self.check_pid(self.pid_path):
                with open(self.pid_path, 'r') as fp:
                    pid = int(fp.read())
                error('(PID: %s) %s' % (pid, locale['already running']))

            # Do first fork.
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)   # Exit first parent.
            except OSError as e:
                error("fork #1 failed: (%d) %s" % (e.errno, e.strerror))
            current_path = os.getcwd()
            os.chdir("/")
            os.umask(0)
            os.setsid()
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)   # Exit second parent.
            except OSError as e:
                error("fork #2 failed: (%d) %s" % (e.errno, e.strerror))

            si = open(os.devnull, 'r')
            so = open(os.devnull, 'a+')
            se = open(os.devnull, 'a+', 0)
            pid = str(os.getpid())
            with open(self.pid_path, 'w+') as pidfile:
                pidfile.write(str(pid))
            if startmsg:
                echo('(PID: %s) %s' % (pid, startmsg))
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stdout.fileno())
            os.chdir(current_path)
            envvars.daemon = True

    def start(self, daemon=False, api=False):
        try:
            import simpmods  # lint:ok
        except Exception as e:
            error(locale['simpmods error'] % repr(e))

        for modname in envvars.modules.listdir():
            if os.path.isfile(modname):
                try:
                    modname = refile.match(modname).group('name')
                except:
                    continue
            elif os.path.islink(modname):
                continue

            load_res = simpbot.modules.load_module(modname, trace=True)
            if isinstance(load_res, Exception):
                exit(1)

        simpbot.admins.load_admins()
        simpbot.connections.load_servers()
        if len(envvars.admins) == 0:
            error(locale['empty admins'])
        if len(envvars.networks) == 0:
            error(locale['empty networks'])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = simpbot.api.config.LISTEN_HOST
        port = simpbot.api.config.LISTEN_PORT

        if not daemon and not api:
            if sock.connect_ex((host, port)) == 0:
                sock.close()
                error('Address already in use: %s:%s' % (host, port))

        if not daemon:
            self.demonize(locale['started'])

        if not api:
            simpbot.api.server.start()
        else:
            while 1:
                time.sleep(900)

    def stop(self):
        if platform.system() == 'Windows':
            exit(locale['use linux!'])
        elif platform.system() == 'Linux':
            pid_path = self.pid_path
            if not self.check_pid(pid_path):
                error(locale['already stoped'])
            if not os.path.exists(pid_path) or not os.path.isfile(pid_path):
                error(locale['already stoped'])

            with open(pid_path, 'r') as fp:
                pid = int(fp.read())

            try:
                from signal import SIGTERM
                while 1:
                    os.kill(pid, SIGTERM)
                    time.sleep(1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    echo('(PID: %s) %s' % (pid, locale['stoped']))
                    os.remove(pid_path)

    def process(self):
        args = self.parse_args()
        print(dummy.ascii(start=''))

        if args.debug:
            if not args.debug in (10, 20, 30, 40, 50):
                error(locale['invalid debug level'])
            dummy.debug(args.debug, not args.daemon)
        else:
            dummy.debug(40, not args.daemon)

        if args.listen:
            try:
                host, port = args.listen.split(':')
                if not port.isdigit() or int(port) == 0:
                    raise ValueError('Invalid port number: ' + port)
            except ValueError:
                error(locale['invalid syntax'])
            else:
                self.host, self.port = host, int(port)

        if args.stop or args.restart:
            self.stop()
            if not args.restart:
                return

        if args.start or args.restart:
            self.check_root(args.root)
            return self.start(args.daemon, args.no_api)

        if args.info:
            if self.check_pid(self.pid_path):
                with open(self.pid_path, 'r') as fp:
                    pid = int(fp.read())
                echo('(PID: %s) %s' % (pid, locale['simpbot started']))
            else:
                echo(locale['simpbot stoped'])
            return
        self.print_help()


class TestParser(ConfigParser, ServerParser, StatusParser):

    def __init__(self, *args, **kwargs):
        global testing
        testing = True

        super(TestParser, self).__init__(*args, **kwargs)

        test = self.add_argument_group(locale['options for'] % 'test')
        test.add_argument("--system-info",
            help=locale['help system info'],
            action="store_true")

        test.add_argument("--servers",
            help=locale['help servers test'],
            action="store_true")

        test.add_argument("--admins",
            help=locale['help admins test'],
            action='store_true')

        test.add_argument("--config",
            action='store_true',
            help=locale['help conf test'])

        test.add_argument("--connection",
            action='store_true',
            help=locale['help connections test'])

        test.add_argument("--langs",
            action='store_true',
            help=locale['help langs test'])

        test.add_argument("--test-all",
            action='store_true',
            help=locale['help test all'])
        testing = False

    def process(self):
        args = self.parse_args()
        n = 0
        #print(dummy.ascii(start=''))

        if args.debug:
            if not args.debug in (10, 20, 30, 40, 50):
                error(locale['invalid debug level'])
            dummy.debug(args.debug)
        else:
            dummy.debug(40)
        self.check_root(args.root)
        if args.system_info or args.test_all:
            n += 1
            echo('Python: ' + platform.python_version())
            if platform.system() == 'Linux':
                osver = ("%s %s" % (platform.dist()[0], platform.dist()[1]))
            elif platform.system() == 'Windows':
                osver = ("%s %s" % (platform.system(), platform.release()))
            else:
                osver = 'Unknown'
            echo('OS: %s %s' % (osver, platform.architecture()))
            echo('SimpBot v%s' % simpbot.__version__)

        if args.langs or args.test_all:
            n += 1
            self.langs()

        temp_admin = False
        if args.admins or args.test_all:
            n += 1
            if not os.path.exists(envvars.adminspath):
                with open(envvars.adminspath, 'w') as fp:
                    fp.write(dummy.ascii(start=';'))
                    fp.write(samples.admins.sample)
                temp_admin = True

        temp_conf = False

        if args.config or args.test_all:
            n += 1
            if not os.path.exists(envvars.simpbotcfg):
                with open(envvars.simpbotcfg, 'w') as fp:
                    fp.write(dummy.ascii(start='#'))
                    fp.write(samples.simpconf.sample)
                temp_conf = True

        if args.servers or args.connection or args.test_all:
            n += 1
            try:
                self.add('testing-server')
                if args.servers or args.test_all:
                    self.server_list()
            except:
                error(locale['server failed'], False)

            if args.test_all or args.connection:
                pass
            else:
                self.remove('testing-server')

        if args.connection or args.test_all:
            n += 1
            try:
                import simpmods  # lint:ok
            except Exception as e:
                error(locale['simpmods error'] % repr(e))

            for modname in envvars.modules.listdir():
                if os.path.isfile(modname):
                    try:
                        modname = refile.match(modname).group('name')
                    except:
                        continue
                elif os.path.islink(modname):
                    continue

                load_res = simpbot.modules.load_module(modname, trace=True)
                if isinstance(load_res, Exception):
                    exit(1)

            done = []
            @simpbot.handlers.handler(simpbot.handlers.\
            rpl(4, '!{servername} !{version} !{aum} !{acm}'))
            def quiter(irc, ev):
                irc.disconnect()
                time.sleep(2.5)
                done.append(1)

            simpbot.admins.load_admins()
            servercfg = envvars.servers.join('testing-server.ini')
            try:
                connections.load_server(servercfg, envvars.networks, True, 1)
            except Exception as e:
                error('Invalid server config: ' + e)

            if len(envvars.admins) == 0:
                error(locale['empty admins'])
            if len(envvars.networks) == 0:
                error(locale['empty networks'])

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = simpbot.api.config.LISTEN_HOST
            port = simpbot.api.config.LISTEN_PORT

            if sock.connect_ex((host, port)) == 0:
                sock.close()
                error('Address already in use: %s:%s' % (host, port), False)

            #def destroyer():
            #    started = datetime.datetime.now()
            #    msg = False
            #    while 1:
            #        time.sleep(1)
            #        if envvars.api_started:
            #            if not msg:
            #                echo(locale['api started'])
            #                msg = True
            #       else:
            #            print(locale['api stopped'])
            #        t = (started - datetime.datetime.now()).total_seconds()
            #        if len(done) > 0 or t > 30:
            #            if envvars.api_started:
            #                simpbot.api.server.stop()
            #            break
            #_thread.start_new(destroyer, (), {})
            #simpbot.api.server.start()

            t = time.time()
            while 1:
                if len(done) == 0:
                    if (time.time() - t) > 60:
                        break
                    time.sleep(1)

                else:
                    echo(time.strftime(locale['connection successful']))
                    break

            self.remove('testing-server')

        if args.config or args.test_all:
            if temp_conf:
                os.remove(envvars.simpbotcfg)

        if args.admins or args.test_all:
            if temp_admin:
                os.remove(envvars.adminspath)
        if n == 0:
            self.print_help()

#envvars.parsers['base'] = SimpParser
envvars.parsers['conf'] = ConfigParser
envvars.parsers['server'] = ServerParser
envvars.parsers['status'] = StatusParser
envvars.parsers['test'] = TestParser
setattr(argparse, '_', lambda txt: locale[txt] if txt in locale else txt)


def main():
    args = sys.argv
    if len(args) > 1:
        del args[0]

    if len(args) == 0 or args[0] not in envvars.parsers:
        print(locale['available commands'])
        print('=' * len(locale['available commands']))
        print(', '.join(envvars.parsers.keys()))
        exit(1)

    parser = envvars.parsers[args[0]]()
    try:
        parser.process()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as error:
        errmsg = locale['unexpected error'] % repr(error) + '\n'
        sys.stderr.write(errmsg)
        sys.stderr.flush()
        exit(1)


if __name__ == '__main__':
    main()