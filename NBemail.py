#! /usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the BuildTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import sys
from socket import gethostname 
import smtplib

#in python 2.4 some filenames started with a capital letter, while this changed in python 2.5 :-(
try :  #python 2.5 style
  from email import encoders
  from email.message import Message
  from email.generator import Generator
  from email.mime.base import MIMEBase
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText
except ImportError :  #python 2.4 style
  from email import Encoders
  from email.Message import Message
  from email.Generator import Generator
  email_firstletter_capital = True

  from email.MIMEBase import MIMEBase
  from email.MIMEMultipart import MIMEMultipart
  from email.MIMEText import MIMEText
else :
  email_firstletter_capital = False
  
from cStringIO import StringIO

from gzip import GzipFile

import NBprojectConfig
import NBlogMessages

execfile('NBuserParametersDefault.py')
execfile('NBuserParameters.py')

#------------------------------------------------------------------------
#
# This file contains the functions that deal with email
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
# Send email typically about an error.
#  project: coin project name
#  cmd: command being executed. perhaps: "svn update", "./configure", 
#       "make".
#  cmdMsgs: the messages generated by cmd.  This will typically contain
#       errors issued by cmd and additional information about the build.
#------------------------------------------------------------------------
def sendCmdMsgs(project,cmdMsgs,cmd):
  curDir = os.getcwd()

  toAddrs = [unscrambleAddress(MY_EMAIL_ADDR)]
  if SEND_MAIL_TO_PROJECT_MANAGER and NBprojectConfig.PROJECT_EMAIL_ADDRS.has_key(project) :
    scrambledEmailAddress=NBprojectConfig.PROJECT_EMAIL_ADDRS[project]
    unscrambledEmailAddress=unscrambleAddress(scrambledEmailAddress)
    toAddrs.append(unscrambledEmailAddress)

  emailSubject = "NightlyBuild on "+gethostname()+". "+sys.platform+". "+project
  if cmdMsgs.has_key('svn version') :
    emailSubject += " "+cmdMsgs['svn version']
  emailSubject+=". Problem with '" + cmd +"'"

#  emailMsg = "Subject: "+subject+"\n\n"
  emailText = "Dear "+project+" Project Manager,\n\n" \
   +"The nightly build test script reported a problem when building "+project
  if cmdMsgs.has_key('svn version') :
    emailText += " from svn version "+cmdMsgs['svn version']
  emailText += ".\nThe failing command was\n\n\t"+cmd+"\n\n" \
   +"Details on the problem can be found below.\n" \
   +"The cause of the problem may be from one of the projects that "\
   +project+" depends on (externals).\n" \
   +"You can contact the person who ran this test by sending email to: "\
   +unscrambleAddress(MY_EMAIL_ADDR)+".\n"\
   +"We hope you find this report useful.\n\n"

  if cmdMsgs.has_key("configure flags") :
    emailText += "Flags for configure: "+cmdMsgs['configure flags']+'\n'

  emailText += "Operating System: "+sys.platform+" "+os.name+"\n"
  emailText += "Host name: "+gethostname()+"\n"

  if os.environ.has_key("HOSTTYPE") :
    emailText += "Host type: "+os.environ["HOSTTYPE"]+"\n"
  if os.environ.has_key("PROCESSOR_IDENTIFIER") :
    emailText += "Processor: "+os.environ["PROCESSOR_IDENTIFIER"]+"\n"
  if os.environ.has_key("NUMBER_OF_PROCESSORS") :
    emailText += "Number of processors: "+os.environ["NUMBER_OF_PROCESSORS"]+"\n"

  if os.environ.has_key("PATH") :
    emailText += "PATH: "+os.environ["PATH"]+"\n"

  emailText += "Directory: "+curDir+'\n'

  if cmdMsgs.has_key('test') :
    emailText += "\n\nDetected problem when running test:\n"
    emailText += cmdMsgs['test']
    emailText += "\n"
    
  if cmdMsgs.has_key('command history') :
    emailText += "\nHistory of commands called for this build:\n"
    for cmditem in cmdMsgs['command history'] :
      emailText += "  "+cmditem+"\n"

  emailText += "\nstderr messages are:\n" 
  emailText += cmdMsgs['stderr']

  emailText +="\nnightlyBuildScript log:\n"
  emailText +=NBlogMessages.getMessages()
  emailText +="\n"

  if True :  
    emailText += "stdout messages are:\n"
    emailText += cmdMsgs['stdout']
    
    if cmdMsgs.has_key('config.log') :
      emailText += "\n\nconfig.log messages are:\n"
      emailText += cmdMsgs['config.log']
      
    send(toAddrs, emailSubject, emailText)
    
  else :
    emailText += "last stdout messages are:\n"
    # find latest line end before last 500 characters of stdout 
    lineendindex=cmdMsgs['stdout'].rfind('\n',0,-500)
    if lineendindex >= 0 :
      emailText += cmdMsgs['stdout'][lineendindex+1:]
    else :
      emailText += cmdMsgs['stdout']      

    #compose a mime multipart message putting config.log and stdout as attachment
    # following example at http://docs.python.org/lib/node162.html
    emailFull = MIMEMultipart()
    emailFull['Subject'] = emailSubject
    emailFull['To'] = ', '.join(toAddrs)
    emailFull['From'] = unscrambleAddress(SENDER_EMAIL_ADDR)
    emailFull.preamble = "This is a multi-part message in MIME format.\n"
    
    emailFull.attach(MIMEText(emailText))
    
    fp = StringIO()
    gzipfile = GzipFile(mode = 'wb', fileobj = fp)
    gzipfile.write(cmdMsgs['stdout'])
    gzipfile.close()
