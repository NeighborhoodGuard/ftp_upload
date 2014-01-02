################################################################################
#
# Copyright (C) 2013 Neighborhood Guard, Inc.  All rights reserved.
# Original author: Douglas Kerr
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


# top-level directory on the testing machine under which the directories for the
# incoming and processed files, and the simulated cloud server FTP directory
# will be located.  The testing code tacitly assumes all three of these
# directories will be under the same parent directory on the test machine. Also,
# there are a lot of Windows-specific assumptions in the testing code.  Work
# needs to be done to untangle this, and make the code portable to non-Windows
# testing systems
#
ftp_testing_root = "test_system_ftp_root_directory" 

# Set up the testing values for the ftp_upload global vars
#
sep = "/"
incoming_location = ftp_testing_root + sep + "test_system_incoming_directory"
processed_location = ftp_testing_root + sep + "test_system_processed_directory" 
    
ftp_server = "test_ftp_server_hostname"
ftp_username = "test_ftp_server_username"
ftp_password = "test_ftp_server_password"
ftp_destination = sep + "test_ftp_server_destination_directory"

