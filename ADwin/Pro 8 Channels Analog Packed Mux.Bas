'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 2000
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
' 8 Channels analog measurement
'
' ADwin Pro
'
' $Id: Pro 8 Channels Analog Packed Mux.Bas 5655 2011-06-16 13:00:20Z andreas $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
' Module: AD 1 AIN 8/16 o.ä. 
'
' DATA_180, DATA_181

'##################################################

#INCLUDE ADWINPRO_ALL.INC

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

#DEFINE ADR_AIN 1
#DEFINE SLEEPTIME 50

' main variables
#DEFINE WritePointer D2[1]
#DEFINE LoopCounter	D2[2]
#DEFINE BufferSize D2[3]
#DEFINE ValuesCount D2[4]
#DEFINE Flags D2[5]

#DEFINE BUFSIZE 1000000

DIM D1[BUFSIZE] AS LONG AT DRAM_EXTERN ' whole-numbered multiple of values count
DIM D2[200] AS LONG AT DM_LOCAL

DIM Value1, Value2 AS INTEGER

'##################################################
	
SUB SLEEPX(Value)
  
#IF PROCESSOR = T11 THEN
  CPU_SLEEP(Value)
#ELSE
  SLEEP(Value)	
#ENDIF
    
ENDSUB
	
'##################################################

INIT:
	
  ' Processdelay

#IF PROCESSOR = T11 THEN
  PROCESSDELAY = 30000
#ELSE
  PROCESSDELAY = 4000	
#ENDIF
	
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
  ValuesCount = 4 'D2[4]
	
  ' Bit 0 : use LoopCounter
  Flags = 1 'D2[5]
	
  ' ***********************************************
	
  SE_DIFF(ADR_AIN, 1) ' differential mode
	
  SET_MUX(ADR_AIN, 000b) 'channel 1
  SLEEPX(SLEEPTIME)
		
  '##################################################
	
EVENT:
	
  ' read channels 1 - 8
  START_CONV(ADR_AIN)
	
  SET_MUX(ADR_AIN, 001b) ' MUX channel 2
  SLEEPX(SLEEPTIME)
	 
  WAIT_EOC(ADR_AIN)
  Value1 = READADC(ADR_AIN) ' channel 1
	
  START_CONV(ADR_AIN)
		
  SET_MUX(ADR_AIN, 010b) ' MUX channel 3
  SLEEPX(SLEEPTIME)		
 
  WAIT_EOC(ADR_AIN)
  Value2 = READADC(ADR_AIN) ' channel 2 

  START_CONV(ADR_AIN)

  D1[WritePointer] = Value1 + SHIFT_LEFT(Value2,16)
  INC WritePointer

  SET_MUX(ADR_AIN, 011b) ' MUX channel 4
  SLEEPX(SLEEPTIME)
	
  WAIT_EOC(ADR_AIN)
  Value1 = READADC(ADR_AIN) ' channel 3

  START_CONV(ADR_AIN)

  SET_MUX(ADR_AIN, 100b) ' MUX channel 5
  SLEEPX(SLEEPTIME)
		
  WAIT_EOC(ADR_AIN)
  Value2 = READADC(ADR_AIN) ' channel 4

  START_CONV(ADR_AIN)

  D1[WritePointer] = Value1 + SHIFT_LEFT(Value2,16)
  INC WritePointer

  SET_MUX(ADR_AIN, 101b) ' MUX channel 6
  SLEEPX(SLEEPTIME) 
		
  WAIT_EOC(ADR_AIN)
  Value1 = READADC(ADR_AIN) ' channel 5
	
  START_CONV(ADR_AIN)
	
  SET_MUX(ADR_AIN, 110b) ' MUX channel 7
  SLEEPX(SLEEPTIME)
	
  WAIT_EOC(ADR_AIN)
  Value2 = READADC(ADR_AIN) ' channel 6
	
  START_CONV(ADR_AIN)
	
  D1[WritePointer] = Value1 + SHIFT_LEFT(Value2,16)
  INC WritePointer

  SET_MUX(ADR_AIN, 111b) ' MUX channel 8
  SLEEPX(SLEEPTIME)
		
  WAIT_EOC(ADR_AIN)
  Value1 = READADC(ADR_AIN) ' channel 7

  START_CONV(ADR_AIN)

  SET_MUX(ADR_AIN, 000b) ' MUX channel 1
  'SLEEPX(SLEEPTIME)
	
  WAIT_EOC(ADR_AIN)
  Value2 = READADC(ADR_AIN) ' channel 8
	
  D1[WritePointer] = Value1 + SHIFT_LEFT(Value2,16)
  INC WritePointer
	
  ' check writepointer
	
  IF (WritePointer > BUFSIZE) THEN
		
    WritePointer = 1
    INC LoopCounter
	
  ENDIF
						
  '##################################################

	
