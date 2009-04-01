#! /usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import urllib2
import re
import sys
import time

import NBlogMessages
import NBemail
import NBosCommand
import NBcommandline

execfile('NBuserParametersDefault.py')
execfile(NBcommandline.getParameterFile())

#------------------------------------------------------------------------
# Function for executing svn commands
#  svnCmd: String representing svn command
#  dir: Directory where command is to be run from
#  project: Coin project running the command (this is used to provide
#           a better message if an error is detected
#  return: the result of the NBosCommand call;
#          return['returnCode'] is the return code of svn
#------------------------------------------------------------------------
def run(svnCmd,dir,project) :
  if dir != '.' :
    os.chdir(dir)
#    NBlogMessages.writeMessage('  cd '+dir)
  NBlogMessages.writeMessage('  '+svnCmd)
# result = NBosCommand.run(svnCmd)

# sometimes it is necessary to run more than once
  for i in range(1, SVN_UPDATE_TRIALS + 1):
    result = NBosCommand.run(svnCmd)
    if result['returnCode'] == 0 : return result
    time.sleep(SVN_UPDATE_SLEEP_TIME)
    
# if we are here something went wrong

  # we do not send a mail if svn add reported "has binary mime type property"
  # this is a stupid work around that works only if svn add was supposed to add only one binary file
  # this binary file usually still gets added
  if result['returnCode'] != 0 and result['stderr'].find('has binary mime type property')<0:
   NBemail.sendCmdMsgs(project,result,svnCmd)
  return result


#------------------------------------------------------------------------
# Function which returns the latest stable version of a project
#------------------------------------------------------------------------
def latestStableVersion(project) :
  url='https://projects.coin-or.org/'+project+'/chrome/site/'+project+'-latest-stable.txt'
  if project == "CoinAll":
    url='https://projects.coin-or.org/CoinBinary/chrome/site/CoinAll-latest-stable.txt'
  try :
    handle=urllib2.urlopen(url)
    latestStableVersion=handle.read()
    handle.close()
  except urllib2.URLError, why:
    NBlogMessages.writeMessage('  Warning: URLError exception caught while retrieving '+url+': '+str(why))
    return False

  latestStableVersion=re.findall(r'(\d+\.?\d+)',latestStableVersion)
  if len(latestStableVersion) == 1:
    return latestStableVersion[0]

  NBlogMessages.writeMessage('  Warning: Retrieving latest stable version number from '+url+' failed: Got '+latestStableVersion)

  url='https://projects.coin-or.org/svn/'+project+'/stable'
  if project == "CoinAll":
    url = 'https://projects.coin-or.org/svn/'+'CoinBinary/'+project+'/stable'
  try :
    handle=urllib2.urlopen(url)
    html=handle.read()
    handle.close()
  except urllib2.URLError, why:
    NBlogMessages.writeMessage('  Warning: URLError exception caught while retrieving '+url+': '+str(why))
    return False

  # In html code find the latest version number
  #   <li><a href="3.2/">3.2/</a></li>
  #   <li><a href="3.3/">3.3/</a></li>
  r=r'<li><a href="(\d+\.?\d+)/">(\d+\.?\d+)/</a></li>'
  findResult=re.findall(r,html)
  if len(findResult)==0: return False
  latestStableVersionRepeated2Times = findResult[-1:][0]
  latestStableVersion=latestStableVersionRepeated2Times[0]
  return latestStableVersion

#------------------------------------------------------------------------
# Function which returns the latest release version of a project
# If there isn't a release version then False is returned
#------------------------------------------------------------------------
def latestReleaseVersion(project) :
  url='https://projects.coin-or.org/'+project+'/chrome/site/'+project+'-latest-release.txt'
  if project == "CoinAll":
    url='https://projects.coin-or.org/CoinBinary/chrome/site/CoinAll-latest-release.txt'
  try :
    handle=urllib2.urlopen(url)
    latestReleaseVersion=handle.read()
    handle.close()
  except urllib2.URLError, why:
    NBlogMessages.writeMessage('  Warning: URLError exception caught while retrieving '+url+': '+str(why))
    return False

  latestReleaseVersion=re.findall(r'(\d+\.?\d+\.?\d+)',latestReleaseVersion)
  if len(latestReleaseVersion) == 1:
    return latestReleaseVersion[0]

  NBlogMessages.writeMessage('  Warning: Retrieving latest release version number from '+url+' failed: Got '+latestStableVersion)
  
  url='https://projects.coin-or.org/svn/'+project+'/releases'
  if project == "CoinAll":
    url = 'https://projects.coin-or.org/svn/'+'CoinBinary/'+project+'/releases'
  try :
    handle=urllib2.urlopen(url)
    html=handle.read()
    handle.close()
  except urllib2.URLError, why:
    NBlogMessages.writeMessage('  Warning: URLError exception caught while retrieving '+url+': '+str(why))
    return False

  # In html code find the latest version number
  #   <li><a href="1.6.0/">1.6.0/</a></li>
  r=r'<li><a href="(\d+\.?\d+\.?\d+)/">(\d+\.?\d+\.?\d+)/</a></li>'
  findResult=re.findall(r,html)
  if len(findResult)==0: return False
  latestReleaseVersionRepeated2Times = findResult[-1:][0]
  latestReleaseVersion=latestReleaseVersionRepeated2Times[0]
  return latestReleaseVersion


