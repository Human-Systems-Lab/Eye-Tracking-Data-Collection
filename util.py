from threading import Lock
from functools import wraps


def no_recursion(default=None):
    def decorator(f):
        @wraps(f)
        def func(*args, **kwargs):
            if hasattr(func, "_executing") and func._executing:
                return default
            func._executing = True
            ret = f(*args, **kwargs)
            func._executing = False
            return ret

        return func
    return decorator
