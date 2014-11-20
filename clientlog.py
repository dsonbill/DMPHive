import clientconf


Padding = 2

LogLevels = []
LogPadding = [0, 0]
LogTemplate = '[{}]:{}[{}] {}'


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
    if clientconf.CONFIG['LOGGING']['Debugging'] == 'True':
        log(tag, text, *formatargs, level='DEBUG')


def error(tag, text, *formatargs):
    log(tag, text, *formatargs, level='ERROR')