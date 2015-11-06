import shlex
import os
import sys
from collections import deque
import subprocess
import requests

from charmhelpers.core import hookenv


# HELPERS ---------------------------------------------------------------------
def tarball_exists(url):
    """ Checks that ruby tarball exists on mirror
    """
    resp = requests.head(url)
    if resp.status_code == 200:
        return True
    return False


def ruby_dist_dir():
    """ Absolute path of Ruby application dir

    Returns:
    Absolute string of ruby application directory
    """
    config = hookenv.config()
    return os.path.join(hookenv.charm_dir(), config['ruby-application-dir'])


def bundler(cmd):
    """ Runs bundler

    Usage:

       bundler('install')
       bundler('exec rails s')

    Arguments:
    cmd: Command to run can be string or list

    Returns:
    Will halt on error
    """
    if 0 != subprocess.check_call('which bundler', shell=True):
        gem('install bundler')
    hookenv.status_set('maintenance', 'Running Bundler')
    os.chdir(ruby_dist_dir())
    if isinstance(cmd, str):
        cmd = deque(shlex.split(cmd))
    else:
        cmd = deque(cmd)
    cmd.appendleft('bundler')
    try:
        subprocess.check_call(cmd)
        os.chdir(os.getenv('CHARM_DIR'))
    except subprocess.CalledProcessError as e:
        hookenv.status_set("blocked", "Ruby error: {}".format(e))
        sys.exit(0)


def gem(cmd):
    """ Runs gem

    Usage:

       gem('install bundler')

    Arguments:
    cmd: Command to run can be string or list

    Returns:
    Will halt on error
    """
    hookenv.status_set('maintenance', 'Running Gem')
    if isinstance(cmd, str):
        cmd = deque(shlex.split(cmd))
    else:
        cmd = deque(cmd)
    cmd.appendleft('gem')
    try:
        subprocess.check_call(cmd)
        os.chdir(os.getenv('CHARM_DIR'))
    except subprocess.CalledProcessError as e:
        hookenv.status_set("blocked", "Ruby error: {}".format(e))
        sys.exit(0)