#------------------------------------------------------------------------
# Return svn revision number from url
# If not found the return -1
#------------------------------------------------------------------------
def svnRevision(url) :
  retVal=-1
  result = NBosCommand.run('svn info --xml '+svnDir(url))
  if result['returnCode']==0 :
#    reg=r'Last Changed Rev: (\d+)'
    reg=r'<commit\s*revision=\"(\d+)\"'
    found=re.findall(reg,result['stdout'])
    if len(found)!=0 :
      retVal=int(found[0])
  return retVal


#------------------------------------------------------------------------
# Return svn url corresponding to given directory
# If not found the return -1
#------------------------------------------------------------------------
def svnUrl(dir) :
  retVal='error in NBsvnCommand.svnUrl'
  svnCommandText='svn info --xml '+svnDir(dir)
  retVal += ': '+svnCommandText
  result = NBosCommand.run(svnCommandText)
  if result['returnCode']==0 :
    reg=r'<url>(.+)</url>'
    found=re.findall(reg,result['stdout'])
    if len(found)!=0 :
      retVal=found[0]
  return retVal
  

#------------------------------------------------------------------------
# newer(source, target)
# Return true if source and is more recently modified than target,
# (ie return true if source is newer than target and target needs
# to be rebuilt).
#
# If either sourrce or target don't exist then true is returned.
#
#------------------------------------------------------------------------
def newer(source,target) :

  #print '------------------------'
  #print source
  #print target
  #print '------------------------'
  #print ' '
  
  tarRev=svnRevision(target)
  if tarRev==-1 :
    # Target probably does not exist. It does not have an svn revision
    # nubmer, so return that it is out of date.
    return "Does not exist: "+target

  srcRev=svnRevision(source)
  if srcRev==-1 :
    # Source should exist. Something is wrong that will be caught
    # when an 'svn checkout' is done.
    return "Does not exist: "+source

  if srcRev>tarRev :
    return "New revision of: "+source

  # if there is an externals file then process it
  extFileName=os.path.join(target,"Externals")
  if os.path.isfile(extFileName) :
    extFilePtr = open(extFileName, "r")
    line = extFilePtr.readline()

    while line:
      line=line.strip()
      if line!='' :
        if line[0]!='#':
          reg=r'(\S+)(\s+)(\S+)'
          found=re.findall(reg,line)
          if len(found)!=1:
            # something is wrong. Do a rebuild
            return "Assumed out of date when reading: "+extFileName
          found=found[0]
          if len(found)!=3 :
            # something is wrong. Do a rebuild
            return "Assumed out of date when reading: "+extFileName
          extTarget=os.path.join(target,found[0])
          extSource=found[2]
          # Recursive call to see if external indicates rebuild
          msg=newer(extSource,extTarget) 
          if msg :
            extFilePtr.close()
            return msg
      line = extFilePtr.readline()

    extFilePtr.close()

  return False

#------------------------------------------------------------------------
# svnRevisionNumbers(target)
# Return svn version and version of all referenced externals
#
# target is the full path of the directory containing svn checkedout project
#------------------------------------------------------------------------
def svnRevisionNumbers(target) :
  retVal={}
  #stripTarget=target.strip()
  svnRevisions(target,retVal)
  return retVal
def svnRevisions(relPath,revisions) :
  #print "svnRevisions:"
  #print "  relPath="+relPath
  #print revisions
  stripRelPath=relPath.strip()
  #path=os.path.join(basePath,stripRelPath)
  #os.chdir(path)
  
  rev=svnRevision(stripRelPath)
  if rev==-1 : rev = "Error getting svn revision"
  url=svnUrl(stripRelPath)
  revisions[stripRelPath]=url+" "+str(rev)
  
  # get externals
  #print '  url="'+url+'"'
  #print '  relPath="'+stripRelPath+'"'
  #print " "
  result = NBosCommand.run('svn propget svn:externals '+svnDir(url))
  if result['returnCode']!=0 :
    print 'error getting external property'
    print 'url="'+url+'"'
    print 'result='
    print result
    return
  externals = result['stdout']

  for external in externals.split('\n'):
    if external.strip()=="" : continue
    #print "external='"+external+"'"
    p=external.split()
    #print p
    path=os.path.join(stripRelPath,p[0])
    #print path
    svnRevisions(path,revisions)
  return


#------------------------------------------------------------------------
# Function for manipulating directory string to a form needed by svn
#  dir: String representing directory name
#  return: directory in form needed by svn
#
#  On cygwin a directory might be in the form
#     /cygdrive/c/COIN/clp/trunk
#  For some unfortunate reason svn wants the directory to be 
#    c:/COIN/clp/trunk
#------------------------------------------------------------------------
def svnDir(dir) :
  retVal=dir
  if not dir.startswith("/cygdrive/"): return retVal
  # is the 11th character not a /
  if dir.find("/",11) != 11 : return retVal
  retVal=dir[10:11]+":/"+dir[12:]
  return retVal



#r=svnRevisionNumbers(r'F:\COIN\nightlyBuild\buildDir\OS\trunk')
#for cod,rev in r.items():
#  print "  checkout directory: "+cod
#  print "  svn url: "+rev.split()[0]
#  print "  svn revision number: "+rev.split()[1]
#  print " "
