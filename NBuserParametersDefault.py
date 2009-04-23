#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

#----------------------------------------------------------------------
# This file is a template for a user-given parameter file.
# It contains variables that the person running this script need to set or modify.
#----------------------------------------------------------------------
import sys
import datetime

#----------------------------------------------------------------------
# DRYRUN:
#   If set to 1, all configuration processing will be performed, but no work
#   will be done. Useful for debugging.
#----------------------------------------------------------------------
DRYRUN = 0

#----------------------------------------------------------------------
# NIGHTLY_BUILD_ROOT_DIR: 
#   directory where code will be checked out and builds
#   done. If the directory does not exist, it will be created.
#
#   This should be the full path, not a path relative to the
#   nightlyBuild script.
#
#   examples for both unix and windows:
#      NIGHTLY_BUILD_ROOT_DIR = '/home/userid/nbBuildDir'
#      NIGHTLY_BUILD_ROOT_DIR = r'c:\nbBuildDir'
#----------------------------------------------------------------------
NIGHTLY_BUILD_ROOT_DIR = '/xxx'

#----------------------------------------------------------------------
# List of Projects to be processed by script
#----------------------------------------------------------------------
PROJECTS = [
  'CoinUtils',
  'Clp',
  'Cgl',
  'Osi',
  'Cbc',
  'CoinMP',
  'DyLP',
  'FlopC++',
  'Ipopt',
  'Smi',
  'SYMPHONY',
  'Vol',
  'Bonmin',
  'Couenne',
  'CppAD',
  'OS',
  'CoinAll'
]

#----------------------------------------------------------------------
# Addition of GAMSlinks project to list of projects
# Note that testing and sometimes the compilation of the GAMSlinks
# project requires a GAMS system installed in your system.
# A demo system can be obtained from www.gams.com and is sufficent
# to run the tests.
# Further, GAMSlinks needs to know the location of your GAMS system.
# The easiest way is to have this path in your PATH environment variable.
# Note also, that the tests for the GAMSlinks project automatically
# attempt to install the solver links in your GAMS system before testing.
# Finally, GAMSlinks builds only on some selected platforms, see website.
# Windows is very likely to fail.
# Adding -DDISALLOW_PRINTING to the CXXFLAGS turns off printing to
# stdout in Cbc. It might be required to pass the tests. 
#----------------------------------------------------------------------

#PROJECTS.append('GAMSlinks')

#----------------------------------------------------------------------

# Define how a COIN-OR project is to be built and tested. A project can be
# built multiple times in different ways. The keys described here can be
# specified for each build. If a key is not specified for a given build, the
# default behaviour is used (in other words, the values do not carry over from
# one build to the next).

# SvnVersion: Specifies where in subversion the source should be obtained.
#   Examples: 'trunk', 'latestStable', 'releases/1.2.0'
#   Default Value: none
#
#   The special keys 'latestStable' and 'latestRelease' will use the most
#   recent stable or release version, respectively.

# OptLevel: Specifies an optimised build or a debugging build.
#   Legal Values: 'Default' or 'Debug'. 
#   Default Value: `Default'
#
#   `Default' produces an optimised (release) build, `Debug' a debugging build.
#   This is ignored when building with a Microsoft solution (.sln) file
#   because both builds are always created.

# BuildDirSuffix: A string to be used as the suffix for the name of the
#   subdirectory where this build will be created.
#
#   A build is placed in a directory named
#   NIGHTLY_BUILD_ROOT_DIR/<project>/<builddir>. The default value for
#   <builddir> is of the form <svnspec>-<suffix>, where <svnspec> is
#   constructed from the SvnVersion key and <suffix> is constructed from the
#   AdditionalConfigOptions key and the CONFIGURE_FLAGS variable. This default
#   name is guaranteed unique but is not necessarily human-friendly.
#   BuildDirSuffix allows the user to specify a human-friendly value for
#   <suffix>. It is the user's responsibility to ensure that this name is
#   unique for each build of a project.

