#------------------------------------------------------------------------
# This file is distributed under the Common Public License.
# It is part of the TestTools project in COIN-OR (www.coin-or.org)
#------------------------------------------------------------------------

import getopt
import sys

def printUsage() :
    print "Usage: "+sys.argv[0]+" [-p <parameterfile> | --paramfile=<parameterfile>]"


def getParameterFile() :

    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:", ["paramfile"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        printUsage()
        sys.exit(2)
        
    paramfile = "NBuserParameters.py"
    for o, a in opts:
        if o in ("-p", "--paramfile"):
            paramfile = a
        else:
            assert False, "unhandled option"

    return paramfile
