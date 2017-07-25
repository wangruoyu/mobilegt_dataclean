#!/usr/bin/env python
# -*- coding:utf-8 -*-

#安装dpkt和numpy
#sudo apt-get install python-dpkt
#sudo pip install numpy
import sys, getopt
import dpkt
import socket
import binascii
import os
import os.path
import glob
import time
import datetime
import numpy,math
import re
import platform
from orderFlowFile import * 
from cacheNdpi import *
osname=platform.system()
if osname =="Windows":
	print ("Windows tasks")
	import win_inet_pton
elif osname == "Linux":
	print ("Linux tasks")
else:
	print ("Other System tasks")

#计算Kurtosis、Skewness and Standard Error
#The first standardized moment is zero,because the first moment about the mean is always zero.
#The second standardized moment is one,because the second moment about the mean is equal to the variance σ2.
#The third standardized moment is a measure of skewness. 三阶标准矩用于定义偏度
#The fourth standardized moment refers to the kurtosis. 四阶标准矩用于定义峰度,在实际应用中，通常将峰度值做减3处理，使得正态分布的峰度0(正态分布的峰度为常数3，均匀分布的峰度（系数）为常数1.)
def calc_kurt_skew_se(dataArray):
	n=len(dataArray)
	data_mean=dataArray.mean()
	data_std=dataArray.std()
	t_kurt=0.0
	t_skew=0.0
	t_se=0.0
	if not data_std==0:
		for d in dataArray:
			t_kurt+=(d-data_mean)**4/data_std**4
			t_skew+=(d-data_mean)**3/data_std**3		
		#kurtosis=t_kurt/(n-1)-3
		kurtosis=t_kurt/(n-1)
		skewness=t_skew/(n-1)
	else:
		#kurtosis=-3
		kurtosis=0
		skewness=0
	standard_error=data_std/math.sqrt(n)
	return kurtosis,skewness,standard_error

#end def calc_kurt_skew_se
	