# ThirdParty: Specfies the handling of third party codes.
#   Legal Values: 'Yes', 'Allowed', or 'No'.
#   Default Value: `Allowed'
#
#   Some projects provide scripts for downloading third party code. If the
#   value is 'Yes' then these scripts will be run. If the value is 'No' then
#   the options for skipping the use of all third party codes will be specified
#   when running "./configure". If the value is 'Allowed', the options for
#   "./configure" will be set to skip the use of any third party code not
#   specified in the THIRD_PARTY_ALLOWED variable (see below). This key is
#   ignored when building with a Microsoft solution (.sln) file because third
#   party code is never used.

# Distribute: Specifies if the result of the build will be uploaded into the
#   CoinBinary repository.
#   Legal Values: 'Yes' or 'No'.
#   Default Value: `No'
#
#   The upload will fail unless you have write permission in the CoinBinary
#   repository. You must specify a value for the BUILD_BINARIES variable.
#   You should also specify a value for the BUILD_INFORMATION variable.  Both
#   of these are described below. Finally, you probably want to set the
#   ThirdParty key to 'Allowed' or 'No', because COIN cannot distribute
#   binaries which contain third party codes that are not specified in
#   the THIRD_PARTY_ALLOWED variable (see below).

# BuildTypeInfo: Specify a string describing the current build.
#    Default Value: none
#
#    This string is used as part of the archive name that is created if
#    BUILD_BINARIES is on. It should be used to distinguish several builds
#    of the same svn version. See also BUILD_INFORMATION below.

# AdditionalConfigOptions: Specify additional './configure' options to be
#    applied to this specific build.
#    Example: '--enable-cbc-parallel'
#
#    See also CONFIGURE_FLAGS, used to specify addtional `./configure'
#    options for all builds. This key is ignored when building with a
#    Microsoft solution (.sln) file because configure is not run.

# Run: Specify when a specific build should be performed.
#   Legal Values: 'always', 'noSuccessOrAfterChange', 'afterChange'
#   Default: 'noSuccessOrAfterChange'
#
#   nightlyBuild can determine if the source code has been updated
#   since the last time this build was performed. It also records the result
#   of performing the build. Together, these can be used to decide if the
#   build needs to be performed on this run of nightlyBuild.
#   'always':  Always perform this build. This is useful for debugging.
#   'noSuccessOrAfterChange':  Perform this build if the prior run of this
#              build produced an error, or the source code has changed.
#   'afterChange':  Perform this build only if the source code has changed
#              since the last run. This is useful if there is a known problem
#              that is waiting for a fix. There is no point in repeating a
#              known failure unless a possible fix has been committed to svn.

# Reference: Specify that the builds for the referenced project should be added
#    to the list of builds used for this project.
#    Example: 'CoinUtils'
#    Default: none
#
#    Handy in the case where there's a set of common builds that should be
#    performed for all projects. Define them for one project and then reference
#    them from other projects.

# SkipProjects: Specifies a list of external projects that will be skipped
#    in this build.
#    Example: '['Ipopt','ThirdParty/HSL']'
#
#    This list of projects is added to the COIN_SKIP_PROJECTS variable of
#    the `./configure' call. Note that you need to use brackets "[ ]" here,
#    not parentheses "( )". (Put another way, the value should be correct
#    syntax for a python list_display.)

