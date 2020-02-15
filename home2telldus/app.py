import os
from flask import Flask
from flask import request
from flask_restx import Api
from flask_restx import Resource
from flask_restx import fields

from home2telldus.errors import RootException
from home2telldus.errors import ClientMissingCommandError
from home2telldus.errors import ClientMissingDeviceError
from home2telldus.errors import ClientMissingEmailError
from home2telldus.errors import ClientMissingPasswordError
from home2telldus.errors import InvalidEmailOrPasswordError
from home2telldus.errors import InvalidNumberError
from home2telldus.errors import InvalidSecretError
from home2telldus.errors import NotANumberError
from home2telldus.errors import ServerHasNoSecretError
from home2telldus.errors import ServerMissingEmailError
from home2telldus.errors import ServerMissingPasswordError
from home2telldus.errors import UnknownCommandError
from home2telldus.errors import UnknownDeviceError
from home2telldus.h2t import Home2TelldusClient

app = Flask(__name__)
app.config['DEBUG'] = is_debug = os.environ.get('APP_ENV', 'production') == 'debug'

doc_html = """
This is a free API service to enable voice commands from [Google Home](https://store.google.com/product/google_home) to [Telldus Live!](https://live.telldus.com/) via 
[IFTTT](https://ifttt.com/). It was created primarly to support my own DYI home automation setup, but as it is 
already running it might as well respond to external requests as well.

Instructions
---

1) Set up Google Home with a Google Assistant.
2) Set up a Telldus Live! account and configure your devices to use it.
3) Make sure that you use email and password authentication with your Google Home account.
4) Set up a IFTTT account.
5) Link your Google Home to IFTTT. You do not need to do the same with Telldus Live!.
6) When logged in to IFTTT click your profile, and then Create.
7) Choose Google Assistant as a service.
8) Choose "Say a simple phrase" as your trigger.
9) Add your phrase, and other variants of it, and a response. Then click "Create trigger".
10) Choose Webhook as your service and "Make a web request" as the action.
12) Add `http://home2telldus.herokuapp.com/command`, or your own heroku server URL.
13) Use POST as the method.
14) Select `application/json` as the content type.
15) Add your command as a json object in the body. The following is an example:

```
{
    "email": "you@example.com",
    "password": "your_password",
    "device": "Your Device",
    "command": "on"
}
```

You can also set `repeat` and `sleep`. In addition, if you are running your own 
server you  can configure `TELLDUS_EMAIL`, `TELLDUS_PASSWORD` and `APP_SECRET` 
thus enabling the option to use the `secret` argument instead of passing `email` 
and `password`  as arguments. This makes it possible to not have to store your 
password in IFTTT.

16) When all this is done, click create action, and everything should be set up.

Testing Telldus Live! interface
---
Use the testing suit below. default > POST /command > Try it out. 

Source Code
---

Source code can be found on <a href="https://github.com/AndreCAndersen/home2telldus">Github</a>.

Warranty and Risk
---

This service comes with ABSOLUTELY NO WARRANTY, and you use it at your own risk.

Note that query parameters set using a `get` requests will be logged by heroku. This means 
your email and password will be stored in plain text, and retrievable.This means you 
should not use the GET requests with this API. Objects sent by POST requests do not 
seem to be logged by heroku. However, ultimately you will have to trust heroku and the
author of this API that it will not be recorded.
"""

api = Api(app, title='home2telldus API', description=doc_html)

command_arg_doc = {
    'secret': 'A secret set as the APP_SECRET env variable. If used env variables TELLDUS_EMAIL and TELLDUS_PASSWORD will be used as email and password.',
    'email': 'A Telldus Live email. Requires a password.',
    'password': 'A Telldus Live password. Requires an email.',
    'device': 'The name of the device for which a command should be given. Required.',
    'command': 'Accepts either `on` or `off` as commands to the specified device. Required.',
    'repeat': 'An integer saying how many times the command should be given, between 1 and 8. Usefull to make sure the command is actually registered. Default is 4.',
    'sleep': 'How long (seconds) the request should wait between repeated commands. Default is 2 seconds.',
}

default_model = api.model('DefaultModel', {
    'message': fields.String(description='A message from the API.'),
})

error_model = api.model('ErrorModel', {
    'message': fields.String(description='An error message from the API.'),
    'exception': fields.String(description='The exception type of the error.'),
})

command_model = api.model('CommandModel', {
    'secret': fields.String(description=command_arg_doc['secret']),
    'email': fields.String(description=command_arg_doc['email']),
    'password': fields.String(description=command_arg_doc['password']),
    'device': fields.String(description=command_arg_doc['device']),
    'command': fields.String(description=command_arg_doc['command']),
    'repeat': fields.Integer(description=command_arg_doc['repeat']),
    'sleep': fields.Float(description=command_arg_doc['sleep']),
})


