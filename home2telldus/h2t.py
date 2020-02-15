from time import sleep

import requests
from urllib.parse import urlencode

from home2telldus.errors import UnknownCommandError
from home2telldus.errors import UnknownDeviceError


class Home2TelldusClient:

    def __init__(self, email, password):
        self.email = email
        self.password = password
        assert self.email and self.password
        self.session = None

    def __enter__(self):

        self.session = self.login()
        # wsevent_client_list_url = 'https://live.telldus.com/wsevent/clientList?https=1'
        # clients = self.session.get(wsevent_client_list_url).json()
        client_list_url = 'https://live.telldus.com/client/list'
        self.clients = self.session.get(client_list_url).json()['client']
        device_list_url = 'https://live.telldus.com/device/list'
        self.devices = self.session.get(device_list_url).json()['device']

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _find_device(self, device_name):
        for device in self.devices:
            if device['name'] == device_name:
                return device
        raise UnknownDeviceError()

    def _find_method(self, command):
        method_keys = {
            'on': 1,
            'off': 2,
        }
        if command not in method_keys:
            raise UnknownCommandError()

        return self._find_method(command)

    def run_command(self, device_name, command, repeat, sleep_time):
        assert self.session
        device = self._find_device(device_name)
        method = self._find_method(command)

        for _ in range(repeat):  # Repeat this many times to make sure the command is done.
            command_url = 'https://live.telldus.com/device/command?id=%(device_id)s&method=%(method_id)s'
            self.session.get(
                command_url % {
                    'device_id': device['id'],
                    'method_id': method,
                }
            )
            if repeat > 1:
                sleep(sleep_time)

    def login(self):
        session = requests.session()
        live_url = 'https://live.telldus.com/'
        session.get(live_url)
        query_params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.mode': 'checkid_setup',
            'openid.return_to': 'https://live.telldus.com/device/index',
            'openid.realm': 'https://live.telldus.com',
            'openid.ns.sreg': 'http://openid.net/extensions/sreg/1.1',
            'openid.sreg.required': 'email, fullname',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        }
        login_url = 'https://login.telldus.com/openid/server?' + urlencode(query_params)
        form_data = {
            'email': self.email,
            'password': self.password,
        }
        session.post(
            login_url,
            data=form_data,
        )

        return session
