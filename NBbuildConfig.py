#! /usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import sys
import re
import shutil
import stat
try :
  # Many older but currently used versions of python do not have hashlib
  import hashlib
except ImportError:
  importedHashlib=False
else :
  importedHashlib=True

import NBlogMessages
import NBemail
import NBosCommand
import NBsvnCommand
import NBcheckResult
import NBcommandline

execfile('NBuserParametersDefault.py')
execfile(NBcommandline.getParameterFile())

#---------------------------------------------------------------------
# Keep history so same project is not repeatedly getting code from
# subversion repository.
#---------------------------------------------------------------------
SVN_HISTORY = {}
THIRD_PARTY_HISTORY = []

#---------------------------------------------------------------------
# cleanUpName:
# File and directory names are generated and may contain 
# undesireable characters.
# Remove these characters from the name
#---------------------------------------------------------------------
def cleanUpName(messedUpName) :
  cleanedUpName=messedUpName
  
  # Do not remove "-". This will cause problems when removing NBallTestsPassed.
  #cleanedUpName=cleanedUpName.replace('-','')

  cleanedUpName=cleanedUpName.replace('/','-')
  cleanedUpName=cleanedUpName.replace('\\','-')
  cleanedUpName=cleanedUpName.replace(' ','')
  cleanedUpName=cleanedUpName.replace('"','')
  cleanedUpName=cleanedUpName.replace("'",'')
  cleanedUpName=cleanedUpName.replace("=",'-')
  cleanedUpName=cleanedUpName.replace(":",'')
  cleanedUpName=cleanedUpName.replace(";",'')
  cleanedUpName=cleanedUpName.replace('--enable','')
  cleanedUpName=cleanedUpName.replace('--','-')
  cleanedUpName=cleanedUpName.replace('*','')
  return cleanedUpName[:240]

#---------------------------------------------------------------------
# cleanUpThirdPartyDirs:
# Cleans a list of thirdparty dirs by taking suspicious entries out
#  (.svn, .OLD, and non-directory entries....).
#---------------------------------------------------------------------
def cleanUpThirdPartyDirs(thirdPartyBaseDir, thirdPartyDirs) :
  for d in thirdPartyDirs[:] :
    if d=='.svn' : 
      thirdPartyDirs.remove(d)
      continue
    thirdPartyDir=os.path.join(thirdPartyBaseDir,d)
    if not os.path.isdir(thirdPartyDir) :
      thirdPartyDirs.remove(d)
      continue
    if d.endswith('.OLD') :
      NBlogMessages.writeMessage('  removing '+d)
      shutil.rmtree(thirdPartyDir)
      fileToBeRemoved=os.path.join(thirdPartyDir[0:-4], 'NBinstalldone')
      if os.path.isfile(fileToBeRemoved) :
        os.remove(fileToBeRemoved)
      thirdPartyDirs.remove(d)
      continue

#---------------------------------------------------------------------
# writeResults:
# After running a command write stdout and stderr to a file
#---------------------------------------------------------------------
def writeResults(result,filenameSuffix) :
  cleanedUpSuffix=cleanUpName(filenameSuffix)
  stdoutfile=open('NBstdout-'+cleanedUpSuffix,'w')
  stdoutfile.write(result['stdout'])
  stdoutfile.close()
  stderrfile=open('NBstderr-'+cleanedUpSuffix,'w')
  stderrfile.write(result['stderr'])
  stderrfile.close()
  
#---------------------------------------------------------------------
# setFilesWritable:
# Sets all files and directories to be readable, writeable, and executable.
# So shutil.rmtree on Windows can remove the whole dir.
#---------------------------------------------------------------------
def setFilesWritable(dir) :
  for root, dirs, files in os.walk(dir):
    for name in files:
        #print "change mode of file "+name+" in "+root
        os.chmod(os.path.join(root, name), stat.S_IRWXU)
    for name in dirs:
        #print "change mode of dir  "+name+" in "+root
        os.chmod(os.path.join(root, name), stat.S_IRWXU)


  