@api.route('/command')
@api.doc(
    get={'params': command_arg_doc},
)
class CommandResource(Resource):

    @api.marshal_with(default_model, mask=False)
    def get(self):
        return self._handle_request(request.args)

    @api.marshal_with(default_model, mask=False)
    @api.expect(command_model)
    def post(self):
        return self._handle_request(request.json)

    @classmethod
    def _handle_request(cls, args):
        email, password = cls._get_email_and_password(args)
        command, device_name = cls._get_command_and_device(args)
        repeat = cls._get_argument('repeat', 4, 1, 8, int)
        sleep_time = cls._get_argument('sleep', 2, 0, 2, float)

        with Home2TelldusClient(email, password) as client:
            client.run_command(device_name, command, repeat, sleep_time)

        return {'message': 'Command was successfully sent.'}

    @classmethod
    def _get_email_and_password(cls, args):
        actual_secret = os.environ.get('APP_SECRET')
        claimed_secret = args.get('secret')
        if claimed_secret and not actual_secret:
            raise ServerHasNoSecretError()
        elif claimed_secret and actual_secret:
            email = os.environ.get('TELLDUS_EMAIL')
            if not email:
                raise ServerMissingEmailError()
            password = os.environ.get('TELLDUS_PASSWORD')
            if not password:
                raise ServerMissingPasswordError()
            if actual_secret != claimed_secret:
                raise InvalidSecretError()
        else:
            email = args.get('email')
            if not email:
                raise ClientMissingEmailError()
            password = args.get('password')
            if not password:
                raise ClientMissingPasswordError()
        return email, password

    @classmethod
    def _get_argument(cls, arg_key, default_value, from_value, to_value, number_type):
        value = request.args.get(arg_key)
        if value:
            try:
                value = number_type(value)
            except Exception:
                raise NotANumberError(arg_key)
            if not (from_value <= value <= to_value):
                raise InvalidNumberError(arg_key)
        else:
            value = default_value
        return value

    @classmethod
    def _get_command_and_device(cls, args):
        device = args.get('device')
        if not device:
            raise ClientMissingDeviceError()
        command = args.get('command')
        if not command:
            raise ClientMissingCommandError()
        return command, device


@api.errorhandler(RootException)
@api.marshal_with(error_model, mask=False)
def handle_root_exception(error):
    return {
        'message': 'An error occurred.',
        'exception': 'RootException'
    }, 400


@api.errorhandler(ClientMissingCommandError)
@api.marshal_with(error_model, mask=False, code=401)
def handle_client_missing_command_error(error):
    return {
        'message': 'Client did not provide `command` query parameter.',
        'exception': 'ClientMissingCommandError'
    }, 401


@api.errorhandler(ClientMissingDeviceError)
@api.marshal_with(error_model, mask=False, code=401)
def handle_client_missing_device_error(error):
    return {
        'message': 'Client did not provide `device` query parameter.',
        'exception': 'ClientMissingDeviceError'
    }, 401


@api.errorhandler(ClientMissingEmailError)
@api.marshal_with(error_model, mask=False, code=401)
def handle_client_missing_email_error(error):
    return {
        'message': 'Client did not provide `email` query parameter.',
        'exception': 'ClientMissingEmailError'
    }, 401


@api.errorhandler(ClientMissingPasswordError)
@api.marshal_with(error_model, mask=False, code=401)
def handle_client_missing_password_error(error):
    return {
        'message': 'Client did not provide `password` query parameter.',
        'exception': 'ClientMissingPasswordError'
    }, 401


@api.errorhandler(InvalidEmailOrPasswordError)
@api.marshal_with(error_model, mask=False, code=400)
def handle_invalid_number_error(error):
    return {
        'message': 'Invalid email or password supplied.',
        'exception': 'InvalidEmailOrPasswordError'
    }, 400  # Technically it can be a 500 too.


@api.errorhandler(InvalidNumberError)
@api.marshal_with(error_model, mask=False, code=400)
def handle_invalid_number_error(error):
    return {
        'message': 'Client supplied a `%s` query of illegal size.',
        'exception': 'InvalidNumberError' % error.arg_key
    }, 400


@api.errorhandler(InvalidSecretError)
@api.marshal_with(error_model, mask=False, code=401)
def handle_invalid_secret_error(error):
    return {
        'message': 'Client provided the incorrect `secret` query parameter.',
        'exception': 'InvalidSecretError'
    }, 401


@api.errorhandler(NotANumberError)
@api.marshal_with(error_model, mask=False, code=400)
def handle_not_a_number_error(error):
    return {
        'message': 'Client did not supply a valid number as the `%s` query parameter.',
        'exception': 'ClientMissingCommandError' % error.arg_key
    }, 400


@api.errorhandler(ServerHasNoSecretError)
@api.marshal_with(error_model, mask=False, code=500)
def handle_server_has_no_secret_error(error):
    return {
        'message': 'Server is not configured with a `APP_SECRET` environmental variable.',
        'exception': 'ServerHasNoSecretError'
    }, 500


@api.errorhandler(ServerMissingEmailError)
@api.marshal_with(error_model, mask=False, code=500)
def handle_server_missing_email_error(error):
    return {
        'message': 'Server is not configured with `TELLDUS_EMAIL` environmental variable.',
        'exception': 'ServerMissingEmailError'
    }, 500


@api.errorhandler(ServerMissingPasswordError)
@api.marshal_with(error_model, mask=False, code=500)
def handle_server_missing_password_error(error):
    return {
        'message': 'Server is not configured with `TELLDUS_PASSWORD` environmental variable.',
        'exception': 'ServerMissingPasswordError'
    }, 500


@api.errorhandler(UnknownCommandError)
@api.marshal_with(error_model, mask=False, code=400)
def handle_unknown_command_error(error):
    return {
        'message': 'Client provided an unknown `command` query parameter.',
        'exception': 'UnknownCommandError'
    }, 400


@api.errorhandler(UnknownDeviceError)
@api.marshal_with(error_model, mask=False, code=400)
def handle_unknown_device_error(error):
    return {
        'message': 'Client provided an unknown `device` query parameter.',
        'exception': 'UnknownDeviceError'
    }, 400
