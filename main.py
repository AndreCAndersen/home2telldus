import fire

from home2telldus.app import app
from home2telldus.h2t import Home2TelldusClient


class Home2TelldusCli:

    def run_command(self, device_name, command, email=None, password=None):
        with Home2TelldusClient(email, password) as client:
            client.run_command(device_name, command)

    def run_server(self):
        app.run(host='0.0.0.0', use_reloader=False, threaded=True)


if __name__ == '__main__':
    fire.Fire(Home2TelldusCli)
