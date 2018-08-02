# Release Notes for FTP_Upload

## v2.0.0 - 2018/07/28
_Doug Kerr_

* Version 2.0.0 includes an automated installation and configuration
mechanism for Debian Linux derivatives.  It was designed and tested on 
Ubuntu 16.04 LTS and has not yet been tested on other Debian derivatives.
* Also included is software to allow remote access to the upload machine
using SSH tunnels.
* The `ftp_upload` program is now installed as a Linux service along with 
the remote access tunnel daemon `cktunnel`.
* The `ftp_upload.py`program is now configured via a .conf file, 
rather than in Python
directly, and the `localsettings.py` file has been eliminated.
* The `ftp_upload.py` code has not been materially changed in this release, 
other than for the new .conf file configuration mechanism.  It has been tested
on Windows as well as Linux.

### Known Issues

* Need to add a graceful shutdown mechanism so that, for example, FTP connections are not terminated in mid-transfer.
* The internal `current_priority_threads` counter appears to slowly increase, rather than reflecting the correct number of threads that are uploading the files for "today."  Increases are on the order of one bogus count for every 5,000 to 10,000 files transferred.  This is not a major problem, but has the effect of slowly eliminating the multi-threading for transferring the current day's images, resulting in reduced performance. Workaround: restart the program.

## v1.5.5 - 2017/04/14
_Doug Kerr_

* Fix long-standing bug wherein image files would occasionally be FTPed to the
destination directory on the cloud server, rather than the _date_/_location_ 
subdirectory below the destination directory.
* Fix the testing code (originally developed on Windows) to work on both
Linux and Windows.
* Add Developer Notes in the doc directory explaining how to set up and run
the testing code.


## v1.5.1 - 2014/02/12
_Doug Kerr_

* Fix FTP timeout setting.  FTP timeout was not active in previous release due to coding error.
* Fix typo in README.

## v1.5 - 2013/12/31
_Doug Kerr, Howard Matis_

* Add log rotation.
* Normalize line endings.
* Remove rename of extant log file on startup.  The code now appends to any extant `ftp_upload.log` file at startup.
* Add version string and print to log at startup.
* Add AGPL 3.0 permission statement to source files, and add full text of license to repo.
* Add/update copyright strings to reflect ownership by Neighborhood Guard, Inc.
* Move release notes from ftp_upload.py to this file.
* Add README file.

## v1.4 - 2013/09/21
_Doug Kerr_

* Add timeout to FTP connection to prevent threads from hanging.

## v1.3 - 2013/09/14
_Doug Kerr_

* Rename extant log file on startup.
* Dump all thread stacks to log on Ctl-C/Keyboard Interrupt.
