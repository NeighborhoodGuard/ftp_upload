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
ftp_testing_root = "C:/fup_testing" 

# Set up the testing values for the ftp_upload global vars
#
sep = "/"
incoming_location = ftp_testing_root + sep + "incoming"
processed_location = ftp_testing_root + sep + "processed" 
    
ftp_server = "localhost"
ftp_username = "ng"
ftp_password = "ng"
ftp_destination = sep + "destination"

