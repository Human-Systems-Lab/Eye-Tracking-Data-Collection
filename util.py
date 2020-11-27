from threading import Lock, current_thread
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


def debug_fn(use_thread_id=False, print_args=False, print_ret=False, member_fn=False):
    def decorator(f):
        @wraps(f)
        def func(*args, **kwargs):
            if print_args:
                if use_thread_id:
                    print(
                        "Entering function %s on thread %s\nargs: %s\nkwargs: %s\n" %
                        (f.__name__, current_thread().getName(), str(args[1:] if member_fn else args), str(kwargs))
                    )
                else:
                    print(
                        "Entering function %s\nargs: %s\nkwargs: %s\n" %
                        (f.__name__, str(args[1:] if member_fn else args), str(kwargs))
                    )
            else:
                if use_thread_id:
                    print(
                        "Entering function %s on thread %s\n" %
                        (f.__name__, current_thread().getName())
                    )
                else:
                    print(
                        "Entering function %s\n" %
                        (f.__name__,)
                    )
            try:
                ret = f(*args, **kwargs)
                if print_ret:
                    if use_thread_id:
                        print(
                            "Exiting function %s on thread %s...\nReturn value %s\n" %
                            (f.__name__, current_thread().getName(), str(ret))
                        )
                    else:
                        print(
                            "Exiting function %s...\nReturn value %s\n" %
                            (f.__name__, str(ret))
                        )
                else:
                    if use_thread_id:
                        print(
                            "Exiting function %s on thread %s...\n" %
                            (f.__name__, current_thread().getName())
                        )
                    else:
                        print(
                            "Exiting function %s...\n" %
                            (f.__name__,)
                        )
                return ret
            except Exception as e:
                if use_thread_id:
                    print(
                        "Encountered exception in function %s on thread %s" %
                        (f.__name__, current_thread().getName())
                    )
                else:
                    print(
                        "Encountered exception in function %s" %
                        (f.__name__,)
                    )
                print(e)
                print()
                raise e
        return func
    return decorator
