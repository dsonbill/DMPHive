# Control
Debugging = True
Loop = None


# Formatting
Padding = 2
LogLevels = []
LogPadding = [0, 0]
LogTemplate = '[{}]:{}[{}] {}'


# This is probably useless; leaving for reference
#def async_logging(func):
#    log_coroutine = asyncio.coroutine(func)
#    def set_coroutine(*args, **kwargs):
#        if Loop is not None:
#            asyncio.async(log_coroutine(*args, **kwargs), loop=Loop)
#    return set_coroutine


def calculate_padding(size):
    for text in LogLevels:
        if LogPadding[0] < len(text):
            LogPadding[0] = len(text)
    LogPadding[1] = LogPadding[0] + size


def log(tag, content, *formatargs, level='LOG'):
    if level not in LogLevels:
        LogLevels.append(level)
        calculate_padding(Padding)
    print(LogTemplate.format(level, ' ' * (LogPadding[1] - len(level)), tag, content.format(*formatargs)))


def debug(tag, text, *formatargs):
    if Debugging:
        log(tag, text, *formatargs, level='DEBUG')


def error(tag, text, *formatargs):
    log(tag, text, *formatargs, level='ERROR')


def exception(tag, text, exception_instance, *formatargs):
    error(tag, 'Exception  [ {} ]  While {}'.format(type(exception_instance), text), *formatargs)
    log(tag, str(exception_instance.with_traceback(None)), level='EXCEPT')