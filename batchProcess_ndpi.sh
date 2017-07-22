#/bin/bash

#/usr/local/bin/ndpiReader -i 1_00003_20160108145942.pcap -v 2 > ../ndpi/201608145942.dpi
#变量pcap数据目录下的所有pcap文件,调用ndpiReader处理,结果存储到ndpi目录的.dpi文件中

if [ $# -ne 1 ]
then
	echo "!!!Please input pcapdata directory!!!"
	echo "example:"
	echo $0 /home/liuzhen/pcapdata
	echo "The shell script argument is pcapdataroot directory name"
	exit 0
fi
PCAP_DATA_DIR=$1
if [ ! -d "$PCAP_DATA_DIR" ]
then
	echo directory $PCAP_DATA_DIR not exist! please check pcap data directory.
	exit 0
fi
cd $PCAP_DATA_DIR
NDPI_DATA_DIR=../ndpi
if [ ! -d "$NDPI_DATA_DIR" ]
then
	mkdir $NDPI_DATA_DIR
fi
allPcapFile=`ls *.pcap`
totalNum=`echo $allPcapFile | wc -w`
LOGFILE=`date +%s`_batchProcess.log
echo "Total: $totalNum "
echo "$allPcapFile"
echo "begin process one by one"
echo "Total: $totalNum" > $LOGFILE
echo "$allPcapFile" >> $LOGFILE
echo "begin process one by one" >> $LOGFILE


NDPI_CMD=/usr/local/bin/ndpiReader
#/usr/local/bin/ndpiReader -i 1_00003_20160108145942.pcap -v 2 > ../ndpi/1_00003_20160108145942.dpi
for pcapFile in $allPcapFile
do
	ndpiFile=${pcapFile%%.pcap}
	$NDPI_CMD -i $pcapFile -v 2 > $NDPI_DATA_DIR/$ndpiFile.dpi
	#echo "$NDPI_CMD -i $pcapFile -v 2 > $NDPI_DATA_DIR/$ndpiFile.dpi"
done