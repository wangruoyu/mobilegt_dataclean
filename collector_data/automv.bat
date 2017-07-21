@REM bat 批处理－取年、月、日、时、分、秒、毫秒 
@REM 取年份：echo %date:~0,4% 
@REM 取月份：echo %date:~5,2% 
@REM 取日期：echo %date:~8,2% 
@REM 取星期：echo %date:~10,6% 
@REM 取小时：echo %time:~0,2% 
@REM 取分钟：echo %time:~3,2% 
@REM 取秒：echo %time:~6,2% 
@REM 取毫秒：echo %time:~9,2%

@REM 用set 设置一个数值 
@REM set times=10 我们可以用来进行循环次数所用。然后用
@REM echo %times%  输出数值
@REM 然后用写for循环：
@REM FOR /l %%i in (1,1,%times%) do (
@REM echo %%i%
@REM )
@REM /L表示循环1次加上N，N由IN (0,1,%times%)中的第二个数字决定，此处为加上1
@REM %%i IN (1,1,%times%)表示从1开始，每次加1，直到10

@echo start auto mv files...
@echo =========================
@echo off & setlocal enableDelayedExpansion

@set SRCDIR=D:\scutwlan_data
@set DSTDIR=H:\scutwlan_data
@echo SRC:!SRCDIR!
@echo DST:!DSTDIR!
@REM @set times=10
@REM @echo 重复 %times% 次
@REM FOR /L %%i IN (1,1,%times%) do (

:LOOP
	@set year=!date:~0,4!
	@REM @set year=!date:~2,2!
	@set month=!date:~5,2!
	@set day=!date:~8,2!

	FOR /R %SRCDIR% %%s IN (*.pcap) DO (
		
		@set cur_hour=!time:~0,2!
		@REM @set cur_min1=%time:~3,1%
		@set cur_min=!time:~3,2!
		@REM @set /a precur_min=%cur_min%-1
		@REM @set cur_sec=!time:~6,2!

		@set cur_ymdh=!year!!month!!day!!cur_hour!
		@REM @echo cur_ymdh:!cur_ymdh!
		@REM @set cur_hms=!cur_hour!!cur_min!!cur_sec!
		
		@REM 文件名样例:D:\scutwlan_data\1_00005_20160107151918.pcap
		@REM 文件名样例:01234567890123456789012345678901234567890123
		@REM 文件名样例:00000000001111111111222222222233333333334444
		@REM @echo %%s
		@set name=%%s
		@REM @set ymdh_name=!name:~25,14!
		@set ymdh_name=!name:~25,10!
		@set min_name=!name:~35,2!
		@REM @echo name:!name!
		@REM @echo ymdh_name:!ymdh_name!
		@REM @set /a v=!cur_ymdh!-!ymdh_name!
		@REM @echo v=!v!
		@set NEEDMV=0
		IF !cur_ymdh! GEQ !ymdh_name! (
			IF !cur_ymdh! GTR !ymdh_name! (
				@set NEEDMV=1
			) ELSE (
				@set cur_min1=!cur_min:~0,1!
				@set /a cur_min2=!cur_min:~1,1!-1
				@REM @echo !cur_min2!
				@set min_name1=!min_name:~0,1!
				@set min_name2=!min_name:~1,1!
				IF !cur_min1! GTR !min_name1! (
					@set NEEDMV=1
				) ELSE (
					IF !cur_min1! EQU !min_name1! (
						IF !cur_min2! GTR !min_name2! @set NEEDMV=1
					)
				)
			)
		)
		IF !NEEDMV! GTR 0 (
			IF not exist !DSTDIR!\!ymdh_name!\ (
				@REM @echo need mkdir !DSTDIR!\!ymdh_name!
				mkdir !DSTDIR!\!ymdh_name!
			)
			@echo need move %%s !DSTDIR!\!ymdh_name!\ >> process.log
			move %%s !DSTDIR!\!ymdh_name!\
		) ELSE (
			@REM @echo don't need mv file %%s
		)
	)
	
@REM 暂停N秒
	@set N=60
	@REM @echo 处理完毕，稍后!N!秒再次检查文件目录!SRCDIR!
	@ping 0.0.0.0 -n %N% > nul
@REM timeout %N%
	GOTO loop

@REM )

@echo on

