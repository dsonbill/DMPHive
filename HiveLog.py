__author__ = 'William C. Donaldson'

Debugging = True
Padding = 2

LogLevels = []
LogPadding = [0, 0]
LogTemplate = '[{}]:{}[{}] {}'


def log(tag, text, level='LOG'):
    if level not in LogLevels:
        LogLevels.append(level)
        calculate_padding(Padding)
    if level == 'DEBUG' and Debugging:
        print(LogTemplate.format(level, ' ' * (LogPadding[1] - len(level)), tag, text))
    elif level != 'DEBUG':
        print(LogTemplate.format(level, ' ' * (LogPadding[1] - len(level)), tag, text))


def calculate_padding(size):
    for text in LogLevels:
        if LogPadding[0] < len(text):
            LogPadding[0] = len(text)
    LogPadding[1] = LogPadding[0] + size