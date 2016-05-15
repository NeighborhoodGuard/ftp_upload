#FTP_Upload#

###Summary###

FTP_Upload is part of a software suite from [Neighborhood Guard](http://neighborhoodguard.org) to upload images from IP cameras and organize them into Web pages for easy access and review.

FTP_Upload is an application written in Python intended run on a machine local to one or more IP cameras.  The camera(s) upload  images to this local machine either via FTP or by using it as a network share.  The local machine acts as a buffer to offload the camera images quickly, then copy them upstream to a server elsewhere on the Internet, as upstream bandwidth and server availability permit.

Uploaded images are stored on locally after upload for a retention period set by "retain_days" - watch that you don't set this too long and fill up your storage.

The FTP_Upload software takes care of transferring these image files to the server via FTP, then deleting them from the local machine once they have been successfully transferred and the retention period has elapsed.

###Installation and Configuration###

Program is traditionally installed in directory /ftp_upload

- localsetting.py contains the settings that are particular to your installation - you should localize this file, you should not change the file ftp_upload.py

In the following example the paths for setup on Raspberry Pi (PiGuard) is used.
- set the incoming_location to /home/pi/images.incoming
- incoming_location = "/home/pi/images.incoming"
- set the processed_location to /home.pi.images.uploaded
- processed_location = "/home/pi/images.uploaded"


set the name of your cloud server “ftp.[your_neighborhood].org as ftp_server
- ftp_server = "ftp.ng_demo.org"
set your username and password for logging into your cloud server
- ftp_username = "ng_demo_user"
- ftp_password = "ng_demo_password"
set the destination directory on the cloud ftp server.
- ftp_destination = "/video" # remember to start with /


### Known Problem ###
Will fill up the disk under certain circumstances 
- No mechanism to reduce retained images if disk is approaching full
- No mechanism to reduce intake of new images, purge old not uploaded images if upload is unavailable.
No alerting of exceptions - fail silently.
Insecure upload using ftp (password in clear text) 

###License###

FTP_Upload is open-source software available under the terms of the Affero GPL 3.0 license.  If the Affero GPL license does not meet your needs, other licensing arrangements are available from Neighborhood Guard, Inc.

###Contact Information###
If you have questions about this software, please contact:

Neighborhood Guard Development team

Douglas Kerr, dougk at halekerr dot com, Board member for Software, Neighborhood guard

or, 

Jesper Jurcennoks, jesper at jurcenoks dot com, President of Neighborhood guard
