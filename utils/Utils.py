from datetime import datetime
from config import Constants


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_date_time_object(value, as_str=False):
    """
    :param value: [long/str] UNIX Timestamp or Date Time string in "%Y-%m-%d %H:%M:%S" format
    :param as_str: [bool] If str is True, return date time string in "%Y-%m-%d %H:%M:%S" format, otherwise datetime obj
    :return: datetime object instance or date time string in "%Y-%m-%d %H:%M:%S" format
    """
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        return datetime.utcfromtimestamp(float(value)).strftime(Constants.DATE_TIME_FORMAT) \
            if as_str else datetime.utcfromtimestamp(float(value))
    elif isinstance(value, str):
        try:
            return datetime.strptime(value, Constants.DATE_TIME_FORMAT).strftime(Constants.DATE_TIME_FORMAT) \
                if as_str else datetime.strptime(value, Constants.DATE_TIME_FORMAT)
        except Exception as datetime_error:
            raise datetime_error
    else:
        raise Exception("Value should be UNIX timestamp or date time string")
