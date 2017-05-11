# coding:utf8
import socket
from rpc.tcp_connection import TcpConnection
from rpc.rpc_channel import RpcChannel
import logger


class TcpClient(TcpConnection):

    def __init__(self, ip, port, stub_factory, service_factory):
        TcpConnection.__init__(self, None, (ip, port))
        self.logger = logger.get_logger('TcpClient')
        self.stub_factory = stub_factory
        self.service_factory = service_factory
        self.channel = None
        self.stub = None
        self.service = None

    def close(self):
        self.disconnect()

    def sync_connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.peername)
        except socket.error, msg:
            sock.close()
            self.logger.warning("sync_connect failed %s with remote server %s", msg, self.peername)
            return False

        # after connected, do the nonblocking setting
        sock.setblocking(0)
        self.set_socket(sock)
        self.setsockopt()
        self.handle_connect()
        return True

    def async_connect(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt()
        self.connect(self.peername)

    def handle_connect(self):
        self.logger.info('connection established.')
        self.status = TcpConnection.ST_ESTABLISHED

        #service是被动接收方，stub是主动发送方
        self.service = self.service_factory()
        self.channel = RpcChannel(self.service, self)
        self.stub = self.stub_factory(self.channel)
        self.attach_rpc_channel(self.channel)
        

    def handle_close(self):
        TcpConnection.handle_close(self)

    def writable(self):
        if self.status == TcpConnection.ST_ESTABLISHED:
            return TcpConnection.writable(self)
        else:
            return True
