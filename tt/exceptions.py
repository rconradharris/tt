class TTException(Exception):
    pass


class StatusChangeException(TTException):
    pass


class BadTaskId(TTException):
    pass
