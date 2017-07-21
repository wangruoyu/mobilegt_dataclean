#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, getopt
import binascii
import os
import time
import datetime
import re

def usage():
	print 'python statAppGraphlet.py -r <root data directory> -o <result directory> -i <interval> -d <delimiter> -n <need_createdTime>'
	print 'statAppGraphlet.py usage:'
	print '-r, --rootDir: .flow & flow.feature file root directory'
	print '-o, --outputDir: output root directory'
	print '-i, --interval: interval second'
	print '-d, --delimiter: \\t or , or :'
	print '-n, --need_createdTime: True or False'
	print "all output field:\n"
	#print '#appName\t#createdTime\t#n1\t#n2\t#n3\t#n4\t#n5\t#o12<o-1>\t#o21<o-2>\t#o23<o-3>\t#o32<o-4>\t#o34<o-5>\t#o43<o-6>\t#o45<o-7>\t#o54<o-8>\t#u12<u-1>\t#u21<u-2>\t#u23<u-3>\t#u32<u-4>\t#u34<u-5>\t#u43<u-6>\t#u45<u-7>\t#u54<u-8>\t#alpha12<a-1>\t#alpha21<a-2>\t#alpha23<a-3>\t#alpha32<a-4>\t#alpha34<a-5>\t#alpha43<a-6>\t#alpha45<a-7>\t#alpha54<a-8>\t#beta21<b-1>\t#beta23<b-2>\t#beta32<b-3>\t#beta34<b-4>\t#beta43<b-5>\t#beta45<b-6>\t#destroyedList\n'
	print 'example:'
	print '\tpython statAppGraphlet.py -r D:\\MobileGT\\data_clean -o D:\\MobileGT\\data_output'
	print '\tpython statAppGraphlet.py -r D:\\MobileGT\\data_new_clean -o D:\\MobileGT\\data_output -i 60'
	print '\tpython statAppGraphlet.py -r D:\\MobileGT\\data_new_clean -o D:\\MobileGT\\data_output -i 180 -d ,'
	print '\tpython statAppGraphlet.py -r D:\\MobileGT\\data_new_clean -o D:\\MobileGT\\data_output -i 180 -d , -n True'
	print 'result:\tplease see {FLOW_FILE_PREFIX}_statGraphletResult.graphlet in output root directory'
	
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
	opts, args = getopt.getopt(sys.argv[1:],'hr:o:i:d:n',["rootDir=","outputDir=","interval=","delimiter=","need_createdTime="])
except getopt.GetoptError:
	usage()
	sys.exit(2)
delimiter='\t'
need_createdTime=False;
interval=180
if len(opts) < 2 :
	usage()
	sys.exit()
for op, value in opts:
	if op in ("-r", "--rootDir"):			
		input_dir = value
		print("input_dir:["+input_dir+"]")
	if op in ("-o", "--outputDir"):			
		output_dir = value
		print("output_dir:["+output_dir+"]")
	elif op in("-i","--interval"):
		interval=eval(value)
		print("interval:["+str(interval)+"]")
	elif op in("-d","--delimiter"):
		delimiter=value
		print("delimiter:["+delimiter+"]")
	elif op in("-n","--need_createdTime"):
		need_createdTime=value
		print("need_createdTime:["+need_createdTime+"]")
	elif op == '-h':
		usage()
		sys.exit()
	
#找出WORKING_DIR目录及子目下所有名为flow.feature文件，存放到flowFeatureFileNames变量中
#flowFeatureFileNames={'/home/ubuntu/data/train/day02/44cd4ccc_20160630_flow/flow.feature','/home/ubuntu/data/train/day01/44cd4ccc_20160627_flow/flow.feature'}
#WORKING_DIR='/home/ubuntu/data/train/'
WORKING_DIR=input_dir
flowFeatureFileNames=find_file_by_pattern('flow.feature',WORKING_DIR)
print flowFeatureFileNames

