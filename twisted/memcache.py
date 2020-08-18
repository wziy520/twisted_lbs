#!/usr/bin/env python
# encoding: utf-8
import elasticache_auto_discovery
from pymemcache.client.hash import HashClient
from pymemcache.client.base import Client
import configparser
import logging
import os

import logger.logger as logger

EXPIRE_TIME = 300

# logger = logging.getLogger("memcached: ")
# logger.setLevel(logging.DEBUG)

# fh = logging.FileHandler("log-memcached.log")
# fh.setLevel(logging.INFO)

# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)

# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# ch.setFormatter(formatter)
 
# fh.setFormatter(formatter)
# ### Protocol Implementation
# logger.addHandler(ch)
 
# logger.addHandler(fh)


class memcache():

	def __init__(self):
		cf = configparser.ConfigParser()
		cf.read("./config/config.ini")
		# elasticache settings       # simcomlbs.0rxi5f.cfg.cnw1.cache.amazonaws.com.cn:11211
		if "memcachedendpoint" in os.environ:
			memcachedendpoint = os.environ['memcachedendpoint']
		else:
			memcachedendpoint = cf.get("SimcomLBSMemcached", "memcachedServer")

		if "memcachedport" in os.environ:
			memcachedport = os.environ['memcachedport']
		else:
			memcachedport = cf.get("SimcomLBSMemcached", "memcachedServer")

		logger.info("%s : %s"%(memcachedendpoint, memcachedport))

		#-------------Hash client for AWS memcached ------------------------------------------------------
		# elasticache_config_endpoint = endpoint + ":" + port
		# nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
		# nodes = map(lambda x: (x[1], int(x[2])), nodes)
		# self.memcache_client = HashClient(nodes)
		#------------------------------------------------------------------------------------------
		# ----------------Directlly connected to pod memecached------------------------------------
		self.memcache_client = Client(memcachedendpoint, memcachedport)
		self.memcache_client.set(self, 'abcd123', "1234ab")
		#----------------------------------------------------------------------------------
	def aaa():
		print("aaa")
	def set(self, imei = None, str_data = None):
		logger.info("set imei: %s str: %s "%(imei, str_data))
		self.memcache_client.set(imei, str_data, EXPIRE_TIME)
	def get(self, imei=''):
		value = self.memcache_client.get(imei)
		logger.info("get imei: %s str: %s "%(imei, value))
		return value

# mem_client=memcache()
# mem_client.set(imei=123,str_data="123")
# mem_client.get(imei=123)
