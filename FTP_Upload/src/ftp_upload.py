################################################################################
#
# Copyright (C) 2013-2018 Neighborhood Guard, Inc.  All rights reserved.
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

######################################################################################
#                                                                                    #
# Program to upload images as part of the Neighborhood Guard software suite.         #
# Program only uploads files and directories whose pathnames conform to the          #
# date/time format.                                                                  #
#                                                                                    #
######################################################################################



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
import StringIO
import ConfigParser
import platform

version_string = "2.3.1"

    
max_threads = 8 # max number of total threads when needed one thread will be used for purging job, rest of time all threads will be used for upload.
reserved_priority_threads = 3 # previousdays can only upload multithreaded when running today threads fall below this number.
current_priority_threads=0 # global variable shared between threads keeping track of running priority threads.


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

        
def change_create_ftp_dir(ftp_connection, dirname):
    # dirname is relative or absolute
    
    if ftp_connection != None:
        try:
            ftp_connection.cwd(dirname)
        except ftplib.error_perm :
            try:
                ftp_connection.mkd(dirname)
                ftp_connection.cwd(dirname)     
            except Exception, e:
                logging.warning("can't make/change to ftp directory %s" % dirname)
                logging.exception(e)
                return False
        
    return True

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
    daydirs = sorted(daydirs)

    return daydirs	


def connect_to_ftp():
    ftp_connection = None   
    try:
        ftp_connection = ftplib.FTP(cfg.ftp_server, cfg.ftp_username, 
                                    cfg.ftp_password, timeout=30)
        logging.debug(ftp_connection.getwelcome())
        logging.debug("current directory is: %s", ftp_connection.pwd())
        logging.debug("changing directory to: %s", cfg.ftp_destination)
        ftp_connection.cwd(cfg.ftp_destination)
        logging.debug("current directory is: %s", ftp_connection.pwd())
    except ftplib.error_perm, e:
        logging.error("Failed to open FTP connection, %s", e)
        ftp_connection = None
        logging.info("Sleeping 10 minutes before trying again")
        time.sleep(600)
    except Exception, e:
        logging.error("Unexpected exception in connect_to_ftp():")
        logging.exception(e)
        if ftp_connection != None:
            ftp_connection.close()  # close any connection to cloud server
        ftp_connection = None
        
    return ftp_connection

def quit_ftp(ftp_connection):
    if ftp_connection != None :
        try:
            ftp_connection.quit()
            logging.debug("ftp connection successfully closed")
        except Exception, e:
            #logging.warning("Exception during FTP.quit():", e)
            logging.warning("Exception during FTP.quit():")
            logging.exception(e)

    
def storefile(ftp_dir, filepath, donepath, filename, today):
    global current_priority_threads
    if today:
        current_priority_threads += 1
        logging.info("current Priority threads %s", current_priority_threads)
        
    ftp_connection = connect_to_ftp()
    if ftp_connection != None:
        if not change_create_ftp_dir(ftp_connection, ftp_dir):
            # if we can't create or change to the ftp_dir for some reason
            # (probably transient), abort storing the file, and let it be
            # picked up by the main loop next time around
            logging.warn("storefile: aborting; couldn't change to %s" % ftp_dir)
            quit_ftp(ftp_connection)
            if today:
                current_priority_threads -= 1
            return
            
        logging.info("Uploading %s", filepath)
        try:
            filehandle = open(filepath, "rb")
            ftp_connection.storbinary("STOR " + filename, filehandle)
            filehandle.close()
            logging.info("file : %s stored on ftp", filename)
            logging.info("moving file to Storage")

            try :
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
                logging.warning("can't move file %s, possible sharing violation", filepath )
                logging.exception(e)

        except Exception, e:
            logging.error("Failed to store ftp file: %s: %s", filepath, e)
            logging.exception(e)
            filehandle.close()
            logging.info("Sleeping 10 minutes before trying again")
            time.sleep(600)
                
        quit_ftp(ftp_connection)
    
    else :
        time.sleep(600)
    # end if

    if today :
        current_priority_threads -= 1

    return

