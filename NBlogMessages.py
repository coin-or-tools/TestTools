#! /usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import time
import os
import NBcommandline

execfile('NBuserParametersDefault.py')
execfile(NBcommandline.getParameterFile())

LOG_MESSAGES=''
FULL_LOG_MESSAGES=''
logfile=''

def clearMessages():
  global LOG_MESSAGES
  global FULL_LOG_MESSAGES
  FULL_LOG_MESSAGES+=LOG_MESSAGES
  LOG_MESSAGES=''

def getMessages():
  global LOG_MESSAGES
  return LOG_MESSAGES


def getAllMessages():
  global LOG_MESSAGES
  global FULL_LOG_MESSAGES
  retVal = FULL_LOG_MESSAGES+LOG_MESSAGES
  return retVal

def openLogFile():
  global logfile
  logfile=open(os.path.join(NIGHTLY_BUILD_ROOT_DIR,LOGFILE), 'a')
    
def closeLogFile():
  global logfile
  logfile.close()

#------------------------------------------------------------------------
# Function to write log messages
#------------------------------------------------------------------------
def writeMessage( msg ) :
  global LOG_MESSAGES
  logMsg = time.strftime("%d %b %H:%M:%S: ")
#  logMsg = time.ctime(time.time())+': '
  logMsg += msg
  LOG_MESSAGES+=logMsg+'\n'
  if LOGPRINT :
    print logMsg
  if len(LOGFILE) > 0 and not LOGFILE.isspace() :
    global logfile
    logfile.write(logMsg+'\n')
    logfile.flush()
