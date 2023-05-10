class ServiceNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)
class ExceedsLengthException(Exception):
    def __init__(self, message):
        super().__init__(message)