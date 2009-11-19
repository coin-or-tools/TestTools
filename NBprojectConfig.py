#! /usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import NBcheckResult
import NBcommandline

try :
  # Can not import this on some platforms because they may not have MySQLdb
  import NBcbcRunTimes
except ImportError:
  importedCbcRunTimes=False
else :
  importedCbcRunTimes=True

#to get MAKECMD  
execfile('NBuserParametersDefault.py')
execfile(NBcommandline.getParameterFile())

#----------------------------------------------------------------------
# This file defines variables which describe how the specific
# coin-or projects are to be tested and who are their managers.
#----------------------------------------------------------------------

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS = {}
SLN_BLD_TEST = {}
CFG_BLD_POSTCHECKOUT = {}
CFG_BLD_TEST = {}
CFG_BLD_INSTALL = {}
CFG_BLD_VALGRIND_TEST = {}
SLN_FILE = {}
SLN_DIR = {}


#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['CoinUtils'] = 'ladanyi _AT_ us _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['CoinUtils']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':'CoinUtils/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check': [ NBcheckResult.valgrindErrorMessage,
                              NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['CoinUtils']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]


SLN_BLD_TEST['CoinUtils']=[
                  {'dir':r'CoinUtils\MSVisualStudio',
                   'cmd':MSVS_VERSION+'\unitTestCoinUtils\Release\unitTestCoinUtils',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage] },
                  {'dir':r'CoinUtils\MSVisualStudio',
                   'cmd':MSVS_VERSION+'\unitTestCoinUtils\Debug\unitTestCoinUtils',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage] } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['DyLP'] = 'lou _AT_ cs _DOT_ sfu _DOT_ ca'

CFG_BLD_TEST['DyLP']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.noSolverInterfaceTestingIssueMessage ] },
                  {'dir': os.path.join('Osi','test'),
                   'cmd': '.'+os.sep+'unitTest -testOsiSolverInterface -netlibDir=_NETLIBDIR_ -cerr2cout',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.noSolverInterfaceTestingIssueMessage] } ]

