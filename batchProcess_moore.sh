#/bin/bash
if [ $# -ne 1 ]
then
	echo "!!!Please confirm current working directory!!!"
	echo "$0 delete out/,output_*, and move output_*.arff，please confirm your current working directoryoore."
	echo "example:"
	echo $0 /mnt/hgfs/243aa171/
	echo "The shell script argument is dataroot directory name, MUST endof /, ie. CANNOT IGNORE /"
	exit 0
fi
DEVICEID_DIR=$1
allDateDir=`ls -F $DEVICEID_DIR | grep "/$"`
totalNum=`echo $allDateDir | wc -w`
LOGFILE=`date +%s`_batchProcess.log
echo "Total: $totalNum "
echo "$allDateDir"
echo "begin process one by one"
echo "Total: $totalNum" > $LOGFILE
echo "$allDateDir" >> $LOGFILE
echo "begin process one by one" >> $LOGFILE
for dateDir in $allDateDir
do
	#clean tmp data
	rm -rf out
	rm -rf output_*
	
	absDateDir=$DEVICEID_DIR$dateDir
	echo process......$absDateDir
	echo process......$absDateDir >> $LOGFILE
	find $absDateDir -name "*.pcap" -exec ls {} \; > dumpfile
	perl flowCreator.pl dumpfile
	perl attributeGenerator.pl filelist
	#
	#output_14996070743254650279_data.stats.a_b
	#1234567891234567891234567891
	#
	last_id_str_op=""
	for str_op in `ls output_*`
	do
		id_str_op=`expr substr $str_op 1 28`
		if [ "$id_str_op" != "$last_id_str_op" ]
		then
			last_id_str_op=$id_str_op
			#./arffCreator output_14996070743254650279_
			echo ./arffCreator.sh $id_str_op >> $LOGFILE
			./arffCreator.sh $id_str_op			
		fi	
	done
	
	#move result .arff file to $absDateDir 
	cp output_*.arff $absDateDir	 
done
echo "process completed!" >> $LOGFILE
