# coding:utf8
import socket
import asyncore
import logger


class TcpConnection(asyncore.dispatcher):

    DEFAULT_RECV_BUFFER = 4096
    ST_INIT = 0
    ST_ESTABLISHED = 1
    ST_DISCONNECTED = 2

    def __init__(self, sock, peername):
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logger.get_logger('TcpConnection')
        self.peername = peername

        self.writebuff = ''
        self.recv_buff_size = TcpConnection.DEFAULT_RECV_BUFFER

        self.status = TcpConnection.ST_INIT
        if sock:
            self.status = TcpConnection.ST_ESTABLISHED
            self.setsockopt()

        self.rpc_channel = None

    def setsockopt(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def get_rpc_channel(self):
        return self.rpc_channel

    def attach_rpc_channel(self, channel_interface):
        self.rpc_channel = channel_interface

    def is_established(self):
        return self.status == TcpConnection.ST_ESTABLISHED

    def set_recv_buffer(self, size):
        self.recv_buff_size = size

    def disconnect(self):
        if self.status == TcpConnection.ST_DISCONNECTED:
            return

        if self.rpc_channel:
            self.rpc_channel.on_disconnected()
        self.rpc_channel = None

        if self.socket:
            asyncore.dispatcher.close(self)

        self.status = TcpConnection.ST_DISCONNECTED

    def getpeername(self):
        return self.peername

    def handle_close(self):
        self.logger.debug('handle_close')
        asyncore.dispatcher.handle_close(self)
        self.disconnect()

    def handle_expt(self):
        self.logger.debug('handle_expt')
        asyncore.dispatcher.handle_expt(self)
        self.disconnect()

    def handle_error(self):
        self.logger.debug('handle_error')
        asyncore.dispatcher.handle_error(self)
        self.disconnect()

    def handle_read(self):
        self.logger.debug('handle_read')
        data = self.recv(self.recv_buff_size)
        if data:
            if not self.rpc_channel:
                self.logger.debug("not rpc_channel")
                return
            self.rpc_channel.input_data(data)

    def handle_write(self):
        self.logger.debug('handle_write')
        if self.writebuff:
            size = self.send(self.writebuff)
            self.writebuff = self.writebuff[size:]

    def writable(self):
        return len(self.writebuff) > 0

    def send_data(self, data):
        self.writebuff += data