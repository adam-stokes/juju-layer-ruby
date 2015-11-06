import os
import sys
from shutil import rmtree
from multiprocessing import cpu_count
from shell import shell
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
    cmds = [
        'env RUBY_CFLAGS="-O3" ./configure --prefix=/usr '
        '--disable-install-rdoc',
        'make -j{}'.format(cpu_count()),
        'make install'
    ]

    for cmd in cmds:
        hookenv.log('Running compile command: {}'.format(cmd))
        sh = shell(cmd, record_output=False)
        if sh.code > 0:
            hookenv.status_set('blocked',
                               'Problem with Ruby: {}'.format(sh.errors()))
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

    sh = shell('wget -q -O /tmp/ruby.tar.gz {}'.format(url))
    if sh.code > 0:
        hookenv.status_set('blocked',
                           'Problem downlading Ruby: {}'.format(sh.errors()))
        sys.exit(0)


def extract_ruby():
    if os.path.exists(WORKDIR):
        rmtree(WORKDIR)
    os.makedirs(WORKDIR)
    os.chdir('/tmp')
    cmd = ('tar xf ruby.tar.gz -C {} --strip-components=1'.format(WORKDIR))
    sh = shell(cmd)
    if sh.code > 0:
        hookenv.status_set(
            'blocked',
            'Problem extracting ruby: {}:{}'.format(cmd,
                                                    sh.errors()))
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
    sh = shell('which bundler')
    if sh.code > 0:
        gem('install bundler')
    hookenv.status_set('maintenance', 'Running Bundler')
    os.chdir(ruby_dist_dir())
    if not isinstance(cmd, str):
        hookenv.log('{} must be a string'.format(cmd), 'error')
        sys.exit(0)
    cmd = "bundle {} -j{}".format(cmd, cpu_count())
    os.chdir(os.getenv('CHARM_DIR'))
    sh = shell(cmd, record_output=False)

    if sh.code > 0:
        hookenv.status_set("blocked", "Ruby error: {}".format(sh.errors()))
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
    if not isinstance(cmd, str):
        hookenv.log('{} must be a string'.format(cmd), 'error')
        sys.exit(0)
    cmd = "gem --no-ri --no-rdoc {}".format(cmd)
    os.chdir(os.getenv('CHARM_DIR'))
    sh = shell(cmd, record_output=False)
    if sh.code > 0:
        hookenv.status_set("blocked", "Ruby error: {}".format(sh.errors()))
        sys.exit(0)
