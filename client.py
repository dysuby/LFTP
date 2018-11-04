import socket
from utils import logger, operation

class Client:
    def __init__(self, host, port):
        self.address = (host, port)

    def handle(self, filename, operation = operation.Iget):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(bytes(filename, 'utf-8'), self.address)
        f = open('receive', 'wb')
        while True:
            data = s.recv(1024)
            f.write(data)
            s.sendto(bytes('ACK', 'utf-8'), self.address)
            if len(data) < 1024:
                break
        f.close()
        s.close()

if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999
    client = Client(HOST, PORT)
    client.handle('test.jpg')