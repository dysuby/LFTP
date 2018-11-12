from datetime import datetime


class logger:
    """
    example: {time} - {prefix} {info}
    """
    def __init__(self, prefix):
        self.prefix = prefix
    
    def log(self, info):
        print('{} - {} {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.prefix, info))

class operation:
    """
    Iget - download file from server

    Isend - upload file to server
    """
    Iget = 'Iget'
    Isend = 'Isend'
