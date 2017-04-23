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

import unittest
import ftp_upload
import datetime
import os.path
import shutil
import time
import threading
import ftplib
import subprocess
import logging
import random
import testsettings
import sys

class ForceDate(datetime.date):
    """Force datetime.date.today() to return a specifiable date for testing
    purposes. Use "datetime.time = ForceDate" in testing code prior to code
    under test calling datetime.date.today()
    
    See also 
    http://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working
    """
    
    fdate = datetime.date(2000,1,1)
    
    @classmethod
    def setForcedDate(cls, date):
        """Set the date that datetime.date.today() will return.
        :param date: The date object to be returned by today().
        """
        cls.fdate = date
    
    @classmethod
    def today(cls):
        return cls.fdate


class SleepHook():
    
    origSleep = None
    callback = None
        
    @classmethod
    def _captureSleep(cls):
        if cls.origSleep == None:
            cls.origSleep = time.sleep
            time.sleep = cls._hookedSleep        
    
    @classmethod
    def _hookedSleep(cls, seconds):
        cls._captureSleep()
        if cls.callback == None:
            cls.origSleep(seconds)
        else:
            cls.callback(seconds)
            
    @classmethod        
    def setCallback(cls, callback):
        cls._captureSleep()
        cls.callback = callback
        
    @classmethod
    def removeCallback(cls):
        if cls.origSleep != None:
            time.sleep = cls.origSleep
            cls.origSleep = None
        cls.callback = None
        
    @classmethod
    def realSleep(cls, seconds):
        cls.origSleep(seconds)
    
    
class MockFTP(ftplib.FTP):
    # class vars
    origFTP = None
    quitException = False
    randomConnectException = False
    randomStorbinaryException = False
    
    @classmethod
    def patchFTP(cls):
        cls.origFTP = ftplib.FTP
        ftplib.FTP = MockFTP
        
    @classmethod
    def unpatchFTP(cls):
        ftplib.FTP = cls.origFTP
        cls.origFTP = None
        
    @classmethod
    def setQuitException(cls):
        cls.quitException = True
    
    @classmethod    
    def clearQuitException(cls):
        cls.quitException = False    
        
    def quit(self):
        if MockFTP.quitException:
            if MockFTP.origFTP != None:
                MockFTP.origFTP.quit(self)  # don't leave the test FTP server dangling
            raise Exception("Test exception to simulate failure on FTP.quit()")
        else:
            if MockFTP.origFTP == None:
                ftplib.FTP.quit(self)
            else:
                MockFTP.origFTP.quit(self)
  
    @classmethod
    def setRandomConnectException(cls):
        cls.randomConnectException = True
    
    @classmethod    
    def clearRandomConnectException(cls):
        cls.randomConnectException = False    
        
    def connect(self, host):
        if MockFTP.randomConnectException and random.randint(1,5)==1:
#             if MockFTP.origFTP != None:
#                 MockFTP.origFTP.quit(self)  # don't leave the test FTP server dangling
            raise Exception("Test exception to simulate failure on FTP.connect(host)")
        else:
            if MockFTP.origFTP == None:
                ftplib.FTP.connect(self, host)
            else:
                MockFTP.origFTP.connect(self, host)
        
    @classmethod
    def setRandomStorbinaryException(cls):
        cls.randomStorbinaryException = True
    
    @classmethod    
    def clearRandomStorbinaryException(cls):
        cls.randomStorbinaryException = False    
        
    def storbinary(self, command, filehandle):
        if MockFTP.randomConnectException and random.randint(1,5)==1:
#            Commented out next three lines because ftp_upload will call quit 
#            (seems like there should be a better way, though) XXX
#             if MockFTP.origFTP != None:
#                 logging.info("MockFTP.storbinary(): about to quit() connection before raising test exception")
#                 MockFTP.origFTP.quit(self)  # don't leave the test FTP server dangling
            raise Exception("Test exception to simulate failure on FTP.storbinary(command, file)")
        else:
            if MockFTP.origFTP == None:
                ftplib.FTP.storbinary(self, command, filehandle)
            else:
                MockFTP.origFTP.storbinary(self, command, filehandle)
        

ftp_testing_root = testsettings.ftp_testing_root
ftp_testing_dest = testsettings.ftp_testing_dest

moduleUnderTest = ftp_upload

def deleteTestImages():
    """Set up the directories on the local machine under ftp_testing_root
    to represent the dirs on the ftp_upload machine and the Cloud server
    """
    moduleUnderTest = ftp_upload
    
    shutil.rmtree(moduleUnderTest.incoming_location, True, None)
    os.mkdir(moduleUnderTest.incoming_location)
    
    shutil.rmtree(moduleUnderTest.processed_location, True, None)
    os.mkdir(moduleUnderTest.processed_location)
    
    cloudTestDir = os.path.join(ftp_testing_root, ftp_testing_dest)
    shutil.rmtree(cloudTestDir, True, None)
    os.mkdir(cloudTestDir)
