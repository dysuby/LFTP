import socketserver
import threading
from utils import logger, operation
from sender import Sender
from receiver import Reciever

pool = {}

class ServerHandler(socketserver.BaseRequestHandler):
    """
    handle udp requests
    """

    def setup(self):
        host, port = self.client_address
        self.logger = logger('client: {}:{}'.format(host, port))

    def handle(self):
        host, port = self.client_address
        if pool.get(self.client_address) == None:
            opt, filename = str(self.request[0].strip(), 'utf-8').split(' ')
            if opt == operation.Iget:
                pool[self.client_address] = Sender(host, port, filename)
            else:
                pool[self.client_address] = Reciever(host, port, filename)

        worker = pool[self.client_address]
        worker.work(self.request[1])
        if worker.done:
            pool.pop(self.client_address)
            self.logger.log('{} {} done'.format(worker.opt, worker.filename))
        else:
            self.logger.log('{}: {} / {} bytes'.format(worker.filename, worker.f.tell(), worker.statinfo.st_size))


if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999

    server = socketserver.UDPServer((HOST, PORT), ServerHandler)

    logger('Server: ').log('Listen on {}:{}'.format(HOST, PORT))
    
    server.serve_forever()
