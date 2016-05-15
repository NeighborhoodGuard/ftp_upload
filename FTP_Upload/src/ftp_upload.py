################################################################################
################################################################################
#
# Copyright (C) 2013-2016 Neighborhood Guard, Inc.  All rights reserved.
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

######################################################################################
#                                                                                    #
# Program to upload images as part of the Neighborhood Guard software suite.         #
# Program only uploads files and directories whose pathnames conform to the          #
# date/time format.                                                                  #
#                                                                                    #
######################################################################################


# Standard Python Libraries
import os.path
import shutil
import datetime
import re
import time
import ftplib
import threading
import logging.handlers
import sys
import traceback
import signal
import getopt
import socket
import platform
import subprocess
import string
import itertools
import mimetools
import mimetypes
import urllib
import urllib2

# Local library part of ftp_upload
import localsettings


# 3rd Party libraries not part of default Python and needs to be installed
if localsettings.use_sftp==True:
    import pysftp # pip install pysftp 

version_string = "1.8.0"

current_priority_threads=0 # global variable shared between threads keeping track of running priority threads.

try:
    use_http_post = localsettings.use_http_post
except AttributeError:
    logging.warning("http post variables not found")
    use_http_post = False
 


#########################################################################
#
# MultiPartForm copied from https://pymotw.com/2/urllib2/#uploading-files
#
# License: https://pymotw.com/2/about.html
# The source code included here is copyright Doug Hellmann and licensed under the BSD license.
#
# Copyright Doug Hellmann, All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright notice appear in all copies and that both
# that copyright notice and this permission notice appear in supporting documentation, and that the name of
# Doug Hellmann not be used in advertising or publicity pertaining to distribution of the software without
# specific, written prior permission.
#
# DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER 
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH
#  THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
#########################################################################

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


def http_post(filepath, camera, date=None, status=False):

    logging.info("trying to upload %s via http" % filepath)

    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    # Add the username and password.
    # If we knew the realm, we could use it instead of None.
    password_mgr.add_password(None, localsettings.http_post_url, localsettings.http_username, localsettings.http_password)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)

    urllib2.install_opener(opener)
    
    form = MultiPartForm()
    form.add_field('camera', camera)
    if status:
        form.add_field('status', 'true')
    
    if date<>None:
        form.add_field('date', date)
        
    form.add_field('submit', 'submit')

    # Add the file
    form.add_file('file', os.path.basename(filepath), fileHandle=open(filepath))

    request = urllib2.Request(localsettings.http_post_url)

    body = str(form)
    request.add_header('Content-type', form.get_content_type())
    request.add_header('Content-length', len(body))
    request.add_data(body)
    
    logging.debug("data ='%s'" % body)
    try:
        response = urllib2.urlopen(request)
        response_code = response.getcode()
    except urllib2.URLError, e:
        logging.warning("urlopen error '%s'" % e)
        response_code = 599
        
    logging.info("http response: %s" % response_code)

    return response_code
 

def mkdir(dirname):
    try:
        os.mkdir(dirname)
    except:
        pass


def rmdir(dirname):
    try:
        os.rmdir(dirname)
    except:
        pass

def change_create_server_dir(server_connection, dirname):
    logging.debug("FTP_UPLOAD:Starting change_create_server_dir()")

    # dirname is relative or absolute

    if use_http_post:
        logging.debug("no creating is directories when using http_post")
    else:
        if server_connection != None:
            if localsettings.use_sftp == True:
                try:
                    server_connection.cwd(dirname)
                except IOError, e :
                    try:
                        server_connection.mkdir(dirname)
                        server_connection.cwd(dirname)
                    except Exception, e:
                        logging.warning("FTP_UPLOAD:can't make sftp directory %s" % dirname)
                        logging.exception(e)
            else:
                try:
                    server_connection.cwd(dirname)
                except ftplib.error_perm :
                    try:
                        server_connection.mkd(dirname)
                        server_connection.cwd(dirname)
                    except Exception, e:
                        logging.warning("FTP_UPLOAD:can't make ftp directory %s" % dirname)
                        logging.exception(e)
            #endif
    logging.debug("FTP_UPLOAD:Ending change_create_server_dir()")
    return

