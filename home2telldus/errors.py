class RootException(BaseException):
    pass


class ClientMissingCommandError(RootException):
    pass


class ClientMissingDeviceError(RootException):
    pass


class ClientMissingEmailError(RootException):
    pass


class ClientMissingPasswordError(RootException):
    pass


class InvalidNumberError(RootException):
    def __init__(self, arg_key):
        self.arg_key = arg_key


class InvalidSecretError(RootException):
    pass


class NotANumberError(RootException):
    def __init__(self, arg_key):
        self.arg_key = arg_key


class ServerHasNoSecretError(RootException):
    pass


class ServerMissingEmailError(RootException):
    pass


class ServerMissingPasswordError(RootException):
    pass


class UnknownCommandError(RootException):
    pass


class UnknownDeviceError(RootException):
    pass
