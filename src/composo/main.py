from pathlib import Path

import fire

from composo import ioc
from appdirs import user_config_dir


def main():
    ioc.App.config.from_yaml(Path(user_config_dir("composo")) / "config.yaml")
    app = ioc.App.app()
    fire.Fire(app)


def run():
    app = ioc.App.app()
    app.new("test", lang="shell")


if __name__ == "__main__":
    run()