def dir2date(indir):
    #extract date from indir style z:\\ftp\\12-01-2
    searchresult = re.search(r".*/([0-9]{4})-([0-9]{2})-([0-9]{2})", indir)
    if searchresult == None:     #extract date from indir style 12-01-2
        searchresult = re.search(r".*([0-9]{4})-([0-9]{2})-([0-9]{2})", indir)
        
    if searchresult != None:
        year= int(searchresult.group(1))
        month = int(searchresult.group(2))
        day = int(searchresult.group(3))
    else:
        year = None
        month = None
        day = None

    return (year, month, day)


def get_daydirs(location):
    daydirlist = os.listdir(location)

    daydirs=[]
    for direc in daydirlist:
        (year, unused_month, unused_day) = dir2date(direc)
        dirpath = os.path.join(location, direc)
        if os.path.isdir(dirpath) and year != None:
            daydirs.append((dirpath,direc))
        #endif 
    daydirs = sorted(daydirs)

    return daydirs


def connect_to_server():
    logging.debug("FTP_UPLOAD:Starting connect_to_server()")

    server_connection = None
    if use_http_post :
        logging.debug("No connect to server when using http POST")
    else:
        
        if localsettings.use_sftp==True:
            # SFTP Version
            try:
                server_connection = pysftp.Connection(localsettings.ftp_server, username=localsettings.ftp_username,password=localsettings.ftp_password)
                logging.debug("FTP_UPLOAD: Connected to %s", localsettings.ftp_server)
                logging.debug("FTP_UPLOAD:current directory is: %s", server_connection.pwd)
                logging.debug("FTP_UPLOAD:changing directory to: %s", localsettings.ftp_destination)
                server_connection.cwd(localsettings.ftp_destination)
                logging.debug("FTP_UPLOAD:current directory is: %s", server_connection.pwd)
            except pysftp.SSHException, e:
                if e=="Error reading SSH protocol banner" :
                    logging.info("timeout connecting to SSH on cloud server - Server overloaded?")
                else :
                    logging.error("FTP_UPLOAD:Unexpected exception in connect_to_server():")
                    logging.exception(e)
                if server_connection != None:
                    server_connection.close()  # close any connection to cloud server
                server_connection = None
            except Exception, e:
                logging.error("FTP_UPLOAD:Unexpected exception in connect_to_server():")
                logging.exception(e)
                if server_connection != None:
                    server_connection.close()  # close any connection to cloud server
                server_connection = None
            #endif
                
        else:
            # FTP Version
            try:
                server_connection = ftplib.FTP(localsettings.ftp_server,localsettings.ftp_username,localsettings.ftp_password,timeout=30)
                logging.debug(server_connection.getwelcome())
                logging.debug("FTP_UPLOAD:current directory is: %s", server_connection.pwd())
                logging.debug("FTP_UPLOAD:changing directory to: %s", localsettings.ftp_destination)
                server_connection.cwd(localsettings.ftp_destination)
                logging.debug("FTP_UPLOAD:current directory is: %s", server_connection.pwd())
            except ftplib.error_perm, e:
                logging.error("FTP_UPLOAD:Failed to open FTP connection, %s", e)
                server_connection = None
                message = "Sleeping " + str(localsettings.sleep_err_seconds/60) + " minutes before trying again"
                logging.info(message)
                time.sleep(localsettings.sleep_err_seconds)
            except Exception, e:
                logging.error("FTP_UPLOAD:Unexpected exception in connect_to_server():")
                logging.error("FTP_UPLOAD: localsettings.ftp_server = %s", localsettings.ftp_server)
                logging.exception(e)
                if server_connection != None:
                    server_connection.close()  # close any connection to cloud server
                server_connection = None
         # endif
    #endif
    logging.debug("FTP_UPLOAD:Ending connect_to_server()")   
    return server_connection

def quit_server(server_connection):
    logging.debug("FTP_UPLOAD:Starting quit_server()")

    # no need for "if use_http_post" here as server_connection is None when using http POST and if it is not then lets close it.

    if server_connection != None :
        if localsettings.use_sftp==True:
            # SFTP Version
            try:
                server_connection.close()
                logging.debug("FTP_UPLOAD:ftp connection successfully closed")
            except Exception, e:
                logging.warning("FTP_UPLOAD:Exception during FTP.quit():")
                logging.exception(e)
        else:
            # FTP Version
            try:
                server_connection.quit()
                logging.debug("FTP_UPLOAD:ftp connection successfully closed")
            except Exception, e:
                logging.warning("FTP_UPLOAD:Exception during FTP.quit():")
                logging.exception(e)
    logging.debug("FTP_UPLOAD:Ending quit_server()")
    return
    
