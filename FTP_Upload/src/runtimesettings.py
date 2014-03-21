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

# These settings are for experts
# Most users do not need to modify them

import logging

#
# These settings are used to run the program, test and write new code
#

# logging level for console output
console_log_level = logging.INFO

# logging level for output to log file(s)
logfile_log_level = logging.INFO

# max number of previous log files to save, one log file per day
logfile_max_days = 10

# frequency of saving the logfile
rotate = "midnight"

# name of log file
ftp_upload_log = 'ftp_upload.log'

# Frequency that the log time is written to server (in minutes)
# Note information in the log will not be uploaded between the last
# time the log is written and midnight
#save_log_time = 1
save_log_time = 60

# Flag to stop the main loop for test purposes.
# Only for manipulation by testing code; always set to False in this file
#
terminate_main_loop = False 

# Flag to indicate that there were files to be uploaded during main loop
# Only for use by testing code
#
uploads_to_do = False
#        
# encapsulate former if __name__ == "__main__" code in main() function for ease of testing

 
