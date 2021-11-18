import traceback
from pathlib import Path
import os
import yaml

class Composo:

    def __init__(self, plugins, config):
        self.__plugins = plugins
        self.__config = config

    def _load_plugin(self, lang, config):
        try:
            plugin = self.__plugins[lang].load().init(config)
            return plugin

        except KeyError as e:
            print(traceback.format_exc())
            print(f"no plugin found for language {lang}, available plugins are: {[k for k, _ in self.__plugins.items()]}")

    def new(self, name, lang:str="python", init=False, **kwargs): # flavour="bin", config=None, dry_run=False, license="mit"):
        config = {**self.__config, **kwargs}
        config["lang"] = lang
        plugin = self._load_plugin(lang, config)
        plugin.new(name=name)
        if init:
            plugin.init(name)

    def init(self, path=".", **kwargs):
        cwd = Path(os.getcwd())
        target_path = cwd / Path(path)

        with open(target_path / ".composo.yaml") as f:
            try:
                existing_config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)

        config = {**self.__config, **existing_config, **kwargs}
        lang = config["lang"]
        plugin = self._load_plugin(lang, config)
        plugin.init(path)