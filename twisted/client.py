#!/usr/bin/env python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
# encoding: utf-8
from __future__ import print_function

from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
import logging
import time

class EchoClient(LineReceiver):
	end = b"Bye-bye!"

	def connectionMade(self):
		self.t1=time.time()
		print(self.t1)
		#print(time.time().strftime("%Y-%m-%d %H:%M:%S", time.time()))
		data = [0x39, 0x00, 0x00, 0x00, 0x56, 0x31, 0x2e, 0x31,0x2e, 0x31, 0x06, 0x01, 0x01, 0x00, 0x00, 0x00,0x11, 0x02, 0x38,\
 				0x36, 0x31, 0x34, 0x37, 0x37,0x30, 0x33, 0x33, 0x38, 0x38, 0x39, 0x30, 0x39,\
 				0x36, 0x03, 0x03, 0x00, 0x08, 0x04, 0x34, 0x36,0x30, 0x30, 0x31, 0x20, 0x03, 0x08, 0x01, 0x0a,0x0a, 0x24, 0x18, 0x15,\
  				0x20, 0xa1, 0x00, 0xbb, 0xff]
 		# 4G data
 		#data = b"9\x00\x00\x00V1.1.1\x06\x01\x01\x00\x00\x00\x11\x02861477033889096\x03\x03\x00\x08\x0446001 \x03\x08\x01\n\n$\x18\x15 \xa1\x00\xbb\xff"
# #     # data test
#		data = b'GET / HTTP/1.1\r\nHost: 54.223.57.33\r\nX-Request-ID: 3c0f775008df989124412f7ab5f72839\r\nX-Real-IP: 10.233.1.129\r\nX-Forwarded-For: 10.233.1.129\r\nX-Forwarded-Host: 54.223.57.33\r\nX-Forwarded-Port: 80\r\nX-Forwarded-Proto: http\r\nX-Scheme: http\r\nUser-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Mobile/14D27 MicroMessenger/6.5.5 NetType/WIFI Language/en\r\nAccept: */*\r\nAccept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4\r\n\r\n'
		# 2g data
		#data = b"G\x00\x00\x00V1.1.1\x06\x01\x03\x00\x00\x00\x11\x02357713009999993\x03\x03\x00\x08\x0446000\x00\x03\x08\x05\x08\x05<3)\xe3\xd3\xff\x08\x05<3'\xe3\xbc\xff\x08\x05<3(\xe3\xb2\xff"
		# cdma data
		#data = b"9\x00\x00\x00V1.1.1\x06\x01\x01\x00\x00\x00\x11\x02868821042641050\x03\x03\x01\x08\x0446003 \x03\x08\x01\n\x0b\x146\x02\x00\x049\x00\x00"
		#data = b"M\x00\x00\x00V1.1.1\x06\x01\x0b\x00\x00\x00\x11\x02868821042641050\x03\x03\x00\x08\x0446001 \x03\x08\x01\n\n+%\xc8\xeb\x00\x00\xad\xff\n\n+%\xec\xc8\x00\x00\xa9\xff\n\n+%\x81\xc9\x00\x00\xa7\xff"

		#data = b"9\x00\x00\x00V1.1.1\x06\x01\t\x00\x00\x00\x11\x02868821042641050\x03\x03\x00\x08\x0446011 \x03\t\x01\n\n\x0ew3u\n\r\x9f\xff"

		data = [0x47, 0x00, 0x00, 0x00, 0x56, 0x31, 0x2e, 0x31, 0x2e, 0x31, 0x06, 0x01, 0x17, 0x00, 0x00, 0x00, 0x11, 0x02, 0x33, 0x35,\
		 0x37, 0x37, 0x31, 0x33, 0x30, 0x30, 0x39, 0x39, 0x39, 0x39, 0x39, 0x39, 0x33, 0x03, 0x03, 0x00, 0x08, 0x04, 0x34, 0x36, 0x30, \
		 0x30, 0x30, 0x00, 0x03, 0x08, 0x05, 0x08, 0x05, 0x16, 0x18, 0x33, 0x55, 0xca, 0xff, 0x08, 0x05, 0x16, 0x18, 0x35, 0x55, 0xc0, \
		 0xff, 0x08, 0x05, 0x16, 0x18, 0x0c, 0x55, 0xbc, 0xff]
		#data = b'9\x00\x00\x00V1.1.1\x06\x01\x02\x00\x00\x00\x11\x02861742352641050\x03\x03\x01\x08\x0446003 \x03\x08\x03\n\x0b\x146\x02\x00`x\x00\x00'
		# data = b'/\x00\x00\x00V1.1.1\x06\x01\x03\x00\x00\x00\x11\x02865831622641050\x03\x03\x00\x08\x0446001 \x03\x08\x08'
		data= b'9\x00\x00\x00V1.1.1\x06\x01\x04\x00\x00\x00\x11\x02865368762641033\x03\x03\x00\x08\x0446000 \x03\x08\x05\n\n8&\x82r\xbb\x0c\xa0\xff'
		self.sendLine(bytes(data))
		#print(time.strftime("%Y-%m-%d %H:%M:%S", time.time()))
#		self.sendLine(b'\n\r')
 #       self.sendLine(b"What a fine day it is.")
 #       self.sendLine(self.end)


	def lineReceived(self, line):
		print("some received")
		print(line, len(line))
		for d in line:
			print(hex(d), end=' ')
		print("received ends")
		self.t2 =time.time()
		print(self.t2)
		print(self.t2 - self.t1)
 #       datas = line.decode('utf_16_be')

 #       print("receive:", datas, type(datas))
		#if line == self.end:
		self.transport.loseConnection()



class EchoClientFactory(ClientFactory):
	protocol = EchoClient

	def __init__(self):
		self.done = Deferred()


	def clientConnectionFailed(self, connector, reason):
		print('connection failed:', reason.getErrorMessage())
		self.done.errback(reason)


	def clientConnectionLost(self, connector, reason):
		print('connection lost:', reason.getErrorMessage())
		self.done.callback(None)



def main(reactor):
	factory = EchoClientFactory()
	reactor.connectTCP('54.223.57.33', 8000, factory)
	# reactor.connectTCP('52.82.61.185', 8000, factory)
	#reactor.connectTCP('localhost', 80, factory)
	return factory.done



if __name__ == '__main__':
	task.react(main)
