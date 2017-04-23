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

sep = "/"

# the relative path from the ftp_testing_root to the testing destination directory.
# This points to the same directory as ftp_destination below
#
ftp_testing_dest = "cloud"

#
##### Configuration Section 
#
# Generally, the variables above and below this section won't need to be
# changed.
#

# top-level directory on the testing machine under which the directories for the
# incoming and processed files, and the simulated cloud server FTP directory
# will be located.  The testing code tacitly assumes all three of these
# directories will be under the same parent directory on the test machine.
#
ftp_testing_root = "/home/testuser/ftp_upload_test"

ftp_username = "testuser"
ftp_password = "testpasswd"

# this is the path of the FTP destination directory (the root of the tree into
# which files will be written on the cloud server) relative to the FTP login
# directory
#
ftp_destination = sep + "ftp_upload_test" + sep + ftp_testing_dest

#
##### End of Configuration Section 
#
# Generally, the variables above and below this section won't need to be
# changed.
#

# Set up the testing values for the ftp_upload global vars
#
incoming_location = ftp_testing_root + sep + "incoming"
processed_location = ftp_testing_root + sep + "processed" 
    
ftp_server = "localhost"

