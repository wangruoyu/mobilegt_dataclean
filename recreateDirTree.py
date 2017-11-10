#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, getopt
import os
import re
import shutil

def usage():
	print 'python recreateDirTree.py -r <root data directory>'
	print 'recreateDirTree.py usage:'
	print '-r, --rootDir: .flow file root directory'

	print 'example:'
	print '\tpython recreateDirTree.py -r D:\\MobileGT\\data_clean' 
	print 'result:\tplease see directory tree in flows'

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
flowFileNames=find_file_by_pattern('.flow',WORKING_DIR)
#print flowFileNames

for name in flowFileNames:
	
	flowDirName=os.path.dirname(name)
	flowDirDirName=os.path.dirname(flowDirName)
	dirName=os.path.basename(flowDirName)
	#dirName:44cd4ccc_20160627_flow
	l1=dirName.split('_')
	deviceId=l1[0]
	dateDate=l1[1]
	#如果.flow文件所在的目录不是在flows目录下，创建flows目录，并把.flow文件的目录移动到flows目录下
	if not os.path.basename(flowDirDirName)=="flows":
		if not os.path.exists(flowDirDirName+os.path.sep+"flows"):
			os.mkdir(flowDirDirName+os.path.sep+'flows')
		if not os.path.exists(flowDirDirName+os.path.sep+'flows'+os.path.sep+dirName):
			shutil.move(flowDirName,flowDirDirName+os.path.sep+'flows')
		flowRootDirName=flowDirDirName
	else:
		flowRootDirName=os.path.dirname(flowDirDirName)
	if not os.path.exists(flowRootDirName+os.path.sep+deviceId):
		os.mkdir(flowRootDirName+os.path.sep+deviceId)
	if not os.path.exists(flowRootDirName+os.path.sep+deviceId+os.path.sep+dateDate):
		os.mkdir(flowRootDirName+os.path.sep+deviceId+os.path.sep+dateDate)