#    attachment = MIMEText(cmdMsgs['stdout'])
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(fp.getvalue())
    fp.close()
    if email_firstletter_capital :
      Encoders.encode_base64(attachment)
    else :
      encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='stdout.log.gz')
    emailFull.attach(attachment)
  
    if cmdMsgs.has_key('config.log') :
      fp = StringIO()
      gzipfile = GzipFile(mode = 'wb', fileobj = fp)
      gzipfile.write(cmdMsgs['config.log'])
      gzipfile.close()
#      attachment = MIMEText(cmdMsgs['config.log'])
      attachment = MIMEBase('application', 'octet-stream')
      attachment.set_payload(fp.getvalue())
      fp.close()
      if email_firstletter_capital :
        Encoders.encode_base64(attachment)
      else :
        encoders.encode_base64(attachment)
      attachment.add_header('Content-Disposition', 'attachment', filename='config.log.gz')
      emailFull.attach(attachment)
    
    #use a Generator to generate email, so we can turn off wrapping the header (because of our enormous subject length)
    fp = StringIO()
    g = Generator(fp, maxheaderlen=0)
    g.flatten(emailFull)
    
    sendWHdr(toAddrs,fp.getvalue())
#    sendWHdr(toAddrs,emailFull.as_string())

  NBlogMessages.writeMessage( "  email sent regarding "+project+" running '"+cmd+"'" )

def send(toAddrs,subject,message):
    sender = unscrambleAddress(SENDER_EMAIL_ADDR)  
    emailMsg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
       % (sender, ", ".join(toAddrs), subject))
    emailMsg += message

    sendWHdr(toAddrs, emailMsg)


#------------------------------------------------------------------------
# Send email (or store in a file)
#------------------------------------------------------------------------
def sendWHdr(toAddrs,msgWHeader):

  #store email in a file instead of sending
  if len(EMAIL_STOREFILE) > 0 and not EMAIL_STOREFILE.isspace() :
    NBlogMessages.writeMessage( '  store email in file '+EMAIL_STOREFILE)
    emailfile=open(NIGHTLY_BUILD_ROOT_DIR+'/'+EMAIL_STOREFILE, 'a')
    emailfile.write(msgWHeader)
    emailfile.write("\n\n")
    emailfile.close()
    return

  # Get smtp server password
  if os.path.isfile(SMTP_PASSWORD_FILENAME) :
    pwFilePtr = open(SMTP_PASSWORD_FILENAME,'r')
    smtppass  = pwFilePtr.read().strip()
    #print smtppass
    pwFilePtr.close()
  else :
    NBlogMessages.writeMessage( "Failure reading pwFileName=" + SMTP_PASSWORD_FILENAME )
    sys.exit(1)
    
  session = smtplib.SMTP(SMTP_SERVER_NAME,SMTP_SERVER_PORT)
  #session.set_debuglevel(1)
  if SMTP_SSL_SERVER==1 :
    session.ehlo('x')
    session.starttls()
    session.ehlo('x')  
  session.login(unscrambleAddress(SMTP_USER_NAME),smtppass)

  rc = session.sendmail(unscrambleAddress(SENDER_EMAIL_ADDR),toAddrs,msgWHeader)
  if rc!={} :
    NBlogMessages.writeMessage( 'session.sendmail rc='  )
    NBlogMessages.writeMessage( rc )
  session.quit()

#------------------------------------------------------------------------
# Decrypt email address 
#------------------------------------------------------------------------
def unscrambleAddress( scrambledEmailAddress ) :
  retVal = scrambledEmailAddress
  retVal = retVal.replace(' _AT_ ','@')
  retVal = retVal.replace(' _DOT_ ','.')
  return retVal

