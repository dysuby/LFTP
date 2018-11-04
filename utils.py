from datetime import datetime


def logger(str):
    print('{} - {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str))
