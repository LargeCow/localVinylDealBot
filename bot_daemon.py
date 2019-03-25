import sys, os, time, atexit, signal

from artists import ARTISTS
import config
from functions import run_bot
import logging
from datetime import datetime as dt

import praw

now = dt.now()

logging.basicConfig(filename=f'vinyl-deal-bot-logs-{now.year}-{now.month}-{now.day}.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')


class daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:

                pid = int(pf.read().strip())
                logging.info(f'Found pidfile {self.pidfile}')
        except IOError:
            pid = None

        if pid:
            logging.critical(f'pidfile {self.pidfile} already exists. Is the daemon already running?')
            sys.exit(1)

        # Start the daemon
        logging.info('Starting the daemon')
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        logging.info('Searching for the PID file...')
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            logging.critical(f'Could not locate pidfile {self.pidfile}')
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            logging.info('Stopping the processes')
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        logging.info('Restarting the daemon...')
        self.stop()
        self.start()
        logging.info('Restarted the daemon!')

    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by
        start() or restart()."""

        logging.info('The bot started successfully!!')
        try:
            client = praw.Reddit(
                username=config.USER_NAME,
                password=config.PASSWORD,
                client_id=config.CLIENT_ID,
                client_secret=config.CLIENT_SECRET,
                user_agent=config.USER_AGENT
            )
            bot = run_bot(client, ARTISTS)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    bot_daemon = daemon('/tmp/vinyl-deal-bot-daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            bot_daemon.start()
        elif 'stop' == sys.argv[1]:
            bot_daemon.stop()
        elif 'restart' == sys.argv[1]:
            bot_daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
