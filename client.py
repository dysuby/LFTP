import socket
import sys
import time
import select
import threading
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
        sc.bind(('', self.client_port))
        if opt == Operation.Iget:
            kw = {Field.FILE_NAME: Constant.SERVER_PATH +
                  filename, Field.RWND: self.rwnd, Field.OPT: opt}

            self.send(sc, kw)
            data = sc.recv(Constant.MSS + Field.HEADER_LEN)
            kw, _ = PACK.deserialize(data)
            self.server_addr = self.server_addr[0], kw[Field.PORT]
            sc.close()
            worker = Reciever(self.server_addr, self.client_port, Constant.SERVER_PATH + filename,
                              Constant.CLIENT_PATH + str(time.time()), Constant.THROW_RATE)
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
    client1 = Client(int(sys.argv[3]), server_addr)
    a = threading.Thread(target=client1.handle, args=(sys.argv[2], sys.argv[1]))

    client2 = Client(int(sys.argv[3]) + 1, server_addr)
    b = threading.Thread(target=client2.handle, args=(sys.argv[2], sys.argv[1]))

    a.start()
    b.start()