def putfile(server_connection, ftp_dir, filepath, filename):
    # server_connection - established ftp or sftp connection
    # ftp_dir - the directory on the ftp server where the files are stored
    # filepath - the directory and filename to the local file where the file is coming from
    # filename - filename of the file to upload, this is used on the ftp server, locally it is contained in the filepath

    if use_http_post:
        logging.info("FTP_UPLOAD:Uploading %s", filepath)
        pathlist = os.path.dirname(filepath).split(os.sep)
        
        camera = pathlist[-1]
        date = pathlist[-2]
        
        if http_post(filepath, camera, date) == 200:
            success=True
            logging.info("FTP_UPLOAD:file : %s stored via http post", filename)
        else:
            success=False
            logging.info("FTP_UPLOAD:file : error during http post upload of %s", filename)
    else:
        
        change_create_server_dir(server_connection, ftp_dir)
        logging.info("FTP_UPLOAD:Uploading %s", filepath)
        try:
            if localsettings.use_sftp==True:
                server_connection.put(filepath, remotepath=ftp_dir+"/"+filename, preserve_mtime=True)
            else:
                filehandle = open(filepath, "rb")
                server_connection.storbinary("STOR " + filename, filehandle)
                filehandle.close()
            #endif
            logging.info("FTP_UPLOAD:file : %s stored on ftp", filename)
            success=True
        except Exception, e:
            logging.error("FTP_UPLOAD:Failed to store ftp file: %s: %s", filepath, e)
            logging.exception(e)
            filehandle.close()
            success=False
        
    return success

    
def storefile(ftp_dir, filepath, donepath, filename, today):
    # ftp_dir - the directory on the ftp server where the files are stored
    # filepath - the directory and filename to the local file where the file is coming from
    # donepath - this is where the file goes once it has been uploaded.
    # filename - filename of the file to upload, this is used on the ftp server, locally it is contained in the filepath
    # today - flag telling process the priority to assign to the work.
    
    logging.debug("FTP_UPLOAD:Starting storefile()")
    
    global current_priority_threads
    if today:
        current_priority_threads += 1
        logging.info("FTP_UPLOAD:current Priority threads %s", current_priority_threads)
        
    server_connection = connect_to_server()
    if server_connection != None or use_http_post == True :
        if putfile(server_connection, ftp_dir, filepath, filename) :
            logging.info("FTP_UPLOAD:moving file to Storage")

            try:
                # if the directory we want to move the file into doesn't exist,
                # create it.  This is a hack.  It's intended to recover from the
                # case where the purge process has deleted an old storage day-
                # directory, but for whatever reason, there are still files in
                # the incoming area for that day that need to be FTP'd to the
                # server
                #
                donedir = os.path.dirname(donepath)
                if not os.path.exists(donedir):
                    os.makedirs(donedir)
                    
                shutil.move(filepath, donepath)
            except Exception, e:
                logging.warning("FTP_UPLOAD:can't move file %s, possible sharing violation", filepath )
                logging.exception(e)

        else:
            message = "Sleeping " + str(localsettings.sleep_err_seconds/60) + " minutes before trying again"
            logging.info(message)
            time.sleep(localsettings.sleep_err_seconds)
                
        quit_server(server_connection)
    
    else :
        message = "Sleeping " + str(localsettings.sleep_err_seconds/60) + " minutes before trying again - general error"
        logging.info(message)
        time.sleep(localsettings.sleep_err_seconds)
    # end if

    if today :
        current_priority_threads -= 1
        
    logging.debug("FTP_UPLOAD:Ending storefile()")
        
    return

