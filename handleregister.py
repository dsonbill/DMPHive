import asyncio
import clientlog

MESSAGE_HANDLERS = {}
LOG_TAG = 'REGISTER'


def message_handler(func):
    @asyncio.coroutine
    def meta_func(*args, **kwargs):
        clientlog.debug(LOG_TAG, "Called Message Handler  [ {} ]  With Args  [ {}, {} ]", func.__name__, args, kwargs)
        yield from func(*args, **kwargs)
    MESSAGE_HANDLERS[func.message_namespace + func.__name__] = meta_func
    clientlog.debug(LOG_TAG, 'Registered Message Handler  [ {} ]', func.__name__)