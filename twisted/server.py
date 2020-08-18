#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import requests
from requests.adapters import HTTPAdapter
from enum import Enum
import json
import time
import configparser
import logging
import inspect
import argparse
import os
import numpy
from logger import logger
import random


# logging.basicConfig(filename='app.log',level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s',datefmt='%Y-%m-%d')
# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s',datefmt='%Y-%m-%d')

#from memcache import memcache
from memlocal import memcache



#LBSDataType =Enum("Data", ("sequenceId", 'ismi', ))
class ReqLbsDataType(Enum):
	sequenceId = 1
	imsi = 2
	netType = 3
	mccAndMnc = 4
	cellInfo = 5
	customerId = 6
	fwVersion = 7
	reqPostionType = 8
	servControl = 9
	extCellInfo = 10
	cdmaCellInfo = 11
	imei = 12
	servRespCode = 0x80
	logLat = 0x81
	positonAccuracy = 0x82
	positionAdr = 0x83
	servTime = 0x84

class ReqLabInfo(Enum):
	OK = 0
	Para_Error = 1
	Service_Expired = 2
	Position_Error = 3
	Position_Timeout = 4
	Auth_Fail  = 5
	Report_Errorbts_Success = 6
	Report_Errorbts_Fail  = 7
	Over_quota  = 8
	Unknow_Error = 99

class ReqLabRespInfo(Enum):
	OK = 'OK'
	INVALID_USER_KEY = 'INVALID_USER_KEY'
	SERVICE_NOT_EXIST = 'SERVICE_NOT_EXIST'
	SERVICE_RESPONSE_ERROR ='SERVICE_RESPONSE_ERROR'
	INSUFFICIENT_PRIVILEGES = 'INSUFFICIENT_PRIVILEGES'
	OVER_QUOTA = 'OVER_QUOTA'
	INVALID_PARAMS = 'INVALID_PARAMS'
	UNKNOWN_ERROR = 'UNKNOWN_ERROR'

