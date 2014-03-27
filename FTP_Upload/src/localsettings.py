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
#   "incoming_location" is the location of the uploaded images from the camera  #
#   "processed_location" is where uploaded images are stored                     #
#   "ftp_server" is the name of the ftp_server                                   #
#   "ftp_username" is the username to the ftp server                             #
#   "ftp_password" is the password to the ftp server                             #
#   "ftp_destinationn" is the directory on the ftp server for the images         #
#   ftp_destination must exist (safety check)                                    #
#                                                                                #
##################################################################################

incoming_location = "/home/pi/images.incoming"  # the sample values are the defaults for RaspGuard
processed_location = "/home/pi/images.uploaded" # Make sure this directory is NOT below the incoming_location as you will be creating an endlees upload loop

ftp_server = "ftp.ng_demo.org"
ftp_username = "ng_demo_user"
ftp_password = "ng_demo_passowrd"
ftp_destination = "/video.yourneighborhood.org" # remember to start with /
delete=True # must be True for Purge to work
	
	
retain_days = 6 # number of days to retain local images (on the Raspberry Pi). (Data retention on the destination FTP server is set somewhere else)

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

