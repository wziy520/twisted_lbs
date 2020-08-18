#!/usr/bin/env python
# encoding: utf-8
import logging

# class logger(self, message,logger_level = logging.INFO, logger_name = ''):
# 	log = logging.getLogger(logger_name)
# 	log.setLevel(logging.DEBUG)

# 	# fh = logging.FileHandler("log-memcached.log")
# 	# fh.setLevel(logging.INFO)

# 	ch = logging.StreamHandler()
# 	ch.setLevel(logger_level)

# 	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 	ch.setFormatter(formatter)
	 
# 	# fh.setFormatter(formatter)
# 	### Protocol Implementation
# 	log.addHandler(ch)


 
# logger.addHandler(fh)


logger = logging.getLogger("simcom-lbs")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("simcom-lbs.log")
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
 
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
 
logger.addHandler(fh)
logger.addHandler(ch)