def storedir(dirpath, ftp_dir, done_dir, today):
    global current_priority_threads
    
    logging.info("FTP_UPLOAD:starting storedir()")
    logging.info("FTP_UPLOAD:dirpath = %s", dirpath)
    logging.info("FTP_UPLOAD:ftp_dir = %s", ftp_dir)
    logging.info("FTP_UPLOAD:done_dir = %s", done_dir)

    server_connection = connect_to_server()
    change_create_server_dir(server_connection, ftp_dir)
    quit_server(server_connection)
    
    mkdir(done_dir)
    
    files = sorted(os.listdir(dirpath))
    for filename in files:
        filepath = os.path.join(dirpath, filename)
        donepath = os.path.join(done_dir, filename)
        if os.path.isfile(filepath):

            current_threads = threading.active_count()
            logging.info("FTP_UPLOAD:current threads: %s", current_threads)

            if (current_threads >= localsettings.max_threads) or (not today and current_priority_threads>=localsettings.reserved_priority_threads):
                # to many threads running already, upload ftp in current thread (don't move forward until upload is done)
                storefile(ftp_dir, filepath, donepath, filename, today)
                current_threads = threading.active_count()
                logging.info("FTP_UPLOAD:current threads: %s", current_threads)
            else:
                
                # start new thread
                logging.info("FTP_UPLOAD:starting new storefile thread")
                threading.Thread(target=storefile, args=(ftp_dir, filepath, donepath, filename, today)).start()
                current_threads = threading.active_count()
                logging.info("FTP_UPLOAD:current threads: %s", current_threads)
            #end if
            
        elif os.path.isdir(filepath):
            logging.info("FTP_UPLOAD:Handling subdirectory %s", filepath)
            new_ftp_dir = ftp_dir + "/" + filename
            storedir(filepath, new_ftp_dir, donepath, today)
        # end if
    # end for

    rmdir(dirpath)
    logging.debug("FTP_UPLOAD:Ending storedir()")
    
    return

    
def deltree(deldir):
    logging.info("FTP_UPLOAD:deltree: %s", (deldir))
    files_to_be_deleted = sorted(os.listdir(deldir))
    for file2del in files_to_be_deleted:
        filepath = os.path.join(deldir, file2del)
        if os.path.isdir(filepath):
            deltree(filepath)
            rmdir(filepath)
        else:
            logging.info("FTP_UPLOAD:deleting %s", filepath)
            if localsettings.delete == False :
                logging.info("FTP_UPLOAD:would have deleted %s here - to really delete change delete flag to True", filepath)
            else :
                os.remove(filepath)
    rmdir(deldir)
    return

files_purged = False    # only used by testing code

def purge_old_images(purge_dir):
    global files_purged
    # Purge directories in Purge_dir, does not delete purge_dir itself
    purge_daydirs=get_daydirs(purge_dir)
    logging.debug("FTP_UPLOAD:list of directories to be purged: %s", purge_daydirs[0:-localsettings.retain_days])
    files_purged = False
    for purge_daydir in purge_daydirs[0:-localsettings.retain_days]:
        (dirpath, unused_direc) = purge_daydir
        logging.info("FTP_UPLOAD:purging directory %s", dirpath)
        deltree(dirpath)
        files_purged = True
    return


def isdir_today(indir):
    (processingyear,processingmonth, processingday) = dir2date(indir)
    current = datetime.date.today()

    return (processingyear==current.year and processingmonth == current.month and processingday==current.day)

    
def storeday(daydir, today=False):
    logging.debug("FTP_UPLOAD:Starting storeday()")

    try:
        (dirpath, direc) = daydir
        logging.info("FTP_UPLOAD:processing directory %s", direc)
        ftp_dir = localsettings.ftp_destination + "/" + direc
        done_dir = os.path.join(localsettings.processed_location, direc)
        storedir(dirpath, ftp_dir, done_dir, today)
    except Exception, e:
        logging.exception(e)
    
    logging.debug("FTP_UPLOAD:Ending storeday()")
    return

def storedays(daydirs):
    logging.debug("FTP_UPLOAD:Starting storedays()")
    try:
        for daydir in daydirs:
            storeday(daydir)
    except Exception, e:
        logging.error("FTP_UPLOAD:Unexpected exception in storedays()")
        logging.exception(e)
    logging.debug("FTP_UPLOAD:Ending from storedays()")
    return

def dumpstacks():
    '''For debugging purposes, dump a stack trace for each running thread
    to the log'''
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    logging.info("FTP_UPLOAD:User requested stack dumps"+("\n".join(code)))

def sighandler(signum, frame):
    dumpstacks()

