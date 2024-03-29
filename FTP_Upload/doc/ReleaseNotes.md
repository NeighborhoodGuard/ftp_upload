# Release Notes for FTP_Upload

## v2.4.0 - 2023/09/04
_Doug Kerr_

* Upgrade to Python 3
* Upgrade to Ubuntu 22.04 LTS
* Fix minor bugs

### Known Issues

* With the current implementation of `avahi-daemon`, it may be theoretically impossible to guarantee that `findaxiscam` will be able to find the DHCP (as opposed to ZeroConf) address of the Axis camera if the machine it's running on has more than one network interface.
* The installation and configuration code expects that the cloud server's upload account (the account on the cloud server to which images files will be uploaded) can be accessed via SSH using a password.  In cases such as AWS where use of a password is deprecated in favor of using a private-public keys, there is no provision yet in the configuration code to enter a private key for access to the upload account.  For the installation software to succeed, the private key must be copied to `~/.ssh/id_rsa` in the upload machine's maintenance account prior to running the installation software.
* The remote access code incorrectly handles the target machine name in a case sensitive manner.  Until this is fixed, the machine name entered when running `starttunnel` must be identical in case to the name given to the machine during the setup process.
* Sometimes the tunnel test (`test_tunnel`) in `testSystem.sh` fails on the first attempt, even though the tunnel software is properly set up.
* Need to add a graceful shutdown mechanism so that, for example, FTP connections are not terminated in mid-transfer.
* The main test in `testSystem.sh`, `test_ftp_upload` currently requires that the test server's upload account home directory be the root of the file tree accessible via FTP.  This is not the case for the current CommunityView server, so the test will fail if the CommunityView server is used.
* The internal `current_priority_threads` counter appears to slowly increase, rather than reflecting the correct number of threads that are uploading the files for "today."  Increases are on the order of one bogus count for every 5,000 to 10,000 files transferred.  This is not a major problem, but has the effect of slowly eliminating the multi-threading for transferring the current day's images, resulting in reduced performance. Workaround: restart the program.

## v2.3.1 - 2020/03/05
_Doug Kerr_

* Fix bug in `findaxiscam`.
* Implement `addllroute` service to insure that there is a link-local (aka ZeroConf) route in the routing table. This should maximize the chance that `findaxiscam` will be able to find a camera on the local network.


## v2.3.0 - 2020/02/22
_Doug Kerr_

* Test on Ubuntu Server 18.04 LTS.  Fix bugs related to inconsistencies between 16.04 and 18.04, and bugs related to installing on a Server rather than Desktop version of the OS.
## v2.2.0 - 2020/01/30
_Doug Kerr_

* Improve the prompts in the configuration GUI.
* Put the installer configuration file, `uploader.conf`, into a standard directory, `/etc/opt/ftp_upload`.
* Fix a bug wherein the installer would sometimes ask for a passphrase when generating an SSH key.
* Make various improvements to the documentation.

## v2.1.0 - 2018/08/22
_Doug Kerr_

* Version 2.1.0 adds the `findaxiscam` utility and its associated manual page.  `Findaxiscam` is a Linux command-line utility that finds Axis IP cameras on the local network in a manner similar to the Axis IP Utility.

## v2.0.0 - 2018/07/28
_Doug Kerr_

* Version 2.0.0 includes an automated installation and configuration mechanism for Debian Linux derivatives.  It was designed and tested on Ubuntu 16.04 LTS and has not yet been tested on other Debian derivatives.
* Also included is software to allow remote access to the upload machine using SSH tunnels.
* The `ftp_upload` program is now installed as a Linux service along with the remote access tunnel daemon `cktunnel`.  * The `ftp_upload.py`program is now configured via a .conf file, rather than in Python directly, and the `localsettings.py` file has been eliminated.
* The `ftp_upload.py` code has not been materially changed in this release, other than for the new .conf file configuration mechanism.  It has been tested on Windows as well as Linux.

## v1.5.5 - 2017/04/14
_Doug Kerr_

* Fix long-standing bug wherein image files would occasionally be FTPed to the destination directory on the cloud server, rather than the _date_/_location_ subdirectory below the destination directory.
* Fix the testing code (originally developed on Windows) to work on both Linux and Windows.
* Add Developer Notes in the doc directory explaining how to set up and run the testing code.


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