def main(argv):
	try:
		opts, args = getopt.getopt(argv,'hr:i:d:m:a:s:',["rootDir=","deviceId=","dataDate=","min=","addr=","skip_pcap="])
	except getopt.GetoptError:
		print 'python buildStream.py -r <data root directory> -i <deviceId> -d <data date> -m <minnum> -a <tunaddr_prefix> -s <skip_pcap>'
		sys.exit(2)
	input_dir=""
	input_min=2
	input_tunaddr=""
	input_skip_pcap='False'
	input_deviceid=''
	input_dataDate=''
	if len(opts) < 1 :
		usage()
		sys.exit()
	for op, value in opts:
		if op in ("-r", "--rootDir"):			
			input_dir = value
			print("input_dir:"+input_dir)
		elif op in("-i","--deviceId"):
			input_deviceid = value
			print("input_deviceid:%s" %(input_deviceid))
		elif op in("-d","--dataDate"):
			input_dataDate = value
			print("input_dataDate:%s" %(input_dataDate))
		elif op in("-m","--min"):
			input_min = int(value)
			print("input_min:%s" %(input_min))
		elif op in("-a","--addr"):
			input_tunaddr = value
			print("tunaddr_prefix:%s" %(input_tunaddr))
		elif op in("-s","--skip_pcap"):
			input_skip_pcap = value
			print("skip_pcap:%s" %(input_skip_pcap))
		elif op == '-h':
			usage()
			sys.exit()

	UserIP_prefix=input_tunaddr
	#最少报文数,即流的报文数小于该数则不处理
	MIN_PKTNUM=input_min
	#数据文件存放目录,包括.pcap文件和.socket文件的目录
	#WORKING_DIR='/home/liuzhen/mergedata/44cd4ccc/20160630'
	#WORKING_DIR='/home/liuzhen/mergedata/94346c37/20160816'
	#WORKING_DIR=input_dir
	#DATA_ROOT_DIR='/home/liuzhen/mergedata'
	DATA_ROOT_DIR=input_dir
	#WORKING_DIR=DATA_ROOT_DIR+'/'+input_deviceid+'/'+input_dataDate
	#WORKING_DIR=DATA_ROOT_DIR+os.path.sep+input_deviceid+os.path.sep+input_dataDate
	#构建WORKING_DIR_LIST
	
	list_deviceid=input_deviceid.split()
	list_dataDate=input_dataDate.split()
	print("input deviceid:%s" %(list_deviceid))
	print("input dataDate:%s" %(list_dataDate))
	WORKING_DIR_LIST=[]
	allFilesInRoot=os.listdir(DATA_ROOT_DIR)
	allDirInRoot=[]
	#print(allFilesInRoot)
	for file in allFilesInRoot:
		if file=="flows":
			continue
		abs_file=DATA_ROOT_DIR+os.path.sep+file
		if os.path.isdir(abs_file) and (not list_deviceid or file in list_deviceid):
			allDirInRoot.append(file)
	print("all deviceid:%s" %(allDirInRoot))
	for deviceidDir in allDirInRoot:
		allFilesInDeviceidDir=os.listdir(DATA_ROOT_DIR+os.path.sep+deviceidDir)
		for dataDateDir in allFilesInDeviceidDir:
			abs_dataDateDir=DATA_ROOT_DIR+os.path.sep+deviceidDir+os.path.sep+dataDateDir
			if os.path.isdir(abs_dataDateDir) and (not list_dataDate or dataDateDir in list_dataDate):
				WORKING_DIR_LIST.append(abs_dataDateDir)
	print(WORKING_DIR_LIST)
	for WORKING_DIR in WORKING_DIR_LIST:
		#组流的结果存放到数据文件根目录的flows/目录下
		#FLOW_DIR=WORKING_DIR+'/flow'
		#FLOW_DIR=DATA_ROOT_DIR+'/flows/'+input_deviceid+'_'+input_dataDate+'_flow'
		#FLOW_DIR=DATA_ROOT_DIR+os.path.sep+'flows'+os.path.sep+input_deviceid+'_'+input_dataDate+'_flow'
		print("process %s" %(WORKING_DIR))
		tmp1=os.path.split(WORKING_DIR)
		dataDate_field=tmp1[1]
		tmp2=os.path.split(tmp1[0])
		deviceId_field=tmp2[1]
		FLOW_DIR=DATA_ROOT_DIR+os.path.sep+'flows'+os.path.sep+deviceId_field+'_'+dataDate_field+'_flow'		
		os.chdir(DATA_ROOT_DIR)
		if not os.path.exists(FLOW_DIR):
			os.makedirs(FLOW_DIR)
	
		#处理的异常数据存放到flow/目录下的exception.log文件中
		#EXCEPTION_LOG=FLOW_DIR+'/exception.log'
		EXCEPTION_LOG=FLOW_DIR+os.path.sep+'exception.log'
		exceptionLog=open(EXCEPTION_LOG,'w')
		#exceptionLog=open(EXCEPTION_LOG,'a')
	
		if input_skip_pcap=='False' or input_skip_pcap=='false':
			#
			print '开始处理.pcap文件进行组流'
			#pcapFileName='1_00001_20160630183417.pcap'
			#pcapFileName='1_00001_20160630070554.pcap'
			#pcapFileName='1_00001_20160816190922.pcap'
			#pcapFileNames=os.listdir(WORKING_DIR)
			#使用glob模块支持通配符,且输出的为全路径文件名
			pcapFileNames=glob.glob(WORKING_DIR+os.path.sep+'*.pcap')
			#排序,/home/liuzhen/mergedata/243aa171/20170516/1_00003_20170516003426.pcap,提取出20170516003426出来排序.
			#-------------------------------------------------------^*************^----
			#------------------------------------------------------(-19)---------(-5)--
			pcapFileNames.sort(key=lambda x:int(x[-19:-5]))
			#flowFileNames=[]
			#每个流会创建一个文件，所以注意linux同时打开文件数的限制，使用ulimit -n 10000限制可打开1万个文件		
			flowFiles={}
			#需限制打开的文件数目
			MAXOPEN_NUM=300
			openFiles={}#记录文件打开使用记录，filename:count，计数规则:count=count/2+1或0，即每次更新计数时除2，文件被选中操作+1，其它+0
			notFirstOpen=[]#记录曾经打开过的文件名
			for name in pcapFileNames:
				fullName=name
				#前面改使用glob模块,无需再组合全路径已经检查是否为.pcap文件
				#fullName=os.path.join(WORKING_DIR,name)			
				#if not (os.path.isfile(fullName) and fullName.endswith('.pcap')):
				#	continue
				print("process %s..." %(name))
				pcapFilePrefix=fullName.split('.')[0]
				pcapF=open(fullName,'rb') #windlows下运行出现dpkt.dpkt.NeedData ERROR,加上'rb'打开模式就没有问题
				pcap=dpkt.pcap.Reader(pcapF)
	
				#(ts,frame)=pcap.next()
				index=0
				skip=False
				for ts,frame in pcap:
					index=index+1
					#eth=dpkt.ethernet.Ethernet(frame) #//File encapsulation: Ethernet type
					#print `eth`
					#ip=eth.data
					try:
						#ip=dpkt.ip.IP(frame) #//File encapsulation: Raw IP
						eth=dpkt.ethernet.Ethernet(frame)#//File encapsulation: Ethernet
						ip=eth.data
						skip=False
						srcAddr=socket.inet_ntop(socket.AF_INET,ip.src)
						dstAddr=socket.inet_ntop(socket.AF_INET,ip.dst)
					except Exception as ex:
						skip=True
						exceptionLog.write(pcapFilePrefix+'-'+str(index)+' PKT ERROR.'+str(ex)+'\n')
					if skip:
						continue
					#如10.*.*.2 userIP(用户IP运行时由-a <tunaddr> 参数传入)
					#srcAddr is userIP & dstAddr is not userIP: direction=1, 流出流量
					#srcAddr is not userIP & dstAddr is userIP: direction=0, 流入流量
					direction=0
					#if srcAddr.startswith("10."):
					#	if not dstAddr.startswith("10."):
					if srcAddr.startswith(UserIP_prefix):
						if not dstAddr.startswith(UserIP_prefix):
							direction=1
							ipUser=srcAddr
							ipInternet=dstAddr
						else:
							exceptionLog.write(pcapFilePrefix+'-'+str(index)+' '+srcAddr+' '+dstAddr+'\n')
							#print(index,srcAddr,dstAddr)
							continue
					else:
						if dstAddr.startswith(UserIP_prefix):
							direction=0
							ipUser=dstAddr
							ipInternet=srcAddr
						else:
							exceptionLog.write(pcapFilePrefix+'-'+str(index)+' '+srcAddr+' '+dstAddr+'\n')
							#print(srcAddr,dstAddr)
							continue
					#ip.p //17: UDP    6: TCP	1:ICMP
					if ip.p==17:
						protocol='UDP'
					elif ip.p==6:
						protocol='TCP'
					else:
						exceptionLog.write(pcapFilePrefix+'-'+str(index)+' NOT UDP|TCP ip.p='+str(ip.p)+'\n')
						#print('pass ip.p=%s' %(ip.p))
						continue
					try:
						pkt=ip.data
						payload=pkt.data
						sport=pkt.sport
						dport=pkt.dport
						skip=False
					except Exception as ex:
						skip=True
						exceptionLog.write(pcapFilePrefix+'-'+str(index)+' PKT ERROR.'+str(ex)+'\n')
					if skip:
						continue
					if direction==1:
						portUser=pkt.sport
						portInternet=pkt.dport
					else:
						portUser=pkt.dport
						portInternet=pkt.sport
					timeStr=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ts))
					tt=`ts`.split('.')
					#如果载荷长度为0
					#if len(payload)==0:
					#	exceptionLog.write('%s %s.%s %s %s %s %s %s %s %s\n' %(index,timeStr,tt[1],ipUser,portUser,ipInternet,portInternet,protocol,direction,binascii.hexlify(str(payload))))
					#else:		
						#print('%s.%s' %(timeStr,tt[1]),ipUser,portUser,ipInternet,portInternet,protocol,direction,binascii.hexlify(str(payload)))
					flowKey=ipUser+'-'+str(portUser)+'-'+protocol+'-'+ipInternet+'-'+str(portInternet)
					if flowFiles.has_key(flowKey):
						flowFile=flowFiles.get(flowKey)
					else:
						#检查打开文件是否超过阈值,超过一个阈值则要选择计数最小的打开文件关闭，然后然后打开新的文件
						#openFiles记录了打开了哪些文件，并对每个文件打开访问过程进行计数，每打开一次计数/2再加1，每没打开一次计数/2
						if len(openFiles)>MAXOPEN_NUM:
							mincount=1
							for openFileName,openFileCount in openFiles.items():
								if openFileCount<=mincount:
									mincount=openFileCount
									min_FileName=openFileName
								#endif
							#end for openFileName
							flowFiles[min_FileName].close()		#关闭选中的文件
							del flowFiles[min_FileName]			#删除打开文件描述
							del openFiles[min_FileName]			#删除打开文件记录
						#end if len(openFiles)
						#flowFile=open(FLOW_DIR+'/'+flowKey+'.flow','w');
						if flowKey in notFirstOpen:
							flowFile=open(FLOW_DIR+os.path.sep+flowKey+'.flow','a');
						else:
							notFirstOpen.append(flowKey)
							flowFile=open(FLOW_DIR+os.path.sep+flowKey+'.flow','w');
							flowFile.write('#pkt_position(pcapFile-index)|packet_direction(1:output,0:input)|ip.len|payload.len|timestamp|timestamp-distance(2016-01-01 0:0:0)|payload\n')
						flowFiles[flowKey]=flowFile
						openFiles[flowKey]=0.0			#初始计数值为0.0，注意用小数
						
					#pktKey: pcapFilePrefix-index  example: 1_00001_20160630062731-1
					#pktKey: pcapFilePrefix-index
					#pktKey direction bytes timestamp payload
					d1 = datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S')
					d2 = datetime.datetime.strptime('2016-01-01 0:0:0', '%Y-%m-%d %H:%M:%S')
					delta = d1 - d2
					ts_distance=delta.total_seconds()+float('0.'+tt[1])
					flowFile.write('%s|%s|%s|%s|%s|%s|%s\n' %(pcapFilePrefix+'-'+str(index),direction,ip.len,len(payload),timeStr+'.'+tt[1],`ts_distance`,binascii.hexlify(str(payload))))
					#更新文件计数
					for name,count in openFiles.items():
						if name==flowKey:
							openFiles[name]=count/2.0+1		#打开的文件，计数/2+1
						else:
							openFiles[name]=count/2.0		#打开文件外的其他文件，计数/2
				pcapF.close()				
				#end for ts,frame in pcap
			#
			#end all pcap file
			#
			#关闭所有打开的flow文件
			for key,flowFile in flowFiles.items():
				flowFile.close()
			#调用orderFowFile.py里面的函数,按报文时间大小顺序调整文件里面报文顺序
			OVERWRITE="True"
			#FLOW_DIR
			orderFlowFile(FLOW_DIR,OVERWRITE)		
			exceptionLog.close()
		else:
			print('跳过.pcap文件组流')
		
		#
		#处理.dpi文件得到应用名称列表
		#
		#flowAppMapList={flowkey:appList}
		#applist={appName:[timestamp_list]}
		#timestamp格式为'20160108113050'
		#
		print('开始处理.dpi文件')
		input_ndpiFileDir=WORKING_DIR
		input_ndpiFile=""
		input_userIPPrefix=UserIP_prefix
		NDPI_DIR=input_ndpiFileDir
		NDPI_FILE=input_ndpiFile
		UserIP_prefix=input_userIPPrefix
		flowAppMapList=cacheNdpiFile(NDPI_DIR,UserIP_prefix,NDPI_FILE)
		print('.dpi文件处理完毕')
		#flowAppMapList:{flowkey--->{appname:[filename_time_list]}------timestamp-----格式为'20160108113050'
		#flowkey=ipUser+'-'+portUser+'-'+protocol+'-'+ipInternet+'-'+portInternet
		
		#
		#开始处理前面处理组流生成的流文件
		#	
		
		#ssl
		## Server Hello with certificate | Client Hello
		## This allows SSL 3.X, which includes TLS 1.0, known internally as SSL 3.1
		#^(.?.?\x16\x03.*\x16\x03|.?.?\x01\x03\x01?.*\x0b)
		#python
		regex_str='^((..)?(..)?1603(..)*1603|(..)?(..)?0103(01)?(..)*0b)'	
		regex_ssl=re.compile(regex_str)
		
		FLOW_MAX_INTERVAL=300#最大流间隔时间300秒
		FF_EXCEPTION_LOG=FLOW_DIR+os.path.sep+'flowfeature_exception.log'
		ff_exceptionLog=open(FF_EXCEPTION_LOG,'w')		#print('#flowkey,总报文数,字节数,报文大小(最小,最大,平均,标准差),报文到达时间间隔(最小,最大,平均,标准差),流持续时间,appName')
		#flowFeatureFile=open(FLOW_DIR+'/flow.feature','w')
		flowFeatureFile=open(FLOW_DIR+os.path.sep+'flow.feature','w')
		flowFeatureFile.write('#flowkey(设备IP<1>,设备端口<2>,协议<3>,对端IP<4>,对端端口<5>),created<6>,destroyed<7>,appName<8>,encrypted_tag<9>,总报文数<10-1>,字节数<11-2>,报文大小(最小<12-3>,最大<13-4>,平均<14-5>,标准差<15-6>,峰度<16-7>,偏度<17-8>,标准误差<18-9>),报文到达时间间隔(最小<19-10>,最大<20-11>,平均<21-12>,标准差<22-13>),流持续时间<23-14>,IN总报文数<24-1>,IN字节数<25-2>,IN报文大小(最小<26-3>,最大<27-4>,平均<28-5>,标准差<29-6>,峰度<30-7>,偏度<31-8>,标准误差<32-9>),IN报文到达时间间隔(最小<33-10>,最大<34-11>,平均<35-12>,标准差<36-13>),IN流持续时间<37-14>,OUT总报文数<38-1>,OUT字节数<39-2>,OUT报文大小(最小<40-3>,最大<41-4>,平均<42-5>,标准差<43-6>,峰度<44-7>,偏度<45-8>,标准误差<46-9>),OUT报文到达时间间隔(最小<47-10>,最大<48-11>,平均<49-12>,标准差<50-13>),OUT流持续时间<51-14>\n')
		#使用.dpi文件,flowApp自动填充数据
		flowApp=flowAppMapList
		#flowAppMapList:{flowkey--->{appname:[filename_time_list]}------filename_time-----格式为'20160108113050'
		#flowkey=ipUser+'-'+portUser+'-'+protocol+'-'+ipInternet+'-'+portInternet
		#
	
		flowFiles=os.listdir(FLOW_DIR)
		print("开始处理流文件(共%s个文件),统计流属性." %(len(flowFiles)))
		for name in flowFiles:
			fullName=os.path.join(FLOW_DIR,name)
			if not (os.path.isfile(fullName) and fullName.endswith('.flow')):
				continue
			#print 'process flowfile '+fullName
			flowKey=name[0:len(name)-5]
			flowFile=open(fullName,'r')
			#skip=flowKey.find('-')
			#flowkey_skipIpUser=flowKey[skip:]
			
			payloadBytes_all=[]#列表,里面存放的是字典{分割的流编号:[属于该流的报文数据]}
			ipBytes_all=[]
			pktTSs_all=[]
			in_payloadBytes_all=[]
			in_ipBytes_all=[]
			in_pktTSs_all=[]
			out_payloadBytes_all=[]
			out_ipBytes_all=[]
			out_pktTSs_all=[]
			encrypted_tag_all=[]#'normal'
			allAppName=[]#保存flowkey对应的所有可能的appName
			if flowApp.has_key(flowKey):
				for name in flowApp[flowKey]:
					allAppName.append(name)
			else:
				ff_exceptionLog.write('flow %s( %s) cannot found appName' %(flowKey,flowKey))
			#print("allAppName:%s" %(allAppName))
			#flowkey每一个可能的应用都创建一个数据记录器用于存放属于该应用的报文统计数据
			for index in range(len(allAppName)):
				payloadBytes_all.append({0:[]})
				ipBytes_all.append({0:[]})
				pktTSs_all.append({0:[]})
				in_payloadBytes_all.append({0:[]})
				in_ipBytes_all.append({0:[]})
				in_pktTSs_all.append({0:[]})
				out_payloadBytes_all.append({0:[]})
				out_ipBytes_all.append({0:[]})
				out_pktTSs_all.append({0:[]})
				encrypted_tag_all.append({0:'normal'})
			#pkt_position(pcapFile-index)|packet_direction(1:output,0:input)|ip.len|payload.len|timestamp|timestamp-distance(2016-01-01 0:0:0)|payload
			#flow文件内容：/home/liuzhen/mergedata/44cd4ccc/20160615/20160615-17625|1|65|13|2016-06-15 23:14:56.842539|14426096.842539|0c000401083d10d45abecfe95a
			lasttimestamp=0
			split_flow=0
			for line in flowFile:
				if line.startswith('#'):
					continue
				tt=line.split('|')
				tttime=tt[4].split('.')
				pkttimestamp=time.mktime(time.strptime(tttime[0],"%Y-%m-%d %H:%M:%S"))+float('0.'+tttime[1]) #秒数表示的时间
				#flowApp/flowAppMapList:{flowkey--->{appname:[filename_time_list]}------filename_time-----格式为'20160108113050'
				#flowkey=ipUser+'-'+portUser+'-'+protocol+'-'+ipInternet+'-'+portInternet
	
				selectedIndex=-1
				minDistance=0
				first=True#如果是第一个,则无需比较,直接设置,后面所有的值才开始比较
				#
				#比较报文时间同filename_time,选择比filename_time时间小且离filename_time最近的
				#每个应用类别可能有几个filename_time,需要全部比较
				#
				for index in range(len(allAppName)):										
					time_list=flowApp[flowKey][allAppName[index]]
					#print("time_list:%s" %(time_list))
					#取出识别为某个应用类型的所有filename_time,逐个比较,选出最合适的(比filename_time时间小且离filename_time最近的)
					for filename_time in time_list:
						ts=time.mktime(time.strptime(filename_time,"%Y%m%d%H%M%S"))
						distance=pkttimestamp-ts#报文时间-文件名时间
						if first:
							first=False
							minDistance=distance
							selectedIndex=index
						else:
							if minDistance<=0 and distance<=0 and abs(distance)<abs(minDistance):
								minDistance=distance	#找到更合适的
								selectedIndex=index
							elif distance<=0 or distance<minDistance:
								minDistance=distance	#找到更合适的
								selectedIndex=index
							else:
								pass						
					
					appName=allAppName[selectedIndex]
						
				if selectedIndex<0:
					continue
				if tt[1]=='1':
					isOutFlow=True
				else:
					isOutFlow=False
				if lasttimestamp==0:
					lasttimestamp=pkttimestamp
				if (pkttimestamp-lasttimestamp)>FLOW_MAX_INTERVAL:
					lasttimestamp=pkttimestamp
					split_flow=split_flow+1
					payloadBytes_all[selectedIndex][split_flow]=[]
					ipBytes_all[selectedIndex][split_flow]=[]
					pktTSs_all[selectedIndex][split_flow]=[]
					in_payloadBytes_all[selectedIndex][split_flow]=[]
					in_ipBytes_all[selectedIndex][split_flow]=[]
					in_pktTSs_all[selectedIndex][split_flow]=[]
					out_payloadBytes_all[selectedIndex][split_flow]=[]
					out_ipBytes_all[selectedIndex][split_flow]=[]
					out_pktTSs_all[selectedIndex][split_flow]=[]
					encrypted_tag_all[selectedIndex][split_flow]='normal'
						
				ipBytes_all[selectedIndex][split_flow].append(int(tt[2]))
				payloadBytes_all[selectedIndex][split_flow].append(int(tt[3]))
				if isOutFlow:
					out_ipBytes_all[selectedIndex][split_flow].append(int(tt[2]))
					out_payloadBytes_all[selectedIndex][split_flow].append(int(tt[3]))
				else:
					in_ipBytes_all[selectedIndex][split_flow].append(int(tt[2]))
					in_payloadBytes_all[selectedIndex][split_flow].append(int(tt[3]))
				
				pktTSs_all[selectedIndex][split_flow].append(pkttimestamp)
				if isOutFlow:
					out_pktTSs_all[selectedIndex][split_flow].append(pkttimestamp)
				else:
					in_pktTSs_all[selectedIndex][split_flow].append(pkttimestamp)
				match=regex_ssl.match(tt[6])
				if match:
					encrypted_tag_all[selectedIndex][split_flow]='SSL'
			
			for index in range(len(allAppName)):
				appName=allAppName[index]
				created='NDPI'
				destroyed='NDPI'
				
				for split_index in pktTSs_all[index]:
					encrypted_tag=encrypted_tag_all[index][split_index]
					#不考虑方向统计
					pktTSArray=numpy.array(pktTSs_all[index][split_index])
					pktTSArray.sort()
					pktIntervals=[]
					for i in range(1,len(pktTSArray)):
						pktIntervals.append(pktTSArray[i]-pktTSArray[i-1])
					#流入方向统计t
					in_pktTSArray=numpy.array(in_pktTSs_all[index][split_index])
					in_pktTSArray.sort()
					in_pktIntervals=[]
					for i in range(1,len(in_pktTSArray)):
						in_pktIntervals.append(in_pktTSArray[i]-in_pktTSArray[i-1])
					#流出方向统计
					out_pktTSArray=numpy.array(out_pktTSs_all[index][split_index])
					out_pktTSArray.sort()
					out_pktIntervals=[]
					for i in range(1,len(out_pktTSArray)):
						out_pktIntervals.append(out_pktTSArray[i]-out_pktTSArray[i-1])
					
					#只有MIN_PKTNUM报文的流忽略
					if len(pktTSs_all[index][split_index])<MIN_PKTNUM or len(in_pktTSs_all[index][split_index])<MIN_PKTNUM or len(out_pktTSs_all[index][split_index])<MIN_PKTNUM:
						#print 'flow '+flowKey+'( '+flowKey+') split_index ['+str(split_index)+'] in pkts num:'+str(len(in_pktTSs_all[index][split_index]))+'\tout pkts num:'+str(len(out_pktTSs_all[index][split_index]))
						ff_exceptionLog.write('flow %s( %s) split_index[%s] IN pkts num:%s\tOUT pkts num:%s\n' %(flowKey,flowKey,split_index,len(in_pktTSs_all[index][split_index]),len(out_pktTSs_all[index][split_index])))
						continue
					#narray=numpy.array(L),narray.min(),narray.max(),narray.mean(),narray.sum(),narray.var(),narray.std()
					pktIntervalArray=numpy.array(pktIntervals)
					ipByteArray=numpy.array(ipBytes_all[index][split_index])
					payloadByteArray=numpy.array(payloadBytes_all[index][split_index])
					in_pktIntervalArray=numpy.array(in_pktIntervals)
					in_ipByteArray=numpy.array(in_ipBytes_all[index][split_index])
					in_payloadByteArray=numpy.array(in_payloadBytes_all[index][split_index])
					out_pktIntervalArray=numpy.array(out_pktIntervals)
					out_ipByteArray=numpy.array(out_ipBytes_all[index][split_index])
					out_payloadByteArray=numpy.array(out_payloadBytes_all[index][split_index])				
					#flowkey,总报文数,报文字节数,报文大小(最小,最大,平均,标准差),报文到达时间间隔(最小,最大,平均,标准差),流持续时间
					pktCount=len(payloadByteArray)
					totalPayloadBytes=payloadByteArray.sum()
					minPayload=payloadByteArray.min()
					maxPayload=payloadByteArray.max()
					meanPayload=payloadByteArray.mean()
					stdPayload=payloadByteArray.std()
					totalPktBytes=ipByteArray.sum()
					minPkt=ipByteArray.min()
					maxPkt=ipByteArray.max()
					meanPkt=ipByteArray.mean()
					stdPkt=ipByteArray.std()
					kurtosisPkt,skewnessPkt,standardErrorPkt=calc_kurt_skew_se(ipByteArray)
					minInterval=pktIntervalArray.min()
					maxInterval=pktIntervalArray.max()
					meanInterval=pktIntervalArray.mean()
					stdInterval=pktIntervalArray.std()
					duration=pktIntervalArray.sum()
					#流入方向统计
					in_pktCount=len(in_payloadByteArray)
					in_totalPayloadBytes=in_payloadByteArray.sum()
					in_minPayload=in_payloadByteArray.min()
					in_maxPayload=in_payloadByteArray.max()
					in_meanPayload=in_payloadByteArray.mean()
					in_stdPayload=in_payloadByteArray.std()
					in_totalPktBytes=in_ipByteArray.sum()
					in_minPkt=in_ipByteArray.min()
					in_maxPkt=in_ipByteArray.max()
					in_meanPkt=in_ipByteArray.mean()
					in_stdPkt=in_ipByteArray.std()
					in_kurtosisPkt,in_skewnessPkt,in_standardErrorPkt=calc_kurt_skew_se(in_ipByteArray)
					in_minInterval=in_pktIntervalArray.min()
					in_maxInterval=in_pktIntervalArray.max()
					in_meanInterval=in_pktIntervalArray.mean()
					in_stdInterval=in_pktIntervalArray.std()
					in_duration=in_pktIntervalArray.sum()
					#流出方向统计
					out_pktCount=len(out_payloadByteArray)
					out_totalPayloadBytes=out_payloadByteArray.sum()
					out_minPayload=out_payloadByteArray.min()
					out_maxPayload=out_payloadByteArray.max()
					out_meanPayload=out_payloadByteArray.mean()
					out_stdPayload=out_payloadByteArray.std()
					out_totalPktBytes=out_ipByteArray.sum()
					out_minPkt=out_ipByteArray.min()
					out_maxPkt=out_ipByteArray.max()
					out_meanPkt=out_ipByteArray.mean()
					out_stdPkt=out_ipByteArray.std()
					out_kurtosisPkt,out_skewnessPkt,out_standardErrorPkt=calc_kurt_skew_se(out_ipByteArray)
					out_minInterval=out_pktIntervalArray.min()
					out_maxInterval=out_pktIntervalArray.max()
					out_meanInterval=out_pktIntervalArray.mean()
					out_stdInterval=out_pktIntervalArray.std()
					out_duration=out_pktIntervalArray.sum()
					
					flowFeatureFile.write('%s,%s,%s,%s,%s,%d,%d,%d,%d,%0.5f,%0.5f,%0.5f,%0.5f,%0.5f,%s,%s,%0.5f,%0.5f,%s,%d,%d,%d,%d,%0.5f,%0.5f,%0.5f,%0.5f,%0.5f,%s,%s,%0.5f,%0.5f,%s,%d,%d,%d,%d,%0.5f,%0.5f,%0.5f,%0.5f,%0.5f,%s,%s,%0.5f,%0.5f,%s\n' %(flowKey.replace('-',','),created,destroyed,appName,encrypted_tag,pktCount,totalPktBytes,minPkt,maxPkt,meanPkt,stdPkt,kurtosisPkt,skewnessPkt,standardErrorPkt,minInterval,maxInterval,meanInterval,stdInterval,duration,in_pktCount,in_totalPktBytes,in_minPkt,in_maxPkt,in_meanPkt,in_stdPkt,in_kurtosisPkt,in_skewnessPkt,in_standardErrorPkt,in_minInterval,in_maxInterval,in_meanInterval,in_stdInterval,in_duration,out_pktCount,out_totalPktBytes,out_minPkt,out_maxPkt,out_meanPkt,out_stdPkt,out_kurtosisPkt,out_skewnessPkt,out_standardErrorPkt,out_minInterval,out_maxInterval,out_meanInterval,out_stdInterval,out_duration))
			flowFile.close()
	
		#print "process completed"	
		flowFeatureFile.close()
		ff_exceptionLog.close()

def usage():
	print 'python buildStream.py -r <root data directory> -i <deviceId> -d <dataDate>  -m <minnum> -a <tunaddr_prefix>'
	print 'buildStream.py usage:'
	print '-r, --rootDir: .pcap file root directory'
	print '-i, --deviceId: device id'
	print '-d, --dataDate: data date'
	print '-m, --min: min pkt num'
	print '-a, --addr: tunaddr_prefix'
	print '-s, --skip_pcap: skip_pcap'
	print 'example:'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -i 44cd4ccc -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -i "44cd4ccc 66aed7a1" -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -d 20160821 -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -d "20160821 20160921" -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -i 44cd4ccc -d 20160821 -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -i "44cd4ccc 66aed7a1" -d "20160821 20160921" -m 2 -a 10. -s True'
	print '\tpython buildStream.py -r /home/liuzhen/mergedata -i 44cd4ccc -d 20160821 -m 2 -a 10. -s False'
	print 'result:\tplease see directory /home/liuzhen/mergedata/flows/44cd4ccc_20160821_flow/'
	
if __name__=='__main__':
	main(sys.argv[1:])