#------------------------------------------------------------------------
#  Given a configuration, build and test it.
#
#  configuration['project']= name of project.
#   examples: "Clp", "Ipopt"f
#
#  configuration['rootDir']= root directory of nightlyBuild.
#   This is where the project will be checked out from svn, and
#   where the code will be compiled.  This directory must already
#   exist.  If the testing requires, it needs to contain Netlib & miplib3
#
#  configuration['svnVersion']= svn version to be built.
#   Examples are: "trunk", "stable/3.2", "releases/3.3.3"
#
#  configuration['buildMethod']= Defines method for building code.
#  Choices are:
#    msSoln: use microsoft compiler with a solution (sln) file.
#    unixConfig: use sequence "./configure", "make", "make test"
#
#  configuration['ThirdParty']='yes', 'no', or 'allowed'.
#   If 'yes' then all 3rd party code will be used.
#   If 'allowed' then only 3rd party code in the THIRD_PARTY_ALLOWED list will be used. 
#   If 'no' then no 3rd party code will be used.
#   Only used if configuration['buildMethod']=='unixConfig'
#
#  configuration['configOptions']: Parameters to be passed to configure.
#   The -C option and the options for skipping 3rd party code do not
#   need to be specified.  These will be generated by this function.
#   There are two types of configOptions to be specified.
#   Only used if configuration['buildMethod']=='unixConfig'
#  configuration['configOptions']['unique']= These are options that
#   distinguish different build configurations.  These options are used
#   to generate the vpath directory name where the code will be built.
#   Examples are: "", "--enable-debug" "--enable-parrallel"
#  configuration['configOptions']['invariant']= These are options that
#   that are the same for every build configuration so they don't need
#   to be part of the vpath directory name.
#   Example: 'CXX="g++ -m64" LDFLAGS=-lstdc++'
#  
#  configuration['SkipProjects']= List of COIN projects to skip (exclude)
#    from the build.
#
#  configuration['slnFile']= path and name of solution file if it is not
#    in the standard location.
#    Only used if configuration['buildMethod']=='msSoln'
#
#  configuration['test']=vector of triples indicating tests that 
#    are to be run after building the project. Each triple consists
#    of:
#    'dir': directory where test command is to be issued.
#    'cmd': command to be run with any parameters.
#    'check': vector of functions to be called which will check the 
#           results from running 'cmd' to determine if an error occurred
#------------------------------------------------------------------------
def run(configuration) :
  NBlogMessages.clearMessages()
  NBlogMessages.writeMessage( configuration['project'] )

  # Create svn checkout target directory name
  svnVersionFlattened=cleanUpName(configuration['svnVersion'])

  #---------------------------------------------------------------------
  # Create names of directory where source is located and
  # and were object, libs and executables are located (build directory)
  # To compute build directory, the ./configure options need to be 
  # generated.
  #---------------------------------------------------------------------
  projectBaseDir=os.path.join(configuration['rootDir'],configuration['project'])
  projectCheckOutDir=os.path.join(projectBaseDir,svnVersionFlattened)




  svnCheckOutUrl='https://projects.coin-or.org/svn/'+\
                 configuration['project']+'/'+\
                 configuration['svnVersion']  + ' --non-interactive ' + '--trust-server-cert '
  if configuration['project'] == 'CoinAll' :
    svnCheckOutUrl='https://projects.coin-or.org/svn/CoinBinary/'+\
                 configuration['project']+'/'+\
                 configuration['svnVersion'] + ' --non-interactive ' + ' --trust-server-cert '



  buildDir=svnVersionFlattened

  if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingwOrCygwinOrMsys' :
    if configuration.has_key('BuildDirSuffix') :
      buildDir += '-'+configuration['BuildDirSuffix']
    else :
      if len( configuration['configOptions']['unique']) > 150 and importedHashlib :
        buildDir += hashlib.md5( configuration['configOptions']['unique']).hexdigest()
      else:
        buildDir+=configuration['configOptions']['unique']
      for d in configuration['SkipProjects'] :
        buildDir+="No"+d
      if configuration['ThirdParty']=='yes' :
        buildDir+='-AllThirdParty'
      if configuration['ThirdParty']=='no' :
        buildDir+='-NoThirdParty'
      buildDir=cleanUpName(buildDir)
      if buildDir==svnVersionFlattened : buildDir+='-default'
    
  
  fullBuildDir = os.path.join(projectBaseDir,buildDir)





  NBlogMessages.writeMessage('  SVN source URL: '+svnCheckOutUrl)
  NBlogMessages.writeMessage('  Checkout directory: '+projectCheckOutDir)
  NBlogMessages.writeMessage('  Build directory: '+fullBuildDir)

  if DRYRUN == 1 :
    NBlogMessages.writeMessage(str(configuration))
    return

  
  #for a list of commands that have been executed
  commandHistory = []


  #---------------------------------------------------------------------
  # If nothing has changed and the prior run tested OK or there is
  # a known problem being worked on (`afterChange'), then there
  # is no need to do anything.
  #---------------------------------------------------------------------
  if os.path.isdir(fullBuildDir) :
    os.chdir(fullBuildDir)
    msg=NBsvnCommand.newer(svnCheckOutUrl,projectCheckOutDir)

    if os.path.isfile('NBallTestsPassed') :
      prevRunSuccess=True
      NBlogMessages.writeMessage('  In prior build all test passed')
    else:
      prevRunSuccess=False
      NBlogMessages.writeMessage('  No record of all tests having passed')

    # If new source in svn, then must remove "allTestsPassed" files
    if msg:
      # SVN has changed since last run
      NBlogMessages.writeMessage('  '+msg)
      # Must remove file NBallTestsPassed from all build directories that
      # use projectCheckoutDir for their source code. This is to ensure
      # that make will be run in all the build dirs after "svn update"
      dirs = os.listdir("..")
      for d in dirs :
        if d.startswith(svnVersionFlattened) :
          fileToBeRemoved=os.path.join("..",d,'NBallTestsPassed')
          if os.path.isfile(fileToBeRemoved) :
            os.remove(fileToBeRemoved)
            NBlogMessages.writeMessage('  Removing all test passed record from directory: '+d)
    else :
      # SVN has not changed since last run
      if configuration['Run']=='noSuccessOrAfterChange':
        if prevRunSuccess :
          NBlogMessages.writeMessage('  No changes since previous successful run')
          return
        else: 
          NBlogMessages.writeMessage('  Rerunning. No changes, but no record of successful run')
      elif configuration['Run']=='afterChange' :
        NBlogMessages.writeMessage('  No changes since previous run')
        return
      else:
        NBlogMessages.writeMessage('  No changes but run always selected')

    # Build directory exists, but there's work to do.
    # Completely remove a previous build if the user indicates this
    if configuration['clear previous build'] :
      os.chdir(projectBaseDir)
      NBlogMessages.writeMessage('  Remove previous build in directory '+fullBuildDir)
      try:
        setFilesWritable(fullBuildDir)
        shutil.rmtree(fullBuildDir)
      except (IOError, os.error), why:
        NBlogMessages.writeMessage('  ERROR removing previous build directory: '+str(why))
      except :
        exception = sys.exc_info()[:2]
        NBlogMessages.writeMessage('  ERROR removing previous build directory: '+exception[0])
        NBlogMessages.writeMessage('   '+exception[1])
  else :
    # Build directory does not yet exist.
    NBlogMessages.writeMessage('  Targets have not yet been built')


  #---------------------------------------------------------------------
  # svn checkout or update the project
  #---------------------------------------------------------------------
  # Don't get source from subversion if previously done
  if not SVN_HISTORY.has_key(projectCheckOutDir) :
    if not os.path.isdir(projectBaseDir) :
      os.makedirs(projectBaseDir)
    if not os.path.isdir(projectCheckOutDir) :
      svnCmd='svn ' +\
           'checkout ' +\
           svnCheckOutUrl +\
           ' '+svnVersionFlattened
      commandHistory+=[ svnCmd ]
      svnResult=NBsvnCommand.run(svnCmd,projectBaseDir,configuration['project'])
      if svnResult['returnCode'] != 0 :
        return
      runConfigure = True
    else :
      svnCmd='svn update --non-interactive  --trust-server-cert '
      commandHistory+=[ svnCmd ]
      svnResult=NBsvnCommand.run(svnCmd,projectCheckOutDir,configuration['project'])
      if svnResult['returnCode'] != 0 :
        return
      #check whether a *.in or configure file was updated 
      r=r'(\S+\.in\s)|(configure\s)'
      findResult=re.findall(r,svnResult['stdout'])
      if len(findResult)!=0:
        runConfigure = True
      else :
        runConfigure = False

    SVN_HISTORY[projectCheckOutDir]=runConfigure
    
    if 'postCheckout' in configuration:
      for cmd in configuration['postCheckout'] :
        os.chdir(projectCheckOutDir)
        NBlogMessages.writeMessage('  execute post checkout command '+cmd)
        commandHistory+=[ cmd ]
        result=NBosCommand.run(cmd)
        writeResults(result,cmd)
        if result['returnCode'] :
          NBlogMessages.writeMessage('  Warning: '+cmd+' returned '+str(result['returnCode']))
  else :
    NBlogMessages.writeMessage('  "svn update" skipped. nightlyBuild has already updated for prior build configuration')
    runConfigure=SVN_HISTORY[projectCheckOutDir]

  #---------------------------------------------------------------------
  # If there are third party apps, then get these apps
  # Check if we can build binaries, i.e., that we use only allowed 3rd party
  # codes. If only allowed codes should be built, add others onto skip list
  #---------------------------------------------------------------------
  buildThirdParty = True
  if 'ThirdParty' in configuration and configuration['ThirdParty'] != 'no' :
    thirdPartyBaseDir=os.path.join(projectCheckOutDir,'ThirdParty')
    if os.path.isdir(thirdPartyBaseDir) :
      if thirdPartyBaseDir not in THIRD_PARTY_HISTORY :
        thirdPartyDirs = os.listdir(thirdPartyBaseDir)
        #clean up: take care of .svn, .OLD, and non-directory entries
        cleanUpThirdPartyDirs(thirdPartyBaseDir, thirdPartyDirs)
        for d in thirdPartyDirs :
          dlong = 'ThirdParty/'+d

          # if the 3rdparty code is not in the white list and not skipped,
          # but we want to build only allowed projects,
          # then we add this 3rdparty code into the list of skipped projects
          if configuration['ThirdParty'] == 'allowed' and d not in THIRD_PARTY_ALLOWED and dlong not in configuration['SkipProjects'] :
            configuration['SkipProjects'].append(dlong)
          # everything okay if we skip this project
          if dlong not in configuration['SkipProjects'] and d not in THIRD_PARTY_ALLOWED :
            NBlogMessages.writeMessage('  Warning: we cannot build a binary distribution because of: ' + d)
            buildThirdParty  = False
          install3rdPartyCmd=os.path.join(".","get."+d)
          thirdPartyDir=os.path.join(thirdPartyBaseDir,d)
          os.chdir(thirdPartyDir)
          
          # If the install command or a patch file has been updated
          # since the last install, then do a new install
          if os.path.isfile('NBinstalldone') :
            if NBosCommand.newer(install3rdPartyCmd,'NBinstalldone') :
              os.remove('NBinstalldone')
            else :
              thirdpartyfiles = os.listdir(thirdPartyDir)
              for file in thirdpartyfiles :
                if len(re.findall(r'.patch', file)) != 0 and NBosCommand.newer(file, 'NBinstalldone') :
                  os.remove('NBinstalldone')
          if not os.path.isfile('NBinstalldone') :
            if os.path.isfile(install3rdPartyCmd) :
              NBlogMessages.writeMessage('  '+install3rdPartyCmd)
              commandHistory+=[ install3rdPartyCmd ]
              if configuration['buildMethod']=='mingwOrCygwinOrMsys' :
                install3rdPartyCmd = os.path.join(".","get."+d)
                #what a pain replace("\\", "/") does not work
                # we must split and then join, ugh
                pathParts = install3rdPartyCmd.split("\\")
                sep = '/'
                install3rdPartyCmd = sep.join(pathParts)
                install3rdPartyCmd = "sh -c " + "'" +   install3rdPartyCmd    +  "'"
              installReturn = NBosCommand.run(install3rdPartyCmd)
              if installReturn['returnCode'] :
                NBlogMessages.writeMessage('  Warning: Install of 3rd party code in '+thirdPartyDir+' returned '+str(installReturn['returnCode']))
              else :
                f=open('NBinstalldone','w')
                f.close()
              writeResults(installReturn,install3rdPartyCmd)
          else :
            NBlogMessages.writeMessage('  skipped a new download of '+d)
        THIRD_PARTY_HISTORY.append(thirdPartyBaseDir)
      else : # thirdPartyBaseDir is in THIRD_PARTY_HISTORY
        NBlogMessages.writeMessage('  Skipped a new download of third party code into '+thirdPartyBaseDir)
        # but we still need to test for building binaries even if we already
        # got the ThirdParty code
        buildThirdParty  = True
        thirdPartyDirs = os.listdir(thirdPartyBaseDir)
        #clean up: take care of .svn, .OLD, and non-directory entries
        cleanUpThirdPartyDirs(thirdPartyBaseDir, thirdPartyDirs)
        for d in thirdPartyDirs :
          thirdPartyDir=os.path.join(thirdPartyBaseDir,d)
          dlong = 'ThirdParty/'+d
          # if the 3rdparty code is not in the white list and not skipped, but we want to build only allowed projects,
          # then we add this 3rdparty code into the list of skipped projects
          if configuration['ThirdParty'] == 'allowed' and d not in THIRD_PARTY_ALLOWED and dlong not in configuration['SkipProjects'] :
            configuration['SkipProjects'].append(dlong)
          # everything okay if we skip this project
          if dlong not in configuration['SkipProjects'] and d not in THIRD_PARTY_ALLOWED  :
            NBlogMessages.writeMessage('  Warning: we cannot build a binary distribution because of: ' + d)
            buildThirdParty  = False
    
  #---------------------------------------------------------------------
  # Create the build directory if it doesn't exist
  #---------------------------------------------------------------------
  if not os.path.isdir(fullBuildDir) : 
    os.makedirs(fullBuildDir)
       
  #---------------------------------------------------------------------
  # Source is now available, so now it is time to run config
  #---------------------------------------------------------------------
  if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingwOrCygwinOrMsys':
    skipOptions=''

    if 'SkipProjects' in configuration :
      for d in configuration['SkipProjects'] :
        skipOptions+=' '+d

    # If needed create option for skipping 3rd party code
    if configuration['ThirdParty']=='no' :
      thirdPartyBaseDir=os.path.join(projectCheckOutDir,'ThirdParty')
      if os.path.isdir(thirdPartyBaseDir) :
        thirdPartyDirs = os.listdir(thirdPartyBaseDir)
        cleanUpThirdPartyDirs(thirdPartyBaseDir, thirdPartyDirs)
        for d in thirdPartyDirs :
          skipOptions+=' ThirdParty/'+d

    if skipOptions!='' :
      skipOptions=' COIN_SKIP_PROJECTS="'+skipOptions+'"'

    os.chdir(fullBuildDir)
