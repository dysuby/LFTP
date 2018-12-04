# LFTP

> Required: Python 3.6^



## 使用

服务端：`py server.py`，默认端口为 `11112`

客户端：`py client.py <opt> <filename> <port>`，`opt` 为 `Isend` 或 `Iget`，`filename` 为相对路径，表示要传输或接受的文件名（`test/server` 相对路径），`port` 为客户端的端口，运行时如果服务器不在本地需要更改文件内的配置



## 文件结构

- `test` 存放文件，`server` 为服务器**读写**文件的路径，`client` 同理
- `test.py` 为测试文件，用于判断两个文件是否一致，用法：`py test.py <server_file> <client_file>`
- `utils.py` 为一些工具函数和参数
- `sender.py`/`receiver.py` 为`worker` 类。



## 自定义参数

可在 `utils` 的 `Constant` 类修改。

```python
# 参数说明
CLIENT_PATH = 'test/client/'	# 客户端读写文件的文件夹
SERVER_PATH = 'test/server/'    # 服务端读写文件的文件夹
MSS = 1024						# 一次读文件的大小
SERVER_PORT = 11112				# 服务端主端口
WORKER_PORT = 11113				# worker 初始端口
TIMEOUT = 0.1					# 超时间隔
HANDLE_PRO = 0.5				# 接收方处理数据的概率
THROW_RATE = 0					# 接收方丢包率
```