# This is just about the simplest possible protocol
class LbsRequest(Protocol):

	# accesstype = 0
	# imei = ''
	# smac =''
	# cdma = 0
	# bts = ''
	# nearbts =''
	# serverip =''
	# output='json'
	# key = ''
	def __init__(self):
		self.datalength = 0
		self.fwVersion = ''
		self.sequeneNum = 0                      # set default value to  0 to make start if not sequence value received from module
		self.imsi = ''
		self.netType = 0                         # set default value to 0 means GSM/UMTS/LTE,  1 present to CDMA
		self.mccAndMnc = ''
		self.mcc = ''
		self.mnc = ''
		self.bts = []                            # bts is an array with 3 type of represent
		self.btslac=0
		self.btscellid=0
		self.btsdbm=0
		self.btsStr= ''
		self.customerId = ''
		self.fwVerion = ''
		self.reqPostionType = 1                  # set default value to 1  to request long lat value from amap
		self.servControl = 1                     # set default value to 1 request base station error
		self.imei = ''
		self.smac = ''
		self.cdma = 0
		self.nearbts = ''
		self.nearbtslac = 0
		self.nearbtscellid = 0
		self.nearbtsdbm = 0
		self.cdmabtssid = 0
		self.cdmabtsnid = 0
		self.cdmabtsbid = 0
		self.cdmabtsdbm = 0
		self.serverip = ''
		self.output = 'json'
		self.key = ''
		self.accesstype = 0                       # here always for zero because there are no wifi position
		self.servrespcode = 0                     # default value to z as success
		self.location = ''
		self.longitude = 0
		self.latitude = 0
		self.address = ''
		self.positionResult = 0
		self.positonaccuracy = 0
		self.servertime = 0
		self.writeDatatoModule =[]
		self.amapresponseCode = 10000
		self.positionTime = time.time() * 1000
		self.country = ''
		self.postCode = 0
		self.cityCode = 0
		self.city = ''
		self.data0x80 = []
		self.data0x81 = []
		self.data0x82 = []
		self.data0x83 = []
		self.data0x84 = []
		self.collectData = []
		self.seqData = []
		self.memcachedStr = ''

		self.memcached = memcache()
	def validData(self, data):
		if len(data) > data[0] + 2  or len(data) < data[0] or len(data) < 10:
			return False
		else:
			return True
			
	def dataReceived(self, data):
		self.startTime = time.time()
		logger.info("data received ：" + str(data))
		# for d in data:
		# 	print(hex(d), end=' ')
		# print(' ')
		if self.validData(data) == True:
			self.datalength = data[0]
			self.fwVersion = ''.join(chr(data[i]) for i in [4, 5, 6, 7, 8, 9])
			curindex = 10
			curDataLen = data[curindex]
			datatype = data[curindex +1]
			nextIndex = curDataLen + curindex
			logger.info("current index:  %d , next index :%d"%(curindex, nextIndex))
			while nextIndex < self.datalength:
	#			logger.debug("current :", curindex, nextIndex, self.datalength)
				LbsRequest.parserData(self, data[curindex:nextIndex])
	#            if curindex + data[curindex+1] < self.datalength:
				curindex = nextIndex
	#			logger.debug("next data length :", curindex, data[curindex])
				nextIndex = curindex + data[curindex]
			# logger.debug(self.datalength, self.version, self.sequeneNum, self.imsi, self.netType, self.mccAndMnc, self.nearbtsdbm,
			#       self.nearbtscellid, self.nearbtslac, self.imei, self.reqPostionType)
			LbsRequest.parserData(self, data[curindex:nextIndex])
			cachedData = None
			cachedData = self.memcached.get(self.imei)
			logger.info("cachedData : %s"%cachedData)
			print(type(cachedData))
			if cachedData == None or cachedData == False: 
				if self.btsStr !='':
					LbsRequest.amapRequest(self, data)
					self.writeDatatoModule = LbsRequest.assembledata(self, data, cachedData)
					# serial the data to string  and save into memcached
					if self.longitude != 0 and self.latitude !=0:
						LbsRequest.serialLBSdata(self)
						t1=time.time()
						self.memcached.set(self.imei, self.memcachedStr)
						t2=time.time()
						logger.info("memcache_elapseed: %f"%(t2-t1))
				else:
					self.writeDatatoModule = LbsRequest.assembledata(self, data, cachedData)
				#self.memcached.get(self.imei)
			else:
				#cachedData = json.loads(cachedData)
				logger.debug(cachedData['imei'])
				self.writeDatatoModule = LbsRequest.assembledata(self, data, cachedData)

			logger.info("message send :"+str(self.writeDatatoModule))
			self.transport.write(bytes(self.writeDatatoModule)+ b'\r\n')
			#self.transport.write(bytes(self.writeDatatoModule))
		else:
			logger.info("Echo back :"+str(data))
			self.transport.write(bytes(data))
		self.endTime = time.time()
		logger.info('message sent with elapseed: %f'%(self.endTime - self.startTime))

	def assemble0x80data(self):
		tempdata = [0x03, 0x80]
		logger.info("Assemble 0x80 data")
		# if self.positionState == ReqLabRespInfo.OK.value:
		# 	tempdata.append(0x0)
		# elif self.positionState == ReqLabRespInfo.INVALID_USER_KEY.value:
		# 	tempdata.append(0x01)
		# elif self.positionState == ReqLabRespInfo.SERVICE_NOT_EXIST.value:
		# 	tempdata.append(0x03)
		# elif self.positionState == ReqLabRespInfo.SERVICE_RESPONSE_ERROR.value:
		# 	tempdata.append(0x03)
		# elif self.positionState == ReqLabRespInfo.INSUFFICIENT_PRIVILEGES.value:
		# 	tempdata.append(0x03)
		# elif self.positionState == ReqLabRespInfo.OVER_QUOTA.value:
		# 	tempdata.append(0x08)
		# elif self.positionState == ReqLabRespInfo.INVALID_PARAMS.value:
		# 	tempdata.append(0x03)
		# elif self.positionState == ReqLabRespInfo.UNKNOWN_ERROR.value:
		# 	tempdata.append(99)
		# else:
		# 	tempdata.append(0x0)
		tempdata.append(self.positionResult)
		# for d in tempdata:
		# 	print(hex(d), end=' ')
		# print("0x80 ends", len(tempdata))
		self.data0x80 = tempdata
		logger.info("Assemble 0x80 data :" + str(tempdata))
		return tempdata
	def assemble0x81data(self):

		logger.info("Assemble 0x81 longlac data")

		tempdata = [0x0a, 0x81]
		long_val = int(float(self.longitude) * 1000000)
		tempdata.append(long_val & 0xff)
		tempdata.append((long_val >> 8) & 0xff)
		tempdata.append((long_val >> 16) & 0xff)
		tempdata.append((long_val >> 24) & 0xff)

		lac_value = int(float(self.latitude) * 1000000)
		tempdata.append(lac_value & 0xff)
		tempdata.append((lac_value >> 8) & 0xff)
		tempdata.append((lac_value >> 16) & 0xff)
		tempdata.append((lac_value >> 24) & 0xff)

		logger.info("Assemble 0x81 data :" + str(tempdata))
		# for d in tempdata:
		# 	print(hex(d), end=' ')
		# print("0x81 end", len(tempdata))
		self.data0x81 = tempdata
		return tempdata

	def assemble0x82data(self):
		tempdata = [0x04, 0x82]
		accuracy_val = int(self.positonaccuracy)
		tempdata.append(accuracy_val & 0xff)
		tempdata.append((accuracy_val >> 8) & 0xff)
		# tempdata.extend(hex(int(self.positonaccuracy)).encode('utf_16_be'))
		# for d in tempdata:
		# 	print(hex(d), end=' ')
		# print("0x82 end")
		self.data0x82 = tempdata
		logger.info("Assemble 0x82 accuracy data :" + str(tempdata))
		return tempdata

	def assemble0x83data(self):
		addr = self.address.encode('utf_16_be')
		tempdata = [len(addr) + 2, 0x83]
		tempdata.extend(addr)
