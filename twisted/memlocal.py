#!/usr/bin/env python

import time
import json
import configparser
import logging
import os
from pymemcache.client.base import Client

from logger import logger

# def logger(message):
# 	log = logging.getLogger("memcached: ")
# 	log.setLevel(logging.DEBUG)

# 	# fh = logging.FileHandler("log-memcached.log")
# 	# fh.setLevel(logging.INFO)

# 	ch = logging.StreamHandler()
# 	ch.setLevel(logging.INFO)

# 	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 	ch.setFormatter(formatter)
	 
# 	# fh.setFormatter(formatter)
# 	### Protocol Implementation
# 	log.addHandler(ch)
# 	log.

 
# logger.addHandler(fh)


class memcache():

	def __init__(self):
		cf = configparser.ConfigParser()
		cf.read("./config/config.ini")
		# elasticache settings       # simcomlbs.0rxi5f.cfg.cnw1.cache.amazonaws.com.cn:11211

		if "memcachedendpoint" in os.environ:
			self.memcachedendpoint = os.environ['memcachedendpoint']
		else:
			self.memcachedendpoint = cf.get("SimcomLBSMemcached", "memcachedServer")

		if "memcachedport" in os.environ:
			self.memcachedport = int(os.environ['memcachedport'])
		else:
			self.memcachedport = int(cf.get("SimcomLBSMemcached", "memcachedport"))
		logger.info("%s,%d"%(self.memcachedendpoint,self.memcachedport))	


	def set(self, k, data):
		"""将数据加入到缓存中
		"""
		logger.info("memcached: %s %s: %s"%(data, self.memcachedendpoint,self.memcachedport))
		try:
			client = Client((self.memcachedendpoint, self.memcachedport))
			client.set(k, data, 300)
			logger.debug(data)
			return True
		except Exception as e:
			logger.info(e)
			return False


	def get(self,k):
		"""获取memcached数据
		"""
		try:
			client = Client((self.memcachedendpoint, self.memcachedport))
			return json.loads(client.get(k))
		except Exception as e:
			logger.info(e)
			return False


# def main():


# 	result = get_memcached(k)
# 	if result:
# 		print("这是从缓存中取数据")
# 		show_data(result)
# 	else:
# 		print("这是从数据库取数据")
# 		data = get_data()
# 		show_data(data)
# 		set_memcache(k, data)
# main()