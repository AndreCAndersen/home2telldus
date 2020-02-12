import os


def login():

    telldus_user_name = os.environ.get('TELLDUS_USERNAME')
    telldus_password = os.environ.get('TELLDUS_PASSWORD')

    print(telldus_user_name, telldus_password)
