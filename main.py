import fire
from home2telldus import h2t


class Home2TelldusCli:

    def hello(self):
        h2t.hello()


if __name__ == '__main__':
    fire.Fire(Home2TelldusCli)