#----------------------------------------------------------------------
BUILDS = {
#  'ExampleProjectWithTwoBuilds'   : 
#    [ 
#      { 'SvnVersion':'trunk', 'OptLevel':'Default', 'ThirdParty':'Yes' }, 
#      { 'SvnVersion':'latestStable', 'OptLevel':'Debug', 'ThirdParty':'No' } 
#    ],
   'CoinUtils' : 
     [
       { 'SvnVersion': 'trunk',         'OptLevel': 'Default', 'ThirdParty': 'Allowed', 'Distribute': 'No' } 
     #,{ 'SvnVersion': 'trunk',         'OptLevel': 'Debug',   'ThirdParty': 'Allowed' } 
     #,{ 'SvnVersion': 'latestStable',  'OptLevel': 'Default', 'ThirdParty': 'Allowed' } 
     #,{ 'SvnVersion': 'latestStable',  'OptLevel': 'Debug',   'ThirdParty': 'Allowed' } 
     #,{ 'SvnVersion': 'latestRelease', 'OptLevel': 'Default', 'ThirdParty': 'Allowed' }  
     #,{ 'SvnVersion': 'latestRelease', 'OptLevel': 'Debug',   'ThirdParty': 'Allowed' } 
     ],
   'Osi' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'Clp' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'DyLP' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'SYMPHONY' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'Vol' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'Cgl' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'Cbc' :
     [
       { 'Reference' : 'CoinUtils' } 
       # And build a parallel version with Third Party
      ,{
        'SvnVersion': 'latestStable', 
        'OptLevel': 'Default', 
        'ThirdParty': 'Yes', 
        'AdditionalConfigOptions': '--enable-cbc-parallel',
        'Distribute' : 'No',
        'BuildTypeInfo': 'parallel' 
      }
     ],
   'CoinMP' : 
     [
       { 'Reference' : 'CoinUtils' }
     ],
   'Smi' : 
     [ 
       { 'Reference' : 'CoinUtils' } 
     ],
   'FlopC++' : 
     [ 
       { 'Reference' : 'CoinUtils' }
     ],
   'Ipopt' : 
     [ 
       { 'SvnVersion': 'trunk',        'OptLevel': 'Default', 'ThirdParty':'Allowed', 'Distribute': 'No' }
     #,{ 'SvnVersion': 'trunk',        'OptLevel': 'Debug',   'ThirdParty':'Yes' }
     #,{ 'SvnVersion': 'latestStable', 'OptLevel': 'Default', 'ThirdParty':'Yes' }
     #,{ 'SvnVersion': 'latestRelease','OptLevel': 'Default', 'ThirdParty':'Yes' }
     ],
   'CoinAll' :
     [
       { 'SvnVersion': 'trunk', 'OptLevel': 'Default', 'ThirdParty':'Allowed', 'Distribute': 'Yes' },
       { 'SvnVersion': 'trunk', 'OptLevel': 'Debug',   'ThirdParty':'Allowed', 'Distribute': 'Yes' }
     ],
   'LaGO' :
     [
       { 'Reference' : 'Ipopt' }
     ],
   'Couenne' : 
     [
       { 'Reference' : 'CoinUtils' }
     ],
   'Bonmin' : 
     [ 
       { 'SvnVersion': 'trunk',        'OptLevel': 'Default', 'ThirdParty':'Yes', 'Distribute': 'No' }
      #,{ 'SvnVersion': 'latestStable', 'OptLevel': 'Default', 'ThirdParty':'Yes' }
     ],
   'OS' :
     [ 
       { 'Reference' : 'Ipopt' } 
     #,{ 'SvnVersion': 'trunk',        'OptLevel': 'Default', 'ThirdParty': 'No', 'SkipProjects': ['Ipopt'] } 
     #,{ 'SvnVersion': 'trunk',        'OptLevel': 'Debug',   'ThirdParty': 'No', 'SkipProjects': ['Ipopt'] } 
     #,{ 'SvnVersion': 'latestStable', 'OptLevel': 'Default', 'ThirdParty': 'No', 'SkipProjects': ['Ipopt'] } 
     #,{ 'SvnVersion': 'latestRelease','OptLevel': 'Default', 'ThirdParty': 'No', 'SkipProjects': ['Ipopt'] } 
     ],
   'CppAD' : 
     [ 
       { 'SvnVersion': 'trunk',        'OptLevel': 'Default', 'ThirdParty': 'Allowed', 'AdditionalConfigOptions':'--with-Example --with-TestMore IPOPT_DIR='+NIGHTLY_BUILD_ROOT_DIR+'/Ipopt/trunk-default' } 
     #,{ 'SvnVersion': 'trunk',        'OptLevel': 'Default', 'ThirdParty': 'Allowed', 'AdditionalConfigOptions':'--with-Example --with-TestMore', 'Distribute': 'No' }
     #,{ 'SvnVersion': 'trunk',        'OptLevel': 'Debug',   'ThirdParty': 'No', 'AdditionalConfigOptions':'--with-Example --with-TestMore' } 
     #,{ 'SvnVersion': 'latestStable', 'OptLevel': 'Default', 'ThirdParty': 'No', 'AdditionalConfigOptions':'--with-Example --with-TestMore' } 
     #,{ 'SvnVersion': 'latestRelease','OptLevel': 'Default', 'ThirdParty': 'No', 'AdditionalConfigOptions':'--with-Example --with-TestMore' } 
     ],
   'GAMSlinks' :
     [ 
       { 'Reference' : 'Ipopt' }
     ]
  }

