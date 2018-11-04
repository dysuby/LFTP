class Sender:
    
    def __init__(self, host, port, filename):
        self.address = (host, port)
        self.f = open(filename, 'rb')
        self.filename = filename
        self.done = False

    def send(self, socket):
        data = self.f.read(1024)
        if data:
            socket.sendto(data, self.address)
        else:
            self.f.close()
            self.done = True