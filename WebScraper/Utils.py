
import time
import threading
import hashlib
from w3lib.url import canonicalize_url

DICT_OR_SINGLE_VALUES = (dict, bytes)


def arg2iter(arguments):
    """
        Convert input parameters into strictly iterable list objects
    """
    if not arguments:
        return []
    elif not isinstance(arguments, DICT_OR_SINGLE_VALUES) and hasattr(arguments, '__iter__'):
        return arguments
    else:
        return [arguments]


def get_md5(string):
    return hashlib.md5(to_bytes(string)).hexdigest()


def to_bytes(str, encoding=None):
    if isinstance(str, bytes):
        return str
    if not encoding:
        encoding = "utf-8"

    return str.encode(encoding)


class setInterval(object):
    def __init__(self, interval, func, *args, **kwargs):
        self.interval = interval
        self.func = func
        self.stop_event = threading.Event()
        thread = threading.Thread(target=self.__task_func, args=(self.stop_event, *args), kwargs=kwargs)
        thread.start()

        thread.join()

    def __task_func(self, *args, **kwargs):
        """
        Using the characteristics of threading event, wait(timeout) will block the current process and will continue after timeout
        Event will return true after calling the set() method, then exit the loop and end the setInterval call
        :param args:
        :param kwargs:
        :return:
        """

        next_time = time.time() + self.interval
        while not self.stop_event.wait(next_time - time.time()):
            next_time += self.interval
            self.func(*args, **kwargs)

    def cancel(self):
        self.stop_event.set()


def request_fingerprint(url):
    fp = hashlib.sha1()
    fp.update(to_bytes(canonicalize_url(url=url)))

    return fp.hexdigest()
