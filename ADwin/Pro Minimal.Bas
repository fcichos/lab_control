'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 1000
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
' Minimal communication example ADlog - ADwin Pro
'
' ADwin Pro / Pro II
'
' $Id: Pro Minimal.Bas 7790 2015-03-18 14:50:25Z andreas $
'
' (C) 2003-2015 Jäger computergesteuerte Messtechnik GmbH
'
' DATA_180, DATA_181

'##################################################

#DEFINE BUFSIZE 100000

DIM DATA_180[BUFSIZE] AS LONG AT DRAM_EXTERN ' whole-numbered multiple of values count
DIM DATA_181[200] AS LONG AT DM_LOCAL

INIT:
  
  ' Processdelay

#IF PROCESSOR = T12 THEN
  PROCESSDELAY = 100000
#ENDIF
#IF PROCESSOR = T11 THEN
  PROCESSDELAY = 30000
#ENDIF
#IF PROCESSOR = T10 THEN
  PROCESSDELAY = 4000
#ENDIF
#IF PROCESSOR = T9 THEN
  PROCESSDELAY = 4000  
#ENDIF

  
  DATA_181[1] = 1
  DATA_181[3] = BUFSIZE
  DATA_181[4] = 1
  DATA_181[5] = 0

EVENT:
  
  PAR_1 = DATA_181[1]

  DATA_180[PAR_1] = PAR_1

  INC(PAR_1)
  IF (PAR_1 > BUFSIZE) THEN PAR_1 = 1
  
  DATA_181[1] = PAR_1
