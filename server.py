import socketserver
import socket
import threading
from utils import logger


class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


class ServerHandler(socketserver.BaseRequestHandler):
  def handle(self):
    pass


if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999

    server = UDPServer((HOST, PORT), ServerHandler)

    server_thread = threading.Thread(target=server.serve_forever)

    server_thread.start()

    logger('Listen on {}:{}'.format(HOST, PORT))