for name in flowFeatureFileNames:
	#fullName=os.path.join(WORKING_DIR,name)
	#flowFeatureFile=open(fullName,'r')
	flowFeatureFile=open(name,'r')
	flowDirName=os.path.dirname(name)
	outputPrefix=os.path.basename(flowDirName)
	#statGraphletResult=open(flowDirName+"\\statGraphletResult.graphlet",'w')
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	statGraphletResult=open(output_dir+os.path.sep+outputPrefix+"_statGraphletResult.graphlet",'w')
	##flowkey(设备IP<1>,设备端口<2>,协议<3>,对端IP<4>,对端端口<5>),created<6>,destroyed<7>,appName<8>,encrypted_tag<9>,总报文数<10-1>,字节数<11-2>,报文大小(最小<12-3>,最大<13-4>,平均<14-5>,标准差<15-6>),报文到达时间间隔(最小<16-7>,最大<17-8>,平均<18-9>,标准差<19-10>),流持续时间<20-11>,IN总报文数<21-1>,IN字节数<22-2>,IN报文大小(最小<23-3>,最大<24-4>,平均<25-5>,标准差<26-6>),IN报文到达时间间隔(最小<27-7>,最大<28-8>,平均<29-9>,标准差<30-10>),IN流持续时间<31-11>,OUT总报文数<32-1>,OUT字节数<33-2>,OUT报文大小(最小<304-3>,最大<35-4>,平均<36-5>,标准差<37-6>),OUT报文到达时间间隔(最小<38-7>,最大<39-8>,平均<40-9>,标准差<41-10>),OUT流持续时间<42-11>
	#10.77.2.2,37361,TCP,118.178.213.227,80,1485490563,1485490628,贪吃蛇大作战,normal,17,1140,0,319,67.0588235294,121.270466114,5.60283660889e-05,741.28884697,50.8973291814,178.906414354,814.357266903,6,277,0,277,46.1666666667,103.231804961,0.0318269729614,63.6978919506,13.6990443707,25.0328236684,68.4952218533,11,863,0,319,78.4545454545,128.637166718,5.60283660889e-05,741.28884697,81.4357266903,220.75237443,814.357266903
	appNameList=set()
	
	#graphlets:{created:graphlet}			即字典: created---graphlet
	#	graphlet=graphlets[created]
	#graphlet:{index:graphData}	即字典: index---graphData
	#	graphData=graphlet[index]=graphlets[created][index]
	#	index 0:grapletNode0=set()
	#	index 1:grapletNode1=set()
	#	index 2:grapletNode2=set()	
	#	index 3:grapletNode3=set()
	#	index 4:grapletNode4=set()
	#	index 5:grapletEdge0=set()
	#	index 6:grapletEdge1=set()
	#	index 7:grapletEdge2=set()
	#	index 8:grapletEdge3=set()
	#	index 9:destroyedList=[]
	
	print("process file:"+name)
	graphlets={}
	#appNames={}		#appNames={created:appName},如果appName可能有多个则用|线分割
	appName_flowNums={}		#flowNums={created:appFlowNum}	appFlowNum={appName:flowNum}
	appName_pktNums={}		#pktNums={created:appPktNum}	appPktNum={appName:pktNum}
	appName_byteNums={}		#byteNums={created:appByteNum}	appByteNum={appName:byteNum}
	for line in flowFeatureFile:
		#解析每条流，按graphletKey分组构建graphlet，每个graphlet包含的流在{interval}/60分钟内(即第一条流的created时间与最后一条流的created时间差不超过{interval}秒. <流不是按创建时间的从小到大的顺序?该问题应如何处理?>)

		#graphlet：deviceIP-protocol-devicePort-internetPort-internetIP
		l1=line.split(',')
		if line.startswith('#') or len(l1)!=42:
			#print line
			continue		
		created=l1[5].strip()
		destroyed=l1[6].strip()
		appName=l1[7].strip()
		deviceIP=l1[0].strip()
		protocol=l1[2].strip()
		devicePort=l1[1].strip()
		internetPort=l1[4].strip()
		internetIP=l1[3].strip()
		
		foundcreated='-1'
		for createdtime in graphlets:
			if abs(eval(created)-eval(createdtime))<=interval:
				foundcreated=createdtime
				break
		if eval(foundcreated)<0:
			foundcreated=created
			graphlets[foundcreated]={}			
			graphlets[foundcreated][0]=set()	#grapletNode0
			graphlets[foundcreated][1]=set()	#grapletNode1
			graphlets[foundcreated][2]=set()	#grapletNode2
			graphlets[foundcreated][3]=set()	#grapletNode3
			graphlets[foundcreated][4]=set()	#grapletNode4
			graphlets[foundcreated][5]=set()	#grapletEdge0
			graphlets[foundcreated][6]=set()	#grapletEdge1
			graphlets[foundcreated][7]=set()	#grapletEdge2
			graphlets[foundcreated][8]=set()	#grapletEdge3
			graphlets[foundcreated][9]=[]		#destroyed
			#if appName=='贪吃蛇大作战':
			#	print foundcreated+':'+destroyed
		graphlets[foundcreated][0].add(deviceIP)
		graphlets[foundcreated][1].add(protocol)
		graphlets[foundcreated][2].add(devicePort)
		graphlets[foundcreated][3].add(internetPort)
		graphlets[foundcreated][4].add(internetIP)
		graphlets[foundcreated][5].add(deviceIP+'-'+protocol)
		graphlets[foundcreated][6].add(protocol+'-'+devicePort)
		graphlets[foundcreated][7].add(devicePort+'-'+internetPort)
		graphlets[foundcreated][8].add(internetPort+'-'+internetIP)
		graphlets[foundcreated][9].append(destroyed)
		#if appName=='贪吃蛇大作战':
		#	print '==========='+str(appName_graphlets['贪吃蛇大作战'][foundcreated][9])
		
		#添加流数目,报文数,字节数统计
		flowNum=1			#流数目
		pktNum=eval(l1[9])	#本条流的报文数
		byteNum=eval(l1[10])#本条流的字节数
		
		if foundcreated not in appName_flowNums:
			#appNames[foundcreated]=set()
			appName_flowNums[foundcreated]={}
			appName_pktNums[foundcreated]={}
			appName_byteNums[foundcreated]={}
			
		#appNames[foundcreated].add(appName)
		
		if appName in appName_flowNums[foundcreated]:
			flowNum+=appName_flowNums[foundcreated][appName]
			pktNum+=appName_pktNums[foundcreated][appName]
			byteNum+=appName_byteNums[foundcreated][appName]
		
		appName_flowNums[foundcreated][appName]=flowNum
		appName_pktNums[foundcreated][appName]=pktNum
		appName_byteNums[foundcreated][appName]=byteNum
		
	print("preprocess file completed!")
	print("compute feature...")
	statGraphletResult.write('#n1\t#n2\t#n3\t#n4\t#n5\t#o12<o-1>\t#o21<o-2>\t#o23<o-3>\t#o32<o-4>\t#o34<o-5>\t#o43<o-6>\t#o45<o-7>\t#o54<o-8>\t#u12<u-1>\t#u21<u-2>\t#u23<u-3>\t#u32<u-4>\t#u34<u-5>\t#u43<u-6>\t#u45<u-7>\t#u54<u-8>\t#alpha12<a-1>\t#alpha21<a-2>\t#alpha23<a-3>\t#alpha32<a-4>\t#alpha34<a-5>\t#alpha43<a-6>\t#alpha45<a-7>\t#alpha54<a-8>\t#beta21<b-1>\t#beta23<b-2>\t#beta32<b-3>\t#beta34<b-4>\t#beta43<b-5>\t#beta45<b-6>\t#flow\t#pkt\t#byte\t#appName-flowNum-pktNum-byteNum|appName-flowNum-pktNum-byteNum...')
	if(not need_createdTime):
		statGraphletResult.write('\t#createdTime\t#destroyedList')
	statGraphletResult.write('\n')
	
	#statGraphletResult.write(graphletKey)
	for createdTime in graphlets:
		grapletNode0=graphlets[createdTime][0]
		grapletNode1=graphlets[createdTime][1]
		grapletNode2=graphlets[createdTime][2]
		grapletNode3=graphlets[createdTime][3]
		grapletNode4=graphlets[createdTime][4]
		grapletEdge0=graphlets[createdTime][5]
		grapletEdge1=graphlets[createdTime][6]
		grapletEdge2=graphlets[createdTime][7]
		grapletEdge3=graphlets[createdTime][8]
		destroyedList=graphlets[createdTime][9]
		#feature(5):n1,n2,n3,n4,n5
		statGraphletResult.write(str(len(grapletNode0))+delimiter+str(len(grapletNode1))+delimiter+str(len(grapletNode2))+delimiter+str(len(grapletNode3))+delimiter+str(len(grapletNode4)))
		#feature(8):o12,o21,o23,o32,o34,o43,o45,o54
		o=[0,0,0,0,0,0,0,0]
		for node in grapletNode0:
			edgeNum=0
			for edge in grapletEdge0:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum==1:
				o[0]+=1
		for node in grapletNode1:
			edgeNum=0
			for edge in grapletEdge0:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum==1:
				o[1]+=1
		for node in grapletNode1:
			edgeNum=0
			for edge in grapletEdge1:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum==1:
				o[2]+=1
		for node in grapletNode2:
			edgeNum=0
			for edge in grapletEdge1:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum==1:
				o[3]+=1
		for node in grapletNode2:
			edgeNum=0
			for edge in grapletEdge2:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum==1:
				o[4]+=1
		for node in grapletNode3:
			edgeNum=0
			for edge in grapletEdge2:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum==1:
				o[5]+=1
		for node in grapletNode3:
			edgeNum=0
			for edge in grapletEdge3:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum==1:
				o[6]+=1
		for node in grapletNode4:
			edgeNum=0
			for edge in grapletEdge3:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum==1:
				o[7]+=1
		#存储只有一个边的节点数属性			
		for i in range(8):
			statGraphletResult.write(delimiter+str(o[i]))
				
		#feature(8):u12,u21,u23,u32,u34,u43,u45,u54
		#平均度数（边数除以节点数）
		u=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		u[0]=len(grapletEdge0)*1.0/len(grapletNode0)
		u[1]=len(grapletEdge0)*1.0/len(grapletNode1)
		u[2]=len(grapletEdge1)*1.0/len(grapletNode1)
		u[3]=len(grapletEdge1)*1.0/len(grapletNode2)
		u[4]=len(grapletEdge2)*1.0/len(grapletNode2)
		u[5]=len(grapletEdge2)*1.0/len(grapletNode3)
		u[6]=len(grapletEdge3)*1.0/len(grapletNode3)
		u[7]=len(grapletEdge3)*1.0/len(grapletNode4)
		for i in range(8):
			statGraphletResult.write(delimiter+'%.3f' %u[i])
			
		#feature(8):alpha12,alpha21,alpha23,alpha32,alpha34,alpha43,alpha45,alpha54
		alpha=[0,0,0,0,0,0,0,0]
		#feature(6):beta21,beta23,beta32,beta34,beta43,beta45
		beta=[0,0,0,0,0,0]
		for node in grapletNode0:
			edgeNum=0
			for edge in grapletEdge0:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum>alpha[0]:
				alpha[0]=edgeNum
		
		for node in grapletNode1:
			edgeNum=0
			for edge in grapletEdge0:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum>alpha[1]:					
				alpha[1]=edgeNum
				maxnode=node
		#计算最大度数的节点的反向度数beta21#graphlet：  [1]   -----  [2]   -----   [3]    -----    [4]     -----   [5]    
		#计算最大度数的节点的反向度数beta21#graphlet：deviceIP--0--protocol--1--devicePort--2--internetPort--3--internetIP
		for edge in grapletEdge1:
			tt=edge.split('-')
			if tt[0]==maxnode:
				beta[0]+=1
			
		for node in grapletNode1:
			edgeNum=0
			for edge in grapletEdge1:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum>alpha[2]:
				alpha[2]=edgeNum
				maxnode=node
		#计算最大度数的节点的反向度数beta23#graphlet：  [1]   -----  [2]   -----   [3]    -----    [4]     -----   [5]    
		#计算最大度数的节点的反向度数beta23#graphlet：deviceIP--0--protocol--1--devicePort--2--internetPort--3--internetIP
		for edge in grapletEdge0:
			tt=edge.split('-')
			if tt[1]==maxnode:
				beta[1]+=1
			
		for node in grapletNode2:
			edgeNum=0
			for edge in grapletEdge1:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum>alpha[3]:
				alpha[3]=edgeNum
				maxnode=node
		#计算最大度数的节点的反向度数beta32#graphlet：  [1]   -----  [2]   -----   [3]    -----    [4]     -----   [5]    
		#计算最大度数的节点的反向度数beta32#graphlet：deviceIP--0--protocol--1--devicePort--2--internetPort--3--internetIP
		for edge in grapletEdge2:
			tt=edge.split('-')
			if tt[0]==maxnode:
				beta[2]+=1
		
		for node in grapletNode2:
			edgeNum=0
			for edge in grapletEdge2:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum>alpha[4]:
				alpha[4]=edgeNum
				maxnode=node
		#计算最大度数的节点的反向度数beta34#graphlet：  [1]   -----  [2]   -----   [3]    -----    [4]     -----   [5]    
		#计算最大度数的节点的反向度数beta34#graphlet：deviceIP--0--protocol--1--devicePort--2--internetPort--3--internetIP
		for edge in grapletEdge1:
			tt=edge.split('-')
			if tt[1]==maxnode:
				beta[3]+=1
		
		for node in grapletNode3:
			edgeNum=0
			for edge in grapletEdge2:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum>alpha[5]:
				alpha[5]=edgeNum
				maxnode=node
		#计算最大度数的节点的反向度数beta43#graphlet：  [1]   -----  [2]   -----   [3]    -----    [4]     -----   [5]    
		#计算最大度数的节点的反向度数beta43#graphlet：deviceIP--0--protocol--1--devicePort--2--internetPort--3--internetIP
		for edge in grapletEdge3:
			tt=edge.split('-')
			if tt[0]==maxnode:
				beta[4]+=1
		
		for node in grapletNode3:
			edgeNum=0
			for edge in grapletEdge3:
				tt=edge.split('-')
				if tt[0]==node:
					edgeNum+=1
			if edgeNum>alpha[6]:
				alpha[6]=edgeNum
				maxnode=node
		#计算最大度数的节点的反向度数beta45#graphlet：  [1]   -----  [2]   -----   [3]    -----    [4]     -----   [5]    
		#计算最大度数的节点的反向度数beta45#graphlet：deviceIP--0--protocol--1--devicePort--2--internetPort--3--internetIP
		for edge in grapletEdge2:
			tt=edge.split('-')
			if tt[1]==maxnode:
				beta[5]+=1
		
		for node in grapletNode4:
			edgeNum=0
			for edge in grapletEdge3:
				tt=edge.split('-')
				if tt[1]==node:
					edgeNum+=1
			if edgeNum>alpha[7]:
				alpha[7]=edgeNum
		
		for i in range(8):
			statGraphletResult.write(delimiter+str(alpha[i]))			
		for i in range(6):
			statGraphletResult.write(delimiter+str(beta[i]))
		totalFlowNum=0
		totalPktNum=0
		totalByteNum=0
		for appName in appName_flowNums[createdTime]:
			totalFlowNum+=appName_flowNums[createdTime][appName]
			totalPktNum+=appName_pktNums[createdTime][appName]
			totalByteNum+=appName_byteNums[createdTime][appName]
		statGraphletResult.write(delimiter+str(totalFlowNum)+delimiter+str(totalPktNum)+delimiter+str(totalByteNum))
		
		statGraphletResult.write(delimiter)
		first=True
		for appName,fn in sorted(appName_flowNums[createdTime].iteritems(),key=lambda d:d[1],reverse=True):
			if first:
				first=False
				statGraphletResult.write(appName+delimiter)
			else:
				statGraphletResult.write('|')
			statGraphletResult.write(appName+'-'+str(appName_flowNums[createdTime][appName])+'-'+str(appName_pktNums[createdTime][appName])+'-'+str(appName_byteNums[createdTime][appName]))

		if need_createdTime:
			statGraphletResult.write(delimiter+createdTime+delimiter+str(len(destroyedList))+':'+str(destroyedList))
		statGraphletResult.write('\n')
		#end one graphlet
	#end all graphlets
	statGraphletResult.close()
	print("compute feature completed!")