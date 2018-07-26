# coding:utf8
from google.protobuf import service
from rpc.rpc_controller import RpcController
import struct
import logger


class RpcChannel(service.RpcChannel):
	def __init__(self, rpc_service, conn):
		super(RpcChannel, self).__init__()
		self.logger = logger.get_logger("RpcChannel")
		self.rpc_service = rpc_service
		self.conn = conn
		
		self.rpc_controller = RpcController(self)
		print "RpcChannel init"
	
	def set_rpc_service(self, rpc_service):
		self.rpc_service = rpc_service
	
	def CallMethod(self, method_descriptor, rpc_controller,
                 request, response_class, done):
		print "RpcChannel CallMethod"
		index = method_descriptor.index
		data = request.SerializeToString()
		total_len = len(data) + 6
		self.logger.debug("CallMethod:%d,%d"%(total_len,index))
		
		self.conn.send_data(''.join([struct.pack('!ih', total_len, index), data]))
		
	def input_data(self, data):
		total_len, index = struct.unpack('!ih', data[0:6])
		self.logger.debug("input_data:%d,%d" % (total_len, index))
		rpc_service = self.rpc_service
		s_descriptor = rpc_service.GetDescriptor()
		method = s_descriptor.methods[index]
		try:
			request = rpc_service.GetRequestClass(method)()
			serialized = data[6:total_len]
			request.ParseFromString(serialized)
			
			rpc_service.CallMethod(method, self.rpc_controller, request, None)
			
		except Exception, e:
			self.logger.error("Call rpc method failed!")
			print "error:",e
			self.logger.log_last_except()
		
		if (len(data) > total_len):
			data = data[total_len:]
			self.input_data(data)
		return True
		
		