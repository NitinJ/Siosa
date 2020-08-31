import functools
import threading


def synchronized(wrapped=None, lock=None):
    if wrapped is None:
        return functools.partial(synchronized, lock=lock)

    @functools.wraps(wrapped)
    def _wrapper(*args, **kwargs):
        synclock = None
        if args[0].lock is None:
            synclock = lock
        if synclock is None:
            synclock = lock
        if synclock is None:
            synclock = threading.RLock()
        with synclock:
            return wrapped(*args, **kwargs)

    return _wrapper


def abstractmethod(func_):
    def abstract_method(*args, **kwargs):
        raise Exception("In-implemented abstract method Exception!")

    return abstract_method
