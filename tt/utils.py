import datetime
import errno
import os


def timedelta_total_seconds(td):
    """Return number of seconds within a timedelta object

    Code taken from Python docs. This is native in 2.7 and later
    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


def get_now():
    now = datetime.datetime.now()
    return now


def format_datetime_str(dt, fmt=None):
    if fmt is None:
        fmt = "%Y-%m-%d %H:%M:%S"
    datetime_str = dt.strftime(fmt)
    return datetime_str


def format_date_str(dt, fmt=None):
    if fmt is None:
        fmt = "%Y-%m-%d"
    datetime_str = dt.strftime(fmt)
    return datetime_str


def get_datetime_from_str(datetime_str):
    fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(datetime_str, fmt)


def mkdirs_easy(dir):
    """mkdirs but don't raise if it exists"""
    try:
        os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
