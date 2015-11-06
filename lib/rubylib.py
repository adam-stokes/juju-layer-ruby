import shlex
import os
import sys
from shutil import rmtree
from collections import deque
from subprocess import check_call, CalledProcessError
from multiprocessing import cpu_count
import requests

from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_install

config = hookenv.config()
WORKDIR = '/tmp/ruby'
COMPILESCRIPT = os.path.join(hookenv.charm_dir(), 'scripts/compileruby.sh')


# HELPERS ---------------------------------------------------------------------
def tarball_exists(url):
    """ Checks that ruby tarball exists on mirror
    """
    resp = requests.head(url)
    if resp.status_code == 200:
        return True
    return False


def install_dev_packages():
    """ Installs any extra dev packages
    """
    pkgs = ['build-essential', 'libreadline-dev', 'libssl-dev',
            'libgmp-dev', 'libffi-dev', 'libyaml-dev',
            'zlib1g-dev', 'libgdbm-dev', 'openssl']
    pkg_file = os.path.join(hookenv.charm_dir(), 'dependencies.txt')
    if os.path.isfile(pkg_file):
        with open(pkg_file, 'r') as fp:
            for pkg in fp:
                pkgs.append(pkg.strip())
    hookenv.log('Installing packages: {}'.format(pkgs), 'debug')
    apt_install(pkgs)


def compile_ruby():
    os.chdir(WORKDIR)
    try:
        check_call(COMPILESCRIPT,
                   shell=True)
    except CalledProcessError as e:
        hookenv.status_set('blocked', 'Unable to compile Ruby: {}'.format(e))
        sys.exit(0)

    hookenv.status_set('maintenance', 'Installing Ruby completed.')


def download_ruby():
    """ Downloads ruby tarball, puts it in /tmp
    """
    url = os.path.join(config['ruby-mirror'],
                       'ruby-{}.tar.gz'.format(config['ruby-version']))
    if not tarball_exists(url):
        hookenv.status_set(
            'blocked',
            'Unable to find {} for download, please check your '
            'mirror and version'.format(url))
        sys.exit(0)

    hookenv.status_set('maintenance',
                       'Installing Ruby {}'.format(url))

    try:
        cmd = ('wget -q -O /tmp/ruby.tar.gz {}'.format(url))
        hookenv.log("Downloading ruby: {}".format(cmd))
        check_call(cmd, shell=True)
    except CalledProcessError as e:
        hookenv.log('Problem downlading: {}:{}'.format(cmd, e),
                    'debug')
        sys.exit(0)


def extract_ruby():
    if os.path.exists(WORKDIR):
        rmtree(WORKDIR)
    os.makedirs(WORKDIR)
    os.chdir('/tmp')
    cmd = ('tar xf ruby.tar.gz -C {} --strip-components=1'.format(WORKDIR))
    try:
        check_call(cmd, shell=True)
    except CalledProcessError as e:
        hookenv.log('Problem extracting ruby: {}:{}'.format(cmd, e),
                    'debug')
        sys.exit(0)


def ruby_dist_dir():
    """ Absolute path of Ruby application dir

    Returns:
    Absolute string of ruby application directory
    """
    config = hookenv.config()
    return os.path.join(hookenv.charm_dir(), config['ruby-application-dir'])


def bundle(cmd):
    """ Runs bundle

    Usage:

       bundle('install')
       bundle('exec rails s')
       bundle('rake db:create RAILS_ENV=production')

    Arguments:
    cmd: Command to run can be string or list

    Returns:
    Will halt on error
    """
    if 0 != check_call('which bundler', shell=True):
        gem('install bundler')
    hookenv.status_set('maintenance', 'Running Bundler')
    os.chdir(ruby_dist_dir())
    if isinstance(cmd, str):
        cmd = deque(shlex.split(cmd))
    else:
        cmd = deque(cmd)
    cmd.appendleft('bundle')
    cmd.append('-j{}'.format(cpu_count()))
    try:
        check_call(cmd)
        os.chdir(os.getenv('CHARM_DIR'))
    except CalledProcessError as e:
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
    cmd.append('--no-ri')
    cmd.append('--no-rdoc')
    try:
        check_call(cmd)
        os.chdir(os.getenv('CHARM_DIR'))
    except CalledProcessError as e:
        hookenv.status_set("blocked", "Ruby error: {}".format(e))
        sys.exit(0)
