# TestTools

The Test Tools project provides Python scripts to automatically:

 1. download
 1. configure 
 1. build
 1. test
 1. install
 1. build binaries

of COIN-OR projects.  If a failure is recognized, the scripts can send an e-mail to the corresponding project manager.

The Test Tools project is managed by JP Fasano. Contributors are JP Fasano, Kipp Martin, and Stefan Vigerske.

## Usage of Test Tools

The main program is nightlyBuild.py.

First, a user need to specify some parameters, e.g., the directory where nightlyBuild checks out and builds project.

Parameters for nightlyBuild are specified via two Python scripts:

 * `NBuserParametersDefault.py` contains default values of all parameters. It should not be modified by the user since it receives updates together with other nightlyBuild scripts.
 * `NBuserParameters.py` is the user specific parameter file. nightlyBuild reads this file after `NBuserParametersDefault.py`, so it should be used to overwrite default values.

To setup parameters, the user should
```
  cp NBuserParametersDefault.py NBuserParameters.py
  vi NBuserParameters.py
```
The nightlyBuild parameters are documented in NBuserParametersDefault.py.
See also the INSTALL file for more information. 

The main script is *nightlyBuild.py*. Assuming Python is in your PATH variable you can invoke nightlyBuild by simply entering at the command line
```
python nightlyBuild.py
```

## What nightlyBuild does...

For each supported COIN-OR project a set of build types can be specified.
A *build type* is a tuple of information containing the

 * `SvnVersion`: which version from the svn repository to built (trunk, latestStable, latestRelease, stable/0.1, ...)?
 * `OptLevel`: should the code be build in optimized mode ("Default") or debugging mode ("Debug")
 * `ThirdParty`: should it be allowed to use third party codes
 * `SkipProjects`: a list of COIN-OR projects (from the externals) that should be skipped in the build
 * `AdditionalConfigOptions`: additional flags for the configure call
 * `Run`: whether to run after always, after changes, or if previously unsuccessful
 * `Distribute`: whether created binaries should be uploaded into the CoinBinary repository
 * `BuildTypeInfo`: an info on the build type to include into the archive file name

For such a build type, nightlyBuild does

 1. *Checkout* the specified version from the svn repository (https://projects.coin-or.org/svn/<project>/...).
 1. *Download third party codes* for which `get.XXX` scripts can be found.
 1. Assemble the parameter for the configure call.
 1. Call *configure*. If there is an error, send a failure report as e-mail and break.
 1. Call *make*. If there is an error, send a failure report as e-mail and break.
 1. If the project has a *test program*, call make test. If there is an error, send a failure report as e-mail and break.
 1. If the project has *unit tests*, call the unit tests. If there is an error, send a failure report as e-mail and break.
 1. If valgrind tests are turned on and the project has a valgrind test specified, valgrind is run on this test. An e-mail with the report of this test is send out.
 1. Run *make install* which will put any libraries that are built into a *lib* directory, any executables into a *bin* directory and the necessary header files into an *include* directory. If there is an error, send a failure report as e-mail and break.
 1. If the user specifies BUILD_BINARIES = 1 then a *zipped archive* is created of the project libraries, binaries, and header files. 
    The string BUILD_INFORMATION is included into the name of the zipped archive. It should specify the platform and compiler.
    The zipped archive is stored in a subdirectory NIGHTLY_BUILD_ROOT_DIR/binaries/<projectname>. 
 1. If distribution of the current build type is turned on, the zipped archive is uploaded into the CoinBinary repository.

There are also rules implemented to avoid the rebuild and test of a project if there has been no change in the code since the last build.

The failure reports contain, next to information about the build type and the system, also the output to stdout and stderr and a config.log file if configure failed.

The output of get.XXX scripts, configure, make, unittests to stdout and stderr is also stored in the build directories for later analysis (e.g., NBmake.stdout).

See the INSTALL file for more information.
