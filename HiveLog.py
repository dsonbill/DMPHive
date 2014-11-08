__author__ = 'William C. Donaldson'

Debugging = True
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
    if level == 'DEBUG' and Debugging:
        print(LogTemplate.format(level, ' ' * (LogPadding[1] - len(level)), tag, content.format(*formatargs)))
    elif level != 'DEBUG':
        print(LogTemplate.format(level, ' ' * (LogPadding[1] - len(level)), tag, content.format(*formatargs)))


def debug(tag, text, *formatargs):
    log(tag, text, *formatargs, level='DEBUG')


def error(tag, text, *formatargs):
    log(tag, text, *formatargs, level='ERROR')