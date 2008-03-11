#! /usr/bin/env python

#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the BuildTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import os
import NBcheckResult

try :
  # Can not import this on some platforms because they may not have MySQLdb
  import NBcbcRunTimes
except ImportError:
  importedCbcRunTimes=False
else :
  importedCbcRunTimes=True

#to get MAKECMD  
execfile('NBuserParametersDefault.py')
execfile('NBuserParameters.py')

#----------------------------------------------------------------------
# This file defines variables which describe how the specific
# coin-or projects are to be tested and who are their managers.
#----------------------------------------------------------------------

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS = {}
SLN_BLD_TEST = {}
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
                             NBcheckResult.standardSuccessMessage ] } ]

CFG_BLD_INSTALL['CoinUtils']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

CFG_BLD_VALGRIND_TEST['CoinUtils']=[
                  {'dir':'CoinUtils/test',
                   'cmd': ' valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check':[] } ]


SLN_BLD_TEST['CoinUtils']=[
                  {'dir':r'CoinUtils\MSVisualStudio',
                   'cmd':'v8\unitTestCoinUtils\Release\unitTestCoinUtils',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage] },
                  {'dir':r'CoinUtils\MSVisualStudio',
                   'cmd':'v8\unitTestCoinUtils\Debug\unitTestCoinUtils',
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
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

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
                             NBcheckResult.endWithWoodw] } ]
CFG_BLD_INSTALL['Clp']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_BLD_TEST['Clp']=[
                  {'dir':r'Clp\MSVisualStudio\v8\clp\Release',
                   'cmd':'clp -dirSample=_SAMPLEDIR_ -unitTest -dirNetlib=_NETLIBDIR_ -netlib',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage,
                             NBcheckResult.endWithWoodw] },
                  {'dir':r'Clp\MSVisualStudio\v8\clp\Debug',
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
                             NBcheckResult.standardSuccessMessage ] } ]

CFG_BLD_INSTALL['SYMPHONY']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_BLD_TEST['SYMPHONY']=[ {
                   'dir':r'SYMPHONY\MSVisualStudio\v8\Release',
                   'cmd':r'symphony -F _NETLIBDIR_\25fv47.mps',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':r'SYMPHONY\MSVisualStudio\v8\Debug',
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
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Osi'] = 'mjs _AT_ ces _DOT_ clemson _DOT_ edu'
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
                             NBcheckResult.noSolverInterfaceTestingIssueMessage] } ]

CFG_BLD_INSTALL['Osi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_BLD_TEST['Osi']=[
                  {'dir':r'Osi\MSVisualStudio\v8\OsiExamplesBuild\Release',
                   'cmd':'OsiExamplesBuild',
                   'check':[ NBcheckResult.rc0 ] },
                  {'dir':r'Osi\MSVisualStudio\v8\OsiExamplesBuild\Debug',
                   'cmd':'OsiExamplesBuild',
                   'check':[ NBcheckResult.rc0 ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Cgl'] = 'robinlh _AT_ us _DOT_ ibm _DOT_ com'
CFG_BLD_TEST['Cgl']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

CFG_BLD_INSTALL['Cgl']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Cbc'] = 'jjforre _AT_ us _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['Cbc']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.cbcMakeTestSuccessMessage ] },
                  {'dir': os.path.join('Cbc','src'),
                   'cmd': '.'+os.sep+'cbc -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] } ]

if importedCbcRunTimes :
  CFG_BLD_TEST['Cbc'][1]['check'].append(NBcbcRunTimes.cbcSaveRuntimes)


CFG_BLD_INSTALL['Cbc']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_BLD_TEST['Cbc']=[
                  {'dir':r'Cbc\MSVisualStudio\v8\cbcSolve\Release',
                   'cmd':'cbcSolve -dirSample=_SAMPLEDIR_ -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] },
                  {'dir':r'Cbc\MSVisualStudio\v8\cbcSolve\Debug',
                   'cmd':'cbcSolve -dirSample=_SAMPLEDIR_ -unitTest -dirMiplib=_MIPLIB3DIR_ -miplib',
                   'check':[ NBcheckResult.rc0to2 ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Ipopt'] = 'andreasw _AT_ us _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['Ipopt']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['Ipopt']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

#third party packages are not optional here

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Bonmin'] = 'pierre _DOT_ bonami _AT_ lif _DOT_ univ-mrs _DOT_ fr'

CFG_BLD_TEST['Bonmin']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['Bonmin']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]
#third party packages are not optional here

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['FlopC++'] = 'Tim _DOT_ Hultberg _AT_ eumetsat _DOT_ int'

CFG_BLD_TEST['FlopC++']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

CFG_BLD_INSTALL['FlopC++']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_FILE['FlopC++']=r'FlopCpp.sln'
SLN_DIR['FlopC++']=r'FlopCpp\MSVisualStudio\v8'
SLN_BLD_TEST['FlopC++']=[
                  {'dir':r'FlopCpp\MSVisualStudio\v8\Release',
                   'cmd':'unitTest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] },
                  {'dir':r'FlopCpp\MSVisualStudio\v8\Debug',
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
                             NBcheckResult.standardSuccessMessage ] } ]


CFG_BLD_VALGRIND_TEST['OS']=[
                  {'dir':'OS/test',
                   'cmd': ' valgrind --tool=memcheck --leak-check=full  --show-reachable=yes ./unitTest',
                   'check':[] } ]


CFG_BLD_INSTALL['OS']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

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
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['CoinAll'] = 'tkr2 _AT_ lehigh _DOT_ edu'
CFG_BLD_TEST['CoinAll']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['CoinAll']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['CppAD'] = 'bradbell _AT_ washington _DOT_ edu'

CFG_BLD_TEST['CppAD']=[
                  {'dir':'',
                   'cmd': os.path.join('.','example','example'),
                   'check':[ NBcheckResult.rc0 ] }, 
                  {'dir':'',
                   'cmd': os.path.join('.','test_more','test_more'),
                   'check':[ NBcheckResult.rc0 ] } ]

CFG_BLD_INSTALL['CppAD']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]
#does not have references to third party packages

#----------------------------------------------------------------------
PROJECT_EMAIL_ADDRS['Smi'] = 'kingaj _AT_ us _DOT_ ibm _DOT_ com'

CFG_BLD_TEST['Smi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' test',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.endWithStarDoneStar ] } ]

CFG_BLD_INSTALL['Smi']=[
                  {'dir':'',
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_BLD_TEST['Smi']=[
                  {'dir':r'Smi\test',
                   'cmd':r'..\MSVisualStudio\v8\unitTestSmi\Release\smiUnitTest',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.endWithStarDoneStar ] },
                  {'dir':r'Smi\test',
                   'cmd':r'..\MSVisualStudio\v8\unitTestSmi\Debug\smiUnitTest',
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
                   'cmd': MAKECMD+' install',
                   'check':[ NBcheckResult.rc0,
                             NBcheckResult.standardSuccessMessage ] } ]

SLN_BLD_TEST['GAMSlinks']=[ ]
#does have references to third party packages
