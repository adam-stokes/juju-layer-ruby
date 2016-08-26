from charms.reactive import (
    set_state,
    remove_state,
    when,
    when_not
)

from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_purge

# ./lib/rubylib
import rubylib

config = hookenv.config()


@when_not('ruby.installed')
def install_ruby():

    """ Installs defined ruby
    """
    # Cleanup any packaged ruby
    hookenv.log('Installing ruby', 'debug')

    # Install prereqs
    rubylib.install_dev_packages()

    # Download
    rubylib.download_ruby()

    # Extract
    rubylib.extract_ruby()

    # Install
    rubylib.compile_ruby()

    set_state('ruby.installed')


@when('ruby.installed')
def ruby_avail():

    """ Sets the ruby available state

    Emits:
    ruby.available: Emitted once the runtime has been installed
    """
    hookenv.status_set('active', 'Ruby is ready!')
    set_state('ruby.available')


@when_not('ruby.installed')
def ruby_unavail():

    """ Sets remove ruby.available
    """
    remove_state('ruby.available')
