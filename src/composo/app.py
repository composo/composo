class Composo:

    def __init__(self, plugins):
        self.__plugins = plugins

    def new(self, name, lang:str="python", config=None, dry_run:bool=False, **kwargs): # flavour="bin", config=None, dry_run=False, license="mit"):

        if config is None:
            config = dict(dry_run=str(dry_run).lower())

        try:
            plugin = self.__plugins[lang].load().init(config)
            plugin.new(name=name, **kwargs)  # , flavour=flavour, license=license)

        except KeyError as e:
            print(f"no plugin found for language {lang}, available plugins are: {[k for k, _ in self.__plugins.items()]}")

