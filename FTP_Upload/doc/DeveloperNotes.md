# Developer Notes for FTP_Upload #
## Unit Tests ##
### Overview ###

The FTP_Upload "unit tests" were written long after application 
code was developed, and are more along the lines of system tests 
than anything else.  The tests are written using PyUnit, which is the
standard test framework for Python, and is included in the Python
distribution as the `unittest` library module.

The test code expects an FTP server to be running on the test
machine so that FTP_Upload can upload files via FTP as it would
during normal operation, and the uploaded files along with their 
directory structure can be verified for correctness by the test code.

The tests set up an incoming directory for FTP_Upload to be used
as the root of the file tree into which 
images are placed with appropriate pathnames, i.e., in the form

>
>*incoming_directory*/*date*/*location*/*image_name*.jpg
> 

The tests also set up a "processed" directory into which 
FTP_Upload will place the images (with the same pathname
structure) once the images have been uploaded to the FTP server.

Finally, the test code sets up a directory to be the destination
directory that the FTP server will use as the root of the file
tree created by the process of FTP_Upload uploading the test
image files.

### Test Setup and Configuration ###

#### Configuration Variables ####

The configuration variables for the tests are found in 
`FTP_Upload/src/test/testsettings.py`.

The `ftp_testing_root` variable should be set to the full
path of the directory in the test machine's file system under
which all the test files will be written.  As a safety measure,
this directory must already exist 
in order for the tests to run. All other test directories, e.g.,
the incoming, processed and FTP destination directories, will be
created under the `ftp_testing_root` as needed by the test code or 
by FTP_Upload during the test runs.

The `ftp_server` can probably be left set to the default `localhost`,
since the FTP server is expected to be running directly on the test
machine.

The `ftp_username` and `ftp_password` can be left as they are or
changed, as long as a corresponding user name and password are set
up on the local FTP server.

### Local FTP Server ###

As mentioned above, there must be an FTP server set up on the test
machine so that FTP_Upload can actually upload files using FTP.
For a Windows test machine, we recommend using FileZilla Server
for ease of installation and configuration, though
any FTP server should work.

You will need to set up an account on the FTP server for the test code
that has the same user name and password as have been set in 
`testsettings.py`.  Set the account's home directory to be the same as
the `ftp_testing_root` you configured in `testsettings.py`, and give
the account all permissions on that directory, e.g., read, write,
create files and directories, delete files and directories, etc.

### Unix/Linux Utilities ###

The test code uses a couple of Unix/Linux utilities, `ls` and `sed`, 
to help analyze the results produced by testing FTP_Upload.
Therefore, these two commands must be available in the execution path 
(`PATH` variable) of the test process.  If the tests are being run
under Windows, these are not part of the standard command set.

When running under Windows, the simplest way to set this up is
to install Git (which you probably already installed in order to 
download the FTP_Upload repository), and then to run the tests from the
`Git Bash` command line.  `Git Bash` includes a very complete set of
Unix/Linux utilities in its execution path, including `ls` and `sed`.
You can also run the tests
from the Windows command line by adding the appropriate path to your
execution path, e.g., `\Program Files\Git\bin`.

Lastly, Windows versions of `ls` and `sed` utilities can also be found in the 
[UnxUtils package available from SourceForge](unxutils.sourceforge.net).

### PYTHONPATH Environment Variable ###

The tests are located in the directory `FTP_Upload/src/test` 
while the FTP_Upload
code that is being tested is located in the `FTP_Upload/src` directory.
In order for the test code to find the FTP_Upload code, you must set
the `PYTHONPATH` environment variable to include the path to the 
FTP_Upload code.  For example, if you make `FTP_Upload/src/test` 
your current
directory before executing the tests, 
you could simply say in `Git Bash`,

	PYTHONPATH=..; export PYTHONPATH

or on the Windows command line,

	set PYTHONPATH ..

### Running the Tests ###

The easiest way to run the tests is to `cd` to the `FTP_Upload/src/test` directory and
give the command,

	python TestUpload.py

The test produces a lot of output, because FTP_Upload sends all of its
logging output to the console as well as to the log file.  (The log
file is created in the current directory.)  What you're looking for is
that at the end of the test run, the Python `unittest` package should
print a couple lines similar to,

	Ran 4 tests in 18.486s
	
	OK

which indicates that all the test passed.  Otherwise, it will print
a failure message for each test that failed, showing its name and
where in the code the failure occurred.  