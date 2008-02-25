#! /usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the BuildTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import sys
import re
import shutil
try :
  # Many older but currently used versions of python does not have hashlib
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

execfile('NBuserParametersDefault.py')
execfile('NBuserParameters.py')

#---------------------------------------------------------------------
# Keep history so same project is not repeatedly getting code from
# subversion repository.
#---------------------------------------------------------------------
SVN_HISTORY = {}
THIRD_PARTY_HISTORY = []

#---------------------------------------------------------------------
# Keep ThirdParty directories for testing for building binaries
#---------------------------------------------------------------------
THIRD_PARTY_DIRECTORIES = []


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
  cleanedUpName=cleanedUpName.replace('--enable','')
  cleanedUpName=cleanedUpName.replace('--','-')
  return cleanedUpName


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
#  configuration['noThirdParty']=True or False (optional). If False 
#   then 3rd party code will be used. If not specified then 3rd part
#   code will be skipped.
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
#    examples: "Ipopt", "Ipopt DyLP"
#
#  configuration['slnFile']= path and name of solution file if it is not
#    in the standard location.
#    Only used if configuration['buildMethod']=='unixConfig'
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
                 configuration['svnVersion']

  buildDir=svnVersionFlattened

  if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingw' :
  
   
    if len( configuration['configOptions']['unique']) > 150 and importedHashlib :
      buildDir += hashlib.md5( configuration['configOptions']['unique']).hexdigest()
    else:
      buildDir+=configuration['configOptions']['unique']
    if 'SkipProjects' in configuration :
      buildDir+="No"+configuration['SkipProjects']
    if 'noThirdParty' in configuration : 
      if configuration['noThirdParty'] :
        buildDir+='-NoThirdParty'
    buildDir=cleanUpName(buildDir)
    if buildDir==svnVersionFlattened : buildDir+='-default'
    
  
  fullBuildDir = os.path.join(projectBaseDir,buildDir)





  NBlogMessages.writeMessage('  SVN source URL: '+svnCheckOutUrl)
  NBlogMessages.writeMessage('  Checkout directory: '+projectCheckOutDir)
  NBlogMessages.writeMessage('  Build directory: '+fullBuildDir)



  
  #for a list of commands that have been executed
  commandHistory = []

  #---------------------------------------------------------------------
  # Completely remove a previous build if the user indicates this
  #---------------------------------------------------------------------
  if configuration['clear previous build'] and os.path.isdir(fullBuildDir) :
    NBlogMessages.writeMessage('  Remove previous build in directory '+fullBuildDir)
    try:
      shutil.rmtree(fullBuildDir)
    except shutil.Error :
      NBlogMessages.writeMessage('  Warning: removal of directory '+fullBuildDir+' failed.')

  #---------------------------------------------------------------------
  # If nothing has changed and the prior run tested OK or there is
  # a known problem being worked on, then there
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
  else :
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
      svnCmd='svn update'
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
  else :
    NBlogMessages.writeMessage('  "svn update" skipped. nightlyBuild has already updated for prior build configuration')
    runConfigure=SVN_HISTORY[projectCheckOutDir]

  #---------------------------------------------------------------------
  # If there are third party apps, then get these apps
  #---------------------------------------------------------------------
  buildThirdParty = True
  if 'noThirdParty' in configuration :
    if not configuration['noThirdParty'] :
      thirdPartyBaseDir=os.path.join(projectCheckOutDir,'ThirdParty')
      if os.path.isdir(thirdPartyBaseDir) :
        if thirdPartyBaseDir not in THIRD_PARTY_HISTORY :
          thirdPartyDirs = os.listdir(thirdPartyBaseDir)
          #clean up: take care of .svn, .OLD, and non-directory entries
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
            THIRD_PARTY_HISTORY.append( d)
          for d in thirdPartyDirs :
            if d=='.svn' : continue
            thirdPartyDir=os.path.join(thirdPartyBaseDir,d)
            if not os.path.isdir(thirdPartyDir) : continue

            # everything okay if we skip this project
            THIRD_PARTY_DIRECTORIES.append(thirdPartyBaseDir)
            if 'SkipProjects' in configuration :
              if d not in configuration['SkipProjects']  and d not in ThirdPartyAllowed  :
                NBlogMessages.writeMessage('  Warning: we cannot build a binary distribution because of: ' + d)
                buildThirdParty  = False
            else :
              if d not in ThirdPartyAllowed   :
                NBlogMessages.writeMessage('  Warning: we cannot build a binary distribution because of: ' + d)
                buildThirdParty  = False        
            install3rdPartyCmd=os.path.join(".","get."+d)
            os.chdir(thirdPartyDir)
            # If the install command has been updated since the last
            # install, then do a new install
            if os.path.isfile('NBinstalldone') :
              if NBosCommand.newer(install3rdPartyCmd,'NBinstalldone') :
                os.remove('NBinstalldone')
            if not os.path.isfile('NBinstalldone') :
              if os.path.isfile(install3rdPartyCmd) :
                NBlogMessages.writeMessage('  '+install3rdPartyCmd)
                commandHistory+=[ install3rdPartyCmd ]
                if configuration['buildMethod']=='mingw' :
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
        else :
          NBlogMessages.writeMessage('  Skipped a new download into '+thirdPartyBaseDir)
          # but we still need to test for building binaries even if we already
          # got the ThirdParty code
          buildThirdParty  = True
          for d in THIRD_PARTY_DIRECTORIES :
            if d=='.svn' : continue
            thirdPartyDir=os.path.join(thirdPartyBaseDir,d)
            if not os.path.isdir(thirdPartyDir) : continue
            # everything okay if we skip this project
            if 'SkipProjects' in configuration :
              if d not in configuration['SkipProjects']  and d not in ThirdPartyAllowed  :
                NBlogMessages.writeMessage('  Warning: we cannot build a binary distribution because of: ' + d)
                buildThirdParty  = False
            else :
              if d not in ThirdPartyAllowed   :
                NBlogMessages.writeMessage('  Warning: we cannot build a binary distribution because of: ' + d)
          #
          #
    
  #---------------------------------------------------------------------
  # Create the build directory if it doesn't exist
  #---------------------------------------------------------------------
  if not os.path.isdir(fullBuildDir) : 
    os.makedirs(fullBuildDir)

  #---------------------------------------------------------------------
  # Source is now available, so now it is time to run config
  #---------------------------------------------------------------------
  if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingw':
    skipOptions=''

    if 'SkipProjects' in configuration :
      skipOptions+=configuration['SkipProjects']

    # If needed create option for skipping 3rd party code
    needSkip3PartySkipOptions=False
    if 'noThirdParty' not in configuration : 
      needSkip3PartySkipOptions=True
    elif configuration['noThirdParty'] :
      needSkip3PartySkipOptions=True
    if needSkip3PartySkipOptions :
      thirdPartyBaseDir=os.path.join(projectCheckOutDir,'ThirdParty')
      if os.path.isdir(thirdPartyBaseDir) :
        thirdPartyDirs = os.listdir(thirdPartyBaseDir)
        for d in thirdPartyDirs :
          if d=='.svn' : continue
          skipOptions+=' ThirdParty/'+d

    if skipOptions!='' :
      skipOptions=' COIN_SKIP_PROJECTS="'+skipOptions+'"'

    os.chdir(fullBuildDir)
    NBlogMessages.writeMessage('  cd '+fullBuildDir)

    # Assemble all config options together and create config command
    configOptions ="-C "+configuration['configOptions']['unique']
    configOptions+=configuration['configOptions']['invariant']
    configOptions+=skipOptions
    configOptions=configOptions.replace("  "," ")
    configOptions=configOptions.replace("  "," ")
    configOptions=configOptions.replace('=" ','="')

    #start kipp change
    #
    if configuration['buildMethod']=='mingw' :
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
    #
    #end kipp change

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
    
    #
    # start kipp
    if configuration['buildMethod']=='mingw' :
      result=NBosCommand.run('sh -c '+MAKECMD) 
    else:
      result=NBosCommand.run(MAKECMD)
      
    # end kipp
    # 
    writeResults(result,'make') 

    # Check if make worked
    if result['returnCode'] != 0 :
      result['configure flags']=configOptions
      result['svn version']=configuration['svnVersion']
      result['command history']=commandHistory
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
                          'v8')
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

    vcbuild='vcbuild /u ' + slnFileName + ' $ALL'
             
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
        NBemail.sendCmdMsgs(configuration['project'],error_msg,vcbuild)
        return

  #---------------------------------------------------------------------
  # Run all test executables
  #---------------------------------------------------------------------
  if "test" in configuration :
    for t in range( len(configuration['test']) ) :
      testRelDir=configuration['test'][t]['dir']
      testDir = os.path.join(fullBuildDir,testRelDir)
      testCmd=configuration['test'][t]['cmd']
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
          result['svn version']=configuration['svnVersion']
          result['test']=testResultFail
          result['command history']=commandHistory
          NBemail.sendCmdMsgs(configuration['project'],result,testCmd)
          return


  #---------------------------------------------------------------------
  # Run valgrind on the unitTest
  # We assume a Unix Installation
  #---------------------------------------------------------------------


  #only do this if we have valgrind
  if VALGRIND_TEST == True :
    #check to make sure valgrind is reaally there
    result=NBosCommand.run( "valgrind --help" )
    if result['returnCode'] == 0 :
      if configuration['buildMethod']=='unixConfig' :
        if "valgrind" in configuration :
          for t in range( len(configuration['valgrind']) ) :
            valgrindRelDir=configuration['valgrind'][t]['dir']
            valgrindDir = os.path.join(fullBuildDir, valgrindRelDir)
            valgrindCmd=configuration['valgrind'][t]['cmd']
            if not os.path.isdir( valgrindDir) :
              NBlogMessages.writeMessage('  Directory to run valgrind on unitTest from does not exist:')
              NBlogMessages.writeMessage('    fullBuild directory: ' + fullBuildDir)
              NBlogMessages.writeMessage('    Intended directory: ' + valgrindDir)
              NBlogMessages.writeMessage('    Intended command: ' + valgrindCmd)
              continue
            os.chdir( valgrindDir)
            NBlogMessages.writeMessage('  cd ' + valgrindDir)
            NBlogMessages.writeMessage( '  ' + valgrindCmd )
            commandHistory+=[ valgrindCmd ]
            result = NBosCommand.run(valgrindCmd)
            writeResults(result, valgrindCmd)
            result['svn version']=configuration['svnVersion']
            result['command history'] = commandHistory
            NBemail.sendCmdMsgs(configuration['project'], result, valgrindCmd)
            #if result['returnCode'] != 0 :
            #    result['svn version']=configuration['svnVersion']
            #    result['command history'] = commandHistory
            #    NBemail.sendCmdMsgs(configuration['project'], result, valgrindCmd)
            #    return

  

  #---------------------------------------------------------------------
  # Run all install executables
  # We assume a Unix Installation
  #---------------------------------------------------------------------


  if configuration['buildMethod']=='unixConfig' or configuration['buildMethod']=='mingw':
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
            result['command history']=commandHistory
            NBemail.sendCmdMsgs(configuration['project'],result,installCmd)
            return

    
    #---------------------------------------------------------------------
    # Build the binary distribution
    # We assume a Unix distribution
    #---------------------------------------------------------------------

      if BUILD_BINARIES == 1 :
        # Only build binary if we are using allowed third party software
        if buildThirdParty  == True :
            directories = ""   
            # if the lib  directory is there, add it
            # delete these if already there
            if os.path.isdir( "lib") == True :
              directories  += " lib "

            # if the include directory is there, add it
            if os.path.isdir( "include") == True :
              directories +=  " include "

            # if the examples directory is there, add it
            examplesDir = os.path.join(projectCheckOutDir, configuration['project'], 'examples')
            print examplesDir
            NBlogMessages.writeMessage(' project Examples Directory is ' + examplesDir)
            # copy the examples directory
            if os.path.isdir( examplesDir) == True :
              NBlogMessages.writeMessage(' copy ' + examplesDir + ' to examples')
              copyCmd = 'cp -r '
              copyCmd  += examplesDir
              copyCmd += ' examples'
              result = NBosCommand.run( copyCmd)
              writeResults(result, copyCmd)
              commandHistory+=[ copyCmd ]
              if os.path.isdir( 'examples') == True :  directories +=  " examples"
            ##
            # now get the makefiles
            examplesMakefileDir = os.path.join(fullBuildDir, configuration['project'], 'examples')
            print examplesMakefileDir
            NBlogMessages.writeMessage(' project Examples Makefile Directory is ' + examplesMakefileDir)
            # copy the examples directory
            if os.path.isdir( examplesMakefileDir) == True :
              NBlogMessages.writeMessage(' copy ' + examplesMakefileDir + ' to examplesMakefiles')
              copyCmd = 'cp -r '
              copyCmd  += examplesMakefileDir
              copyCmd += ' examplesMakefiles'
              result = NBosCommand.run( copyCmd)
              writeResults(result, copyCmd)
              commandHistory+=[ copyCmd ]
              if os.path.isdir( 'examplesMakefiles') == True :  directories +=  " examplesMakefiles"




              

              
            # done with examples directory
            #
            # if the bin directory is there, add it
            if os.path.isdir( "bin") == True :
              directories +=  " bin "

            # if the share directory is there, add it
            if os.path.isdir( "share") == True :
              directories +=  " share "

            #if the directory that stores the binaries is not there create it
            binariesDir=os.path.join(projectBaseDir,"binaries")

            if not os.path.isdir( binariesDir ) :
              os.makedirs( binariesDir )

            #configuration['project']
            outputDirectory = os.path.join(binariesDir, configuration['project'])
            print outputDirectory


            if not os.path.isdir( outputDirectory) :
              os.makedirs( outputDirectory)

            # create the output directory
            
            # tar it up
            # buidDir should be name of tar file -- make unique
            tarCmd = 'tar  --exclude=.svn -czvf   '
            #do something better with tar file name
            buildInfo = ''
            if len(BUILD_INFORMATION) > 0 : buildInfo = '-' + BUILD_INFORMATION 
            tarFileName =   configuration['project'] + "-" + buildDir + "-" + sys.platform + buildInfo +".tgz"
            tarCmd += os.path.join(outputDirectory, tarFileName)
            tarCmd += directories

            NBlogMessages.writeMessage( '  '+ tarCmd )
            commandHistory+=[ tarCmd ]
            result=NBosCommand.run( tarCmd)
            writeResults(result, tarCmd)
            #delete the examples directory
            if os.path.isdir( 'examples') == True :
              rmDirCmd = 'rm -rf '
              rmDirCmd += 'examples'
              NBosCommand.run( rmDirCmd)
              commandHistory += [ rmDirCmd]
            #delete the examplesMakefiles directory
            if os.path.isdir( 'examplesMakefiles') == True :
              rmDirCmd = 'rm -rf '
              rmDirCmd += 'examplesMakefiles'
              NBosCommand.run( rmDirCmd)
              commandHistory += [ rmDirCmd]
            if result['returnCode'] != 0 :
                result['svn version']=configuration['svnVersion']
                # figure out what tarResultFail should be
                #result['tar']=tarResultFail
                result['command history']=commandHistory
                NBemail.sendCmdMsgs(configuration['project'],result,  tarCmd)
                writeResults(result, tarCmd)
                return

  
  #---------------------------------------------------------------------
  # Everything build and all tests passed.
  #---------------------------------------------------------------------
  os.chdir(fullBuildDir)
  f=open('NBallTestsPassed','w')
  f.close()
