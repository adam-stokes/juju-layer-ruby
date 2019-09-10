# pylint: disable=import-error
# pylint: disable=no-name-in-module
import os

from charmhelpers.core import hookenv

from charms.layer import snap

config = hookenv.config()


# HELPERS ---------------------------------------------------------------------
def ruby_install():
    """ Downloads ruby-install, gpg verifies it and installs it
    """
    if not snap.is_installed("ruby"):
        snap.install("ruby", channel=config.get("snap-channel"), classic=True)
        hookenv.status_set("maintenance", "Ruby installed from Snapstore {}.".format(
            config.get("snap-channel")))


def ruby_dist_dir():
    """ Absolute path of Ruby application dir

    Returns:
    Absolute string of ruby application directory
    """
    return os.path.join(config["app-path"])


def bundle(*args, **kwargs):
    """ Runs bundle

    Usage:

       bundle('install')
       bundle('exec', 'rails', 's')
       bundle('rake', 'db:create', 'RAILS_ENV=production')

    Arguments:
    cmd: Command to run can be string or list

    Returns:
    Raises sh.ErrorReturnCode on error
    """
    from sh import which
    has_bundler = which("bundle")
    if not has_bundler:
        gem.install("-N", "bundler")

    from sh import bundle as _bundler_internal

    hookenv.status_set("maintenance", "Running Bundler")
    return _bundler_internal.bake(
        *args, **kwargs, _env=os.environ.copy(), _cwd=ruby_dist_dir()
    )()


def gem(*args, **kwargs):
    """ Runs gem

    Usage:

       gem('install', 'bundler')

    Arguments:
    cmd: Command to run can be string or list

    Returns:
    Raises sh.ErrorReturnCode on error
    """
    hookenv.status_set("maintenance", "Running Gem")
    from sh import gem as _gem_internal

    return _gem_internal.bake(
        *args, **kwargs, _env=os.environ.copy(), _cwd=ruby_dist_dir()
    )()