def storedir(dirpath, ftp_dir, done_dir, today):
    global current_priority_threads
    global reserved_priority_threads
    
    logging.info("starting storedir")
    logging.info("dirpath = %s", dirpath)
    logging.info("ftp_dir = %s", ftp_dir)
    logging.info("done_dir = %s", done_dir)

    ftp_connection = connect_to_ftp()
    dir_ok = change_create_ftp_dir(ftp_connection, ftp_dir)
    quit_ftp(ftp_connection)
    if not dir_ok:
        # if we can't create or change to the ftp_dir for some reason
        # (probably transient), abort storing the dir, and let it be
        # picked up by the main loop next time around
        logging.warn("storedir: aborting; couldn't change to %s" % ftp_dir)
        return
    
    mkdir(done_dir)
    
    files = os.listdir(dirpath)
    for filename in files:
        filepath = os.path.join(dirpath, filename)
        donepath = os.path.join(done_dir, filename)
        if os.path.isfile(filepath):
#            storefile(ftp_dir, filepath, donepath, filename)

            current_threads = threading.active_count()
            logging.info("current threads: %s", current_threads)

            if (current_threads >= max_threads) or (not today and current_priority_threads>=reserved_priority_threads):
                # to many threads running already, upload ftp in current thread (don't move forward until upload is done)
                storefile(ftp_dir, filepath, donepath, filename, today)
                current_threads = threading.active_count()
                logging.info("current threads: %s", current_threads)
            else:
                
                # start new thread
                logging.info("starting new storefile thread")
                threading.Thread(target=storefile, args=(ftp_dir, filepath, donepath, filename, today)).start()
                current_threads = threading.active_count()
                logging.info("current threads: %s", current_threads)
            #end if
            
        elif os.path.isdir(filepath):
            logging.info("Handling subdirectory %s", filepath)
            new_ftp_dir = ftp_dir + "/" + filename
            storedir(filepath, new_ftp_dir, donepath, today)
        # end if
    # end for

    rmdir(dirpath)
    
    return

    
def deltree(deldir):
    logging.info("deltree: %s", (deldir))
    files_to_be_deleted = sorted(os.listdir(deldir))
    for file2del in files_to_be_deleted:
        filepath = os.path.join(deldir, file2del)
        if os.path.isdir(filepath):
            deltree(filepath)
            rmdir(filepath)
        else:
            logging.info("deleting %s", filepath)
            if cfg.delete == False :
                logging.info("would have deleted %s here - to really delete change delete flag to True", filepath)
            else :
                os.remove(filepath)
    rmdir(deldir)
    return

files_purged = False    # only used by testing code

def purge_old_images(purge_dir):
    global files_purged
    # Purge directories in Purge_dir, does not delete purge_dir itself
    purge_daydirs=get_daydirs(purge_dir)
    logging.debug("list of directories to be purged: %s", purge_daydirs[0:-cfg.retain_days])
    files_purged = False
    for purge_daydir in purge_daydirs[0:-cfg.retain_days]:
        (dirpath, unused_direc) = purge_daydir
        logging.info("purging directory %s", dirpath)
        deltree(dirpath)
        files_purged = True
    return


def isdir_today(indir):
    (processingyear,processingmonth, processingday) = dir2date(indir)
    current = datetime.date.today()

    return (processingyear==current.year and processingmonth == current.month and processingday==current.day)

    
def storeday(daydir, today=False):
    try:
        (dirpath, direc) = daydir
        logging.info("processing directory %s", direc)
        ftp_dir = cfg.ftp_destination + "/" + direc
        done_dir = os.path.join(cfg.processed_location, direc)
        storedir(dirpath, ftp_dir, done_dir, today)
    except Exception, e:
        logging.exception(e)
    
    return

def storedays(daydirs):
    logging.info("Starting storedays()")
    try:
        for daydir in daydirs:
            storeday(daydir)
    except Exception, e:
        logging.error("Unexpected exception in storedays()")
        logging.exception(e)
    logging.info("Returning from storedays()")
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
    logging.info("User requested stack dumps"+("\n".join(code)))

def sighandler(signum, frame):
    dumpstacks()

def set_up_logging():
    if set_up_logging.not_done:
        # get the root logger and set its level to DEBUG
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # set up the rotating log file handler
        #
        logfile = logging.handlers.TimedRotatingFileHandler('ftp_upload.log', 
                when='midnight', backupCount=cfg.logfile_max_days)
        logfile.setLevel(cfg.logfile_log_level)   # will be reset shortly in main()
        logfile.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)-8s %(threadName)-10s %(message)s',
                '%m-%d %H:%M:%S'))
        logger.addHandler(logfile)
        
        # define a Handler which writes messages equal to or greater than
        # console_log_level to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(cfg.console_log_level)  # will be reset shortly in main()
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        set_up_logging.not_done = False 
set_up_logging.not_done = True  # logging should only be set up once, but
                                # set_up_logging() may be called multiple times when testing
    
