'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 1000
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
' Minimal communication example ADlog - ADwin Light16
'
' ADwin Light16
'
' $Id: Light16 Minimal.BAS 5655 2011-06-16 13:00:20Z andreas $
'
' (C) 2003-2011 Jäger computergesteuerte Messtechnik GmbH
'
' DATA_180, DATA_181

'##################################################

#DEFINE BUFSIZE 100000

DIM DATA_180[BUFSIZE] AS LONG AT DRAM_EXTERN
DIM DATA_181[200] AS LONG AT DM_LOCAL

INIT:
	
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
