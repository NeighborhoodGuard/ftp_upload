# Installing FTP_Upload
## Installing under Linux

As of v2.0.0, FTP_Upload includes an automated installer for Debian derivatives of Linux. The installer uses a simple UI to ask the user some configuration questions, then installs and configures all the required system software plus the FTP_Upload software needed to turn the system into an upload machine that will accept images uploaded from IP cameras and in turn transfer them to a cloud server running [Neighborhood Guard's Community View Software](https://github.com/NeighborhoodGuard/CommunityView).

We developed the installer on Ubuntu Dekstop 16.04 LTS, and recommend you use the current version of Ubuntu for your upload machine.  FTP_Upload has been tested on Ubuntu Server 22.04 LTS.

### Installation Steps

1. On the Linux machine where you wish to install the software, log into the account you wish to use to maintain FTP_Upload.  This account will be referred to as the "maintenance" account and must be able to run the `sudo` command.

1. Prior to installing the software, we recommend that you upgrade your already installed operation system software to the latest available. To do this, open a shell window and give the commands below. This process could take 30 minutes or so if your software has not been upgraded recently.

        sudo apt-get update
        sudo apt-get upgrade

1. When you run the installation software below, it will check for a private key to access the upload account on the cloud server. If a private key does not exist,
it will create a key pair for use with the upload account and install the public key on the server and put the private key into the file `~/.ssh/id_rsa` in the maintentance account on the upoad machine.

    If you already have an SSH private key for the upload account on the cloud server,
copy the private key into the file `~/.ssh/id_rsa` in the maintenance account now.  If the `.ssh` directory does not exist, create it using the command `mkdir ~/.ssh`.  After copying the private key file into `~/.ssh/id_rsa`, make sure that both the `~/.ssh` directory and the key file are readable only by the maintenance account, e.g., 

        chmod 700 ~/.ssh
        chmod 600 ~/.ssh/id_rsa

1. Using a Web browser, go to Neighborhood Guard's [FTP_Upload repository](https://github.com/NeighborhoodGuard/ftp_upload) on Github.  Click the `Clone or download` button, and select the `Download ZIP` item.

    If you are installing onto an Ubuntu Server, which does not have a graphical environment, download the ZIP file using the following command,

        wget https://github.com/NeighborhoodGuard/ftp_upload/archive/master.zip

1. After the ZIP file has been downloaded, extract it into the home directory of the account (or other convenient place).  If you are installing on an Ubuntu Server version, you will probably have to install an unzipping utility first then unzip the file. For example,

        sudo apt-get install unzip
        unzip master.zip

1. Change to the FTP_Upload/configupload directory within the tree of extracted files, and run the script `configupload.sh` using the `sudo` command, and type your password if requested.  For example,

        cd ftp_upload-master/FTP_Upload/configupload
        sudo sh configupload.sh

1. The installation software will present a simple user interface which will ask you to supply information that is needed to configure the Neighborhood Guard software such as the domain name of the cloud server that is running the CommunityView software, the number of days uploaded images should be retained on the upload machine, etc. If you need to, you can abort the installation process at any time and either save your answers to the configuration questions or not. When you select `Install` at the end of the questions, the software will be installed, configured and started.  At that point, the machine is ready to be used as an uploader.

1. If you later decide you need to go back and change the configuration, `cd` to the `configupload` directory and simply run the installer again:

        sudo sh configupload.sh

## Installing Under Windows

There is no automated process for installation under Windows.  In general, you need to accomplish the following tasks to have a successful installation.

* Install 2.7.x Python
* Copy the ftp_upload source code from GitHub and set the configuration
values
* Set up ftp_upload to run on start up
* Set up an FTP server to receive camera images
* Set power management so that the computer never sleeps
* Set the Windows system to reboot after a system failure
* Set the BIOS to start Windows on power up
* Set the firewall to allow incoming FTP connections from the camera(s)
* Set Windows Updates to occur at an innocuous time
* Set up remote access
