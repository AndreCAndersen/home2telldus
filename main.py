import fire
from home2telldus.h2t import Home2TelldusClient


class Home2TelldusCli:

    def run(self, device_name, command, email=None, password=None):
        with Home2TelldusClient(email, password) as client:
            client.run(device_name, command)


if __name__ == '__main__':
    fire.Fire(Home2TelldusCli)
