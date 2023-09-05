# Developer Notes for FTP_Upload #

## Introduction
With release v2.0.0, we added a simple installer for Debian-derivative Linux systems.  We also added a remote access mechanism that works via SSH tunnels.  Additionally, the tunnel daemon, `cktunnel` and `ftp_upload` program are now run as Linux services.

In release v2.1.0, we added the `findaxiscam` utility, along with its manual page, to find Axis IP cameras on the local network.

In release v2.4.0, the Python code was upgraded to Python 3 and the overall
package was upgraded to run on Ubuntu 22.04 LTS.

## Unit and System Tests ##
### Overview ###
There are unit tests and system tests included for much of the code.  We use PyUnit (which is part of the standard Python distribution) for the Python code tests  and [shunit2](http://manpages.ubuntu.com/manpages/trusty/man1/shunit2.1.html) to test the shell scripts such as `configupload.sh` and its supporting files.  The tests for a given set of code are generally in a `test` subdirectory below the code that will be tested.  These tests are intended to be run on the development machine to validate functionality as the code is being worked on.

There is also a simple system test that performs an end-to-end check of the both the `ftp_upload` and the `cktunnel` functionality after the installation is complete.

### System Tests
In `FTP_Upload/test` there is a simple system test called `testSystem.sh` that uses `shunit2` to provide test library support.  This test must be run on the upload machine (not the development machine) after the installation process is complete.  The cloud server that the machine is configured to upload to must also be available.
_N.B.: As of release v2.4.0, some of the tests in testSystem.sh are buggy and
will be fixed in future releases._

To run the tests, change to the `FTP_Upload/test` directory on the upload machine, and give the command,

     sh testSystem.sh

The first test will place some files image files in the incoming directory for `ftp_upload`, and wait until the files are transferred to the cloud server (may take up to one minute). It then checks the cloud server filesystem to see that the files arrived in the proper place.

The second test checks the remote access functionality by requesting a tunnel from the upload machine through the cloud server and back to the upload machine, and verifies that commands can be executed over it.  You will be asked to type the password for your account on the upload machine during the test.  This is not really a "remote" access test, but it does check the functionality of the tunnel system.

The third and fourth tests check `findaxiscam` and its associated manual page.

At the end of the test run, you should see the following:

    Ran 4 tests.
    
    OK


### `configupload` Unit Tests
The unit tests for the `configupload` code are in the `FTP_Upload/configupload/test` directory, and use the `shunit2` library.  

Some of the tests validate the code that sets up a key pair with the cloud server (`testKeys.sh`).  These tests require a test account on an accessible test server as a stand in for the cloud server.  Prior to running the tests, copy the file `test_example.conf` to `test.conf`, and edit it to supply the test server name, account and account password.

Run the tests by giving the following commands in either order:

    sh testUtils.sh
    sh testKeys.sh

At the end of the test run, you should see the following:

    Ran n tests.
    
    OK

where `n` is replaced by the number of tests in each test suite.

### `ftp_upload` Program Tests
The FTP_Upload "unit tests" were written long after application code was developed, and are more along the lines of system tests than anything else.  The tests are written using PyUnit, which is the standard testing framework for Python, and is included in the Python distribution as the `unittest` library module.  These tests, like the `ftp_upload` code itself, work under both Linux and Windows.

The test code expects a local FTP server to be running on the test machine and an FTP account set up for testing so that FTP_Upload can upload files via FTP as it would during normal operation, and the uploaded files along with their directory structure can be verified for correctness by the test code. The tests set up an "incoming" directory for FTP_Upload to be used as the root of the file tree into which images are placed with appropriate pathnames, i.e., in the form,

>
>*incoming_directory*/*date*/*location*/*image_name*.jpg
> 

In production, this directory would be where the local camera(s) would deliver the *date*/*location*/*image_name*.jpg files so that they can be uploaded to the cloud server.

The tests also set up a "processed" directory into which FTP_Upload will place the images (with the same pathname structure) once the images have been uploaded to the local test FTP server.

Finally, the test code sets up a "cloud" directory to be the destination directory that the local test FTP server will use as the root of the file tree into which image files will be deposited by the process of FTP_Upload uploading the test image files.

All three of the above directories will be set up under a single "testing root" directory.

### Test Setup and Configuration ###

#### Configuration Variables ####

The configuration settings for the tests are placed in `FTP_Upload/src/test/test.conf`.  You can copy the sample configuration file, `test_example.conf` to `test.conf` and edit the example settings so that they reflect your testing setup.  

The configuration settings file is made up of name-value pairs in the form,

>
>*name* = *value*
>

The name must start at the left margin (no indentation), and the value part of the pair is entered without quotation marks.  Whitespace is optional on either side of the equals sign, and leading and trailing spaces are removed from the value.

The `ftp_login_path` configuration item needs to be set to the full path (in the file system of the local machine) of the FTP login directory of the test FTP account.

The `ftp_testing_dir` item should be set to the path of the directory under which all the test files will be written (the "testing root" mentioned above) relative to the `ftp_login_path`.  As a safety measure, this directory must already exist in order for the tests to run. All other test directories, i.e., the incoming, processed and cloud directories, will be created under the `ftp_testing_dir` as needed by the test code or by FTP_Upload during the test runs.  If the FTP testing root directory should be the test FTP login directory, set the `ftp_testing_dir` to "." (no quotes).

The `ftp_username` and `ftp_password` can be left as they are or changed, as long as a corresponding user name and password are set up on the local FTP server.  Under Linux, it may be easiest to set the user name and password to that of the user running the tests, and set up the `ftp_testing_dir` to point to somewhere under that user's home directory.

It is essential that both the user account under which the tests are being run and the test FTP account that is used to upload files have permissions to read and write all files and directories in the tree rooted at `ftp_testing_dir`.  See the next section for more information.


#### Local FTP Server ####

As mentioned above, there must be an FTP server set up on the test machine so that FTP_Upload can actually transfer files using FTP.

For a Linux test machine, we recommend ProFTPd as we have tested successfully with it and it is also the FTP server currently in use at DreamHost.

For a Windows test machine, we have no server recommendation at this writing.  We have tested with FileZilla, which has easy installation and configuration, but also allows multiple-level directory paths to be created in a single command, e.g., MKDIR a/b/c where none of a, b or c exist before the command is given.  This is not the behavior of ProFTPd, and this FileZilla behavior masked a bug in testing of FTP_Upload until this was understood.

You will need to have an account set up on the local FTP server for the test code to use that has the same user name and password as are configured in `test.conf`.  Both the account under which the tests are being run, and the testing account on the local test FTP server must have all permissions on the `ftp_testing_dir` directory.  That is, both accounts must be able to read, write, create and delete files and directories.  As mentioned above, it's probably easiest to configure the test setup such that the same account is used to both run the tests, and to log into the FTP server.

#### Unix/Linux Utilities ####

The test code uses three Unix/Linux utilities, `ls`, `sed` and `diff`, to help analyze the results produced by testing FTP_Upload.  Therefore, these three commands must be available in the execution path (`PATH` environment variable) of the test process.  If the tests are being run under Windows, these are not part of the standard command set.

When running under Windows, the simplest way to get these commands into the execution path is to install Git (which you probably already installed in order to download the FTP_Upload repository), and then to run the tests from the `Git Bash` command line. `Git Bash` includes a very complete set of Unix/Linux utilities in its execution path, including these three.  You can also run the tests from the Windows command line by adding the appropriate path to your execution path, e.g., `C:\Program Files\Git\bin`.

Lastly, Windows versions of the `ls`, `sed` and `diff` utilities can also be found in the [UnxUtils package available from SourceForge](unxutils.sourceforge.net).

#### PYTHONPATH Environment Variable ####

The tests are located in the `FTP_Upload/src/test` directory, while the FTP_Upload code that is being tested is located in the `FTP_Upload/src` directory.  If you are not using the Eclipse IDE, in order for the test code to find the FTP_Upload code, you must set the `PYTHONPATH` environment variable to include the path to the FTP_Upload code.  For example, if you make `FTP_Upload/src/test` your current directory before executing the tests, you could simply say in `Git Bash`,

	PYTHONPATH=..; export PYTHONPATH

or on the Windows command line,

	set PYTHONPATH ..
	
If you are using Eclipse, it will set the `PYTHONPATH` automatically.

### Running the Tests ###

The easiest way to run the tests is to `cd` to the `FTP_Upload/src/test` directory and give the command,

	python3 -u TestUpload.py
	
If you are using Eclipse, just select TestUpload.py either in the source window or the Package Explorer and click the Run button.

The test produces a lot of output, because FTP_Upload sends all of its logging output to the console as well as to the log file.  (The log file is created in the current directory.)  What you're looking for is that at the end of the test run, the Python `unittest` package should print a couple lines similar to,

	Ran 4 tests in 18.486s
	
	OK

which indicates that all the test passed.  Otherwise, it will print a failure message for each test that failed, showing its name and where in the code the failure occurred.  
