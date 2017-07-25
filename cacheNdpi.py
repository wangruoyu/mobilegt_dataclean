#!/usr/bin/env python
# -*- coding:utf-8 -*-

#安装numpy
#sudo pip install numpy
import sys, getopt
import os
import os.path
import glob
import time
import datetime
import numpy,math
import re
import platform
osname=platform.system()
if osname =="Windows":
	print ("Windows tasks")
	import win_inet_pton
elif osname == "Linux":
	print ("Linux tasks")
else:
	print ("Other System tasks")

def main(argv):
	try:
		opts, args = getopt.getopt(argv,'hr:u:f:',["ndpiFile=","userIPPrefix="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	input_ndpiFileDir=""
	input_ndpiFile=""
	input_userIPPrefix="10.0."
	if len(opts) < 1 :
		usage()
		sys.exit()
	for op, value in opts:
		if op in ("-r", "--ndpiFileDir"):			
			input_ndpiFileDir = value
			print("input_ndpiFileDir:%s" %(input_ndpiFileDir))
		elif op in ("-u", "--userIPPrefix"):			
			input_userIPPrefix = value
			print("input_userIPPrefix:%s" %(input_userIPPrefix))
		elif op in ("-f", "--ndpiFile"):			
			input_ndpiFile = value
			print("input_ndpiFile:%s" %(input_ndpiFile))
		elif op == '-h':
			usage()
			sys.exit()
	NDPI_DIR=input_ndpiFileDir
	NDPI_FILE=input_ndpiFile
	UserIP_prefix=input_userIPPrefix
	flowAppMapList=cacheNdpiFile(NDPI_DIR,UserIP_prefix,NDPI_FILE)
	print len(flowAppMapList)
	size1=0
	size2=0
	for flowkey in flowAppMapList:
		if len(flowAppMapList[flowkey])>1:
			#print ('%s --> %s' %(flowkey,flowAppMapList[flowkey]))
			size1+=1
			print flowAppMapList[flowkey]
		else:
			size2+=1
	print('size1:%s\tsize2:%s' %(size1,size2))
	#print flowAppMapList
	
def usage():
	print 'python cacheNdpiFile.py -r <ndpi file dir> -u <user ip prefix> -f <ndpi file name>'
	print 'cacheNdpiFile.py usage:'
	print '-r, --ndpiFileDir: ndpi file directory'
	print '-u, --userIPPrefix: user ip prefix'
	print '-f, --input_ndpiFile: ndpi file name, default process all .dpi file in ndpi file directory'
	print 'example:'
	print '\tpython cacheNdpiFile.py -r /home/liuzhen/scut_wlan/ndpi -u 110.66 -f 11_00001_20160108113050.pcap'
	print '\tpython cacheNdpiFile.py -r /home/liuzhen/scut_wlan/ndpi -u 110.66'
	print '\tpython cacheNdpiFile.py -r D:\\Downloads\\data\\scut_wlan\\ndpi -u 110.66 -f 11_00001_20160108113050.pcap'
	print 'result:\tplease see flow file directory'
	
'''
.dpi文件格式样例
Using nDPI (1.8.0) [1 thread(s)]
Reading packets from pcap file 1_00001_20160108113050.pcap...
Running thread 0...
	1	TCP 110.65.5.67:53644 <-> 202.38.193.207:80 [proto: 7/HTTP][1 pkts/636 bytes]
	2	TCP 220.178.213.186:46714 <-> 110.65.10.207:80 [proto: 7/HTTP][1 pkts/198 bytes]
	3	TCP 14.17.43.44:80 <-> 110.65.5.167:62372 [proto: 7/HTTP][1 pkts/186 bytes]
	4	UDP 10.65.10.166:137 <-> 10.65.10.255:137 [proto: 10/NetBIOS][1 pkts/92 bytes]
'''
'''
下面的函数处理.dpi文件,已经前面文件格式样例,
	1. 包含.pcap的行记录了pcap文件名,文件名中包含时间信息
	2. 包含proto:的行为具体应用名称行
	#flowAppMapList:{flowkey--->{appname:[filename_time_list]}
	#flowkey=ipUser+'-'+portUser+'-'+protocol+'-'+ipInternet+'-'+portInternet
'''
def cacheNdpiFile(NDPI_DIR,UserIP_prefix,NDPI_FILE):
	if NDPI_FILE=="":
		dpiFileNames=glob.glob(NDPI_DIR+os.path.sep+'*.dpi')	
	else:
		dpiFileNames=[os.path.join(NDPI_DIR,NDPI_FILE)]
	print dpiFileNames
	flowAppMapList={}
	for dpiFileName in dpiFileNames:
		ndipFile=open(dpiFileName,'r')
		timestamp=''
		for line in ndipFile:
			if ".pcap" in line:
				ll=line.split()			#Reading packets from pcap file 1_00001_20160108113050.pcap...
				fn=ll[5].split(".")			#1_00001_20160108113050.pcap
				ts=fn[0].split("_")			#1_00001_20160108113050
				timestamp=ts[2]				#20160108113050
				continue
			elif "[proto:" in line:	
				ll=line.split()				#	2	TCP 220.178.213.186:46714 <-> 110.65.10.207:80 [proto: 7/HTTP][1 pkts/198 bytes]
				index=ll[0]					#2
				protocol=ll[1]				#TCP
				ipport1=ll[2].split(":")	#220.178.213.186:46714
				ip1=ipport1[0]				#220.178.213.186
				port1=ipport1[1]			#46714			
				ipport2=ll[4].split(":")	#110.65.10.207:80
				ip2=ipport2[0]				#110.65.10.207
				port2=ipport2[1]			#80
				if ip1.startswith(UserIP_prefix) and (not ip2.startswith(UserIP_prefix)):
					ipUser=ip1
					portUser=port1
					ipInternet=ip2
					portInternet=port2
				elif (not ip1.startswith(UserIP_prefix)) and ip2.startswith(UserIP_prefix):
					ipUser=ip2
					portUser=port2
					ipInternet=ip1
					portInternet=port1
				else:
					#error log
					continue
				p1=ll[6].split("/")		#7/HTTP][1
				p2=p1[1].split("][")	#HTTP][1
				appName=p2[0]			#HTTP
				if appName=="Unknown":
					continue
			else:
				continue
			flowkey=ipUser+'-'+portUser+'-'+protocol+'-'+ipInternet+'-'+portInternet
			
			if flowAppMapList.has_key(flowkey):			
				if flowAppMapList[flowkey].has_key(appName):
					if timestamp in flowAppMapList[flowkey][appName]:
						continue
					else:
						flowAppMapList[flowkey][appName].append(timestamp)
				else:
					flowAppMapList[flowkey][appName]=[timestamp]
			else:
				flowAppMapList[flowkey]={}
				flowAppMapList[flowkey][appName]=[timestamp]	
			
		ndipFile.close()		
	return flowAppMapList
	
if __name__=='__main__':
	main(sys.argv[1:])