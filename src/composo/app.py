import traceback
from pathlib import Path
import os

import yaml


class Composo:
    """
    Composo cmdline tool for bootstrapping projects.

    :Example:

        $ composo new my-project --plugin=python
    """

    def __init__(self, plugins, config):
        self.__plugins = plugins
        self.__config = config

    def _load_plugin(self, plugin, config):
        try:
            plugin = self.__plugins[plugin].load().init(config)
            return plugin

        except KeyError as e:
            print(traceback.format_exc())
            print(f"no plugin found with name '{plugin}', available plugins are: {[k for k, _ in self.__plugins.items()]}")

    def new(self, name: str, plugin: str = "python", init=False, **kwargs):
        """
        Create a new project directory by the name of the chosen project name. The plugin will place
        a `.composo.yaml` file into the target directory for further configuration.

        :param name: the name of the project to be created
        :param plugin: the name of the plugin to be used
        :param init: whether the project is initiated directly
        :param kwargs: additional arguments that ares used by the activated plugin

        :Examples:

            Create a new project named "my-project" with the plugin "python" without initializing it

            $ composo new my-project --plugin=python

            Create a new project named "my-project" with the plugin "python" and initialize it

            $ composo new my-project --plugin=python --init
        """
        config = {**self.__config, **kwargs, "plugin": plugin}
        loaded_plugin = self._load_plugin(plugin, config)
        loaded_plugin.new(name=name)
        if init:
            loaded_plugin.init(name)

    def init(self, path: str = ".", **kwargs):
        """
        Initialize the project in the given path or the current working directory

        :param path: the location of the project to be initialized
        :param kwargs: additional arguments that might be passed to the activated plugin

        :Examples:

            Create a project and initialize it afterwards externally:

            $ composo new my-project --plugin=python

            $ composo init --path=./my-project

            Create a project and initialize it in the project directory:

            $ composo new my-project --plugin=python

            $ cd my-project

            $ composo init

            In either way you can modify the generated `.composo.yaml` file before you initialize the project.
            An example `.composo.yaml` file would be:

            | app:\n
            |   name:\n
            |     class: MyProject\n
            |     package: my_project\n
            |     project: my-project\n
            | author:\n
            |   email: a.rand.developer@email.de\n
            |   name: A. Rand Developer\n
            | cache_dir: /home/arand/.cache/composo\n
            | ci:\n
            |   gitlab:\n
            |     pages: true\n
            | conf_dir: /home/arand/.config/composo\n
            | license: mit\n
            | plugin: python\n
            | vcs:\n
            |   git:\n
            |     github:\n
            |       name: ARand\n

        """
        cwd = Path(os.getcwd())
        target_path = cwd / Path(path)

        with open(target_path / ".composo.yaml") as f:
            try:
                existing_config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)

        config = {**self.__config, **existing_config, **kwargs}
        plugin = config["plugin"]
        plugin = self._load_plugin(plugin, config)
        plugin.init(target_path)
