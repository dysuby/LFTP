import os
import socket
import threading
import queue
import select
from math import ceil
from utils import Logger, PACK, Constant, CongestionControl as CC, Field


class Window:

    def __init__(self, ws):
        self.q = []
        self.base = 0
        self.next = 0
        self.ws = ws
        self.cwnd = 1
        self.dupack = 0
        self.ssthresh = 64
        self.state = CC.SLOW_START
        self.action = CC.TRANS
        self.logger = Logger('CC Control: ')

    def ack(self, acknum):
        # 拥塞控制
        if self.state == CC.SLOW_START:
            self.slowStart(acknum)
        elif self.state == CC.AVOID_CONGEST:
            self.avoid(acknum)
        else:
            self.quickRecover(acknum)

        # GBN
        if acknum == self.base:
            self.base += 1
            self.q = self.q[1:]
            self.logger.log('Correct ACK {}'.format(acknum))

        self.logger.log('Current state: {} action: {} cwnd: {} ssthresh: {} NonACK: {} NonSend: {}'.format(
            self.state, self.action, self.cwnd, self.ssthresh, self.base, self.next))

    def canSend(self, rwnd):
        return len(self.q) < min([self.cwnd, self.ws, rwnd])

    def push(self, data):
        self.q.append(data)

    def getNonSend(self):
        ret = self.q[self.next - self.base:], self.next
        self.next += len(ret[0])
        return ret

    def getNonACK(self):
        return self.q[:self.next - self.base], self.base

    def slowStart(self, acknum):
        if self.cwnd >= self.ssthresh:
            self.state = CC.AVOID_CONGEST
            self.avoid(acknum)
        elif acknum == self.base:
            self.cwnd += 1
            self.dupack = 0
            self.action = CC.TRANS
        else:
            self.dupack += 1
            self.action = CC.NONE
            if self.dupack == 3:
                self.toQuickR()

    def toQuickR(self):
        self.state = CC.QUICK_RECOVER
        self.action = CC.RETRANS
        self.ssthresh = self.cwnd / 2
        self.cwnd = self.ssthresh + 3

    def avoid(self, acknum):
        if acknum == self.base:
            self.cwnd += (1 / self.cwnd)
            self.dupack = 0
            self.action = CC.TRANS
        else:
            self.dupack += 1
            self.action = CC.NONE
            if self.dupack == 3:
                self.toQuickR()

    def timeout(self):
        self.ssthresh = self.cwnd / 2
        self.cwnd = 1
        self.dupack = 0
        self.state = CC.SLOW_START
        self.action = CC.RETRANS

    def quickRecover(self, acknum):
        if acknum < self.base:
            self.cwnd += 1
            self.action = CC.TRANS
        elif acknum == self.base:
            self.state = CC.AVOID_CONGEST
            self.cwnd = self.ssthresh
            self.dupack = 0
            self.action = CC.NONE


class Sender:

    def __init__(self, addr, port, filename, rwnd):
        try:
            self.statinfo = os.stat(filename)
            self.filename = filename
            f = open(filename, 'rb')
            self.file = f.read()
            f.close()
        except:
            Logger.err('Non-exist file')
            raise
        self.logger = Logger('Sender {}/Receiver {}:{}'.format(port, *addr))
        self.receiver_addr = addr
        self.done = False
        self.rwnd = rwnd
        self.window = Window(100)
        self.port = port
        self.sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sc.bind(('localhost', self.port))

        self.lastSeq = ceil(self.statinfo.st_size / Constant.MSS)
        self.f_seq = 0

    def read(self):
        if self.file:
            ret = self.file[:Constant.MSS]
            self.file = self.file[Constant.MSS:]
            return ret
        else:
            return b''

    def run(self):
        self.logger.log('Begin to work')

        self.window.push(b'')   # 启动报文

        while self.window.canSend(self.rwnd):
            data = self.read()
            if not data:
                self.window.push(b'')
                break
            else:
                self.window.push(data)
                self.f_seq += 1
                self.logger.log('Push SEQ {} into queue'.format(self.f_seq))

        actors = queue.deque([self.sendTo(), self.recvFrom()])
        while actors:
            task = actors.popleft()
            try:
                next(task)
                actors.append(task)
            except StopIteration:
                pass
            except ConnectionResetError:
                actors.clear()
        self.logger.log('Work Done')
        self.sc.close()

    def sendTo(self):
        kw = {Field.PORT: self.port, Field.SEQ_NUM: self.lastSeq}
        while not self.done:
            if self.rwnd == 0:
                self.logger.log(
                    'Waiting client free current SEQ: {}'.format(kw[Field.SEQ]))
                self.sc.sendto(PACK.serialize(b'', kw), self.receiver_addr)
            if self.window.action == CC.NONE:
                self.logger.log('No Action')
            else:
                if self.window.action == CC.TRANS:
                    seqs, seqnum = self.window.getNonSend()
                    self.logger.log(
                        'Transmit {} packets from seqnum: {}'.format(len(seqs), seqnum))
                elif self.window.action == CC.RETRANS:
                    seqs, seqnum = self.window.getNonACK()
                    self.logger.log(
                        'Retransmit {} packets from seqnum: {}'.format(len(seqs), seqnum))
                for data in seqs:
                    self.logger.log('Sending SEQ: {}'.format(seqnum))
                    kw[Field.SEQ] = seqnum
                    data = PACK.serialize(data, kw)
                    self.sc.sendto(data, self.receiver_addr)
                    if seqnum == self.lastSeq:
                        self.logger.log('Last File SEQ: {}'.format(seqnum))
                    seqnum += 1
            yield

    def recvFrom(self):
        while True:
            rl, _, _ = select.select([self.sc], [], [], Constant.TIMEOUT)
            if rl:
                response = self.sc.recv(Constant.MSS)
                kw = PACK.deserialize(response)[0]
                self.rwnd = kw[Field.RWND]
                self.logger.log('receive ACK: {}'.format(kw[Field.ACK]))

                self.window.ack(kw[Field.ACK])
                while self.window.canSend(self.rwnd):
                    data = self.read()
                    if not data:
                        self.logger.log('All file data pushed into queue')
                        self.window.push(b'')
                        break
                    else:
                        self.window.push(data)
                        self.f_seq += 1
                        self.logger.log(
                            'Push SEQ {} into queue'.format(self.f_seq))
                if kw[Field.ACK] == self.lastSeq:
                    self.logger.log('Last seq ACKed')
            else:
                self.logger.log('Timeout')
                self.window.timeout()
            yield
