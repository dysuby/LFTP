import socketserver
import threading
from utils import logger, operation
from sender import Sender
from receiver import Reciever

senders = {}
receivers = {}

sender_lock = threading.Lock()
receiver_lock = threading.Lock()

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
        self.logger = logger('client: {}:{}'.format(host, port))
        self.logger.log('Recieve request from {}:{}'.format(host, port))

    def handle(self):
        host, port = self.client_address
        if senders.get(self.client_address) == None:
            filename = str(self.request[0].strip(), 'utf-8')
            sender_lock.acquire()
            senders[self.client_address] = Sender(host, port, filename)
            sender_lock.release()

        sender = senders[self.client_address]
        sender.send(self.request[1])
        if sender.done:
            self.logger.log('Send {} done'.format(sender.filename))


if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999

    server = UDPServer((HOST, PORT), ServerHandler)

    server_thread = threading.Thread(target=server.serve_forever)

    server_thread.start()

    logger('Server: ').log('Listen on {}:{}'.format(HOST, PORT))
