'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 10000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = PC-JULIA  PC-JULIA\Testuser
'<Header End>
'
' 1 Channel analog measurement
'
' ADwin-X
'
' $Id: ?????? 1 Channel analog.BAS $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
'
' DATA_180, DATA_181

'##################################################

#Include ADwin-X.inc

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

' main variables
#DEFINE WritePointer D2[1]
#DEFINE LoopCounter  D2[2]
#DEFINE BufferSize D2[3]
#DEFINE ValuesCount D2[4]
#DEFINE Flags D2[5]

#DEFINE BUFSIZE 1000000 ' whole-numbered multiple of values count
  
DIM D1[BUFSIZE] AS LONG 
DIM D2[200] AS LONG 

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
      
  
  Rem start continuous conversion with ADC 1, gain 1
  Start_Conv(00000001b, 0, 2)
  
  WAIT_EOC()
  
  '##################################################
  
EVENT:

  'Par_1 = READ_ADC(1)   ' for debug only
  D1[WritePointer] = READ_ADC(1)
  
  INC WritePointer
  
  ' check writepointer
  
  IF (WritePointer > BUFSIZE) THEN
    
    WritePointer = 1
    INC LoopCounter
  
  ENDIF
            
  '##################################################    