#----------------------------------------------------------------------
#On some systems the user might want to set extra options for the
#configure script like compilers...
#example: CONFIGURE_FLAGS = 'CC="gcc" CXX="g++" F77="gfortran" ADD_CXXFLAGS="-m64" ADD_CFLAGS="-m64" ADD_FFLAGS="-m64"'
#----------------------------------------------------------------------

CONFIGURE_FLAGS = ''

#---------------------------------------------------------------------
#On some systems, e.g. Windows/msys32, you might want to specify the
#name of the make program. 
#example: MAKECMD='gmake'
#---------------------------------------------------------------------

MAKECMD = 'make'

#----------------------------------------------------------------------
#Normally, nightlyBuild does not remove old builds before rebuilding
#a configuration, instead configure might be called and make needs to
#recompile files that changed.
#Setting this flag to 1 makes nightlyBuild remove a build directory
#completely before starting a configure/make/tests run.
#Note, that this can slow down the an anew build significantly. Thus,
#you might consider to use a tool like ccache (http://ccache.samba.org).
#After installing ccache and making it available in the $PATH, putting
#CONFIGURE_FLAGS = 'CC="ccache gcc" CXX="ccache g++" F77="ccache g77"'
#should make nightly build use ccache.
#----------------------------------------------------------------------

CLEAR_PREVIOUS_BUILD = 0

#----------------------------------------------------------------------
# LOGPRINT:
#   switch for logoutput to stdout. If set to 1 (default) log will go to
#   stdout, if set to 0, then not.
# LOGFILE: 
#   If not empty, then log messages will go to this file.
#   If LOGPRINT is 1, then log messages will go to stdout as well.
#   The LOGFILE will be used relative to the NIGHTLY_BUILD_ROOT_DIR, i.e.,
#   log will be written into NIGHTLY_BUILD_ROOT_DIR+'/'+LOGFILE
#   To generate log file names that incorporate a timestamp, you can use,
#   for example,
#   LOGFILE = 'nb'+ ts.strftime("%y%m%d%H%M") + '.log'
#----------------------------------------------------------------------

LOGPRINT = 1
LOGFILE = ''