def make_logfile_basename():

    logfile_basename = os.path.join(localsettings.base_location, "ftp_upload", 'ftp_upload.log')

    return  logfile_basename

def set_up_logging():
    if set_up_logging.not_done:
        # get the root logger and set its level to DEBUG
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # set up the rotating log file handler
        #
        logfile = logging.handlers.TimedRotatingFileHandler(make_logfile_basename(),
                when='midnight', backupCount=localsettings.logfile_max_days)
        logfile.setLevel(localsettings.logfile_log_level)
        logfile.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)-8s %(threadName)-10s %(message)s',
                '%m-%d %H:%M:%S'))
        logger.addHandler(logfile)
        
        # define a Handler which writes messages equal to or greater than
        # console_log_level to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(localsettings.console_log_level)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        set_up_logging.not_done = False       
set_up_logging.not_done = True  # logging should only be set up once, but
                                # set_up_logging() may be called multiple times when testing

def help():
    print "ftpupload.py [-h] [-s] [-l]"
    print "-h, --help       This help"
    print "-s, --status     Upload status to the cloud server and exit"
    print "-l, --log        Upload yesterdays logfile and exit"
    print "no options       Continously upload images to the cloud server"
    
    return
                                
# Flag to stop the main loop for test purposes.
# Only for manipulation by testing code; always set to False in this file
#
terminate_main_loop = False 

# Flag to indicate that there were files to be uploaded during main loop
# Only for use by testing code
#
uploads_to_do = False
        
# encapsulate former if __name__ == "__main__" code in main() function for ease of testing
#
    
def continous_upload():
    global uploads_to_do    # for testing only
    
    signal.signal(signal.SIGINT, sighandler)    # dump thread stacks on Ctl-C
    logging.info("FTP_UPLOAD:Program Started, version %s", version_string)
    try:
        mkdir(localsettings.processed_location)
        # Setup the threads, don't actually run them yet used to test if the threads are alive.
        processtoday_thread = threading.Thread(target=storeday, args=())
        process_previous_days_thread = threading.Thread(target=storedays, args=())

        purge_thread = threading.Thread(target=purge_old_images, args=())

        
        while True:
            
            daydirs = get_daydirs(localsettings.incoming_location)
            
            #reverse sort the days so that today is first
            daydirs = sorted(daydirs, reverse=True)
         
            # Today runs in 1 thread, all previous days are handled in 1 thread starting with yesterday and working backwards.
                
            previous = 0    # starting index of possible previous days' uploads
            uploads_to_do = False
            if len(daydirs) > 0:
                uploads_to_do = True
                if isdir_today(daydirs[0][0]):
                    if not processtoday_thread.is_alive():
                        processtoday_thread = threading.Thread(target=storeday, args=(daydirs[0],True))
                        processtoday_thread.start()
                    previous = 1
                    
            if len(daydirs) > previous:
                uploads_to_do = True
                # Only if previous days is not running, run it to check that everything is processed.
                if not process_previous_days_thread.is_alive():
                    process_previous_days_thread = threading.Thread(target=storedays, 
                                                                    args=(daydirs[previous:],))
                    process_previous_days_thread.start()


            if not purge_thread.is_alive():
                purge_thread = threading.Thread(target=purge_old_images, args=(localsettings.processed_location,))
                purge_thread.start()
                    
            
            logging.info("FTP_UPLOAD:Sleeping 1 minute for upload")
            logging.info("FTP_UPLOAD:Time is %s", time.ctime() )          
            try:
                 time.sleep(localsettings.sleep_upload) # sleep
                
            # hitting Ctl-C to dump the thread stacks will interrupt
            # MainThread's sleep and raise IOError, so catch it here
            except IOError, e:
                logging.warn("Main loop sleep interrupted")
                
            if terminate_main_loop:     # for testing purposes only
                break
    except Exception, e:
        logging.error("FTP_UPLOAD:Unexpected exception in main()")
        logging.exception(e)
        raise   # rethrow so unit test code will know something went wrong

        
    return

