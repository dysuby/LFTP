import socket
import sys
import time
import select
from utils import Logger, Operation, Constant, PACK, Field
from sender import Sender
from receiver import Reciever


class Client:
    def __init__(self, client_port, server_addr):
        self.server_addr = server_addr
        self.client_port = client_port
        self.rwnd = 20
        self.logger = Logger('Client: ')

    def handle(self, filename, opt=Operation.Iget):
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.bind(('localhost', self.client_port))
        if opt == Operation.Iget:
            kw = {Field.FILE_NAME: Constant.SERVER_PATH +
                  filename, Field.RWND: self.rwnd, Field.OPT: opt}

            self.send(sc, kw)
            data = sc.recv(Constant.MSS + Field.HEADER_LEN)
            kw, _ = PACK.deserialize(data)
            self.server_addr = self.server_addr[0], kw[Field.PORT]
            sc.close()
            worker = Reciever(self.server_addr, self.client_port, Constant.SERVER_PATH + filename,
                              Constant.CLIENT_PATH + str(time.time()), 0.5)
        else:
            kw = {Field.OPT: opt, Field.FILE_NAME: filename, Field.OPT: opt}

            self.send(sc, kw)
            data = sc.recv(Constant.MSS + Field.HEADER_LEN)
            kw, _ = PACK.deserialize(data)
            self.server_addr = self.server_addr[0], kw[Field.PORT]
            sc.close()
            worker = Sender(self.server_addr, self.client_port,
                            Constant.CLIENT_PATH + filename, kw[Field.RWND])
        worker.run()

    def send(self, sc, kw):
        data = PACK.serialize(b'', kw)
        sc.sendto(data, self.server_addr)
        rl, _, _ = select.select([sc], [], [], Constant.TIMEOUT)
        while not rl:
            sc.sendto(data, self.server_addr)
            rl, _, _ = select.select([sc], [], [], Constant.TIMEOUT)


if __name__ == '__main__':
    server_addr = 'localhost', Constant.SERVER_PORT
    client = Client(int(sys.argv[3]), server_addr)
    client.handle(sys.argv[2], sys.argv[1])
