import socketserver
import threading
from utils import logger, operation


class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    """
    use for mixin
    """
    pass


class ServerHandler(socketserver.BaseRequestHandler):
    """
    handle udp requests
    """

    def setup(self):
        host, port = self.client_address
        self.logger = logger(threading.current_thread().name)
        self.logger.log('Recieve request from {}:{}'.format(host, port))

    def handle(self):
        filename = str(self.request[0].strip(), 'utf-8')
        f = open(filename, 'rb')
        l = f.read(1024)
        socket = self.request[1]
        while l:
            socket.sendto(l, self.client_address)
            l = f.read(1024)
        self.logger.log('Send {} done'.format(filename))


if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999

    server = UDPServer((HOST, PORT), ServerHandler)

    server_thread = threading.Thread(target=server.serve_forever)

    server_thread.start()

    logger('Server: ').log('Listen on {}:{}'.format(HOST, PORT))
