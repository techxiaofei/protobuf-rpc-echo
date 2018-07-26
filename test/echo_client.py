# coding:utf8
import sys
sys.path.append('../')

from proto.game_service_pb2 import IEchoService_Stub,IEchoClient,RequestMessage
from rpc.tcp_client import TcpClient
import asyncore

LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 1888

# 被调用方,接收调用方(stub)的rpc请求
class MyEchoClientReply(IEchoClient):
	def echo_reply(self, rpc_controller, request, done):
		print "MyEchoClientReply:%s"%request.msg
		

if __name__ == "__main__":
	request = RequestMessage()
	request.msg = "just for test"
	
	client = TcpClient(LISTEN_IP, LISTEN_PORT, IEchoService_Stub, MyEchoClientReply)
	client.sync_connect()
	
	client.stub.echo(None, request, None)

	request2 = RequestMessage()
	request2.msg = "just for test2"
	client.stub.echo(None, request2, None)
	asyncore.loop()