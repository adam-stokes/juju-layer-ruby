import sys
import sh
import tempfile
from pathlib import Path
from multiprocessing import cpu_count

from charmhelpers.core import hookenv
from charmhelpers.core.host import chdir

config = hookenv.config()


def install_script():
    """ Installs ruby-install a helper script for installing rubies
    """
    if sh.which('ruby-install'):
        return
    ruby_install_source = (
        Path(__file__).parents[2] / 'files/ruby-install.tar.gz')
    hookenv.status_set('maintenance', 'Installing ruby-install script')
    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            sh.tar('-xzvf', ruby_install_source, '--strip 1')
            sh.make('install')
    hookenv.status_set('active', 'ready')


def install():
    """ Installs rubies
    """
    ruby_runtime = config.get('ruby-runtime', 'ruby')
    ruby_version = config.get('ruby-version', 'stable')

    hookenv.status_set('maintenance', 'Installing {} - {}'.format(
        ruby_runtime,
        ruby_version))
    sh.ruby_install(ruby_runtime, ruby_version)

    bundler_exists = sh.which('bundler')
    if not bundler_exists:
        hookenv.status_set('maintenance', 'Installing bundler')
        sh.gem('install', '-N', 'bundler')
    hookenv.status_set('active', 'ready')


def gem(cmd):
    if isinstance(cmd, str):
        cmd = cmd.split(' ')
    try:
        sh.gem(cmd)
    except sh.ErrorReturnCode as error:
        hookenv.status_set(
            "blocked", "Ruby gem install failed: {}".format(
                error.stderr))
        sys.exit(1)


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
    my_bundler = sh.bundle.bake('-j{}'.format(cpu_count()))
    hookenv.status_set('maintenance', 'Running Bundler')
    try:
        if isinstance(cmd, str):
            cmd = cmd.split(' ')
        my_bundler(cmd)
    except sh.ErrorReturnCode as error:
        hookenv.status_set("blocked", "Ruby bundler: {}".format(error.stderr))
        sys.exit(1)
