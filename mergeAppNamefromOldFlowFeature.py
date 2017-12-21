#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, getopt
import os
import re

def usage():
	print 'python mergeAppNamefromOldFlowFeature.py -r <root data directory>'
	print 'mergeAppNamefromOldFlowFeature.py usage:'
	print '-r, --rootDir: flow.feature & flow.feature_old file root directory'

	print 'example:'
	print '\tpython mergeAppNamefromOldFlowFeature.py -r D:\\MobileGT\\data_clean' 
	print 'result:\tplease see flow.feature_merge (merge appName(=NO_SOCKET) field from flow.feature_old)'

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
#oldFlowFeatureFileNames=find_file_by_pattern('flow.feature_old',WORKING_DIR)
#print oldFlowFeatureFileNames

flowFeatureFileNames=find_file_by_pattern('flow.feature',WORKING_DIR)
print "flowFeatureFileNames:"
print flowFeatureFileNames


for name in flowFeatureFileNames:
	oldName=name.replace("feature","old");
	mergeName=name.replace("feature","merge");
	if not os.path.exists(oldName):
		print("cannot not found old flowFeatureFile:"+oldName+" skip!")
		continue

	#
	#旧的流统计属性文件
	#flowkey(1-5),总报文数(6),字节数(7),报文大小(最小8,最大9,平均10,标准差11),报文到达时间间隔(最小12,最大13,平均14,标准差15),流持续时间(16),appName(17),encrypted_tag(18)
	#10.0.0.2,49694,UDP,172.31.0.2,53,4,430,34,181,107.5,73.5,1.90734863281e-06,0.0919489860535,0.0306913057963,0.0433157493311,0.0920739173889,MobileGT,normal
	#
	oldFlowFeatureFile=open(oldName,'r')
	#缓存旧的流统计属性文件中的flowKey和appName
	flowkeyAppNames={}
	for line in oldFlowFeatureFile:
		l1=line.split(',')
		if line.startswith('#') or len(l1)!=18:
			#print line
			continue
		flowkey=l1[0]+','+l1[1]+','+l1[2]+','+l1[3]+','+l1[4]
		appName=l1[16]
		flowkeyAppNames[flowkey]=appName
	oldFlowFeatureFile.close()
	print("flowkeyAppNames size is:"+str(len(flowkeyAppNames)))
	flowFeatureFile=open(name,'r')
	mergeFlowFeatureFile=open(mergeName,'w')
	#
	#新的flow.feature文件格式
	##flowkey(设备IP<1>,设备端口<2>,协议<3>,对端IP<4>,对端端口<5>),created<6>,destroyed<7>,appName<8>,encrypted_tag<9>,总报文数<10-1>,字节数<11-2>,报文大小(最小<12-3>,最大<13-4>,平均<14-5>,标准差<15-6>,峰度<16-7>,偏度<17-8>,标准误差<18-9>),报文到达时间间隔(最小<19-10>,最大<20-11>,平均<21-12>,标准差<22-13>),流持续时间<23-14>,IN总报文数<24-1>,IN字节数<25-2>,IN报文大小(最小<26-3>,最大<27-4>,平均<28-5>,标准差<29-6>,峰度<30-7>,偏度<31-8>,标准误差<32-9>),IN报文到达时间间隔(最小<33-10>,最大<34-11>,平均<35-12>,标准差<36-13>),IN流持续时间<37-14>,OUT总报文数<38-1>,OUT字节数<39-2>,OUT报文大小(最小<40-3>,最大<41-4>,平均<42-5>,标准差<43-6>,峰度<44-7>,偏度<45-8>,标准误差<46-9>),OUT报文到达时间间隔(最小<47-10>,最大<48-11>,平均<49-12>,标准差<50-13>),OUT流持续时间<51-14>
	#
	for line in flowFeatureFile:
		l1=line.split(',')
		if line.startswith('#') or len(l1)!=51:
			#print line
			mergeFlowFeatureFile.write(line)
			continue
		flowkey=l1[0]+','+l1[1]+','+l1[2]+','+l1[3]+','+l1[4]
		appName=l1[7]
		#appName='NO_SOCKET'
		if appName=='NO_SOCKET':
			if flowkeyAppNames.has_key(flowkey):
				appName=flowkeyAppNames[flowkey]
			else:
				appName="NOTFOUND"
		else:
			print('old appName is not NO_SOCKET,do not replace.')
			
		mergeFlowFeatureFile.write(line.replace("NO_SOCKET", appName))
	flowFeatureFile.close()		
	mergeFlowFeatureFile.close()

	