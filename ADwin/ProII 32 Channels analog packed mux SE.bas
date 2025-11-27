'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 2000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = PC-ANDREAS-7P  PC-ANDREAS-7P\Andreas
'<Header End>
'
' 8 Channels analog measurement
'
' ADwin ProII
'
' $Id: ProII 32 Channels analog packed mux SE.bas 7789 2015-03-18 14:46:57Z andreas $
'
' (C) 2003-2015 Jäger computergesteuerte Messtechnik GmbH
'
' Module: adr 1 ProII-AIN 32/18 o.ä. 
'
' DATA_180, DATA_181

'##################################################

#INCLUDE ADWINPRO_ALL.INC

' defines for easy changing 
#DEFINE D1 DATA_180
#DEFINE D2 DATA_181

#DEFINE ADR_AIN 1
#DEFINE SLEEPTIME 400

' main variables
#DEFINE WritePointer D2[1]
#DEFINE LoopCounter  D2[2]
#DEFINE BufferSize D2[3]
#DEFINE ValuesCount D2[4]
#DEFINE Flags D2[5]

#DEFINE BUFSIZE 1000000

DIM D1[BUFSIZE] AS LONG AT DRAM_EXTERN ' whole-numbered multiple of values count
DIM D2[200] AS LONG AT DM_LOCAL

DIM Value1, Value2 AS INTEGER

'##################################################
  
INIT:
  
  ' Processdelay

#IF PROCESSOR = T12 THEN    
  PROCESSDELAY = 100000
#ENDIF
#IF PROCESSOR = T11 THEN    
  PROCESSDELAY = 30000
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
  ValuesCount = 16 'D2[4]
  
  ' Bit 0 : use LoopCounter
  Flags = 1 'D2[5]
  
  ' ***********************************************
  
  P2_SE_DIFF(ADR_AIN, 0) ' single ended
  P2_SEQ_INIT(ADR_AIN, 1, 0, 0FFFFFFFFH, 125)
  P2_SEQ_START(SHIFT_LEFT(1, ADR_AIN - 1))
  
  '##################################################
  
EVENT:
  
  ' use sequence mode for automatic multiplexing and ad-conversion
  
  P2_SEQ_WAIT(ADR_AIN)
  P2_SEQ_READ_PACKED(ADR_AIN, 16, D1, WritePointer)  
  P2_SEQ_START(SHIFT_LEFT(1, ADR_AIN - 1))
  WritePointer = WritePointer + 16
      
  ' check writepointer
  
  IF (WritePointer > BUFSIZE) THEN
    
    WritePointer = 1
    INC LoopCounter
  
  ENDIF
            
  '##################################################

  
