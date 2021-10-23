###
# File created by Leonardo Cencetti on 2/6/21
###
import time
from functools import wraps


def debug_me(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print("[{}] Starting".format(func.__name__))
        out = func(*args, **kwargs)
        print("[{}] Done".format(func.__name__))
        return out

    return decorated


def time_me(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        t0 = time.time()
        out = func(*args, **kwargs)
        print(func.__name__, "took", time.time() - t0, "seconds.")
        return out

    return decorated
