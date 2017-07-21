#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, getopt
import binascii
import os
import time
import datetime
import re

def usage():
	print 'python statAppName.py -r <root data directory>'
	print 'statAppName.py usage:'
	print '-r, --rootDir: .flow & flow.feature file root directory'
	
	print 'example:'
	print '\tpython statAppName.py -r D:\\MobileGT\\data'
	print '\tpython statAppName.py -r D:\\MobileGT\\data_new'
	print 'result:\tplease see statResult.log in root directory'
	
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
		print("input_dir:"+input_dir)
	elif op == '-h':
		usage()
		sys.exit()
	
#找出WORKING_DIR目录及子目下所有名为flow.feature文件，存放到flowFeatureFileNames变量中
#flowFeatureFileNames={'/home/ubuntu/data/train/day02/44cd4ccc_20160630_flow/flow.feature','/home/ubuntu/data/train/day01/44cd4ccc_20160627_flow/flow.feature'}
#WORKING_DIR='/home/ubuntu/data/train/'
WORKING_DIR=input_dir
flowFeatureFileNames=find_file_by_pattern('flow.feature',WORKING_DIR)
print flowFeatureFileNames
statResult=open(WORKING_DIR+"\\statResult.log",'w')

appFlowList={}
appPktList={}
appByteList={}
for name in flowFeatureFileNames:
	#fullName=os.path.join(WORKING_DIR,name)
	#flowFeatureFile=open(fullName,'r')
	flowFeatureFile=open(name,'r')
	##flowkey(设备IP<1>,设备端口<2>,协议<3>,对端IP<4>,对端端口<5>),created<6>,destroyed<7>,appName<8>,encrypted_tag<9>,总报文数<10-1>,字节数<11-2>,报文大小(最小<12-3>,最大<13-4>,平均<14-5>,标准差<15-6>),报文到达时间间隔(最小<16-7>,最大<17-8>,平均<18-9>,标准差<19-10>),流持续时间<20-11>,IN总报文数<21-1>,IN字节数<22-2>,IN报文大小(最小<23-3>,最大<24-4>,平均<25-5>,标准差<26-6>),IN报文到达时间间隔(最小<27-7>,最大<28-8>,平均<29-9>,标准差<30-10>),IN流持续时间<31-11>,OUT总报文数<32-1>,OUT字节数<33-2>,OUT报文大小(最小<304-3>,最大<35-4>,平均<36-5>,标准差<37-6>),OUT报文到达时间间隔(最小<38-7>,最大<39-8>,平均<40-9>,标准差<41-10>),OUT流持续时间<42-11>
	#10.77.2.2,37361,TCP,118.178.213.227,80,1485490563,1485490628,贪吃蛇大作战,normal,17,1140,0,319,67.0588235294,121.270466114,5.60283660889e-05,741.28884697,50.8973291814,178.906414354,814.357266903,6,277,0,277,46.1666666667,103.231804961,0.0318269729614,63.6978919506,13.6990443707,25.0328236684,68.4952218533,11,863,0,319,78.4545454545,128.637166718,5.60283660889e-05,741.28884697,81.4357266903,220.75237443,814.357266903
	for line in flowFeatureFile:
		l1=line.split(',')
		if line.startswith('#') or len(l1)!=42:
			continue
		appName=l1[7].strip()
		pktNum=eval(l1[9])
		byteNum=eval(l1[10])
		flowNum=1
		if appFlowList.has_key(appName):
			flowNum += appFlowList[appName]
			pktNum += appPktList[appName]
			byteNum += appByteList[appName]
		appFlowList[appName]=flowNum
		appPktList[appName]=pktNum
		appByteList[appName]=byteNum

statResult.write('#appName\t#flowNum\t#pktNum\t#byteNum\n')
for appName in appFlowList:
	#print(appName+" "+str(appList[appName]))
	statResult.write(appName+'\t'+str(appFlowList[appName])+'\t'+str(appPktList[appName])+'\t'+str(appByteList[appName])+'\n')
statResult.close()