# pylint: disable=import-error
# pylint: disable=no-name-in-module
import os
import sys
from multiprocessing import cpu_count

import sh

from charmhelpers.core import hookenv

config = hookenv.config()


# HELPERS ---------------------------------------------------------------------
def ruby_install():
    """ Downloads ruby-install, gpg verifies it and installs it
    """
    is_snap_install = config.get("ruby-snap", None)
    ruby_install_version = config.get("ruby-install-version", None)
    if is_snap_install and not ruby_install_version:
        sh.snap.install("ruby --channel {} --classic".format(config.get("ruby-snap")))
        hookenv.status_set("maintenance", "Ruby installed from snapstore.")
        return

    stem = "ruby-install-{}".format(ruby_install_version)
    tarfile = "ruby-install-{}.tar.gz".format(ruby_install_version)
    tarfile_gpg = "ruby-install-{}.tar.gz.asc".format(ruby_install_version)
    sh.wget(
        "-O",
        "/tmp/postmodern.asc",
        "https://raw.github.com/postmodern/postmodern.github.io/master/postmodern.asc",
    )
    sh.gpg("--import", "/tmp/postmodern.asc")
    sh.wget(
        "-O",
        "/tmp/{}".format(tarfile),
        "https://github.com/postmodern/ruby-install/archive/v{}.tar.gz".format(
            ruby_install_version
        ),
    )
    sh.wget(
        "-O",
        "/tmp/{}".format(tarfile_gpg),
        "https://raw.github.com/postmodern/ruby-install/master/pkg/{}".format(
            tarfile_gpg
        ),
    )
    sh.tar("-xzvf", tarfile, _cwd="/tmp")

    for line in sh.make("install", _cwd=stem, _iter=True, _bg_exc=False):
        sh.echo(line)

    try:
        sh.gpg("--verify", "/tmp/{}".format(tarfile_gpg), "/tmp/{}".format(tarfile))
    except sh.ErrorReturnCode as error:
        hookenv.status_set("blocked", "Problem getting ruby-install: {}".format(error))
        hookenv.log("Problem getting ruby-install: {}".format(error))
        sys.exit(1)


def compile_ruby():
    version = config.get("ruby-version", "2.6.4")
    try:
        for line in sh.ruby_install("ruby", version, _iter=True, _bg_exc=False):
            sh.echo(line)
    except sh.ErrorReturnCode as error:
        hookenv.status_set(
            "blocked", "Problem installing ruby v{}: {}".format(version, error)
        )
        hookenv.log("Problem install ruby v{}: {}".format(version, error))
        sys.exit(1)

    hookenv.status_set("maintenance", "Installing Ruby completed.")


def ruby_dist_dir():
    """ Absolute path of Ruby application dir

    Returns:
    Absolute string of ruby application directory
    """
    return os.path.join(config["app-path"])


def bundle():
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
    from sh import bundler as _bundler_internal

    has_bundler = sh.which("bundler")
    if not has_bundler:
        gem.install("-N", "bundler")
    hookenv.status_set("maintenance", "Running Bundler")
    return _bundler_internal.bake(
        "-j", cpu_count(), _env=os.environ.copy(), _cwd=ruby_dist_dir()
    )


def gem():
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

    return _gem_internal.bake(_env=os.environ.copy(), _cwd=ruby_dist_dir())
