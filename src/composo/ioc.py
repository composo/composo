from importlib.metadata import entry_points

import dependency_injector.providers as providers
import dependency_injector.containers as containers

from composo.app import Composo
from composo.shell.plugin import Shell


class Plugins(containers.DeclarativeContainer):
    discovered_plugins = providers.Callable(lambda name: {ep.name: ep for ep in entry_points()[name]},
                                            'composo.plugins')

    shell = providers.Factory(Shell)


class App(containers.DeclarativeContainer):

    app = providers.Factory(Composo,
                            plugins=Plugins.discovered_plugins)
