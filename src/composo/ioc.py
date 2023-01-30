from importlib.metadata import entry_points

import dependency_injector.providers as providers
import dependency_injector.containers as containers
import typer

from composo.app import Composo
from composo.shell.plugin import Shell


class Plugins(containers.DeclarativeContainer):
    discovered_plugins = providers.Callable(lambda name: {ep.name: ep for ep in entry_points().get(name, [])},
                                            'composo.plugins')

    shell = providers.Factory(Shell)


DEFAULT_CONFIG = {
    "author": {
        "name": "A. Rand Developer",
        "email": "a.rand@email.com"
    },
    "vcs": {
        "git": {
            "github": {
                "name": "ARand"
            }
        }
    },
    "license": "mit"
}


class App(containers.DeclarativeContainer):

    config = providers.Configuration("config")
    config.override(DEFAULT_CONFIG)

    typer_app = providers.Factory(typer.Typer,
                                  rich_markup_mode="rich")

    app = providers.Factory(Composo,
                            plugins=Plugins.discovered_plugins,
                            config=config,
                            app=typer_app)
