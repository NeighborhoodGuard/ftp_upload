# Release Notes for FTP_Upload

## v1.5.1 - 2014/02/12
_Doug Kerr_

* Fix FTP timeout setting.  FTP timeout was not active in previous release due to coding error.
* Fix typo in README.

### Known Issues

* Need to add a graceful shutdown mechanism so that, for example, FTP connections are not terminated in mid-transfer.
* Occasionally, image files will be FTPed to the login directory on the FTP server in the cloud, rather than to _date_/_location_ subdirectory on the server. Workaround: restart the program.
* The internal `current_priority_threads` counter appears to slowly increase, rather than reflecting the correct number of threads that are uploading the files for "today."  Increases are on the order of one bogus count for every 5,000 to 10,000 files transferred.  This is not a major problem, but has the effect of slowly eliminating the multi-threading for transferring the current day's images, resulting in reduced performance. Workaround: restart the program.


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