def get_local_ip():

    if platform.system()=="Windows":
        p = subprocess.Popen('ipconfig', shell = False, stdout=subprocess.PIPE)
        p.wait()
        rawtxt = p.stdout.read()

        wifi_interface = re.search('\n.*adapter Wireless Network Connection:.*?IPv4 Address. . . . . . . . . . . : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',rawtxt, flags=re.DOTALL)
        wifi_ip = wifi_interface.groups(0)[0]

        lan_interface = re.search('\n.*adapter Local Area Connection:.*?IPv4 Address. . . . . . . . . . . : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',rawtxt, flags=re.DOTALL)
        lan_ip = lan_interface.groups(0)[0]
    else:
        p = subprocess.Popen("""ifconfig wlan0 | awk '/addr:/ {print $2;}'| sed "s/addr://1" """, shell = True, stdout=subprocess.PIPE)
        p.wait()
        wifi_ip = string.strip(p.stdout.read())

        p = subprocess.Popen("""ifconfig eth0 | awk '/addr:/ {print $2;}'| sed "s/addr://1" """, shell = True, stdout=subprocess.PIPE)
        p.wait()
        lan_ip = string.strip(p.stdout.read())
  
    return wifi_ip, lan_ip
    
def get_os():
    if platform.system()=="Windows":
        os = "{system} {release}".format(system=platform.system(), release=platform.release())
    else:
        p = subprocess.Popen("""cat /etc/os-release | grep PRETTY_NAME | sed 's/PRETTY_NAME="//g' | sed 's/"//g'""", shell = True, stdout=subprocess.PIPE)
        p.wait()
        os = string.strip(p.stdout.read())
    
    return os

def ping(host):
    if platform.system()=="Windows":
        up = (os.system("ping -n 1 " + host) == 0)
    else:
        up = (os.system("ping -c 1 " + host) == 0)

    if up:
        connection="Good"
    else :
        connection="Bad "
        
    return connection

def get_gateway_ip():

    if platform.system()=="Windows":
        p = subprocess.Popen("""route print 0.0.0.0""", shell = True, stdout=subprocess.PIPE)
        p.wait()
        route_print_str = string.strip(p.stdout.read())
        
        searchresult=re.search("\n.*0.0.0.0\s*(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}.)",route_print_str,flags=re.DOTALL)
        gateway_ip=searchresult.groups(0)[0]
        
    else :
        p = subprocess.Popen("""route -n | grep -m 1 "^0.0.0.0" | awk '/0.0.0.0/ {print $2;}'""", shell = True, stdout=subprocess.PIPE)
        p.wait()
        gateway_ip = string.strip(p.stdout.read())

    
    return gateway_ip
    
def get_free_disk():
    if platform.system()=="Windows":
        p = subprocess.Popen("""dir""", shell = True, stdout=subprocess.PIPE)
        p.wait()
        dir_str = string.strip(p.stdout.read())
        
        searchresult=re.search("\n.*Dir\(s\)  ([0-9,]*)",dir_str,flags=re.DOTALL)
        freedisktext=searchresult.groups(0)[0]
        freedisk=int(freedisktext.replace(",",""))
        freediskstring=str(freedisk/1024/1024/1024)+"Gb"
    else:
        p = subprocess.Popen("""df -h / | grep "/dev/root" | sed 's/\/dev\/root *[0-9.]*[GMK] *[0-9.]*[GMK] *//1' | sed 's/ *[0-9]*% \///1'""", shell = True, stdout=subprocess.PIPE)
        p.wait()
        freediskstring = string.strip(p.stdout.read())
        
        p = subprocess.Popen("""df -h /mnt/ngdata | grep "/mnt/ngdata" | sed 's/\/dev\/sda. *[0-9.]*[GMK] *[0-9.]*[GMK] *//1' | sed 's/ *[0-9]*% \/mnt\/ngdata//1'""", shell = True, stdout=subprocess.PIPE)
        p.wait()
        freediskhddstring = string.strip(p.stdout.read())
    
        freediskstring = freediskstring + "   " + freediskhddstring
    
    return freediskstring

def get_day_image_count() :
    if platform.system()=="Windows":
        daycount=len(os.listdir(localsettings.incoming_location))
        imagecount=sum([len(files) for r, d, files in os.walk(localsettings.incoming_location)])
    else:
        cmdstring = """find {incoming_location}/. -type f -name '*.jpg' | wc -l""".format(incoming_location=localsettings.incoming_location)
        p = subprocess.Popen(cmdstring, shell = True, stdout=subprocess.PIPE)
        p.wait()
        daycount = string.strip(p.stdout.read())
        
        cmdstring = """ls -1 {incoming_location} | wc -l""".format(incoming_location=localsettings.incoming_location)
        p = subprocess.Popen(cmdstring, shell = True, stdout=subprocess.PIPE)
        p.wait()
        imagecount = string.strip(p.stdout.read())
        
        
    return (daycount, imagecount)
    
