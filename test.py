import filecmp
import threading
import socket
import time

# print(filecmp.cmp('1542033020.1568065.mp4', 'test.mp4', False))
# print(filecmp.cmp('1542033022.6041052.bmp', 'test.bmp', False))
# # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # for i in range(3):
# #     s.sendto(bytes('2e1','utf-8'), ('localhost', 9999))

# def test1():
#     a = threading.Timer(1, test2)
#     a.setDaemon(False)
#     a.start()
#     return 


# def test2():
#     time.sleep(1)
#     print('1')

# threading.Thread(target=test1).start()

f = open('.gitignore')
d = f.read(100000)
print(d)
d = f.read(100000)
d = f.read(100000)

print('11111111', d)
