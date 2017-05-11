# coding:utf8
import socket
import asyncore

from rpc.tcp_connection import TcpConnection
from rpc.rpc_channel import RpcChannel
import logger


class TcpServer(asyncore.dispatcher):
    '''负责accept链接，并建立一条TcpConnection通道'''
    def __init__(self, ip, port, service_factory):
        asyncore.dispatcher.__init__(self)
        self.logger = logger.get_logger('TcpServer')
        self.ip = ip
        self.port = port
        self.service_factory = service_factory

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.ip, self.port))
        self.listen(50)
        self.logger.info('Server Listening on: ' + str((self.ip, self.port)))

    def handle_accept(self):
        try:
            sock, addr = self.accept()
        except socket.error, e:
            self.logger.warning('accept error: ' + e.message)
            return
        except TypeError, e:
            self.logger.warning('accept error: ' + e.message)
            return

        self.logger.info('accept client from ' + str(addr))
        conn = TcpConnection(sock, addr)
        self.handle_new_connection(conn)

    def stop(self):
        self.close()

    def handle_new_connection(self, conn):
        self.logger.info('handle_new_connection')
        service = self.service_factory()
        rpc_channel = RpcChannel(service, conn)  # TODO, 多个connection的RpcChannel保存
        conn.attach_rpc_channel(rpc_channel)
