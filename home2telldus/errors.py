class RootException(Exception):
    pass


class ClientMissingCommandError(Exception):
    pass


class ClientMissingDeviceError(Exception):
    pass


class ClientMissingEmailError(Exception):
    pass


class ClientMissingPasswordError(Exception):
    pass


class InvalidNumberError(Exception):
    def __init__(self, arg_key):
        self.arg_key = arg_key


class InvalidSecretError(Exception):
    pass


class NotANumberError(Exception):
    def __init__(self, arg_key):
        self.arg_key = arg_key


class ServerHasNoSecretError(Exception):
    pass


class ServerMissingEmailError(Exception):
    pass


class ServerMissingPasswordError(Exception):
    pass


class UnknownCommandError(Exception):
    pass


class UnknownDeviceError(Exception):
    pass
