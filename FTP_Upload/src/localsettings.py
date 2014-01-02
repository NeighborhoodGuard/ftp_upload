################################################################################
#
# Copyright (C) 2013 Neighborhood Guard, Inc.  All rights reserved.
# Original author: Jesper Jercenoks
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

incoming_location = "your_incoming_directory"
processed_location = "your_processed_directory" # Make sure this directory is NOT below the incoming_location as you will be creating an endlees upload loop
	
ftp_server = "your_ftp_server_name"
ftp_username = "your_user_name"
ftp_password = "your_password"
ftp_destination = "/your_destination_dir" # remember to start with /
delete=True # Change to True for Purge to work
	
	
retain_days = 6 # number of days to retain local images. (not on the FTP server)

# Logger settings
#

# logging level for console output
console_log_level = logging.INFO

# logging level for output to log file(s)
logfile_log_level = logging.INFO

# max number of previous log files to save, one log file per day
logfile_max_days = 10

