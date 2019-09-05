# pylint: disable=import-error
# pylint: disable=no-name-in-module
from charmhelpers.core import hookenv
from charms.layer import ruby
from charms.reactive import remove_state, set_state, when, when_not

config = hookenv.config()


@when_not("ruby.installed")
def install_ruby():

    """ Installs defined ruby
    """
    # Cleanup any packaged ruby
    hookenv.log("Installing ruby", "debug")

    # Download, compile, install
    ruby.ruby_install()

    set_state("ruby.installed")


@when("ruby.installed")
@when_not("ruby.available")
def ruby_avail():

    """ Sets the ruby available state

    Emits:
    ruby.available: Emitted once the runtime has been installed
    """
    hookenv.status_set("active", "Ruby is ready!")
    set_state("ruby.available")


@when_not("ruby.installed")
def ruby_unavail():

    """ Sets remove ruby.available
    """
    remove_state("ruby.available")