#		logger.debug(len(tempdata), type(tempdata))
		# for d in tempdata:
		# 	print(hex(d), end=' ')
		# print("0x83 end", len(tempdata))
		self.data0x83 = tempdata
		logger.info("Assemble 0x83 address data :" + str(tempdata))
		return tempdata

	def assemble0x84data(self):
		tempdata = [0x0a, 0x84]
		# curtime = str(int(time.time() * 1000)).encode("utf_16_be")
		# tempdata.extend(curtime)
		#curtime_val = int(time.time() * 1000)
		curtime_val = int(self.positionTime)
		logger.debug(curtime_val)
		tempdata.append(curtime_val & 0xff)
		tempdata.append(curtime_val >> 8 & 0xff)
		tempdata.append(curtime_val >> 16 & 0xff)
		tempdata.append(curtime_val >> 24 & 0xff)
		tempdata.append(curtime_val >> 32 & 0xff)
		tempdata.append(curtime_val >> 40 & 0xff)
		tempdata.append(0)
		tempdata.append(0)
		# for d in tempdata:
		# 	print(hex(d), end=' ')
		# print("0x84 end", len(tempdata))
		self.data0x84 = tempdata
		return tempdata

	def assembleSeqdata(self):
		tempdata =[0x06, 0x01]
		tempdata.append(self.sequeneNum & 0xff)
		tempdata.append(self.sequeneNum >> 8 & 0xff)
		tempdata.append(self.sequeneNum >> 16 & 0xff)
		tempdata.append(self.sequeneNum >> 24 & 0xff)
		self.seqData = tempdata.copy()
		logger.info("Assemble sequence data :" + str(tempdata))
		return tempdata

	def collectLenghtAndVerion(self, data):
		tempdata = []
		tempdata.extend(data[0:10])
		# for d in tempdata:
		# 	print(hex(d), end=' ')
		# print("collect data ends", len(tempdata))
		self.collectData = tempdata.copy()
		logger.info("Collect Length and version data :" + str(tempdata))
		return tempdata

	def serialLBSdata(self):

		self.memcachedStr = json.dumps ({
			'imei': self.imei,
			# 'bts': self.bts,                 # remove bts because sometime the json serial fails
			'net_type': self.netType,
			'mcc' : self.mcc,
			'mnc' : self.mnc,
			'req_position_type': self.reqPostionType,
			'cdma': self.cdma,
			'bts_lac' : self.nearbtslac,
			'bts_cell_id': self.nearbtscellid,
			'bts_dbm' : self.nearbtsdbm,
			'near_bts_lac': self.nearbtslac,
			'near_bts_cell_id': self.nearbtscellid,
			'near_bts_dbm': self.nearbtsdbm,
			'customer_id': self.customerId,
			'fw_version': self.fwVerion,
			'serv_control': self.servControl,
			'cdma_bts_sid': self.cdmabtssid,
			'cdma_bts_nid': self.cdmabtsnid,
			'cdma_bts_bid': self.cdmabtsbid,
			'cdma_bts_dbm': self.cdmabtsdbm,
			'server_resp_code': self.servrespcode,
			'longitude': self.longitude,
			'latitude': self.latitude,
			'positon_accuracy': self.positonaccuracy,
			'address': self.address,
			'country': self.country,
			'city': self.city,
			'city_code': self.cityCode,
			'post_code': self.postCode,
			'position_state': self.positionState,
			'position_time': self.positionTime,
			'data0x80': self.data0x80,
			'data0x81': self.data0x81,
			'data0x82': self.data0x82,
			'data0x83': self.data0x83,
			'data0x84': self.data0x84
		# }, ensure_ascii=False)
		})
		# for k in memcachedStr:
		# 	logger.info("k: %s, v: %s, type: %s"%(k,memcachedStr[k],type(memcachedStr[k])))
		# self.memcachedStr = json.dumps(memcachedStr)
		logger.debug(self.memcachedStr)

	@staticmethod
	def parserData(self, sliceData):
		logger.info("paser " +str(sliceData)+" data into field with type %d"%sliceData[1])
		# for d in sliceData:
		# 	print(hex(d), end=' ')
		# print('parser slice print end')
		if sliceData[1] == ReqLbsDataType.sequenceId.value:
			self.sequeneNum = int(sliceData[2] | sliceData[3] << 8 | sliceData[4] << 16 | sliceData[5] << 24)
		#	logger.debug("self.sequeneNum : ", self.sequeneNum)
		elif sliceData[1] == ReqLbsDataType.imsi.value or sliceData[1] == ReqLbsDataType.imei.value:
			self.imei = ''.join(chr(sliceData[i]) for i in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
			self.imsi = self.imei
		#	logger.debug("self.imei : ", self.imei)
		elif sliceData[1] == ReqLbsDataType.netType.value:
			self.netType = sliceData[2]
			logger.info("self.netType : %d"%self.netType)
		elif sliceData[1] == ReqLbsDataType.mccAndMnc.value:
		#   self.mccAndMnc = ''.join(chr(sliceData[i]) for i in [2, 3, 4, 5, 6, 7])
			self.mcc = ''.join(chr(sliceData[i]) for i in [2, 3, 4])
			self.mnc = ''.join(chr(sliceData[i]) for i in [5, 6, 7])
			self.mccAndMnc = self.mcc + "," + self.mnc
			logger.info("self.mccAndMnc : %s"%self.mccAndMnc)
		elif sliceData[1] == ReqLbsDataType.cellInfo.value:
			self.btslac = sliceData[2] | sliceData[3] << 8
			self.btscellid = sliceData[4] | sliceData[5] << 8
			self.btsdbm = numpy.short(sliceData[6] | sliceData[7] << 8)
			self.bts = [self.btslac, self.btscellid ,self.btsdbm]
			if self.btsStr == '':
				self.btsStr = self.mccAndMnc + ',' + str(self.btslac)+',' + str(self.btscellid) + ',' + str(self.btsdbm)
			else:
				self.btsStr = self.btsStr + "|" + self.mccAndMnc + ',' + str(self.btslac)+',' + str(self.btscellid) + ',' + str(self.btsdbm)
			logger.info("self.btsStr : %s"%(self.btsStr))
		# elif sliceData[1] == ReqLbsDataType.customerId.value:
		#     self.customerId =
		elif sliceData[1] == ReqLbsDataType.reqPostionType.value:
			self.reqPostionType = sliceData[2]
		#	logger.debug("self.reqPostionType : ", self.reqPostionType)
		elif sliceData[1] == ReqLbsDataType.servControl.value:
			self.servControl = sliceData[2]
		#	logger.debug("self.servControl : ", self.servControl)
		elif sliceData[1] == ReqLbsDataType.extCellInfo.value:
			self.btslac = sliceData[2] | sliceData[3] << 8
			self.btscellid = int(sliceData[4] | sliceData[5] << 8 |sliceData[6]  << 16 | sliceData[7] << 24 )
			self.btsdbm = numpy.short(sliceData[8] | sliceData[9] << 8)

			if self.btsStr == '':
				self.btsStr = self.mccAndMnc + ',' + str(self.btslac)+',' + str(self.btscellid) + ',' + str(self.btsdbm)
			else:
				self.btsStr = self.btsStr + "|" +self.mccAndMnc + ',' + str(self.btslac)+',' + str(self.btscellid) + ',' + str(self.btsdbm)
			logger.info("self.btsStr : %s"%(self.btsStr))
		#	logger.debug("self.nearbtslac : ", self.nearbtslac)
		#	logger.debug("self.nearbtscellid : ", self.nearbtscellid)
		#	logger.debug("self.nearbtsdbm : ", self.nearbtsdbm)
		elif sliceData[1] == ReqLbsDataType.cdmaCellInfo.value:
			self.cdmabtssid = sliceData[2] | sliceData[3] << 8
			self.cdmabtsnid = sliceData[4] | sliceData[5] << 8
			self.cdmabtsbid = sliceData[6] | sliceData[7] << 8
			self.cdmabtsdbm = sliceData[8] | sliceData[9] << 8
			logger.info("cdmabtssid: %d, cdmabtsnid :%d,  cdmabtsbid: %d,  cdmabtsdbm: %d"%(self.cdmabtssid,self.cdmabtsnid,self.cdmabtsbid,self.cdmabtsdbm))
		#	logger.debug("self.cdmabtssid : ", self.cdmabtssid)
		#	logger.debug("self.cdmabtsnid : ", self.cdmabtsnid)
		#	logger.debug("self.cdmabtsbid : ", self.cdmabtsbid)
		#	logger.debug("self.cdmabtsdbm : ", self.cdmabtsdbm)
		# elif sliceData[1] == ReqLbsDataType.servRespCode.value:
		#     self.servrespcode = sliceData[2]
		#     logger.debug("self.servrespcode : ", self.servrespcode)
		# elif sliceData[1] == ReqLbsDataType.logLat.value:
		#     self.longitude = sliceData[2] | sliceData[3] << 8 | sliceData[4] << 16 | sliceData[5] << 24
		#     self.latitude =  sliceData[6] | sliceData[7] << 8 | sliceData[8] << 16 | sliceData[9] << 24
		#     logger.debug("self.servrespcode : ", self.servrespcode)
		# elif sliceData[1] == ReqLbsDataType.positonAccuracy.value:
		#     self.positonaccuracy = sliceData[2] | sliceData[3] << 8
		# elif sliceData[1] == ReqLbsDataType.positionAdr.value:
		# elif sliceData[1] == ReqLbsDataType.servTime.value:
		else:
			logger.debug("paser data type not supprt %d"%(sliceData[1]) )

	def assembledata(self, data, cachedData):
		if cachedData == None or cachedData == False:
			LbsRequest.assemble0x80data(self)
			LbsRequest.assemble0x81data(self)
			LbsRequest.assemble0x82data(self)
			LbsRequest.assemble0x83data(self)
			LbsRequest.assemble0x84data(self)
		else:
			self.data0x80 = cachedData['data0x80']
			self.data0x81 = cachedData['data0x81']
			self.data0x82 = cachedData['data0x82']
			self.data0x83 = cachedData['data0x83']
			#self.data0x84 = cachedData['data0x84']
			LbsRequest.assemble0x84data(self)
		sliceData = []
		LbsRequest.collectLenghtAndVerion(self, data)
		LbsRequest.assembleSeqdata(self)
		sliceData.extend(self.collectData)
		sliceData.extend(self.data0x80)
		if self.reqPostionType <= 0x01:
			sliceData.extend(self.data0x81)
			sliceData.extend(self.data0x82)
			sliceData.extend(self.seqData)
		elif self.reqPostionType == 0x02:
			sliceData.extend(self.data0x82)
		elif self.reqPostionType == 0x03:
			sliceData.extend(self.data0x81)
			sliceData.extend(self.data0x82)
			sliceData.extend(self.data0x83)
		elif self.reqPostionType == 0x04:
			sliceData.extend(self.data0x84)
		elif self.reqPostionType == 0x05:
			sliceData.extend(self.data0x81)
			sliceData.extend(self.data0x82)
			sliceData.extend(self.data0x84)
		elif self.reqPostionType == 0x08:
			sliceData.extend(self.data0x84)
		sliceData[0] = len(sliceData) + 2

		return sliceData



	def decodeData(self,data):
		pass

	def amapRequest(self, data):
		rand = random.randint(10000,99999)
		uri = "http://apilocate.amap.com/position"
		accesstype = '?accesstype=0'
		imei = '&imei=' + self.imei
		cdma = '&cdma=' + str(self.netType)
		bts =''
		nearbts =''
		if "|" not in self.btsStr:
			bts = '&bts=' + self.btsStr
			nearbts = '&nearbts=' + self.btsStr
		else:
			bts = '&bts=' + self.btsStr.split("|")[0]
			nearbts = '&nearbts=' + self.btsStr
		output = '&output=json'
		key = '&key=916675bab09315d4d036ad1ae3a2343c'

#        query = {
#            "accesstype": "0",
#            "imei": self.imei,
#            "cdma": "0",
#            "bts": self.mccAndMnc + ',' + str(self.nearbtslac)+',' + str(self.nearbtscellid) + ',' + str(self.nearbtsdbm),
#            "nearbts": self.mccAndMnc + ',' + str(self.nearbtslac)+',' + str(self.nearbtscellid) + ',' + str(self.nearbtsdbm),
#            "output": "json",
#            "key": "916675bab09315d4d036ad1ae3a2343c",
#        }
#        queryStr = json.dumps(query)
#        logger.debug(queryStr)
		if self.netType == 0:
			url = uri + accesstype + imei + cdma + bts + nearbts +output + key
		else:
			bts = '&bts='+str(self.cdmabtssid) + ',' +str(self.cdmabtsnid) +',' +str(self.cdmabtsbid) +',,,' +str(self.cdmabtsdbm)
			url = uri + accesstype + imei + cdma + bts +output + key
		logger.info("randIndex Reuqest : %d with request Amap %s"%(rand,url))

		headers = {
			'Content-Type': "application/json",
		}
		req = requests.Session()
		req.mount('http://', HTTPAdapter(max_retries=3))
		try:
			response=req.get(url,headers=headers,timeout=1)
			logger.info("randIndex Reuqest : %d with data : %s elapseed: %s "%(rand,response.text,response.elapsed.total_seconds()))
			respData = json.loads(response.text)
			self.amapresponseCode = respData['infocode']
			self.amapresponseStatus = respData['status']
			self.positionState = respData['info']
			self.loactetype = respData['result']['type']
			# print(self.amapresponseCode,self.amapresponseStatus,self.positionState )
			if self.amapresponseCode == "10000" and self.amapresponseStatus == '1' and self.positionState == 'OK' and int(self.loactetype) > 0  :
				self.positionResult = 0
				self.location = respData['result']["location"]
				self.longitude = self.location.split(",", 1)[0]
				self.latitude = self.location.split(",", 1)[1]
				self.address = respData['result']['desc']
		#		logger.debug(self.longitude, self.latitude, self.address)
		#        addressbytes = bytes(self.address, encoding='utf_16_be')
				self.city = respData['result']['city']
				self.cityCode = respData['result']['citycode']
				self.country = respData['result']['country']
				self.postCode = respData['result']['adcode']
				self.positonaccuracy = respData['result']['radius']
				self.positionTime = time.time() *1000
			else:
				if 	self.positionState == 'ok' or self.loactetype == '0':
					self.positionResult = 3
				else:
					self.positionResult = 1	
		except requests.exceptions.RequestException as e:
			logger.info("get lbs timout")
			self.positionResult = 4

		#response = requests.request("GET", url, headers=headers, timeout(0.5,0.5))
		

#        response = requests.request("GET", uri, headers=headers, params=queryStr)








def main():
	f = Factory()
	f.protocol = LbsRequest
	if "PORT" in os.environ:
		PORT = int(os.environ['PORT'])
	else:
		PORT = 80
	reactor.listenTCP(PORT, f, interface='')
	logger.info("listening on %d "%PORT)
	reactor.run()

if __name__ == '__main__':
	main()