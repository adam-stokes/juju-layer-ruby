from charms.reactive import (
    set_flag,
    clear_flag,
    when,
    when_not,
    when_any
)

from charmhelpers.core import hookenv

from charms.layer import ruby


@when_not('ruby.installed')
def install_ruby():
    """ Installs defined ruby
    """
    ruby.install_script()
    ruby.install()
    set_flag('ruby.installed')


@when('ruby.installed')
@when_not('ruby.available')
def ruby_avail():
    """ Sets the ruby available state

    Flag:
    ruby.available: set once the runtime has been installed
    """
    hookenv.status_set('active', 'Ruby is ready!')
    set_flag('ruby.available')


@when_not('ruby.installed')
def ruby_unavail():
    """ Sets remove ruby.available
    """
    clear_flag('ruby.available')


@when_any('config.set.ruby-runtime', 'config.set.ruby-version')
def ruby_upgrade():
    """ One of the ruby config vars were updated, re-run ruby installation
    """
    clear_flag('ruby.installed')
