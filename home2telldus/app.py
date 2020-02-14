import os
from flask import Flask
from flask import jsonify
from flask import request

from home2telldus.h2t import Home2TelldusClient

app = Flask(__name__)
app.config['DEBUG'] = is_debug = os.environ.get('ENVIRONMENT', 'production') == 'debug'


@app.route('/')
def main():
    return 'app'


@app.route('/api')
def api():
    return 'api'


@app.route('/api')
def api():
    command = request.args.get('command')
    device_name = request.args.get('device_name')

    with Home2TelldusClient() as client:
        client.run(device_name, command)

    return jsonify({'message': 'success'})