def status():

    logging.info("running ftp_upload:status")

    wifi_ip, lan_ip = get_local_ip()
    hostname=socket.gethostname()
    
    cameraconnection=ping("camera") #put a line in the hostfile to point camera at the camera's ip address
    wificonnection=ping(get_gateway_ip())
    internetconnection=ping("www.google.com")
    dreamhostconnection=ping(localsettings.ftp_server)
    
    (daycount, imagecount) = get_day_image_count()
     
    freedisk=get_free_disk()
     
    statusstr="{time}\n".format(time=time.ctime())
    statusstr+="Name: {name}\n".format(name=hostname)
    statusstr+="OS: {os}\n".format(os=get_os())
    statusstr+="Wi-FI   : {wifiip}\n".format(wifiip=wifi_ip)
    statusstr+="Ethernet: {lanip}\n".format(lanip=lan_ip)
    statusstr+="Connection\n"
    statusstr+=" Camera  : {cameraconnection}   Wi-Fi    : {wificonnection}\n".format(cameraconnection=cameraconnection, wificonnection=wificonnection)
    statusstr+=" Internet: {internetconnection}   Dreamhost: {dreamhostconnection}\n".format(internetconnection=internetconnection, dreamhostconnection=dreamhostconnection)
    statusstr+="Pending Upload: {daycount} Day(s) & {imagecount} Images\n".format(daycount=daycount, imagecount=imagecount)
    statusstr+="Free Disk: {freedisk}\n".format(freedisk=freedisk)
    logging.info(statusstr)
    
    statusfilename = "heartbeat.status"
    statusfile = open(statusfilename, "w")
    statusfile.write(statusstr)
    statusfile.close()
    
    if use_http_post == True:
    
        http_post(statusfilename, hostname, status=True)
        
    else :
        ftp_dir = localsettings.ftp_destination + "/status/" + hostname
        
        server_connection = connect_to_server()
        ftp_dir = localsettings.ftp_destination + "/status/"
        change_create_server_dir(server_connection, ftp_dir)
        ftp_dir += hostname
        
        if server_connection != None:
            if putfile(server_connection, ftp_dir, statusfilename, statusfilename) :
                logging.info("putfile of %s successful" % statusfilename)
            else:
                logging.info("putfile of %s error" % statusfilename)
            quit_server(server_connection)    
        
    return    
        
def log_yesterday():

    hostname=socket.gethostname()

    yesterday = datetime.date.today() - datetime.timedelta(1)
    datestring= yesterday.strftime("%Y-%m-%d")

    logfilepath = make_logfile_basename()+"." + datestring

   
    if use_http_post == True:
    
        http_post(logfilepath, hostname, status=True)
        
    else :
        ftp_dir = localsettings.ftp_destination + "/status/" + hostname
        
        server_connection = connect_to_server()
        ftp_dir = localsettings.ftp_destination + "/status/"
        change_create_server_dir(server_connection, ftp_dir)
        ftp_dir += hostname

        logfilename = os.path.basename(logfilepath)
        
        if server_connection != None:
            if putfile(server_connection, ftp_dir, logfilepath, logfilename) :
                logging.info("putfile of %s successful" % logfilename)
            else:
                logging.info("putfile of %s error" % logfilename)
            quit_server(server_connection)      
    
    return
        
        
def main(argv=None):
    set_up_logging()

    try:
      options, args = getopt.getopt(argv, "hsl",["status", "help", "log"])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for option, arg in options:
        if option in ("-h", "--help"):
            help()
            sys.exit()
        elif option in ("-s", "--status"):
            status()
            sys.exit()
        elif option in ("-l", "--log"):
            log_yesterday()
            sys.exit()
        else:
            logging.error("unhandled option")
            sys.exit()
    #end for
    logging.info("no option")
    continous_upload()

    return
    
if __name__ == "__main__":
    main(sys.argv[1:])
