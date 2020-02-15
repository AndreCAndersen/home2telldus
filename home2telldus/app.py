import os
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields

from home2telldus.errors import RootException
from home2telldus.errors import ClientMissingCommandError
from home2telldus.errors import ClientMissingDeviceError
from home2telldus.errors import ClientMissingEmailError
from home2telldus.errors import ClientMissingPasswordError
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

api = Api(app)

default_model = api.model('DefaultModel', {
    'message': fields.String(description='A message from the API.'),
})

error_model = api.model('ErrorModel', {
    'message': fields.String(description='An error message from the API.'),
    'exception': fields.String(description='The exception type of the error.'),
})

command_model = api.model('CommandModel', {
    'secret': fields.String(),
    'email': fields.String(),
    'password': fields.String(),
    'device': fields.String(),
    'command': fields.String(),
    'repeat': fields.Integer(),
    'sleep': fields.Float(),
})


@app.route('/')
def main():
    return render_template('index.html')


@api.route('/api/command')
@api.doc(
    post={
        'params': {
            'secret': 'A secret set as the APP_SECRET env variable. If used env variables TELLDUS_EMAIL and TELLDUS_PASSWORD will be used as email and password.',
            'email': 'A Telldus Live email. Requires a password.',
            'password': 'A Telldus Live password. Requires an email.',
            'device': 'The name of the device for which a command should be given. Required.',
            'command': 'Accepts either `on` or `off` as commands to the specified device. Required.',
            'repeat': 'An integer saying how many times the command should be given, between 1 and 8. Usefull to make sure the command is actually registered. Default is 4.',
            'sleep': 'How long (seconds) the request should wait between repeated commands. Default is 2 seconds.',
        }
    }
)
class CommandResource(Resource):

    @api.marshal_with(default_model)
    @api.expected(command_model)
    def post(self):
        args = request.json
        email, password = self._get_email_and_password(args)
        command, device_name = self._get_command_and_device(args)
        repeat = self._get_argument('repeat', 4, 1, 8, int)
        sleep_time = self._get_argument('sleep', 2, 0, 2, float)

        with Home2TelldusClient(email, password) as client:
            client.run_command(device_name, command, repeat, sleep_time)

        return jsonify({'message': 'Command was successfully sent.'})

    @classmethod
    def _get_email_and_password(cls, args):
        actual_secret = os.environ.get('APP_SECRET')
        claimed_secret = args['secret']
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
            email = args['email']
            if not email:
                raise ClientMissingEmailError()
            password = args['password']
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
        device = args['device']
        if not device:
            raise ClientMissingDeviceError()
        command = args['command']
        if not command:
            raise ClientMissingCommandError()
        return command, device


@api.errorhandler(RootException)
@api.marshal_with(error_model)
def handle_root_exception(error):
    return {
        'message': 'An error occurred.',
        'exception': 'RootException'
    }, 400


@api.errorhandler(ClientMissingCommandError)
@api.marshal_with(error_model)
def handle_client_missing_command_error(error):
    return {
        'message': 'Client did not provide `command` query parameter.',
        'exception': 'ClientMissingCommandError'
    }, 401


@api.errorhandler(ClientMissingDeviceError)
@api.marshal_with(error_model)
def handle_client_missing_device_error(error):
    return {
        'message': 'Client did not provide `device` query parameter.',
        'exception': 'ClientMissingDeviceError'
    }, 401


@api.errorhandler(ClientMissingEmailError)
@api.marshal_with(error_model)
def handle_client_missing_email_error(error):
    return {
        'message': 'Client did not provide `email` query parameter.',
        'exception': 'ClientMissingEmailError'
    }, 401


@api.errorhandler(ClientMissingPasswordError)
@api.marshal_with(error_model)
def handle_client_missing_password_error(error):
    return {
        'message': 'Client did not provide `password` query parameter.',
        'exception': 'ClientMissingPasswordError'
    }, 401


@api.errorhandler(InvalidNumberError)
@api.marshal_with(error_model)
def handle_invalid_number_error(error):
    return {
        'message': 'Client supplied a `%s` query of illegal size.',
        'exception': 'InvalidNumberError' % error.arg_key
    }, 400


@api.errorhandler(InvalidSecretError)
@api.marshal_with(error_model)
def handle_invalid_secret_error(error):
    return {
        'message': 'Client provided the incorrect `secret` query parameter.',
        'exception': 'InvalidSecretError'
    }, 401


@api.errorhandler(NotANumberError)
@api.marshal_with(error_model)
def handle_not_a_number_error(error):
    return {
        'message': 'Client did not supply a valid number as the `%s` query parameter.',
        'exception': 'ClientMissingCommandError' % error.arg_key
    }, 400


@api.errorhandler(ServerHasNoSecretError)
@api.marshal_with(error_model)
def handle_server_has_no_secret_error(error):
    return {
        'message': 'Server is not configured with a `APP_SECRET` environmental variable.',
        'exception': 'ServerHasNoSecretError'
    }, 500


@api.errorhandler(ServerMissingEmailError)
@api.marshal_with(error_model)
def handle_server_missing_email_error(error):
    return {
        'message': 'Server is not configured with `TELLDUS_EMAIL` environmental variable.',
        'exception': 'ServerMissingEmailError'
    }, 500


@api.errorhandler(ServerMissingPasswordError)
@api.marshal_with(error_model)
def handle_server_missing_password_error(error):
    return {
        'message': 'Server is not configured with `TELLDUS_PASSWORD` environmental variable.',
        'exception': 'ServerMissingPasswordError'
    }, 500


@api.errorhandler(UnknownCommandError)
@api.marshal_with(error_model)
def handle_unknown_command_error(error):
    return {
        'message': 'Client provided an unknown `command` query parameter.',
        'exception': 'UnknownCommandError'
    }, 400


@api.errorhandler(UnknownDeviceError)
@api.marshal_with(error_model)
def handle_unknown_device_error(error):
    return {
        'message': 'Client provided an unknown `device` query parameter.',
        'exception': 'UnknownDeviceError'
    }, 400
