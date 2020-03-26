__doc__ = """
manage global timeout
use short/long/custom_timeout functions to configute global timeout to your needs
"""
import sys
this = sys.modules[__name__]

_implicit_wait = 0.2
_retry_time = 0.2
_long_timeout = 8
_short_timeout = 1
_default_timeout = 3
_custom_timeout = 3
this._current = _default_timeout

this._usage_counter = 1
this._temporery = False


def Get():
    """
    get currently active timeout:
    (timeout, retry_timeout)
    """
    if this._temporery:
        if this._usage_counter < 1:
            this._current = _default_timeout
            this._retry_time = 0.2
            this._temporery = False
        else:
            this._usage_counter -= 1
    return (this._current, this._retry_time)


# def Retry_time():
#     return _retry_time


def Custom_timeout(timeout: int,retry_time: int ,expired=1):
    """
    give a timeout for 'expired' times (default 1 time)    """
    this._current = timeout
    this._retry_time = retry_time
    this._usage_counter = expired
    this._temporery = True


def Long_timeout(expired=1):
    """
    use long timeout for 'expired' times (default 1 time)
    """
    this._current = _long_timeout
    this._usage_counter = expired
    this._temporery = True


def Short_timeout(expired=1):
    """
    use short timeout for 'expired' times (default 1 time)
    """
    this._current = _short_timeout
    this._usage_counter= expired
    this._temporery = True

def Default_timeout():
    """
    set global timeout to default
    """
    this._current = _default_timeout
