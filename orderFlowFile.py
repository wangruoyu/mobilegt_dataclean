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
		opts, args = getopt.getopt(argv,'hf:o:',["flowDir=","overwrite_file="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	input_flowdir=""
	input_overwrite_file='False'
	if len(opts) < 1 :
		usage()
		sys.exit()
	for op, value in opts:
		if op in ("-f", "--flowDir"):			
			input_flowdir = value
			print("input_flowdir:%s" %(input_flowdir))
		elif op in("-o","--overwrite_file"):
			input_overwrite_file = value
			print("input_overwrite_file:%s" %(input_overwrite_file))
		elif op == '-h':
			usage()
			sys.exit()
			
	FLOW_DIR=input_flowdir
	OVERWRITE=input_overwrite_file
	orderFlowFile(FLOW_DIR,OVERWRITE)
	
def orderFlowFile(FLOW_DIR,OVERWRITE):
	flowFiles=os.listdir(FLOW_DIR)
	for name in flowFiles:
		commentsLine=[]
		originFileLine=[]
		originTimestamp=[]		
		orderIndex=[]
	
		fullName=os.path.join(FLOW_DIR,name)
		#print('%s' %(fullName))
		if not (os.path.isfile(fullName) and fullName.endswith('.flow')):
			continue
		flowFile=open(fullName,'r')
		for line in flowFile:
			if line.startswith('#'):
				commentsLine.append(line)
				continue
			originFileLine.append(line)
			tt=line.split('|')
			tttime=tt[4].split('.')
			pkttimestamp=time.mktime(time.strptime(tttime[0],"%Y-%m-%d %H:%M:%S"))+float('0.'+tttime[1]) #秒数表示的时间
			originTimestamp.append(pkttimestamp)
		flowFile.close()
		
		##比较特别的,在某些特定场合下相同的数字也会返回新的顺序
		##应该是因为：缺省的快速排序是一个不稳定的排序法，改成kind='mergesort'就没问题
		##	种类					速度	最坏情况	工作空间	稳定性
		##'quicksort'（快速排序）	1		O(n^2)			0		否
		##'mergesort'（归并排序）	2		O(n*log(n))		~n/2	是
		##'heapsort'（堆排序）		3		O(n*log(n))		0		否
		##譬如：
		#1.排序正常，总数目不超过50时
		#>>> ts_na3=[1,2,3,4,5,6,7,8,9,10,11,12,13,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,48,39,40,41,42,43,44,45,46,47,48,49]
		#>>> numpy.argsort(ts_na3)
		#array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 38, 48, 49], dtype=int64)
		#2.排序两个13出现对调
		#>>> ts_na3=[1,2,3,4,5,6,7,8,9,10,11,12,13,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,48,39,40,41,42,43,44,45,46,47,48,49,50]
		#>>> numpy.argsort(ts_na3)
		#array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 13, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 38, 49, 50], dtype=int64)
		#3.三个相同的14也出现位置调换
		#>>> ts_na3=[1,2,3,4,5,6,7,8,9,10,11,12,14,14,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,48,39,40,41,42,43,44,45,46,47,48,49,50]
		#>>> numpy.argsort(ts_na3)
		#array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 14, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 38, 49, 50], dtype=int64)
		
		ts_na=numpy.array(originTimestamp)
		numpy.set_printoptions(16)
		#print ts_na
		orderIndex=numpy.argsort(ts_na,kind='mergesort')
		index=0
		firstDiff=[]
		#print orderIndex
		for oi in orderIndex:
			if index==oi:
				index+=1
			else:
				firstDiff=[index,oi]
				break;
				
		outputfile=fullName
		#如果参数没有设置为覆盖原文件，怎生成新的后缀为.order的文件
		if not (OVERWRITE=='True' or OVERWRITE=='true'):
			outputfile=fullName+'.order'
		
		#判断是否排序后同排序前一致，若一致又无需生成新文件，则无需进行内容拷贝，保留源文件不动即可
		if len(firstDiff)==0 and (OVERWRITE=='True' or OVERWRITE=='true'):
			#print('%s don't need order' %(name))
			pass			
		else:
			if len(firstDiff)==0:
				#print('%s dont need adjust order but need copy' %(name))
				pass
			else:
				print('%s need adjust order:%s' %(name,firstDiff))
				
			outputflowFile=open(outputfile,'w')
			#print('%s' %(outputfile))
			for line in commentsLine:
				outputflowFile.write(line)
				#print('%s' %(line))				
			for oi in orderIndex:
				outputflowFile.write(originFileLine[oi])
				#print('%s' %(originFileLine[oi]))				
			outputflowFile.close()
	
def usage():
	print 'python orderFlowFile.py -f <flow directory> -r <retain file>'
	print 'orderFlowFile.py usage:'
	print '-f, --flowDir: .flow file directory'
	print '-o, --overwritefile: overwrite file'
	print 'example:'
	print '\tpython orderFlowFile.py -f /home/liuzhen/mergedata/flows/44cd4ccc_20160629_flow -o True'
	print '\tpython orderFlowFile.py -f D:\\Downloads\\data\\flows\\44cd4ccc_20160629_flow -o False'
	print 'result:\tplease see flow file directory'
	
if __name__=='__main__':
	main(sys.argv[1:])