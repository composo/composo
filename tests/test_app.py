from pathlib import Path

from composo.app import Composo

EXAMPLE_CONTENT_SMALL = """
app:
  name:
    class: TestProj
    package: test_proj
    project: test-proj
plugin: test
"""

EXAMPLE_CONTENT = """
app:
  type:
    standalone: true
    tool: true
  name:
    class: TestProj
    package: test_proj
    project: test-proj
author:
  email: arand.devel@email.de
  name: A. Rand Developer
cache_dir: /home/arand/.cache/test-proj
ci:
  gitlab:
    autoversion: false
    licensing: false
    mypy: true
    package: false
    pages: true
    pytest: true
    cml: false
conf_dir: /home/arand/.config/test-proj
plugin: test
license: mit
vcs:
  git:
    github:
      name: JanSurft
"""

TEST_FILES = {'/home/arand/projects/test-proj/.composo.yaml': EXAMPLE_CONTENT_SMALL}


class MockFile(object):
    def __init__(self, content):
        self.__content = content

    def read(self, size=None):
        if size is None:
            return self.__content
        else:
            out = self.__content[:size]
            self.__content = self.__content[size:]
            return out

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass


class MockFileOpener(object):
    def __init__(self, test_files):
        self.__test_files = test_files

    def open(self, path: Path, *args, **kwargs):
        try:
            return MockFile(self.__test_files[str(path)])
        except KeyError as e:
            raise FileNotFoundError from e


class MockLogger:
    def __init__(self):
        self.msgs = []

    def debug(self, msg):
        self.msgs.append(("DEBUG", msg))

    def warning(self, msg):
        self.msgs.append(("WARNING", msg))

    def warn(self, msg):
        self.warning(msg)

    def info(self, msg):
        self.msgs.append(("INFO", msg))

    def error(self, msg):
        self.msgs.append(("ERROR", msg))


class MockPlugin:

    def __init__(self, config):
        self.config = config
        self.new_call_data = None
        self.init_call_data = None

    def new(self, **kwargs):
        self.new_call_data = {**self.config, **kwargs}

    def init(self, path, **kwargs):
        self.init_call_data = {**self.config, **kwargs}


class MockPluginLoader:

    def __init__(self):
        self.initializer = None

    def load(self):
        class Initializer:
            def __init__(self):
                self.plugin = None

            def init(self, config):
                self.plugin = MockPlugin(config)
                return self.plugin

        self.initializer = Initializer()
        return self.initializer


class MockTyperApp:

    def callback(self, **kwargs):
        ...

    def command(self, **kwargs):
        ...


def test_composo_new_proper_argument_and_config_forwarding():
    # mock_logger = MockLogger()
    loader = MockPluginLoader()
    fopener = MockFileOpener(test_files=TEST_FILES)
    app = Composo(plugins={"test": loader}, config={"is_test": True}, app=MockTyperApp(),
                  fopen=fopener.open, getcwd=lambda: "/home/arand/projects/test-proj")

    app.new("test-proj", plugin="test", dry_run=True)

    plugin = loader.initializer.plugin

    assert plugin.new_call_data == {"dry_run": True, "plugin": "test", "name": "test-proj", "is_test": True,
                                    "template": "default"}
    assert plugin.init_call_data is None


def test_composo_init_proper_argument_and_config_forwarding():
    # mock_logger = MockLogger()
    loader = MockPluginLoader()
    fopener = MockFileOpener(test_files=TEST_FILES)
    app = Composo(
        plugins={"test": loader}, config={"dry_run": True, "is_test": True}, app=MockTyperApp(), fopen=fopener.open,
        getcwd=lambda: "/home/arand/projects/test-proj"
    )

    app.init(dry_run=True)

    plugin = loader.initializer.plugin
    expected = {'app': {'name': {'class': 'TestProj',
                                 'package': 'test_proj',
                                 'project': 'test-proj'}},
                "dry_run": True,
                "plugin": "test",
                "is_test": True
                }
    assert plugin.init_call_data == expected
    assert plugin.new_call_data is None
