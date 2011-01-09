class TTException(Exception):
    pass


class StatusChangeException(TTException):
    pass


class BadTaskId(TTException):
    pass


class DirectoryNotFound(TTException):
    pass
