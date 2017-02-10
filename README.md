# FTP_Upload #

### Summary ###

FTP_Upload is part of a software suite from 
[Neighborhood Guard](http://neighborhoodguard.org) 
to upload images from IP cameras and organize them into Web pages for 
easy access and review.

FTP_Upload is an application written in Python intended run on a machine
local to one or more IP cameras.  The camera(s) upload  images to this
local machine either via FTP or by using it as a network share. 
The local machine acts as a buffer to offload the camera images quickly,
then copy them upstream to a server elsewhere on the Internet, as
upstream bandwidth and server availability permit.

The FTP_Upload software takes care of transferring these image files to
the server via FTP, then deleting them from the local machine once they
have been successfully transferred and an expiration period has elapsed.

### Installation and Configuration ###
See the [Installation](FTP_Upload/doc/Installation.md)
documentation in the `FTP_Upload/doc` directory.

### Remote Access ###
The FTP_Upload software package includes a remote access mechanism that
allows users to connect to and manage
the upload machine from anywhere on the Internet
even though the upload machine is likely behind a NAT firewall.
Please see the [Remote Access](FTP_Upload/doc/RemoteAccess.md)
documentation in the `FTP_Upload/doc` directory.

### Developer Information ###
Developers should read the [Release Notes](FTP_Upload/doc/ReleaseNotes.md)
and the [Developer Notes](FTP_Upload/doc/DeveloperNotes.md)

### License ###
FTP_Upload is open-source software available under the terms of the
Affero GPL 3.0 license.  If the Affero GPL license does not meet your
needs, other licensing arrangements are available from
Neighborhood Guard, Inc.

### Contact Information ###
If you have questions about this software, please contact:

Douglas Kerr, dougk at halekerr dot com, Board member for Software
