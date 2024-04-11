import traceback
from enum import Enum
from pathlib import Path

from typing import Optional
from importlib.metadata import version as get_module_version

import click
import typing
import yaml
import typer
from click import UsageError
from rich.panel import Panel
from typer import rich_utils

from typer.core import TyperCommand as TyperCommandBase
from typer.rich_utils import _make_rich_rext, _get_rich_console


# typer.rich_utils.STYLE_HELPTEXT = ""


class Composo:
    """
    Composo cmdline tool for bootstrapping projects.

    :Example:

        $ composo new my-project --plugin=python
    """

    def __init__(self, plugins, config, app: typer.Typer, fopen: typing.Callable, getcwd: typing.Callable):
        self.__plugins = plugins
        self.__config = config
        self._app = app
        self._open = fopen
        self._getcwd = getcwd

    def load_commands(self):
        PluginsEnum = Enum(
            "PluginsEnum",
            names=[(name, name) for name in self.__plugins.keys()],
            module=__name__,
        )

        @self._app.callback(invoke_without_command=True)
        def get_version(
                ctx: typer.Context,
                version: bool = typer.Option(
                    False,
                    "--version",
                    "-v",
                    help="Print version and exit.",
                ),
        ) -> None:
            """
            Composo cmdline tool for bootstrapping projects.
            """
            if version:
                typer.echo(f"composo {get_module_version('composo')}")
                raise typer.Exit()
            elif ctx.invoked_subcommand is None:
                rich_utils.rich_format_error(UsageError("Missing command", ctx=ctx))
                raise typer.Exit(1)

        epilog = """
Create a new project named "my-project" with the plugin "python" without initializing it

    [dim]$ composo new my-project --plugin=python[/dim]

Create a new project named "my-project" with the plugin "python" and initialize it

    [dim]$ composo new my-project --plugin=python --init[/dim]
"""

        class TyperCommand(TyperCommandBase):

            def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
                # if not rich:
                # return super().format_help(ctx, formatter)
                epilog = self.epilog
                self.epilog = None
                rich_utils.rich_format_help(
                    obj=self,
                    ctx=ctx,
                    markup_mode=self.rich_markup_mode,
                )
                if epilog is not None:
                    console = _get_rich_console()
                    epilogue_text = _make_rich_rext(text=epilog, markup_mode="rich")
                    # console.print(Padding(Align(epilogue_text, pad=False), 1))

                    console.print(Panel(
                        epilogue_text,
                        border_style="dim",
                        title="Examples",
                        title_align="left",
                    ))

        def get_plugin():
            sorted_plugins = sorted(list(self.__plugins.keys()))
            return next(iter(sorted_plugins), None)

        @self._app.command(
            # context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
            epilog=epilog,
            cls=TyperCommand
        )
        def new(ctx: typer.Context, name: str = typer.Argument(..., help="the NAME of the project to be created"),
                plugin: Optional[PluginsEnum] = typer.Option(get_plugin(), help="the name of the plugin to be used"),
                init: Optional[bool] = typer.Option(False, help="whether the project is initialized directly"),
                dry_run: Optional[bool] = typer.Option(False, help="use dry run or not")):
            """
            Create a new project named NAME

            The plugin will create a directory named NAME and place a [dim italic].composo.yaml[/dim italic] file
            into the target directory for further configuration.
            """
            if plugin is None:
                rich_utils.rich_format_error(
                    UsageError("No installed plugins could be found, please install a composo plugin", ctx=ctx))
                raise typer.Exit(1)
            else:
                self.new(name=name, plugin=plugin.value, init=init, dry_run=dry_run)
                raise typer.Exit()

        epilog_init = """

Create a project and initialize it afterwards externally:
[dim]
    $ composo new my-project --plugin=python
    $ composo init --path=./my-project
[/dim]

Create a project and initialize it in the project directory:
[dim]
    $ composo new my-project --plugin=python
    $ cd my-project
    $ composo init
[/dim]
In either way you can modify the generated [dim].composo.yaml[/dim] file before you initialize the project.
An example [dim].composo.yaml[/dim] file would be:

[dim red]
    app:
      name:
        class: MyProject
        package: my_project
        project: my-project
    author:
      email: a.rand.developer@email.de
      name: A. Rand Developer
    cache_dir: /home/arand/.cache/composo
    ci:
      gitlab:
        pages: true
    conf_dir: /home/arand/.config/composo
    license: mit
    plugin: python
    vcs:
      git:
        github:
          name: ARand
[/]
"""

        @self._app.command(epilog=epilog_init, cls=TyperCommand)
        def init(ctx: typer.Context,
                 path: Path = typer.Argument(Path("."),
                                             help="the PATH to the project root dir for initialization",
                                             exists=True,
                                             file_okay=False,
                                             dir_okay=True,
                                             writable=True,
                                             readable=True,
                                             # resolve_path=True
                                             ),
                 dry_run: Optional[bool] = typer.Option(False, help="use dry run or not")):
            """
            Initialize the project in the given PATH or the current working directory
            """
            code = 0
            try:
                self.init(path, dry_run=dry_run)
            except FileNotFoundError:
                code = 1
                rich_utils.rich_format_error(
                    UsageError(f"Invalid value for '[PATH]': Directory '{path}' must contain '.composo.yaml'", ctx=ctx))
            finally:
                typer.Exit(code)

    def __call__(self, *args, **kwargs):
        self.load_commands()
        self._app()

    def run(self):
        self.load_commands()
        self._app()

    def _load_plugin(self, plugin, config):
        try:
            plugin = self.__plugins[plugin].load().init(config)
            return plugin

        except KeyError:
            print(traceback.format_exc())
            print(f"no plugin found with name '{plugin}', "
                  f"available plugins are: {[k for k, _ in self.__plugins.items()]}")

    def new(self, name: str, plugin: str = "python", template: str = "default", init=False, **kwargs):
        """
        Create a new project directory by the name of the chosen project name. The plugin will place
        a `.composo.yaml` file into the target directory for further configuration.

        :param name: the name of the project to be created
        :param plugin: the name of the plugin to be used
        :param template: the name of the project template to use
        :param init: whether the project is initiated directly
        :param kwargs: additional arguments that ares used by the activated plugin

        :Examples:

            Create a new project named "my-project" with the plugin "python" without initializing it

            $ composo new my-project --plugin=python

            Create a new project named "my-project" with the plugin "python" and initialize it

            $ composo new my-project --plugin=python --init
        """
        config = {**self.__config, **kwargs, "plugin": plugin, "template": template}
        loaded_plugin = self._load_plugin(plugin, config)
        loaded_plugin.new(name=name)
        if init:
            loaded_plugin.init(name)

    def init(self, path: Path = Path("."), **kwargs):
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

            app:\n
              name:\n
                class: MyProject\n
                package: my_project\n
                project: my-project\n
            author:\n
              email: a.rand.developer@email.de\n
              name: A. Rand Developer\n
            cache_dir: /home/arand/.cache/composo\n
            ci:\n
              gitlab:\n
                pages: true\n
            conf_dir: /home/arand/.config/composo\n
            license: mit\n
            plugin: python\n
            vcs:\n
              git:\n
                github:\n
                  name: ARand\n

        """
        cwd = Path(self._getcwd())
        target_path = cwd / Path(path)

        with self._open(target_path / ".composo.yaml") as f:
            try:
                existing_config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)

        config = {**self.__config, **existing_config, **kwargs}
        plugin = config["plugin"]
        plugin = self._load_plugin(plugin, config)
        plugin.init(target_path)
