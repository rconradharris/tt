import datetime
import errno
import os


def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


def get_now():
    now = datetime.datetime.now()
    return now


def get_date_str(fmt=None):
    if fmt is None:
        fmt = "%Y-%m-%d"
    now = get_now()
    date_str = now.strftime(fmt)
    return date_str


def get_datetime_str():
    fmt = "%Y-%m-%d %H:%M:%S"
    return get_date_str(fmt=fmt)


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

