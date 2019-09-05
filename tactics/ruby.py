from charmtools.build.errors import BuildError
from charmtools.build.tactics import ExactMatch, Tactic


class DependenciesTxtTactic(ExactMatch, Tactic):
    FILENAME = "dependencies.txt"
    kind = "dynamic"

    def __call__(self):
        raise BuildError(
            "dependencies.txt is deprecated see "
            "https://github.com/battlemidget/juju-layer-ruby/pull/8"
        )
