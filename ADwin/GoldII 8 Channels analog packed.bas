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
' 8 Channels analog measurement
'
' ADwin GoldII
'
' $Id: GoldII 8 Channels analog packed.bas 5655 2011-06-16 13:00:20Z andreas $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
'
' DATA_180, DATA_181

'##################################################

#INCLUDE ADWINGOLDII.INC

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

#DEFINE SLEEPTIME 200

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
  ValuesCount = 4 'D2[4]

  ' Bit 0 : use LoopCounter
  Flags = 1 'D2[5]	
		
  ' ***********************************************
		
  SEQ_MODE(1, 2)
  SEQ_MODE(2, 2)
  SEQ_SET_DELAY(1,125) 
  SEQ_SET_DELAY(2,125) 
  SEQ_SET_GAIN(1, 0)
  SEQ_SET_GAIN(2, 0)
  SEQ_SELECT(000FFh)
  SEQ_START(11b)
	
  '##################################################
	
EVENT:
	
  D1[WritePointer] = SEQ_READ(1) + SHIFT_LEFT(SEQ_READ(2),16) ' channel 1 / 2
  INC WritePointer
	
  D1[WritePointer] = SEQ_READ(3) + SHIFT_LEFT(SEQ_READ(4),16) ' channel 3 / 4
  INC WritePointer

  D1[WritePointer] = SEQ_READ(5) + SHIFT_LEFT(SEQ_READ(6),16) ' channel 5 / 6
  INC WritePointer

  D1[WritePointer] = SEQ_READ(7) + SHIFT_LEFT(SEQ_READ(8),16) ' channel 7 / 8
  INC WritePointer

  ' check writepointer

  IF (WritePointer > BUFSIZE) THEN
		
    WritePointer = 1
    INC LoopCounter
  
  ENDIF
										
  '##################################################
	
