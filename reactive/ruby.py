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

    # Cleanup any packaged ruby
    hookenv.log('Removing any packaged Ruby', 'debug')
    apt_purge(['ruby'])

    # Install prereqs
    rubylib.install_dev_packages()

    # Download
    rubylib.download_ruby()

    # Extract
    rubylib.extract_ruby()

    # Install
    rubylib.compile_ruby()

    hookenv.status_set('active', 'Ruby is ready!')
    set_state('ruby.available')
