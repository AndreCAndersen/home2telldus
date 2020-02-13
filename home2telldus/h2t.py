import os
from time import sleep

import requests
from urllib.parse import urlencode
import bs4

class Home2TelldusClient:

    def __init__(self, email=os.environ.get('TELLDUS_EMAIL'), password=os.environ.get('TELLDUS_PASSWORD')):
        self.email = email
        self.password = password
        self.session = None

    def __enter__(self):
        print("Entering client.")
        print()

        self.session = self.login()

        # wsevent_client_list_url = 'https://live.telldus.com/wsevent/clientList?https=1'
        # clients = self.session.get(wsevent_client_list_url).json()
        # pprint(clients)

        print('Clients')
        print('  ', 'name', 'id')
        print('  ', '---------------')
        client_list_url = 'https://live.telldus.com/client/list'
        self.clients = self.session.get(client_list_url).json()['client']
        for client in self.clients:
            print('  ', client['name'], client['id'])
        print()

        device_list_url = 'https://live.telldus.com/device/list'
        self.devices = self.session.get(device_list_url).json()['device']
        print('Devices')
        print('  ', 'name', 'id', 'devices', 'online')
        print('  ', '---------------')
        for device in self.devices:
            print('  ', device['name'], device['id'], device.get('devices'), device['online'])
        print()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print()
        print("Exiting client.")

    def run(self, device_name, command):
        assert self.session
        method_keys = {
            'on': 1,
            'off': 2,
        }
        device = next(device for device in self.devices if device['name'] == device_name)
        print('Running Command:', device_name, '->', command)
        for _ in range(5):  # Five times to make sure the command is done.
            command_url = 'https://live.telldus.com/device/command?id=%(device_id)s&method=%(method_id)s'
            response = self.session.get(
                command_url % {
                    'device_id': device['id'],
                    'method_id': method_keys[command],
                }
            )
            print('  ', response.json())
            sleep(2)
        print()

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
        response = session.post(
            login_url,
            data=form_data,
        )

        sup = bs4.BeautifulSoup(response.text, features='html.parser')
        name = sup.find('a', {'class': 'loginItem'}).get_text().split(':')[1].strip()
        print('Logged in')
        print('  ', name)
        print()

        return session
