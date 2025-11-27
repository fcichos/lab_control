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
' 1 Channel analog measurement
'
' ADwin Pro
'
' $Id: Pro 1 Channel Analog.Bas 5655 2011-06-16 13:00:20Z andreas $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
' Module: AD 1 F-AIN 4/16 o.ä. 
'
' DATA_180, DATA_181

'##################################################

#INCLUDE ADWINPRO_ALL.INC

#DEFINE ADR_AIN 1

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

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
  ValuesCount = 1 'D2[4]
	
  ' Bit 0 : use LoopCounter
  Flags = 1 'D2[5]	
	
  ' ***********************************************

  START_CONVF(ADR_AIN, 11b)

  '##################################################
	
EVENT:
	
  WAIT_EOCF(ADR_AIN, 11b)
	
  D1[WritePointer] = READADCF(ADR_AIN, 1)
  INC WritePointer
	
  START_CONVF(ADR_AIN, 11b)
	
  ' check writepointer
	
  IF (WritePointer > BUFSIZE) THEN
		
    WritePointer = 1
    INC LoopCounter
	
  ENDIF
						
  '##################################################
	
