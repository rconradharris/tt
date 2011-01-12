import datetime
import errno
import os


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


def get_date_from_str(date_str):
    fmt = "%Y-%m-%d"
    return datetime.datetime.strptime(date_str, fmt).date()


def date_match(date1, date2):
    """Determine if two datetime/date objs share the same date"""
    return ((date1.day == date2.day) and (date1.month == date2.month) and
            (date1.year == date2.year))


def date2datetime(date1):
    """Return an equivalent datetime obj from date object"""
    year = date1.year
    month = date1.month
    day = date1.day
    datetime1 = datetime.datetime(year, month, day, 0, 0, 0, 0)
    return datetime1


def mkdirs_easy(dir):
    """mkdirs but don't raise if it exists"""
    try:
        os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
