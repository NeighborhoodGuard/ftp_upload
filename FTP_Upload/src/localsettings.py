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

##################################################################################
#                                                                                #
#   "base_loacatation" is the folder where images are stored (end with a slash)  #
#   "incoming_location" is the location of the uploaded images from the camera   #
#   "processed_location" is where uploaded images are stored                     #
#   "ftp_server" is the name of the ftp_server                                   #
#   "ftp_username" is the username to the ftp server                             #
#   "ftp_password" is the password to the ftp server                             #
#   "ftp_destinationn" is the directory on the ftp server for the images         #
#   ftp_destination must exist (safety check)                                    #
#                                                                                #
##################################################################################

	
ftp_server = "charingcrosssherwick.org"
ftp_username = "ftptestcamera"
ftp_password = "TestingFTP"
ftp_destination = "/video" # remember to start with / - This folder must exist
log_destination = "/logfiles/6824Sherwick" # remember to start with / - This folder must existbase_location = "/Users/matis/cameratest/sftp/"
base_location = "/Users/family/cameratest/sftp/"  
incoming_location = base_location + "new"
processed_location = base_location + "uploaded" # Make sure this directory is NOT below the incomming_location as you will be creating an endlees upload loop
	
sftp_server = "charingcrosssherwick.org"
sftp_username = "charingsherwicksftp"
sftp_password = "CameraOnStreet"
sftp_destination = "/home/charingsherwicksftp/video" # remember to start with / - This folder must exist

sleep_err_seconds = 180  #Time to sleep when error (Default = 600)
sleep_upload = 10		 #Time to sleep for new pictures (Default = 60)   (Useful to change during testing)
delete=True # Change to True for Purge to work
		
retain_days = 6 # number of days to retain local images. (not on the FTP server)

