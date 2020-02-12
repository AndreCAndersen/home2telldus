import fire
from home2telldus import h2t


class Home2TelldusCli:

    def login(self):
        h2t.login()


if __name__ == '__main__':
    fire.Fire(Home2TelldusCli)
