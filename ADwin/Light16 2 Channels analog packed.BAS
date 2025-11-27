'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 10000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = VWWARE-XP-AP  VWWARE-XP-AP\Testuser
'<Header End>
'
' 2 Channels analog measurement
'
' ADwin Light16
'
' $Id: Light16 2 Channels analog packed.BAS 5655 2011-06-16 13:00:20Z andreas $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
'
' DATA_180, DATA_181

'##################################################

#INCLUDE ADWL16.INC

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

#DEFINE SLEEPTIME 65

' main variables
#DEFINE WritePointer D2[1]
#DEFINE LoopCounter	D2[2]
#DEFINE BufferSize D2[3]
#DEFINE ValuesCount D2[4]
#DEFINE Flags D2[5]

#DEFINE BUFSIZE 1000000 ' whole-numbered multiple of values count
	
DIM D1[BUFSIZE] AS LONG AT DRAM_EXTERN
DIM D2[200] AS LONG AT DM_LOCAL

DIM Value1, Value2 AS INTEGER

'##################################################
	
INIT:
	
  '
  ' negotiate setup
  '
	
  ' write pointer
  WritePointer = 1 'D2[1]
	
  ' buffer overleap counter
  LoopCounter = 0 'D2[2]
	
  ' buffer size
  BufferSize = BUFSIZE 'D2[3]
	
  ' values count (number of LONGs per step)
  ValuesCount = 1 'D2[4]
	
  ' Bit 0 : use LoopCounter
  Flags = 1 'D2[5]
	
  ' ***********************************************
	
  L16_MODE(1b)
  
  SET_MUX(000b) ' channel 1
  SLEEP(SLEEPTIME)
	
  '##################################################
	
EVENT:

  START_CONV(1b)

  SET_MUX(001b) ' channel 3
  SLEEP(SLEEPTIME)
  	
  WAIT_EOC(1b)
  Value1 = READADC(1) ' channel 1
	
  START_CONV(1b)	

  SET_MUX(000b) ' channel 1
  'SLEEP(SLEEPTIME)
		
  WAIT_EOC(1b)
  Value2 = READADC(1) ' channel 3 
		
  D1[WritePointer] = Value1 + SHIFT_LEFT(Value2,16)
  INC WritePointer

  ' check writepointer
	
  IF (WritePointer > BUFSIZE) THEN
		
    WritePointer = 1
    INC LoopCounter
	
  ENDIF
						
  '##################################################

	
