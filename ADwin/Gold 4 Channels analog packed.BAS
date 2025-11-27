'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 4000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = No
' Info_Last_Save                 = VWWARE-XP-AP  VWWARE-XP-AP\Testuser
'<Header End>
'
' 4 Channels analog measurement
'
' ADwin Gold (12/14 Bit A/D-Wandler)
'
' $Id: Gold 4 Channels analog packed.BAS 5655 2011-06-16 13:00:20Z andreas $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
'
' DATA_180, DATA_181

'##################################################

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

#DEFINE SLEEPTIME 25 ' 14 Bit Multiplexing

' main variables
#DEFINE WritePointer D2[1]
#DEFINE LoopCounter	D2[2]
#DEFINE BufferSize D2[3]
#DEFINE ValuesCount D2[4]
#DEFINE Flags D2[5]

#DEFINE BUFSIZE 1000000 ' whole-numbered multiple of values count

DIM D1[BUFSIZE] AS LONG AT DRAM_EXTERN
DIM D2[200] AS LONG AT DM_LOCAL

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
  ValuesCount = 2 'D2[4]

  ' Bit 0 : use LoopCounter
  Flags = 1 'D2[5]	
		
  ' ***********************************************
		
  SET_MUX(000000b) ' MUX channel 1 / 2
  SLEEP(SLEEPTIME)
	
  '##################################################
	
EVENT:
  
  ' read channels 1 - 4
	
  START_CONV(11000b)

  SET_MUX(001001b) ' MUX channel 3 / 4
  SLEEP(SLEEPTIME)
	
  WAIT_EOC(11000b)

  D1[WritePointer] = READADC12(1) + SHIFT_LEFT(READADC12(2),16) ' channel 1 / 2
  INC WritePointer
	
  START_CONV(11000b) ' MUX channel 1 / 2

  SET_MUX(000000b)
  'SLEEP(SLEEPTIME)
	
  WAIT_EOC(11000b)

  D1[WritePointer] = READADC12(1) + SHIFT_LEFT(READADC12(2),16) ' channel 3 / 4
  INC WritePointer
	
  ' check writepointer
	 
  IF (WritePointer > BUFSIZE) THEN
		
    WritePointer = 1
    INC LoopCounter
  
  ENDIF
										
  '##################################################
	
