from pathlib import Path

import fire
import typer

from typer.testing import CliRunner

from composo import ioc
from appdirs import user_config_dir

from composo.app import Composo


def main():
    ioc.App.config.from_yaml(Path(user_config_dir("composo")) / "config.yaml")
    app = ioc.App.app()
    app()
    # fire.Fire(app)


def run():
    app: Composo = ioc.App.app()
    runner = CliRunner()
    app.load_commands()
    result = runner.invoke(app._app, ["new", "--help"])
    # result = runner.invoke(app._app, ["new", "my-project", "--plugin", "pydvc", "--dry-run"])
    print(result.stdout)
    # app.new("test", lang="shell")


if __name__ == "__main__":
    run()