#----------------------------------------------------------------------
# Values for sending mail:
#  EMAIL_STOREFILE: If set, then e-mails are not sent; instead, they are
#                   stored in a file. The filename is relative to
#                   NIGHTLY_BUILD_ROOT_DIR. If set, then no values for the
#                   SMTP_ variables need to be given.
#  SMTP_SERVER_NAME: The name of the SMTP server. For gmail server this is
#                    smtp.gmail.com
#  SMTP_SERVER_PORT: port number of the smtp server. This is typically 25,
#                    but for gmail server it is 587.
#  SMTP_SSL_SERVER: 0 or 1. If 1 then SMTP uses SSL (sometimes called
#                   startltls). For gmail this is 1.
#  SMTP_LOGIN_REQD: 0 or 1. If 1, valid values must be provided for
#                   SMTP_USER_NAME and SMTP_PASSWORD_FILENAME.
#  SMTP_USER_NAME: The name of an authorized user on the SMTP server. If using
#                  the gmail server, this is gmail_userid@gmail.com, which is
#                  coded as 'gmail_userid _AT_ gmail _DOT_ com.  
#  SMTP_PASSWORD_FILENAME: The name of a file containing smtp user's password
#  SENDER_EMAIL_ADDR: email sent by this script will be from this address
#  MY_EMAIL_ADDR: All problems detected by the script will be sent to
#                 this email address. The intention is for this to be
#                 the email address of the person running this script
#  SEND_MAIL_TO_PROJECT_MANAGER: 0 or 1. If 1 then any problems
#                 detected are sent to MY_EMAIL_ADDRESS and the
#                 project manager.
#----------------------------------------------------------------------
EMAIL_STOREFILE = ''

SMTP_SERVER_NAME = 'xxx.smtp.server.name'
SMTP_SERVER_PORT = 25
SMTP_SSL_SERVER = 0
SMTP_LOGIN_REQD = 1 
SMTP_USER_NAME = 'xxxx'
SMTP_PASSWORD_FILENAME = '/xxx/yyy/smtpPassWordFile'
SENDER_EMAIL_ADDR='xxx _AT_ yyyy _DOT_ edu'
MY_EMAIL_ADDR = SENDER_EMAIL_ADDR

SEND_MAIL_TO_PROJECT_MANAGER = 0


#----------------------------------------------------------------------
# The nightlyBuild will not build a binary by default
# If you want binaries built set the flag BUILD_BINARIES to a nonzero value.
# It is 0 by default
# If BUILD_BINARIES == 1, then tgz archives are build,
# if BUILD_BINARIES == 2, then zip archives are build,
# if BUILD_BINARIES == 3, then tgz and zip archives are build.
# Note: Binaries of project containing ThirdParty software will not be built
#----------------------------------------------------------------------

BUILD_BINARIES = 0

#----------------------------------------------------------------------
# You may wish to include platform, compiler, or other build information
# in the binary build name.
# Example: BUILD_INFORMATION = 'linux-x86-gcc4.2'
#----------------------------------------------------------------------

BUILD_INFORMATION = ''

#----------------------------------------------------------------------
# You may wish to specify a username and password for a svn commit
# into the CoinBinary repository
# By default they are null
#----------------------------------------------------------------------

COINBINARY_SVN_USERNAME = ''
COINBINARY_SVN_PASSWORD = ''


#----------------------------------------------------------------------
# When this parameter is set 1 we force the use of vcbuild in Windows if
# if msys/cygwin/mingw is present
#----------------------------------------------------------------------

FORCE_VCBUILD = 2


#----------------------------------------------------------------------
# Sometimes an svn update does not work and we need to try a second 
# or third time. The default is just one.  
# If more than one svn update is attempted nightlyBuild will wait 
# before making the next update attempt. The default delay is 1 second.
# Increase these numbers if desired in your NBuserParameters.py file.
#----------------------------------------------------------------------

SVN_UPDATE_TRIALS = 1
SVN_UPDATE_SLEEP_TIME = 1


#----------------------------------------------------------------------
# In Linux you may wish to run valgrind to check for memory leaks.
# This feature is off by default
#----------------------------------------------------------------------

VALGRIND_TEST = False

#----------------------------------------------------------------------
# Below is a list of acceptable Third Party code to include
# in the binary distribution
#----------------------------------------------------------------------

THIRD_PARTY_ALLOWED = ['ASL', 'Blas', 'Lapack', 'Mumps', 'GAMSIO', 'Metis']

# THE CURRENT PATH

SCRIPT_PATH = sys.path[ 0]

# Set the version of MS Visual Studio to Build v9 by default
MSVS_VERSION='v9'
