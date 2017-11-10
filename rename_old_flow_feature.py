#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, getopt
import os
import re

def usage():
	print 'python rename_old_flow_feature.py -r <root data directory>'
	print 'rename_old_flow_feature.py usage:'
	print '-r, --rootDir: flow.feature file root directory'

	print 'example:'
	print '\tpython rename_old_flow_feature.py -r D:\\MobileGT\\data_clean' 
	print 'result:\tplease see flow.feature rename to flow.feature_old in same directory'

def find_file_by_pattern(pattern='.*', base=".", circle=True): 
	'''''查找给定文件夹下面所有 ''' 
	re_file = re.compile(pattern) 
	if base == ".": 
		base = os.getcwd() 

	final_file_list = [] 
	print base 
	cur_list = os.listdir(base) 
	for item in cur_list: 
		if item == ".svn": 
			continue 
		full_path = os.path.join(base, item) 
		if full_path.endswith(".doc") or full_path.endswith(".bmp") or full_path.endswith(".wpt") or full_path.endswith(".dot"): 
			continue 

		# print full_path 
		bfile = os.path.isfile(item) 
		if os.path.isfile(full_path): 
			if re_file.search(full_path): 
				final_file_list.append(full_path) 
		else: 
			final_file_list += find_file_by_pattern(pattern, full_path) 
	return final_file_list 

try:
	opts, args = getopt.getopt(sys.argv[1:],'hr:',["rootDir="])
except getopt.GetoptError:
	usage()
	sys.exit(2)

if len(opts) < 1 :
	usage()
	sys.exit()
	
for op, value in opts:
	if op in ("-r", "--rootDir"):			
		input_dir = value
		print("input_dir:["+input_dir+"]")	
	elif op == '-h':
		usage()
		sys.exit()

WORKING_DIR=input_dir
flowFeatureFileNames=find_file_by_pattern('flow.feature',WORKING_DIR)
print flowFeatureFileNames

for name in flowFeatureFileNames:
	os.rename(name,name.replace("feature","old"))

#