################################################################################
#
# Copyright (C) 2013-2014 Neighborhood Guard, Inc.  All rights reserved.
# Original author: Jesper Jurcenoks
# Maintained by the Neighborhood Guard development team
# 
# This file is part of FTP_Upload.
# 
# FTP_Upload is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# FTP_Upload is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with FTP_Upload.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import logging

##################################################################################
#                                                                                #
#   "base_location" is the folder where images are stored (end with a slash)     #
#   "incoming_location" is the location of the uploaded images from the camera   #
#   "processed_location" is where uploaded images are stored                     #
#   "ftp_server" is the name of the ftp_server                                   #
#   "ftp_username" is the username to the ftp server                             #
#   "ftp_password" is the password to the ftp server                             #
#   "ftp_destination" is the directory on the ftp server for the images          #
#   ftp_destination must exist (safety check)                                    #
#                                                                                #
##################################################################################

ftp_server = "ftp.ng_demo.org"    # Always change this
ftp_username = "ng_demo_user"     # and this 
ftp_password = "ng_demo_password" # and this

ftp_destination = "/communityview.yourneighborhood.org" # you must change this
# remember to start with /
# this is the relative path from your home directory

# specific locations are created below this directory
base_location = "/home/pi/"  # Default for Images on SD Card
#base_location = "/mnt/ngdata/" # Default for Images on Harddisk

incoming_location = base_location + "images.incoming"  # the sample values are the defaults for RaspGuard
processed_location = base_location + "images.uploaded" # Make sure this directory is NOT below the incoming_location as you will be creating an endlees upload loop

sleep_err_seconds = 600  #Time to sleep when error (Default = 600)
sleep_upload = 60		 #Time to sleep for new pictures (Default = 60)   (Useful to change during testing)

delete=True # must be True for Purge to work
	
use_sftp = False

if use_sftp==True:
  ftp_destination = "/home/" + ftp_username + ftp_destination

use_http_post = False # True is recommended but requires that communityview_upload_image.py is installed on the server
http_username =  "web_user" #notice this is the username and password of the web-user e.g. the same as people viewing the video
http_password = "web_users_password" # and thus NOT the password used by ftp or sftp to upload images.
http_post_url = "http://communityview.yourneighborhood.org/communityview/communityview_upload_image.py"

  
retain_days = 2 # number of days to retain local images (on the Raspberry Pi). (Data retention on the destination Cloud server is set somewhere else)

# Logger settings
#

# logging level for console output
console_log_level = logging.INFO

# logging level for output to log file(s)
logfile_log_level = logging.INFO

# max number of previous log files to save, one log file per day
logfile_max_days = 10

# thread settings
max_threads = 2 # max number of total threads when needed one thread will be used for purging job, rest of time all threads will be used for upload.
reserved_priority_threads = 1 # previousdays can only upload multithreaded when running today threads fall below this number.

