import fire

from composo import ioc


def main():

    app = ioc.App.app()
    fire.Fire(app)


def test():
    app = ioc.App.app()
    app.new("test", lang="shell")


if __name__ == "__main__":
    test()