CFG_BLD_INSTALL['DyLP']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Clp'] = 'jjforre _AT_ us _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['Clp']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir': os.path.join('Clp','src'),
                   'cmd': '.'+os.sep+'clp -unitTest -dirNetlib=_NETLIBDIR_ -netlib',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.endWithWoodw] },
                  {'dir':'Clp/src',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./clp -unitTest',
                   'check':[ NBcheckResult.valgrindErrorMessage,
                             NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['Clp']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['Clp']=[
                  {'dir':r'Clp\MSVisualStudio\\'+MSVS_VERSION+'\Release',
                   'cmd':'clp -dirSample=_SAMPLEDIR_ -unitTest -dirNetlib=_NETLIBDIR_ -netlib',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.endWithWoodw] },
                  {'dir':r'Clp\MSVisualStudio\\'+MSVS_VERSION+'\Debug',
                   'cmd':'clp -dirSample=_SAMPLEDIR_ -unitTest -dirNetlib=_NETLIBDIR_ -netlib',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.endWithWoodw] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['SYMPHONY'] = 'tkr2 _AT_ lehigh _DOT_ edu'
CFG_BLD_TEST['SYMPHONY']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':'',
                   'cmd': MAKECMD+' fulltest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':'SYMPHONY/test',
                   'cmd':'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check':[ NBcheckResult.valgrindErrorMessage,
                             NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['SYMPHONY']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['SYMPHONY']=[ {
                   'dir':r'SYMPHONY\MSVisualStudio\\'+MSVS_VERSION+'\Release',
                   'cmd':r'symphony -F _NETLIBDIR_\25fv47.mps',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':r'SYMPHONY\MSVisualStudio\\'+MSVS_VERSION+'\Debug',
                   'cmd':r'symphony -F _NETLIBDIR_\25fv47.mps',
                   'check':[ NBcheckResult.rc0 ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Vol'] = 'barahon _AT_ us _DOT_ ibm _DOT_ com'
CFG_BLD_TEST['Vol']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['Vol']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Osi'] = 'mjs _AT_ clemson _DOT_ edu'

CFG_BLD_TEST['Osi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.noSolverInterfaceTestingIssueMessage ] },
                  {'dir': os.path.join('Osi','test'),
                   'cmd': '.'+os.sep+'unitTest -testOsiSolverInterface -netlibDir=_NETLIBDIR_ -cerr2cout',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.noSolverInterfaceTestingIssueMessage] },
                  {'dir':'Osi/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check':[ NBcheckResult.valgrindErrorMessage,
                             NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['Osi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['Osi']=[
                  {'dir':r'Osi\MSVisualStudio\\'+MSVS_VERSION+'\OsiExamplesBuild\Release',
                   'cmd':'OsiExamplesBuild',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':r'Osi\MSVisualStudio\\'+MSVS_VERSION+'\OsiExamplesBuild\Debug',
                   'cmd':'OsiExamplesBuild',
                   'check':[ NBcheckResult.rc0 ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Cgl'] = 'robinlh _AT_ us _DOT_ ibm _DOT_ com'
CFG_BLD_TEST['Cgl']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':'Cgl/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check':[ NBcheckResult.valgrindErrorMessage,
                             NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['Cgl']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Cbc'] = 'bca _AT_ list _DOT_ coin-or _DOT_ org'

CFG_BLD_TEST['Cbc']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.cbcMakeTestSuccessMessage ] },
                  {'dir': os.path.join('Cbc','src'),
                   'cmd': '.'+os.sep+'cbc -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] },
                  {'dir':'Cbc/src',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./cbc -unitTest',
                   'check':[ NBcheckResult.valgrindErrorMessage,
                             NBcheckResult.valgrindLeakMessage ] } ]

if importedCbcRunTimes :
  CFG_BLD_TEST['Cbc'][1]['check'].append(NBcbcRunTimes.cbcSaveRuntimes)


CFG_BLD_INSTALL['Cbc']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['Cbc']=[
                  {'dir':r'Cbc\MSVisualStudio\\'+MSVS_VERSION+'\cbcSolve\Release',
                   'cmd':'cbcSolve -dirSample=_SAMPLEDIR_ -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] },
                  {'dir':r'Cbc\MSVisualStudio\\'+MSVS_VERSION+'\cbcSolve\Debug',
                   'cmd':'cbcSolve -dirSample=_SAMPLEDIR_ -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Ipopt'] = 'andreasw _AT_ watson _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['Ipopt']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':'Ipopt/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./hs071_cpp',
                   'check': [ NBcheckResult.valgrindErrorMessage,
                              NBcheckResult.valgrindLeakMessage ] }, 
                  {'dir':'Ipopt/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./hs071_c',
                   'check': [ NBcheckResult.valgrindErrorMessage,
                              NBcheckResult.valgrindLeakMessage ] },
                  {'dir':'Ipopt/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./hs071_f',
                   'check': [ NBcheckResult.valgrindErrorMessage,
                              NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['Ipopt']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

#third party packages are not optional here

#----------------------------------------------------------------------
#PROJECT_EMAIL_ADDRS['Bonmin'] = 'pierre _DOT_ bonami _AT_ lif _DOT_ univ-mrs _DOT_ fr'

CFG_BLD_TEST['Bonmin']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':'Bonmin/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check': [ NBcheckResult.valgrindErrorMessage
                             #,NBcheckResult.valgrindLeakMessage
                            ] },
                  {'dir':'Bonmin/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./CppExample',
                   'check': [ NBcheckResult.valgrindErrorMessage
                             #,NBcheckResult.valgrindLeakMessage
                            ] } ]

CFG_BLD_INSTALL['Bonmin']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]
#third party packages are not optional here

#----------------------------------------------------------------------
#PROJECT_EMAIL_ADDRS['FlopC++'] = 'Tim _DOT_ Hultberg _AT_ eumetsat _DOT_ int'

CFG_BLD_TEST['FlopC++']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] }
#                  ,{'dir':'FlopCpp/test',
#                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
#                   'check': [ NBcheckResult.valgrindErrorMessage,
#                              NBcheckResult.valgrindLeakMessage ] }
                ]

CFG_BLD_INSTALL['FlopC++']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_FILE['FlopC++']=r'FlopCpp.sln'
SLN_DIR['FlopC++']=r'FlopCpp\MSVisualStudio\\'+MSVS_VERSION
SLN_BLD_TEST['FlopC++']=[
                  {'dir':r'FlopCpp\MSVisualStudio\\'+MSVS_VERSION+'\Release',
                   'cmd':'unitTest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':r'FlopCpp\MSVisualStudio\\'+MSVS_VERSION+'\Debug',
                   'cmd':'unitTest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['OS'] = 'kipp _DOT_ martin _AT_ chicagogsb _DOT_ edu'

CFG_BLD_TEST['OS']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':'OS/test',
                   'cmd': ' valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check': [ NBcheckResult.valgrindErrorMessage,
                              NBcheckResult.valgrindLeakMessage ] } ]

CFG_BLD_INSTALL['OS']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['OS']=[
                  {'dir':r'OS\test',
                   'cmd':'unitTestDebug',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':r'OS\test',
                   'cmd':'unitTestRelease',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]
#third party packages are not optional if Ipopt is not excluded

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['LaGO'] = 'stefan _AT_ math _DOT_ hu-berlin _DOT_ de'
CFG_BLD_TEST['LaGO']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install gams-install test',
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['LaGO']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['CoinAll'] = 'tkr2 _AT_ lehigh _DOT_ edu'

CFG_BLD_TEST['CoinAll']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir': os.path.join('Clp','src'),
                   'cmd': '.'+os.sep+'clp -unitTest -dirNetlib=_NETLIBDIR_ -netlib',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.endWithWoodw] },
                  {'dir':'SYMPHONY',
                   'cmd': MAKECMD+' fulltest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir': os.path.join('Osi','test'),
                   'cmd': '.'+os.sep+'unitTest -testOsiSolverInterface -netlibDir=_NETLIBDIR_ -cerr2cout',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.noSolverInterfaceTestingIssueMessage] },
                  {'dir': os.path.join('Cbc','src'),
                   'cmd': '.'+os.sep+'cbc -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] } ]

CFG_BLD_INSTALL['CoinAll']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['CppAD'] = 'bradbell _AT_ seanet _DOT_ com'

CFG_BLD_TEST['CppAD']=[
                  {'dir':'',
                   'cmd': os.path.join('.','example','example'),
                   'check':[ NBcheckResult.rc0 ] }, 
                  {'dir':'',
                   'cmd': os.path.join('.','test_more','test_more'),
                   'check':[ NBcheckResult.rc0 ] },
# currently valgrind complains about the use of uninitialized data in some code that looks perfectly fine
# therefore we do not include the error check here so far 
                  {'dir':'example',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./example',
                   'check': [ NBcheckResult.valgrindLeakMessage ] } ]

#take out make install for CppAD since it does not confirm to usual coin procedure (it installs into $HOME/include by default!)
#CFG_BLD_INSTALL['CppAD']=[
#                  {'dir':'',
#                   'cmd': MAKECMD+' install',
#                   'check':[ NBcheckResult.rc0,
#                             NBcheckResult.standardSuccessMessage ] } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Smi'] = 'kingaj _AT_ us _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['Smi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.endWithStarDoneStar ] },
                  {'dir':'Smi/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check': [ NBcheckResult.valgrindErrorMessage,
                              NBcheckResult.valgrindLeakMessage] } ]

CFG_BLD_INSTALL['Smi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['Smi']=[
                  {'dir':r'Smi\test',
                   'cmd':r'..\MSVisualStudio\\'+MSVS_VERSION+'\unitTestSmi\Release\smiUnitTest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.endWithStarDoneStar ] },
                  {'dir':r'Smi\test',
                   'cmd':r'..\MSVisualStudio\\'+MSVS_VERSION+'\unitTestSmi\Debug\smiUnitTest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.endWithStarDoneStar ] } ]
#does not have references to third party packages
#TODO: need some check whether make test was successful; what is the behaviour in Smi's unittest if it fails?

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['GAMSlinks'] = 'stefan _AT_ math _DOT_ hu-berlin _DOT_ de'

CFG_BLD_TEST['GAMSlinks']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install gams-install test',
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['GAMSlinks']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['GAMSlinks']=[ ]
#does have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['CoinMP'] = 'bjarni _AT_ maximalsoftware _DOT_ com'

CFG_BLD_TEST['CoinMP']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':'CoinMP/test',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full --show-reachable=yes ./unitTest',
                   'check':[ NBcheckResult.valgrindErrorMessage
                            #,NBcheckResult.valgrindLeakMessage
                           ] } ]

CFG_BLD_INSTALL['CoinMP']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

SLN_BLD_TEST['CoinMP']=[
                  {'dir':r'CoinMP\MSVisualStudio\\'+MSVS_VERSION+'\CoinMP\Release',
                   'cmd':'unitTest',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':r'CoinMP\MSVisualStudio\\'+MSVS_VERSION+'\coinMP\Debug',
                   'cmd':'unitTest',
                   'check':[ NBcheckResult.rc0 ] } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Couenne'] = 'belotti _AT_ lehigh _DOT_ edu'

CFG_BLD_TEST['Couenne']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':'Couenne/src/main',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full --show-reachable=yes ./couenne ../../test/toy.nl',
                   'check':[ NBcheckResult.valgrindErrorMessage
                            #,NBcheckResult.valgrindLeakMessage
                           ] },
                  {'dir':'Couenne/src/main',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full --show-reachable=yes ./couenne ../../test/qquad.nl',
                   'check':[ NBcheckResult.valgrindErrorMessage
                            #,NBcheckResult.valgrindLeakMessage
                           ] },
                  {'dir':'Couenne/src/main',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full --show-reachable=yes ./couenne ../../test/geoid.nl',
                   'check':[ NBcheckResult.valgrindErrorMessage
                            #,NBcheckResult.valgrindLeakMessage
                           ] },
                  {'dir':'Couenne/src/main',
                   'cmd': 'valgrind --tool=memcheck --leak-check=full --show-reachable=yes ./couenne ../../test/small2.nl',
                   'check':[ NBcheckResult.valgrindErrorMessage
                            #,NBcheckResult.valgrindLeakMessage
                           ] }
                  ]

CFG_BLD_INSTALL['Couenne']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

#does have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['ADOL-C'] = 'andrea _DOT_ walther _AT_ uni-paderborn _DOT_ de'

CFG_BLD_TEST['ADOL-C']=[
#                  {'dir':'',
#                   'cmd': MAKECMD+' test',
#                   'check':[ NBcheckResult.rc0 ] },
                  ]

#CFG_BLD_INSTALL['ADOL-C']=[
#                  {'dir':'',
#                   'cmd': MAKECMD+' install' } ]

#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['metslib'] = 'mirko _DOT_ maischberger _AT_ gmail _DOT_ com'

CFG_BLD_POSTCHECKOUT['metslib'] = [ './autogen.sh' ]

CFG_BLD_TEST['metslib']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] },
                  ]

#do not install because it installs into /usr/local
#CFG_BLD_INSTALL['metslib']=[
#                  {'dir':'',
#                   'cmd': MAKECMD+' install' } ]

#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['MOCHA'] = 'dchaws _AT_ gmail _DOT_ com'

CFG_BLD_TEST['MOCHA']=[
#                  {'dir':'',
#                   'cmd': MAKECMD+' test',
#                   'check':[ NBcheckResult.rc0 ] },
                  ]

#do not install because it installs into /usr/local
CFG_BLD_INSTALL['MOCHA']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install' } ]

#does not have references to third party packages

#----------------------------------------------------------------------
