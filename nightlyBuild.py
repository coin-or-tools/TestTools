#!/usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import sys
from socket import gethostname
from sets import Set
import NBprojectConfig
import NBlogMessages
import NBemail
import NBosCommand
import NBsvnCommand
import NBcheckResult
import NBbuildConfig


execfile('NBuserParametersDefault.py')
execfile('NBuserParameters.py')

#------------------------------------------------------------------------
#  Main Program Starts Here
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#  If needed create the top level directory
#------------------------------------------------------------------------
if not os.path.isdir( NIGHTLY_BUILD_ROOT_DIR) :
  os.makedirs(NIGHTLY_BUILD_ROOT_DIR)
os.chdir( NIGHTLY_BUILD_ROOT_DIR)

#------------------------------------------------------------------------
#  If needed open the logfile
#------------------------------------------------------------------------

if len(LOGFILE) > 0 and not LOGFILE.isspace() :
  NBlogMessages.openLogFile()

#------------------------------------------------------------------------
#  Get the data directories if they don't already exist
#------------------------------------------------------------------------
dataBaseDir=os.path.join(NIGHTLY_BUILD_ROOT_DIR,'Data')
if not os.path.isdir(dataBaseDir) :
  os.makedirs(dataBaseDir)
dataDirs=['Netlib','miplib3','Sample']
for d in dataDirs :
  dataDir=os.path.join(dataBaseDir,d)
  if not os.path.isdir(dataDir) :
    svnCmd='svn checkout https://projects.coin-or.org/svn/Data/releases/1.0.4/'+d+' '+d
    svnResult=NBsvnCommand.run(svnCmd,dataBaseDir,'Data')
    if svnResult['returnCode'] != 0 :
      sys.exit(1)
    result=NBosCommand.run('find '+d+' -name \*.gz -print | xargs gzip -d')
netlibDir=os.path.join(dataBaseDir,'Netlib')
miplib3Dir=os.path.join(dataBaseDir,'miplib3')
sampleDir=os.path.join(dataBaseDir,'Sample')

#------------------------------------------------------------------------
# Define loop invariant configuration values
#------------------------------------------------------------------------
configuration={}
configuration['rootDir']=NIGHTLY_BUILD_ROOT_DIR
configurations = Set([""])

#------------------------------------------------------------------------
# Define how code is is to be built. Choices are:
# msSoln: use microsoft compiler with a solution (sln) file.
# unixConfig: use sequence "./configure", "make", "make test"
#------------------------------------------------------------------------
if sys.platform=='win32' :
  configuration['buildMethod']='msSln'
  # see if we are running Mingw/cygwin/msys
  # assume Bourne shell in path
  if FORCE_VCBUILD != 1 :
    result=NBosCommand.run( "sh -c ls" )
    if result['returnCode'] == 0 : configuration['buildMethod']='mingw'
else :
  configuration['buildMethod']='unixConfig'
  
valgrind_ok = False  
if VALGRIND_TEST :
  #check to make sure valgrind is really there
  result=NBosCommand.run( "valgrind --help" )
  valgrind_ok = (result['returnCode'] == 0)
  if not valgrind_ok :
    NBlogMessages.writeMessage("  Warning: valgrind does not work.")
    NBlogMessages.writeMessage("    valgrind --help returned "+result['returnCode'])
    NBlogMessages.writeMessage("    Output of stdout: "+result['stdout'])
    NBlogMessages.writeMessage("    Output of stderr: "+result['stderr'])

