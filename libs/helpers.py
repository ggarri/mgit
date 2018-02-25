import multiprocessing
import traceback
from multiprocessing.pool import Pool


class Color():
    _RED = "\033[1;31m"
    _BLUE = "\033[1;34m"
    _YELLOW = "\033[1;93m"
    _CYAN = "\033[1;36xm"
    _GREEN = "\033[0;32m"
    _RESET = "\033[0;0m"
    _BOLD = "\033[;1m"
    _REVERSE = "\033[;7m"

    @staticmethod
    def red(str):
        return Color.build(str, Color._RED)

    @staticmethod
    def green(str):
        return Color.build(str, Color._GREEN)

    @staticmethod
    def yellow(str):
        return Color.build(str, Color._YELLOW)

    @staticmethod
    def build(str, COLOR):
        return "%s%s%s" % (COLOR, str, Color._RESET)

# Shortcut to multiprocessing's logger
def error(msg, *args):
    return multiprocessing.get_logger().error(msg, *args)

class LogExceptions(object):
    def __init__(self, callable):
        self.__callable = callable

    def __call__(self, *args, **kwargs):
        try:
            result = self.__callable(*args, **kwargs)
        except Exception as e:
            # Here we add some debugging help. If multiprocessing's
            # debugging is on, it will arrange to log the traceback
            error(traceback.format_exc())
            # Re-raise the original exception so the Pool worker can
            # clean up
            raise

        # It was fine, give a normal answer
        return result

class LoggingPool(Pool):
    def apply_async(self, func, args=(), kwds={}, callback=None):
        return Pool.apply_async(self, LogExceptions(func), args, kwds, callback)
