import threading
import time
import socket
import select
from utils import Operation, Constant, Logger, PACK, Field
from sender import Sender
from receiver import Reciever

client_table = {}


class Server:
    """
    handle udp requests
    """

    def __init__(self, host, port):
        self.addr = (host, port)
        self.logger = Logger('Server ')

    def serve(self):
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.bind(self.addr)
        while True:
            rl, _, _ = select.select([sc], [], [])
            data, client_addr = sc.recvfrom(Constant.MSS + Field.HEADER_LEN)

            if client_table.get(client_addr) == None or not client_table.get(client_addr).is_alive():
                kwargs = PACK.deserialize(data)[0]
                if kwargs[Field.OPT] == Operation.Iget:
                    self.logger.log('Receive {} request from {}'.format(
                        Operation.Iget, client_addr))
                    worker = Sender(client_addr, Constant.WORKER_PORT,
                                    kwargs[Field.FILE_NAME], kwargs[Field.RWND])
                elif kwargs[Field.OPT] == Operation.Isend:
                    self.logger.log('Receive {} request from {}'.format(
                        Operation.Isend, client_addr))
                    worker = Reciever(client_addr, Constant.WORKER_PORT, Constant.CLIENT_PATH +
                                      kwargs[Field.FILE_NAME], Constant.SERVER_PATH + str(time.time()), Constant.THROW_RATE)
                else:
                    raise ValueError
                son = threading.Thread(target=worker.run)
                son.start()
                Constant.WORKER_PORT += 1
                client_table[client_addr] = son


if __name__ == '__main__':
    HOST, PORT = '', Constant.SERVER_PORT

    Logger('Server: ').log('Listen on {}:{}'.format(HOST, PORT))

    Server(HOST, PORT).serve()