#     print "ftp_testing_root =", ftp_testing_root
#     print "cloudTestDir =", cloudTestDir


def buildImages(rootPath, day, location, time, startingSeq, count):
    """Build the incoming directories and files to simulate the cameras
    dropping files into the ftp_upload machine
    :param rootPath: Full pathname of the root directory under which the images
    will be built.
    :param day: String representing the name of the 'date' directory.
    :param location: String representing the name of the camera location. 
    directory under the date directory.
    :param time: String representing the time-based portion of the image filename.
    :param startingSeq: The starting sequence number in the image filenames.
    :param count: The number of images files to generate.
    """

    datepath = os.path.join(moduleUnderTest.incoming_location, day)
    if not os.path.exists(datepath):
        os.mkdir(datepath)
    
    locpath = os.path.join(datepath, location)
    if not os.path.exists(locpath):
        os.mkdir(locpath)
        
    for i in range(startingSeq, startingSeq+count):
        filepath = os.path.join(locpath, time + "-%05d" % i + ".jpg")
        shutil.copy("SampleImage.jpg", filepath)


class Test(unittest.TestCase):
    
    origThreadList = None

    def setUp(self):

        module = ftp_upload
        
        # set up test for log file renaming
        bn = "ftp_upload"
        ext = ".log"
        if not os.path.exists(bn+ext):
            open(bn+ext, "w").close

        module.set_up_logging()
        
        # Set up the testing values for the ftp_upload global vars
        #
        module.incoming_location = testsettings.incoming_location
        module.processed_location = testsettings.processed_location          
        module.ftp_server = testsettings.ftp_server
        module.ftp_username = testsettings.ftp_username
        module.ftp_password = testsettings.ftp_password
        module.ftp_destination = testsettings.ftp_destination # remember to start with /
        
       
        # hook the date() method
        datetime.date = ForceDate
        
        # set up clean test directories
        deleteTestImages()
        
        self.origThreadList = threading.enumerate()
        list(self.origThreadList)

 
    def tearDown(self):
        ftp_upload.terminate_main_loop = False
        pass
    
    def testUploadOfTodayAndPrevious(self):
        logging.info("=============== %s ================", sys._getframe().f_code.co_name)
        self.uploadAndValidate(today=True, genFiles=True)
            
    def testUploadOfPreviousDays(self):
        logging.info("=============== %s ================", sys._getframe().f_code.co_name)
        self.uploadAndValidate(today=False, genFiles=True)
            
    def testNoWorkToDo(self):
        logging.info("=============== %s ================", sys._getframe().f_code.co_name)
        self.uploadAndValidate(today=True, genFiles=False)
        
    def uploadAndValidate(self, today, genFiles):
        
        # shell command to do recursive ls then use sed to strip out everything
        # except the size and filename
        ls_sed = ("ls -lR | sed "
                  # remove timestamp (this includes both the "MMM DD HH:MM"
                  # form and the "MMM DD  YYYY" form)
                  "-e \"s/[A-Z][a-z][a-z] [0-9 ][0-9] \\{1,2\\}"
                  "[0-9][0-9]:\\{0,1\\}[0-9][0-9] //\" "
                  # remove permissions, link count, owner, group
                  "-e \"s/^.\\{10\\} \\+[0-9]\\+ \\+[a-zA-Z0-9_-]\\+ \\+"
                  "[a-zA-Z0-9_-]\\+ \\+//\""
                 )
        
        inc = ftp_upload.incoming_location
        troot= ftp_testing_root
        
        # capture the initial state of the incoming files tree (empty)
        out = open( troot + "/orig.ls", "w")
        exitStatus = subprocess.call(ls_sed, cwd=inc, stdout=out, shell=True)
        assert exitStatus == 0  # captured initial empty incoming file tree

        # Build the incoming directories and files to simulate the cameras
        # dropping files into the ftp_upload machine
        #
        if genFiles:
            buildImages(inc, "2013-07-01", "downhill", "12-00-00", 1, 10)
            buildImages(inc, "2013-07-01", "uphill", "12-00-02", 1, 10)
            buildImages(inc, "2013-06-30", "downhill", "11-00-00", 1, 10)
            buildImages(inc, "2013-06-30", "uphill", "11-00-02", 1, 10)
            buildImages(inc, "2013-06-29", "downhill", "10-00-00", 1, 10)
            buildImages(inc, "2013-06-29", "uphill", "10-00-02", 1, 10)

        # capture the state of the incoming files tree after being populated
        out = open( troot + "/incoming.ls", "w")
        exitStatus = subprocess.call(ls_sed, cwd=inc, stdout=out, shell=True)
        assert exitStatus == 0  # captured incoming file tree before processing
           
        if today:
            ForceDate.setForcedDate(datetime.date(2013,7,1))
        else:
            ForceDate.setForcedDate(datetime.date(2013,7,2))
        SleepHook.setCallback(self.terminateTestUpload)
        MockFTP.patchFTP()
        MockFTP.setQuitException()
        MockFTP.setRandomConnectException()
        MockFTP.setRandomStorbinaryException()
        ftp_upload.main()
        MockFTP.clearRandomStorbinaryException()
        MockFTP.clearRandomConnectException()
        MockFTP.clearQuitException()
        MockFTP.unpatchFTP()
        SleepHook.removeCallback()
        
        # capture the state of the processed files tree
        out = open( troot + "/processed.ls", "w")
        exitStatus = subprocess.call(ls_sed, cwd=ftp_upload.processed_location, 
                                     stdout=out, shell=True)
        assert exitStatus == 0  # captured processed file tree after processing
        
        # capture the state of the cloud server files tree
        out = open( troot + "/cloud.ls", "w")
        exitStatus = subprocess.call(ls_sed, cwd=os.path.join(ftp_testing_root, 
                                                              ftp_testing_dest),
                                     stdout=out, shell=True)
        assert exitStatus == 0  # captured server file tree after FTPing files
        
        # capture the final state of the incoming files tree
        out = open( troot + "/final.ls", "w")
        exitStatus = subprocess.call(ls_sed, cwd=inc, stdout=out, shell=True)
        assert exitStatus == 0  # captured incoming file tree after processing
              
        # compare populated input tree before processing to processed tree
        out = open( troot + "/processed.diff", "w")
        exitStatus = subprocess.call("diff incoming.ls processed.ls", 
                                     cwd=troot, stdout=out, shell=True)
        assert exitStatus == 0  # processed file tree == populated incoming tree
       
        # compare populated input tree to the cloud server tree
        out = open( troot + "/cloud.diff", "w")
        exitStatus = subprocess.call("diff incoming.ls cloud.ls", 
                                     cwd=troot, stdout=out, shell=True)
        assert exitStatus == 0  # cloud server tree == populated incoming tree
       
        # compare the initial state of the incoming tree with the final state;
        # they should be identical and empty
        out = open( troot + "/final.diff", "w")
        exitStatus = subprocess.call("diff orig.ls final.ls", 
                                     cwd=troot, stdout=out, shell=True)
        assert exitStatus == 0  # final incoming tree == initial empty tree
         

    def testStorefileWithMissingDoneDirectory(self):
        logging.info("=============== %s ================", sys._getframe().f_code.co_name)
        date = "2010-02-01"
        loc = "downhill"
        filename = "21-22-00-00999.jpg"
        ftp_dir = ftp_upload.ftp_destination+"/"+date+"/"+loc
        filepath = os.path.join(ftp_upload.incoming_location, date, loc, filename)
        donepath = os.path.join(ftp_upload.processed_location, date, loc, filename)
   
        ftp_date_dir = os.path.join(ftp_testing_root, ftp_testing_dest, date)
        os.mkdir(ftp_date_dir)
        buildImages(ftp_upload.incoming_location, date, loc, "21-22-00", 999, 1)
        ftp_upload.storefile(ftp_dir=ftp_dir, filepath=filepath, donepath=donepath, 
                             filename=filename, today=False)
        assert os.path.exists(donepath)
        assert os.path.exists(os.path.join(ftp_date_dir, loc, filename))
        
        
    def sleepOneSecond(self,seconds):
        SleepHook.realSleep(1)
        
    def terminateTestUpload(self,seconds):
        if threading.currentThread().name == "MainThread":
            self.waitForThreads()   # wait for ftp_upload to complete current tasks
            # if we've had a pass through ftp_upload's main loop without
            # finding any work to do, set the terminate flag and return
            if ftp_upload.uploads_to_do == False \
                    and ftp_upload.files_purged == False:
                ftp_upload.terminate_main_loop = True
        else:
            logging.info("terminateTestUpload (sleepHook) called from non-main thread")

    def waitForThreads(self):   # XXX needs fixing: must wait until enumerate only shows main and Thread-1
        wait = True
        while wait:
            wait = False
            for thread in threading.enumerate():
                if self.origThreadList.count(thread) == 0:
                    logging.info("waitForThreads: waiting for "+thread.name)
                    wait = True
                    thread.join()
        logging.info("waitForThreads: done waiting for all threads")
                        
    def continueTestUpload(self, seconds):
        print "SleepHook calls back with", seconds
        SleepHook.removeCallback()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testUpload']
    unittest.main()
