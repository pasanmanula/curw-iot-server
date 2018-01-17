from datetime import datetime, timedelta
from config import Constants


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_date_time_object(value, as_str=False, unix_offset=timedelta()):
    """
    :param value: [long/str] UNIX Timestamp or Date Time string in "%Y-%m-%d %H:%M:%S" format
    :param as_str: [bool] If str is True, return date time string in "%Y-%m-%d %H:%M:%S" format, otherwise datetime obj
    :param unix_offset: [timedelta] If value is provided in UNIX Timestamp, apply the given UTC Offset. Default is 0.
    :return: datetime object instance or date time string in "%Y-%m-%d %H:%M:%S" format
    """
    # -- If UNIX Timestamp
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        return (datetime.utcfromtimestamp(float(value)) + unix_offset).strftime(Constants.DATE_TIME_FORMAT) \
            if as_str else datetime.utcfromtimestamp(float(value)) + unix_offset
    # -- If Date Time string
    elif isinstance(value, str):
        try:
            return datetime.strptime(value, Constants.DATE_TIME_FORMAT).strftime(Constants.DATE_TIME_FORMAT) \
                if as_str else datetime.strptime(value, Constants.DATE_TIME_FORMAT)
        except Exception as datetime_error:
            raise datetime_error
    else:
        raise Exception("Value should be UNIX timestamp or date time string")


def get_float(value, filed_name, logger):
    try:
        return float(value)
    except Exception as error:
        logger.error('%s: %s', filed_name, error)
        raise Exception("Unable to validate %s field value" % filed_name)
