import os
from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = is_debug = os.environ.get('ENVIRONMENT', 'production') == 'debug'


@app.route('/')
def main():
    return 'app'


@app.route('/api')
def api():
    return 'api'