#    NBlogMessages.writeMessage('  cd '+fullBuildDir)

    # Assemble all config options together and create config command
    configOptions ="-C "+configuration['configOptions']['invariant']
    configOptions+=configuration['configOptions']['unique']
    configOptions+=skipOptions
    configOptions=configOptions.replace("  "," ")
    configOptions=configOptions.replace("  "," ")
    configOptions=configOptions.replace('=" ','="')

    if configuration['buildMethod']=='mingwOrCygwinOrMsys' :
      #configCmd = os.path.join(projectCheckOutDir,"configure ")
      configCmd = os.path.join("..",svnVersionFlattened,"configure ")
       # svnVersionFlattened
      #what a pain replace("\\", "/") does not work
      # we must split and then join, ugh
      pathParts = configCmd.split("\\")
      sep = '/'
      configCmd = sep.join(pathParts)
      configCmd = "sh -c " + "'" + configCmd + configOptions +  "'"
    else:
      configCmd = os.path.join(projectCheckOutDir,"configure "+configOptions) 

    # If config was previously run, then no need to run again.
    if (not runConfigure) and NBcheckResult.didConfigRunOK() :
      NBlogMessages.writeMessage("  configure previously ran. Not rerunning.")
    else :
      NBlogMessages.writeMessage("  "+configCmd)
      commandHistory+=[ configCmd ]

      # Finally run config
      result=NBosCommand.run(configCmd)
      result['stdout']=configOptions+"\n"+result['stdout']
      writeResults(result,'config') 

      # Check if configure worked
      if result['returnCode'] != 0 :
        error_msg = result
        error_msg['configure flags']=configOptions
        error_msg['svn version']=configuration['svnVersion']
        error_msg['command history']=commandHistory
        error_msg['svn revision number']=NBsvnCommand.svnRevisionNumbers(projectCheckOutDir)
        logFileName = 'config.log'
        if os.path.isfile(logFileName) :
          logFilePtr = open(logFileName,'r')
          logFileContent = logFilePtr.read()
          logFilePtr.close()
          # try to find out which subproject has failed and read corresponding config.log file
          r=r'configure:.* error: .*[/\\](\w+)[\\/]configure.? failed for .*'
          matches=re.findall(r,logFileContent)
          if len(matches)>0 :
            failedProject=matches[-1]
            NBlogMessages.writeMessage("  configure failed for subproject "+failedProject)
            logFileName = os.path.join(failedProject,"config.log") 
            if os.path.isfile(logFileName) :
              logFilePtr = open(logFileName,'r')
              logFileContent = logFilePtr.read()
              logFilePtr.close()

          # Add contents of log file to message
          error_msg['config.log'] = logFileContent
        NBemail.sendCmdMsgs(configuration['project'],error_msg,configCmd)
        return

    #---------------------------------------------------------------------
    # Run make part of build
    #---------------------------------------------------------------------
    NBlogMessages.writeMessage( '  '+MAKECMD )
    commandHistory+=[ MAKECMD ]
    
    if configuration['buildMethod']=='mingwOrCygwinOrMsys' :
      result=NBosCommand.run('sh -c '+MAKECMD) 
    else:
      result=NBosCommand.run(MAKECMD)
      
    writeResults(result,'make') 
    # Check if make worked
    if result['returnCode'] != 0 :
      result['configure flags']=configOptions
      result['svn version']=configuration['svnVersion']
      result['command history']=commandHistory
      result['svn revision number']=NBsvnCommand.svnRevisionNumbers(projectCheckOutDir)
      NBemail.sendCmdMsgs(configuration['project'],result,'make')
      return

  if configuration['buildMethod']=='msSln' :
    #---------------------------------------------------------------------
    # Source is now available, so now it is time to run vcbuild
    #---------------------------------------------------------------------

    if configuration.has_key('slnDir') :
      slnFileDir = os.path.join(projectCheckOutDir,configuration['slnDir'])
    else :
      slnFileDir = os.path.join(projectCheckOutDir,\
                          configuration['project'],\
                          'MSVisualStudio',\
                          MSVS_VERSION)
    if not os.path.isdir(slnFileDir) :
      NBlogMessages.writeMessage("  Solution file directory does not exist: "+slnFileDir)
      return

    os.chdir(slnFileDir)
    NBlogMessages.writeMessage('  cd '+slnFileDir)

    if configuration.has_key('slnFile') :
      slnFileName = configuration['slnFile']
    else :
      slnFileName = configuration['project']+'.sln'
    if not os.path.isfile(slnFileName) :
      NBlogMessages.writeMessage("  Solution file does not exist '" \
                                 +slnFileName \
                                 +"' in directory " \
                                 +slnFileDir )

      return

    #vcbuild='vcbuild /u ' + slnFileName + ' $ALL'
    # Horand Gassmann asked for errfile, logcommands & logfile
    vcbuild='vcbuild /u /errfile:NBerrfile-vcbuild /logcommands /logfile:NBlogfile-vcbuild ' + slnFileName + ' $ALL'
             
    NBlogMessages.writeMessage("  "+vcbuild)
    commandHistory+=[ vcbuild ]

    # Finally run vcbuild
    result=NBosCommand.run(vcbuild)
    writeResults(result,'vcbuild') 

    # Check if vcbuild worked
    if result['returnCode'] != 0 :
        error_msg = result
        error_msg['svn version']=configuration['svnVersion']
        error_msg['command history']=commandHistory
        error_msg['diagnostic files']=['NBerrfile-vcbuild','NBlogfile-vcbuild']
        error_msg['svn revision number']=NBsvnCommand.svnRevisionNumbers(projectCheckOutDir)
        NBemail.sendCmdMsgs(configuration['project'],error_msg,vcbuild)
        return

  #---------------------------------------------------------------------
  # Run all test executables
  #---------------------------------------------------------------------
  if "test" in configuration :
    for t in range( len(configuration['test']) ) :
      testCmd=configuration['test'][t]['cmd']
      testRelDir=configuration['test'][t]['dir']
      testDir = os.path.join(fullBuildDir,testRelDir)
      if not os.path.isdir(testDir) :
        NBlogMessages.writeMessage('  Directory to run test from does not exist:')
        NBlogMessages.writeMessage('    Intended directory: '+testDir)
        NBlogMessages.writeMessage('    Intended command: '+testCmd)
        continue
      os.chdir(testDir)
      NBlogMessages.writeMessage('  cd '+testDir)

      NBlogMessages.writeMessage( '  '+testCmd )
      commandHistory+=[ testCmd ]
      result=NBosCommand.run(testCmd)
      writeResults(result,testCmd)
        
      for testFunc in configuration['test'][t]['check'] :
        result['buildDir']=fullBuildDir
        result['srcDir']=projectCheckOutDir
        testResultFail=testFunc(result,configuration['project'])
        if testResultFail :
          result['configure flags']=configOptions
          result['svn version']=configuration['svnVersion']
          result['test']=testResultFail
          result['command history']=commandHistory
          result['svn revision number']=NBsvnCommand.svnRevisionNumbers(projectCheckOutDir)
          NBemail.sendCmdMsgs(configuration['project'],result,testCmd)
          return

  #---------------------------------------------------------------------
  # Run all install executables
  # We assume a Unix Installation
  #---------------------------------------------------------------------

  if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingwOrCygwinOrMsys':
    if "install" in configuration :
      for t in range( len(configuration['install']) ) :
        installRelDir=configuration['install'][t]['dir']
        installDir = os.path.join(fullBuildDir, installRelDir)
        installCmd=configuration['install'][t]['cmd']
        if not os.path.isdir( installDir) :
          NBlogMessages.writeMessage('  Directory to run install from does not exist:')
          NBlogMessages.writeMessage('    Intended directory: '+installDir)
          NBlogMessages.writeMessage('    Intended command: '+installCmd)
          continue
        os.chdir(installDir)
        NBlogMessages.writeMessage('  cd '+installDir)
        NBlogMessages.writeMessage( '  '+installCmd )
        commandHistory+=[ installCmd ]
        result=NBosCommand.run(installCmd)
        writeResults(result,installCmd)
        if result['returnCode'] != 0 :
            result['svn version']=configuration['svnVersion']
            # figure out what installResultFail should be
            #result['install']=installResultFail
            result['configure flags']=configOptions
            result['command history']=commandHistory
            result['svn revision number']=NBsvnCommand.svnRevisionNumbers(projectCheckOutDir)
            NBemail.sendCmdMsgs(configuration['project'],result,installCmd)
            return

      # after install, go back into build directory 
      os.chdir(fullBuildDir)
    
      #---------------------------------------------------------------------
      # Build the binary distribution
      # We assume a Unix distribution
      #---------------------------------------------------------------------

      # Only build binary if we are using allowed third party software
      if BUILD_BINARIES > 0 and buildThirdParty:
        try:
          #if the directory that stores the binaries is not there create it
          binariesDir=os.path.join(projectBaseDir,"binaries")
          if not os.path.isdir( binariesDir ) :
            os.makedirs( binariesDir )
          
          archiveName  = configuration['project'] 
          archiveName += "-"+svnVersionFlattened.replace('releases-','').replace('stable-','')
          if len(BUILD_INFORMATION) > 0 :
            archiveName += "-"+BUILD_INFORMATION
          if configuration['configOptions']['unique'].find('--enable-debug')>=0 :
            archiveName += "-debug"
          if 'buildTypeInfo' in configuration and len(configuration['buildTypeInfo']) > 0 :
            archiveName += "-"+configuration['buildTypeInfo']
        
          archiveDir = os.path.join(binariesDir, archiveName)
          if os.path.isdir(archiveDir) :
            NBlogMessages.writeMessage('  delete old archive directory '+archiveDir)
            setFilesWritable(archiveDir)
            shutil.rmtree(archiveDir)
          os.makedirs( archiveDir )
        
          NBlogMessages.writeMessage('  copy files for binary distribution into directory '+archiveDir)
          # if the lib directory is there, copy it
          if os.path.isdir( "lib") :
            #NBlogMessages.writeMessage('  copy lib directory')
            shutil.copytree("lib", os.path.join(archiveDir, "lib"), True)

          # if the include directory is there, copy it
          if os.path.isdir( "include") :
            #NBlogMessages.writeMessage('  copy include directory')
            shutil.copytree("include", os.path.join(archiveDir, "include"), True)
        
          # copy the examples directory
          examplesDir = os.path.join(projectCheckOutDir, configuration['project'], 'examples')
          #NBlogMessages.writeMessage('  Examples Directory is ' + examplesDir)
          if os.path.isdir( examplesDir) :
            #NBlogMessages.writeMessage('  copy examples source directory '+examplesDir)
            shutil.copytree(examplesDir, os.path.join(archiveDir, "examples"), True)
          
          # copy the examples Makefiles directory
          examplesMakefileDir = os.path.join(fullBuildDir, configuration['project'], 'examples')
          #NBlogMessages.writeMessage('  Examples Makefile Directory is ' + examplesMakefileDir)
          if os.path.isdir( examplesMakefileDir) :
            #NBlogMessages.writeMessage('  copy examples makefile directory ' + examplesMakefileDir)
            shutil.copytree(examplesDir, os.path.join(archiveDir, 'examplesMakefiles'), True)

          # copy the examples directory in base directory, if there
          if os.path.isdir( "examples") :
            #NBlogMessages.writeMessage('  copy examples directory to examples')
            shutil.copytree("examples", os.path.join(archiveDir, "examples"), True)

          # if the bin directory is there, copy it
          if os.path.isdir( "bin") :
            #NBlogMessages.writeMessage('  copy bin directory')
            shutil.copytree("bin", os.path.join(archiveDir, "bin"), True)

          # if the share directory is there, copy it
          if os.path.isdir( "share") :
            #NBlogMessages.writeMessage('  copy share directory')
            shutil.copytree("share", os.path.join(archiveDir, "share"), True)
          
          shutil.copy(os.path.join(SCRIPT_PATH,"NBReadMe.txt"), os.path.join(archiveDir,"README"))
          
          # tar and/or zip them up
          os.chdir(binariesDir)

          tarFileName = archiveName+".tgz"
          zipFileName = archiveName+".zip"

          tarCmd = 'tar  --exclude=.svn   --exclude=config.*  -czvf   '
          if sys.platform == 'win32' :
            zipCmd = 'zip -r '
          else :
            zipCmd = 'zip -yr '

          tarCmd += tarFileName+' '+archiveName
          if  BUILD_INFORMATION.find("mingw") > 0 :
            #zipCmd += 'a -tzip' + ' ' +zipFileName+' '+archiveName+' -x\\!*.svn'
            zipCmd += 'a -tzip' + ' ' +zipFileName+' '+archiveName +' -x!*.svn'
          else :
            zipCmd += zipFileName+' '+archiveName+' -x \\*/.svn/\\*'

          failedCmd = ''
          if BUILD_BINARIES & 1 :
            NBlogMessages.writeMessage( '  '+ tarCmd )
            commandHistory+=[ tarCmd ]
            result=NBosCommand.run( tarCmd)
            writeResults(result, tarCmd)
            if result['returnCode']!=0 : failedCmd = tarCmd

          if BUILD_BINARIES & 2 and failedCmd == '':
            NBlogMessages.writeMessage( '  '+ zipCmd )
            commandHistory+=[ zipCmd ]
            result=NBosCommand.run( zipCmd)
            writeResults(result, zipCmd)
            if result['returnCode']!=0 : failedCmd = zipCmd

          if result['returnCode'] != 0 :
            result['svn version']=configuration['svnVersion']
            result['command history']=commandHistory
            error_msg['svn revision number']=NBsvnCommand.svnRevisionNumbers(projectCheckOutDir)
            NBemail.sendCmdMsgs(configuration['project'], result, failedCmd)
            writeResults(result, failedCmd)
            return
      
          # remove directory where we collected files for binary distribution...
          setFilesWritable(archiveDir)
          shutil.rmtree(archiveDir)

          # upload archive files to CoinBinary server
          if configuration['Distribute'] == True :
            #checkout/update binary directory from CoinBinary server
            distributeDirectory = os.path.join(projectBaseDir,"distribute")
            svnCheckoutCmd = 'svn checkout -N https://projects.coin-or.org/svn/CoinBinary/binary/'+configuration['project']+' '+distributeDirectory
            commandHistory+=[ svnCheckoutCmd ]
            svnResult=NBsvnCommand.run(svnCheckoutCmd,'.',configuration['project'])
            if svnResult['returnCode'] != 0 :
              return
            #put archive files into distribution directory
            archives=[]
            if BUILD_BINARIES & 1 :
              shutil.copy(os.path.join(binariesDir, tarFileName), distributeDirectory)
              archives.append(tarFileName)
            if BUILD_BINARIES & 2 :
              shutil.copy(os.path.join(binariesDir, zipFileName), distributeDirectory)
              archives.append(zipFileName)

            os.chdir(distributeDirectory)
            for archive in archives :
              #add archive files to repository (should just happen nothing if already existing in repo)
              svnAddCmd = 'svn add '+archive
              commandHistory+=[ svnAddCmd ]
              svnResult=NBsvnCommand.run(svnAddCmd,'.',configuration['project'])
              if svnResult['returnCode'] != 0 and svnResult['stderr'].find('has binary mime type property')<0:
                return
              #set mime type to binary so that there is no confusion about endlines
              svnPropsetCmd = 'svn propset svn:mime-type application/octet-stream '+archive
              commandHistory+=[ svnPropsetCmd ]
              svnResult=NBsvnCommand.run(svnPropsetCmd,'.',configuration['project'])
              if svnResult['returnCode'] != 0 :
                return

            #commit repository
            svnCommitCmd =  'svn commit --non-interactive '
            svnCommitCmd += '-m "nightlyBuild: adding or updating archive '+archiveName+'" '
            if len(COINBINARY_SVN_USERNAME) :
              svnCommitCmd += '--username '+COINBINARY_SVN_USERNAME+' '
            if len(COINBINARY_SVN_PASSWORD) :
              svnCommitCmd += '--password '+COINBINARY_SVN_PASSWORD+' '
            if len(COINBINARY_SVN_PASSWORD)==0 :
              commandHistory+=[ svnCommitCmd ]
            svnResult=NBsvnCommand.run(svnCommitCmd,'.',configuration['project'])
            if svnResult['returnCode'] != 0 :
              return

          os.chdir(fullBuildDir)
        except (IOError, os.error), why:
          NBlogMessages.writeMessage(' ERROR in creating or distributing binary distribution: '+str(why))
          result={'stdout':'', 'stderr':str(why), 'svn version':configuration['svnVersion'], 'command history':commandHistory}
          NBemail.sendCmdMsgs(configuration['project'], result, 'creating or distributing binary distribution')
          return
#        except :
#          print "Unexpected error:", sys.exc_info()[0]
#          result={'stdout':'', 'stderr':sys.exc_info()[0], 'svn version':configuration['svnVersion'], 'command history':commandHistory}
#          NBemail.sendCmdMsgs(configuration['project'], result, 'creating or distributing binary distribution')
#          return

  
  #-----------------------------------------------------------------------------
  # Everything build, all tests passed, and binaries were build and distributed.
  #-----------------------------------------------------------------------------
  os.chdir(fullBuildDir)
  f=open('NBallTestsPassed','w')
  f.close()
