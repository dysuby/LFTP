from datetime import datetime


class PACK:
    @staticmethod
    def serialize(data, kwargs={}):
        res = '{}{}'.format(len(kwargs), Field.CUT)
        for key, value in kwargs.items():
            res += '{}:{}{}'.format(key, value, Field.CUT)
        res = bytes(res, 'utf-8') + data
        return res

    @staticmethod
    def deserialize(data):
        fileds = data.split(bytes(Field.CUT, 'utf-8'))
        kw = {}
        end = int(fileds[0]) + 1
        for i in range(1, end):
            key, value = fileds[i].split(b':')
            key = key.decode()
            if key in [Field.FILE_NAME, Field.OPT]:
                value = value.decode()
            else:
                value = int(value)
            kw[key] = value
        return kw, b''.join(fileds[end:])


class Logger:
    """
    output: {time} - {prefix} {info}
    """

    def __init__(self, prefix):
        self.prefix = prefix

    def log(self, info):
        print('{} - {} {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.prefix, info))

    @staticmethod
    def err(e):
        print('{} - Error: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))


class Operation:
    """
    Iget - download file from server

    Isend - upload file to server
    """
    Iget = 'Iget'
    Isend = 'Isend'


class Constant:
    """
    some constant value
    """
    Iget = 'Iget'
    Isend = 'Isend'
    CLIENT_PATH = 'test/client/'
    SERVER_PATH = 'test/server/'
    MSS = 1024
    CLIENT_PORT = 11111
    SERVER_PORT = 11112
    WORKER_PORT = 11113
    TIMEOUT = 0.01


class Field:
    RWND = 'rwnd'
    ACK = 'ACK'
    PORT = 'port'
    SEQ = 'seq'
    SEQ_NUM = 'sn'

    FILE_NAME = 'fn'
    OPT = 'opt'

    HEADER_LEN = 200
    CUT = '|!@#$%^&*()'


class CongestionControl:
    SLOW_START = 'slow start'
    AVOID_CONGEST = 'avoid congest'
    QUICK_RECOVER = 'quick recover'

    TRANS = 'tranmits'
    RETRANS = 'retransmits'
    NONE = 'non'
