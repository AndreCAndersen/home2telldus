import os
import requests
from urllib.parse import urlencode


class FailedLoginException(Exception):
    pass


def login():

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

    headers = {
        'Cache-Control': 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0',
        'Connection': 'close',
        'Content-Length': '0',
        'Content-Type': 'text/html; charset=UTF-8',
        'Location': login_url,
        'Pragma': 'no-cache',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'strict-transport-security': 'max-age=0',
        'X-Content-Type-Options': 'nosniff',
        'X-DNS-Prefetch-Control': 'off',
        'X-Xss-Protection': '1',
    }

    form_data = {
        'email': os.environ.get('TELLDUS_EMAIL'),
        'password': os.environ.get('TELLDUS_PASSWORD'),
    }

    response = requests.post(
        login_url,
        data=form_data,
        headers=headers
    )

    if 'You are logging on to the site' in response.text:
        print('SUCCESSFULLY LOGGED IN!')
        print(dict(response.cookies))
    else:
        raise FailedLoginException()