#------------------------------------------------------------------------
# Loop once for each project (get code, compile & link, and test).
#------------------------------------------------------------------------
for p in PROJECTS :

  configuration['project']=p
  configuration['clear previous build']=CLEAR_PREVIOUS_BUILD

  #------------------------------------------------------------------------
  # Loop once for each build configuration of p
  #------------------------------------------------------------------------
  buildConfigs = BUILDS[p]
  for bc in buildConfigs:
    

    #--------------------------------------------------------------------
    # Does build reference another project's build configuration.
    # If yes, then build p as specified by the reference project.
    #--------------------------------------------------------------------
    if 'Reference' in bc :
      referencedConfigs = BUILDS[ bc['Reference'] ]
      for c in referencedConfigs :
        buildConfigs.append(c)
      continue

    #--------------------------------------------------------------------
    # Setup subversion verion
    #--------------------------------------------------------------------
    if 'SvnVersion' not in bc :
      print 'Error. BUILDS does not contain SvnVersion'
      print '       Project is '+p
      print '       BuildConfig is '+str(bc)
      sys.exit(1)
    if bc['SvnVersion']=='latestStable' :
      lsv=NBsvnCommand.latestStableVersion(p)
      if not lsv :
        print 'Error. BUILDS configured to use lastest stable svn version'
        print '       Project does not have a stable version or error retreiving version number'
        print '       Project is '+p
        print '       BuildConfig is '+str(bc)
        print '       Skipping this BuildConfig'
        continue
      configuration['svnVersion']='stable/'+lsv
    elif bc['SvnVersion']=='latestRelease' :
      lrv=NBsvnCommand.latestReleaseVersion(p)
      if not lrv :
        print 'Error. BUILDS configured to use lastest release svn version'
        print '       Project does not have a release version or error retreiving version number'
        print '       Project is '+p
        print '       BuildConfig is '+str(bc)
        print '       Skipping this BuildConfig'
        sys.exit(1)
      configuration['svnVersion']='releases/'+lrv
    else:
      configuration['svnVersion']=bc['SvnVersion']

    #--------------------------------------------------------------------
    # Make sure optlevel specified
    #--------------------------------------------------------------------
    if 'OptLevel' not in bc :
      print 'Error. BUILDS does not contain OptLevel'
      print '       Project is '+p
      print '       BuildConfig is '+str(bc)
      sys.exit(1)
    elif bc['OptLevel']!="Debug" and bc['OptLevel']!="Default" :
      print 'Error. BUILDS has unrecognized OptLevel'
      print '       Project is '+p
      print '       BuildConfig is '+str(bc)
      print '       Expected OptLevel: Debug or Default'
      sys.exit(1)

    #--------------------------------------------------------------------
    # Process Parameters that are used by unix configure style build
    #--------------------------------------------------------------------
    if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingw':
      #--------------------------------------------------------------------
      # Doing a unix config type build.  Grab unix config parms
      #--------------------------------------------------------------------

      #--------------------------------------------------------------------
      # Setup usage of 3rd Party code
      # If not specified, use the moderate setting 'allowed'
      #--------------------------------------------------------------------
      if 'ThirdParty' in bc:
        if bc['ThirdParty'].lower() not in ['yes', 'no', 'allowed'] :
          print 'Error. ThirdParty entry of Build type configuration contains invalided value '+bc['ThirdParty']
          sys.exit(1)
        configuration['ThirdParty'] = bc['ThirdParty'].lower();
      else :
        configuration['ThirdParty'] = 'allowed'

      #--------------------------------------------------------------------
      # Set config options
      #--------------------------------------------------------------------
      configuration['configOptions']={}
      configuration['configOptions']['unique']=""
      configuration['configOptions']['invariant']=""

      if bc['OptLevel']=='Debug' :
        configuration['configOptions']['unique']+=" --enable-debug"
      if 'AdditionalConfigOptions' in bc :
        configuration['configOptions']['unique']+=" "+bc['AdditionalConfigOptions']

      configuration['configOptions']['invariant']+=" "+ CONFIGURE_FLAGS

      #--------------------------------------------------------------------
      # Deal with coin projects to be skipped by ./config
      #--------------------------------------------------------------------
      if 'SkipProjects' in bc :
        configuration['SkipProjects']=bc['SkipProjects']
      else :
        configuration['SkipProjects']=[]
      
      #---------------------------------------------------------------------
      # Set up test commands
      #---------------------------------------------------------------------
      configuration['test']={}
      if NBprojectConfig.CFG_BLD_TEST.has_key(p) :
        configuration['test'] = NBprojectConfig.CFG_BLD_TEST[p][:]
        # Remove valgrind tests, if valgrind is not there, the user does not want them, or we do not build in debug mode
        if not valgrind_ok or bc['OptLevel'] != "Debug" :
          for testitem in configuration['test'][:] :
            if testitem['cmd'].find('valgrind')>=0 :
              configuration['test'].remove(testitem)
      # If no test commands, remove from configuration
      if len(configuration['test'])==0 :
        configuration.pop('test')

      #---------------------------------------------------------------------
      # Set up install executables
      #---------------------------------------------------------------------
      configuration['install']={}
      if NBprojectConfig.CFG_BLD_INSTALL.has_key(p) :
        configuration['install']=NBprojectConfig.CFG_BLD_INSTALL[p]
      else :
        # No test executables so remove from configuration
        configuration.pop('install')
        
      if 'buildTypeInfo' in configuration :
        configuration.pop('buildTypeInfo')
      if 'BuildTypeInfo' in bc :
        configuration['buildTypeInfo'] = bc['BuildTypeInfo']
      elif 'buildTypeInfo' in bc :
        configuration['buildTypeInfo'] = bc['buildTypeInfo']

      #---------------------------------------------------------------------
      # Set up distribution of binaries
      #---------------------------------------------------------------------
      configuration['Distribute']=False
      if 'Distribute' in bc and bc['Distribute'].lower()=='yes' :
        configuration['Distribute']=True
        
    if configuration['buildMethod']=='msSln' :
      #--------------------------------------------------------------------
      # Doing a microsoft solution  build.  Grap ms sln parms
      #--------------------------------------------------------------------

      #---------------------------------------------------------------------
      # Set up test executables
      #---------------------------------------------------------------------
      configuration['test']={}
      if NBprojectConfig.SLN_BLD_TEST.has_key(p) :
        configuration['test']=NBprojectConfig.SLN_BLD_TEST[p]
      else :
        # No test executables so remove from configuration
        configuration.pop('test')

        
      #---------------------------------------------------------------------
      # If solution file is not in standard place then specify it's location
      #---------------------------------------------------------------------
      configuration['slnFile']=''
      if NBprojectConfig.SLN_FILE.has_key(p) :
        configuration['slnFile']=NBprojectConfig.SLN_FILE[p]          
      else :
        configuration.pop('slnFile')
      configuration['slnDir']=''
      if NBprojectConfig.SLN_DIR.has_key(p) :
        configuration['slnDir']=NBprojectConfig.SLN_DIR[p]          
      else :
        configuration.pop('slnDir')
        

      #--------------------------------------------------------------------
      # Set msbuild configuration parm (Release or Debug)
      #--------------------------------------------------------------------
      #if bc['OptLevel']=='Debug' :
      #  configuration['msbuild']="Debug"
      #else :
      #  configuration['msbuild']="Release"

    #---------------------------------------------------------------------
    # Get Run parm and pass it along
    #---------------------------------------------------------------------
    configuration['Run']='noSuccessOrAfterChange'
    if 'Run' in bc :
      if bc['Run'].lower()=='afterchange' :
        configuration['Run']='afterChange'
      elif bc['Run'].lower()=='always' :
        configuration['Run']='always'
               
    #---------------------------------------------------------------------
    # Modify any executable commands to have location of data directories
    #---------------------------------------------------------------------
    if configuration.has_key('test') :
      for t in range( len(configuration['test']) ) :
        testCmd=configuration['test'][t]['cmd']
        testCmd=testCmd.replace('_NETLIBDIR_',netlibDir)
        testCmd=testCmd.replace('_MIPLIB3DIR_',miplib3Dir)
        testCmd=testCmd.replace('_SAMPLEDIR_',sampleDir)
        configuration['test'][t]['cmd']=testCmd

    #--------------------------------------------------
    # Build & Test the configuration, if not previously done
    #--------------------------------------------------
    if str(configuration) not in configurations :
      NBbuildConfig.run(configuration)
      configurations=configurations | Set([str(configuration)])
    


NBlogMessages.writeMessage( "nightlyBuild.py Finished" )

# Email log messages to person running script
toAddrs = [NBemail.unscrambleAddress(MY_EMAIL_ADDR)]
subject = "NightlyBuild Log on "+sys.platform+" from "+gethostname()
NBemail.send(toAddrs,subject,NBlogMessages.getAllMessages())

#------------------------------------------------------------------------
#  If needed close the logfile
#------------------------------------------------------------------------

if len(LOGFILE) > 0 and not LOGFILE.isspace() :
  NBlogMessages.closeLogFile()

sys.exit(0)

