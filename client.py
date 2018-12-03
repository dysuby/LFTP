import socket
import sys
import time
import select
from utils import Logger, Operation, Constant, PACK, Field
from sender import Sender
from receiver import Reciever


class Client:
    def __init__(self, host, port):
        self.server_addr = (host, port)
        self.client_port = Constant.CLIENT_PORT
        self.rwnd = 20
        self.logger = Logger('Client: ')

    def handle(self, filename, opt=Operation.Iget):
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.bind(('localhost', self.client_port))
        if opt == Operation.Iget:
            kw = {Field.FILE_NAME: Constant.SERVER_PATH +
                filename, Field.RWND: self.rwnd, Field.OPT: opt}
    
            data = PACK.serialize(b'', kw)
            sc.sendto(data, self.server_addr)
            rl, _, _ = select.select([sc], [], [], Constant.TIMEOUT)
            while not rl:
                sc.sendto(data, self.server_addr)
                rl, _, _ = select.select([sc], [], [], Constant.TIMEOUT)

            data = sc.recv(Constant.MSS + Field.HEADER_LEN)
            kw, _ = PACK.deserialize(data)
            self.server_addr = self.server_addr[0], kw[Field.PORT]
            worker = Reciever(self.server_addr, self.client_port, Constant.SERVER_PATH + filename,
                Constant.CLIENT_PATH + '{}.{}'.format(str(time.time()), filename.split('.')[-1]))
        else:
            sc.bind(('localhost', self.client_port))
            kw = {Field.OPT: Constant.Isend,
                  Field.FILE_NAME: filename, Field.OPT: opt}
            data = PACK.serialize(b'', kw)
            sc.sendto(data, self.server_addr)
            rl, _, _ = select.select([sc], [], [], Constant.TIMEOUT)
            while not rl:
                sc.sendto(data, self.server_addr)
                rl, _, _ = select.select([sc], [], [], Constant.TIMEOUT)

            data = sc.recv(Constant.MSS + Field.HEADER_LEN)
            kw, _ = PACK.deserialize(data)
            self.server_addr = self.server_addr[0], kw[Field.PORT]
            worker = Sender(self.server_addr, self.client_port,
                            Constant.CLIENT_PATH + filename, kw[Field.RWND])
        sc.close()
        worker.run()

if __name__ == '__main__':
    HOST, PORT = 'localhost', Constant.SERVER_PORT
    client = Client(HOST, PORT)
    client.handle(sys.argv[2], sys.argv[1])
