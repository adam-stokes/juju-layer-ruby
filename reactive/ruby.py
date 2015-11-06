import os
import sys
from shutil import rmtree
from subprocess import check_call, CalledProcessError

from charms.reactive import (
    hook,
    set_state,
    remove_state
)

from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_purge

# ./lib/rubylib
import rubylib

config = hookenv.config()


@hook('install')
def install_ruby():
    """ Installs defined ruby

    Emits:
    nodejs.available: Emitted once the runtime has been installed
    """
    remove_state('ruby.available')
    hookenv.log('Removing any packaged Ruby', 'debug')
    apt_purge(['ruby'])
    url = os.path.join(config['ruby-mirror'], config['ruby-version'])
    if not rubylib.tarball_exists(url):
        hookenv.status(
            'blocked',
            'Unable to find {} for download, please check your '
            'mirror and version'.format(url))
        sys.exit(0)

    hookenv.status_set('maintenance',
                       'Installing Ruby {}'.format(config['']))

    try:
        cmd = ('wget -O /tmp/ruby.tar.gz {}.tar.gz'.format(url))
        hookenv.log("Downloading ruby: {}".format(cmd))
        check_call(cmd, shell=True)
    except CalledProcessError as e:
        hookenv.log('Problem downlading: {}:{}'.format(cmd, e),
                    'debug')
        sys.exit(0)

    if os.path.exists('/tmp/ruby'):
        rmtree('/tmp/ruby')
    os.makedirs('/tmp/ruby')
    os.chdir('/tmp')
    cmd = ('tar xvf ruby.tar.gz -C /tmp/ruby --strip-components=1')
    try:
        check_call(cmd, shell=True)
    except CalledProcessError as e:
        hookenv.log('Problem extracting ruby: {}:{}'.format(cmd, e),
                    'debug')
        sys.exit(0)
    os.chdir('/tmp/ruby')
    try:
        check_call('./configure', shell=True)
        check_call('make', shell=True)
        check_call('make install', shell=True)
    except CalledProcessError as e:
        hookenv.log('Unable to compile Ruby: {}'.format(e))
        sys.exit(0)

    hookenv.status_set('maintenance', 'Installing Ruby completed.')

    hookenv.status_set('active', 'Ruby is ready!')
    set_state('ruby.available')
