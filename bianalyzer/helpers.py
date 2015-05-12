# -*- coding: utf-8 -*-
from functools import wraps
import time

from .errors import InvalidArgumentError
from .texts import BianalyzerText


def retriable_n(retry_count=3, time_sleep=0.2, exceptions=(Exception,)):
    def retriable_n_deco(func):
        @wraps(func)
        def wrapper(*args, **kw):
            for i in range(1, retry_count):
                try:
                    return func(*args, **kw)
                except Exception, e:
                    if isinstance(e, exceptions):
                        print ('%s(*%s, **%s) try %i failed, retrying: %s' % (func.__name__, args, kw, i, e))
                        time.sleep(time_sleep)
                    else:
                        raise
            else:
                return func(*args, **kw)
        return wrapper
    return retriable_n_deco


def check_text_collection(texts, raise_error=True):
    for text in texts:
        is_bianalyzer_text = isinstance(text, BianalyzerText)
        if not is_bianalyzer_text:
            if raise_error:
                raise InvalidArgumentError('texts', text, 'All texts in the collection must be of type BianalyzerText')
            return False

    return True
