#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, getopt
import binascii
import os
import time
import datetime
import re
import shutil
def usage():
	print 'python cleanFlow.py -r <root data directory>'
	print 'cleanFlow.py usage:'
	print '-r, --rootDir: .flow & flow.feature file root directory'
	
	print 'example:'
	print '\tpython cleanFlow.py -r D:\\MobileGT\\data'
	print '\tpython cleanFlow.py -r D:\\MobileGT\\data_new'
	print 'result:\tplease see rootDir_clean directory'

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
	
#WORKING_ROOT_DIR='/home/5ubuntu/data/train/'
#WORKING_ROOT_DIR='D:\\MobileGT\\data_infer'
WORKING_ROOT_DIR=input_dir
#TARGET_ROOT_DIR='D:\\MobileGT\\data_infer_clean'
TARGET_ROOT_DIR=input_dir+'_clean'
#读取dataApp.txt文件，若存在newAppName则该应用的流数据保留，否则删除之
##appName	#flowNum	#pktNum	#byteNum	#newAppName		
#NOT FOUND	19780	219134	52341502		
#下载管理	9310	454036	306256350		Download
old2NewAppNameList={}
dataAppFile=open(os.path.join(WORKING_ROOT_DIR,'dataApp.txt'),'r')
for line in dataAppFile:
	if line.startswith('#'):
		continue
	l1=line.strip().split('\t')	
	if len(l1)!=5:
		continue
	oldAppName=l1[0].strip()
	newAppName=l1[4].strip()
	old2NewAppNameList[oldAppName]=newAppName
print len(old2NewAppNameList)	
	
#找出WORKING_ROOT_DIR目录及子目下所有名为.flow文件，存放到flowFileNames变量中
flowFeatureFileNames=find_file_by_pattern('flow.feature',WORKING_ROOT_DIR)
#print flowFeatureFileNames

#
for name in flowFeatureFileNames:

	flowFeatureFile=open(name,'r')
	srcDir=os.path.dirname(name)
	flowFeatureFileName=os.path.basename(name)
	dstDir=srcDir.replace(WORKING_ROOT_DIR,TARGET_ROOT_DIR)
	if not os.path.exists(dstDir):
		os.makedirs(dstDir)
	newFlowFeatureFile=open(os.path.join(dstDir,flowFeatureFileName),'w')
	print('process ' + srcDir + '---->' + dstDir)
	##flowkey(设备IP<1>,设备端口<2>,协议<3>,对端IP<4>,对端端口<5>),created<6>,destroyed<7>,appName<8>,encrypted_tag<9>,总报文数<10-1>,字节数<11-2>,报文大小(最小<12-3>,最大<13-4>,平均<14-5>,标准差<15-6>),报文到达时间间隔(最小<16-7>,最大<17-8>,平均<18-9>,标准差<19-10>),流持续时间<20-11>,IN总报文数<21-1>,IN字节数<22-2>,IN报文大小(最小<23-3>,最大<24-4>,平均<25-5>,标准差<26-6>),IN报文到达时间间隔(最小<27-7>,最大<28-8>,平均<29-9>,标准差<30-10>),IN流持续时间<31-11>,OUT总报文数<32-1>,OUT字节数<33-2>,OUT报文大小(最小<304-3>,最大<35-4>,平均<36-5>,标准差<37-6>),OUT报文到达时间间隔(最小<38-7>,最大<39-8>,平均<40-9>,标准差<41-10>),OUT流持续时间<42-11>
	#10.77.2.2,37361,TCP,118.178.213.227,80,1485490563,1485490628,贪吃蛇大作战,normal,17,1140,0,319,67.0588235294,121.270466114,5.60283660889e-05,741.28884697,50.8973291814,178.906414354,814.357266903,6,277,0,277,46.1666666667,103.231804961,0.0318269729614,63.6978919506,13.6990443707,25.0328236684,68.4952218533,11,863,0,319,78.4545454545,128.637166718,5.60283660889e-05,741.28884697,81.4357266903,220.75237443,814.357266903
	for line in flowFeatureFile:		
		if line.startswith('#'):
			newFlowFeatureFile.write(line)
			continue
		l1=line.split(',')
		if len(l1)!=42:
			continue
		appName=l1[7].strip()
		flowkey=l1[0]+'-'+l1[1]+'-'+l1[2]+'-'+l1[3]+'-'+l1[4]
		pktNum=eval(l1[9])
		if old2NewAppNameList.has_key(appName):
			#if os.path.exists(os.path.join(srcDir,flowkey+'.flow')):
			newFlowFeatureFile.write(line.replace(appName,old2NewAppNameList[appName]))
				#拷贝flow文件到目标目录
				#shutil.copyfile(os.path.join(srcDir,flowkey+'.flow'),os.path.join(dstDir,flowkey+'.flow'))
			#else:
			#	print 'flow file not found:'+line
			
	newFlowFeatureFile.close()
	