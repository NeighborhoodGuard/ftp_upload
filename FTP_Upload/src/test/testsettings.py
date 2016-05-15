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


# Top-level directory on the testing machine under which the directories for the
# incoming and processed files, and the simulated cloud server FTP directory
# will be located.  The testing code expects all three of these
# directories to be under the same parent directory on the test machine.
# As a safety measure, this directory must exists in order for the tests to run.
#
# This variable is the only variable that definitely needs to be
# configured for your test setup. The value shown is just an example. 
#
ftp_testing_root = "C:/fup_testing"

#
# The remaining variables below can be left as is.
#

# The information needed to access the local FTP server on the testing machine.
# These values may be left as is or changed, but an account must exist with the
# configured user name and password on the test FTP server.
#
ftp_server = "localhost"
ftp_username = "ng"
ftp_password = "ng"


# The sub-directories of ftp_testing_root.  These are created automatically
# by the test code.
#
sep = "/"
incoming_location = ftp_testing_root + sep + "incoming"
processed_location = ftp_testing_root + sep + "processed" 
ftp_destination = sep + "destination"
    