class Config():
    pass

cfg = Config()

def conf_log_level(level_str):
    d = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARN,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
        }
    return d.get(level_str)

def get_config(confpath=None):
    global cfg
    
    if get_config.done:
        return True
    
    # set up the default config values
    defaults = {
        'delete': 'True',
        'retain_days': '6',
        'console_log_level': 'info',
        'logfile_log_level': 'info',
        'logfile_max_days': '10'
        }
    
    # if the confpath has been supplied, use it. Otherwise,
    # select a search path for the config file based on the OS.
    # 
    plat = platform.system()
    if confpath:
        search = (".",)
    elif plat == "Windows":
        search = (".",)
    elif plat == "Linux":
        search = (".", "/etc/opt/ftp_upload", "/etc/ftp_upload", "/etc")
    else:
        search = (".",)
        
    # open and read the config file. If we can't find a config file,
    # return with an error
    #
    if not confpath:
        confpath = "ftp_upload.conf"
    file_str = None
    for searchdir in search:
        try:
            path = os.path.join(searchdir, confpath)
            file_str = open(path, 'r').read()
            if file_str:
                break
        except IOError:
            pass
    if not file_str:
        return False
    
    # parse the config file    
    #
    sect = "forcedsection"
    conf_str = "[" + sect + "]\n"  + file_str
    conf_fp = StringIO.StringIO(conf_str)
    cp = ConfigParser.SafeConfigParser(defaults)
    cp.readfp(conf_fp)
    
    # save the config items in the global config object
    #
    cfg.incoming_location = cp.get(sect, "incoming_location")
    cfg.processed_location = cp.get(sect, "processed_location")
    cfg.ftp_server = cp.get(sect, "ftp_server")
    cfg.ftp_username = cp.get(sect, "ftp_username")
    cfg.ftp_password = cp.get(sect, "ftp_password")
    cfg.ftp_destination = "/" + cp.get(sect, "ftp_destination")
    cfg.delete = cp.getboolean(sect, "delete")
    cfg.retain_days = cp.getint(sect, "retain_days")
    cfg.console_log_level = conf_log_level(cp.get(sect, "console_log_level"))
    cfg.logfile_log_level = conf_log_level(cp.get(sect, "logfile_log_level"))
    cfg.logfile_max_days = cp.getint(sect, "logfile_max_days")
    
    get_config.done = True
    return True
get_config.done = False # Config should only be set up once.
                        # This flag prevents multiple setups when get_config()
                        # is called multiple times during testing.


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
def main():
    global uploads_to_do    # for testing only
    
    if not get_config():
        print >> sys.stderr, "ftp_upload: Can't open config file!"
        sys.exit(1)
        
    set_up_logging()
    
    signal.signal(signal.SIGINT, sighandler)    # dump thread stacks on Ctl-C
    logging.info("Program Started, version %s", version_string)
    try:
        mkdir(cfg.processed_location)
        # Setup the threads, don't actually run them yet used to test if the threads are alive.
        processtoday_thread = threading.Thread(target=storeday, args=())
        process_previous_days_thread = threading.Thread(target=storedays, args=())

        purge_thread = threading.Thread(target=purge_old_images, args=())

        
        while True:
            
            daydirs = get_daydirs(cfg.incoming_location)
            
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
                purge_thread = threading.Thread(target=purge_old_images, 
                                                args=(cfg.processed_location,))
                purge_thread.start()
                    
            
            logging.info("Sleeping 1 minute for upload")
            logging.info("Time is %s", time.ctime() )          
            try:
                time.sleep(60) # sleep 1 minute
                
            # hitting Ctl-C to dump the thread stacks will interrupt
            # MainThread's sleep and raise IOError, so catch it here
            except IOError, e:
                logging.warn("Main loop sleep interrupted")
                
            if terminate_main_loop:     # for testing purposes only
                break
    except Exception, e:
        logging.error("Unexpected exception in main()")
        logging.exception(e)
        raise   # rethrow so unit test code will know something went wrong

if __name__ == "__main__":
    main()
