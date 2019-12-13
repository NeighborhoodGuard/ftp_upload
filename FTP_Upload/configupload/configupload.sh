#!/bin/sh
################################################################################
#
# Copyright (C) 2018 Neighborhood Guard, Inc.  All rights reserved.
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
 
# This script will collect configuration values from the user, then install
# and configure all software required to turn this machine into a Neighborhood
# Guard upload machine.  It will receive images from properly configured IP
# cameras and upload them to a cloud server running Neighborhood Guard's
# CommunityView software.

# version of the configupload software
version="2.1.0"

. ./utils.sh
. ./confui.sh
. ./keys.sh

# install the package or packages indicated in the first argument
install_wait() {
    local pkgs="$1"
    local wtime=5
    local maxtries=36
    local tries=$maxtries
    while ! apt-get -qqy install $pkgs
    do
        if [ $tries -eq $maxtries ]
        then
            echo "(First install attempt failed." \
                "Will retry for up to three minutes.)" > /dev/tty
        fi
        echo "Waiting $wtime seconds and trying again."
        sleep "$wtime"
        tries=`expr $tries - 1`
        if [ "$tries" = 0 ]
        then
            echo "CANNOT INSTALL REQUIRED SYSTEM SOFTWARE"
            return 1
        fi
    done
    return 0
}


# directories required for install of ftp_upload and cktunnel
#
code_dir=/opt/ftp_upload
config_dir=/etc/opt/ftp_upload
var_dir=/var/opt/ftp_upload
log_dir=$var_dir/log
inc_dir=$var_dir/incoming
proc_dir=$var_dir/processed
initd_dir=/etc/init.d
tun_code_dir=/opt/cktunnel
tun_config_dir=/etc/opt/cktunnel
systemd_dir=/lib/systemd/system
fac_code_dir=/opt/findaxiscam
fac_link_dir=/usr/local/bin
fac_lman_dir=/usr/local/man/man1
fac_man_dir=$fac_code_dir/man

# log file for this script
scriptlog=configupload.log

# shell to use as a no-login shell for the camera's FTP account
nologinshell=/bin/false

# global to hold the name of the section that produced an unexpected error
#
task=""

# on unexpected exit, print an error message and the error output for that task
#
errorexit() {
    tac "$scriptlog" | sed "/$task/,\$d" | tac >&2
    echo -n "\033[31m\033[1m" > /dev/tty   # red, bold text
    echo "An unexpected error occurred while $task." | tee -a "$scriptlog" >&2
    echo "Please see above or examine the log file: $scriptlog." \
        | tee -a "$scriptlog" >&2
    echo -n "\033[0m" > /dev/tty    # reset text style
    echo `date --rfc-3339=seconds` "Error exit configupload" >> "$scriptlog"
    exit 1
}

# perform the actions to configure this machine to be an uploader
#
# usage: configure config_file
#
configure() {
    local cfg="$1"
    
    # Set up to catch unexpected errors and notify user
    #
    trap errorexit EXIT
    set -e
    
    # set up this machine's NetBIOS name
    #
    task="updating this machine's hostname"
    echo "***** $task" | tee /dev/tty
    local hostname="`get_config $cfg um_name`"
    hostnamectl set-hostname $hostname
    sed -i "s/127\\.0\\.1\\.1.*$/127.0.1.1\t$hostname/" /etc/hosts
    # restart the daemons that advertise our name; this list may be incomplete
    systemctl restart avahi-daemon.service systemd-logind.service
    
    task="updating the available system software listing"
    echo "***** $task" | tee /dev/tty
    # update and upgrade the system
    apt-get update  # info output to log
    # XXX apt-get upgrade
    
    # install the required system software
    #
    task="downloading and installing new required system software"
    echo "***** $task" | tee /dev/tty
    
    # install debconf-utils so we can pre-configure proftpd not to ask the user
    # whether it should be run under inetd or standalone
    install_wait debconf-utils  # info output to log
    echo "proftpd-basic shared/proftpd/inetd_or_standalone select standalone" \
        | debconf-set-selections   # info output to log
        
    # install all the required packages
    local pkgs="openssh-server sshpass tightvncserver proftpd samba shunit2"
    install_wait "$pkgs"    # info output to log
    systemctl restart nmbd  # restart in case nmbd was already installed

    # create the ftp_upload directories for code, log and images
    #
    task="creating required directories"
    echo "***** $task" | tee /dev/tty
    create_dir $code_dir
    create_dir $config_dir
    create_dir $var_dir
    create_dir $log_dir
    create_dir $inc_dir
    create_dir $proc_dir
    create_dir $tun_code_dir
    create_dir $tun_config_dir
    create_dir $fac_code_dir
    create_dir $fac_man_dir
    create_dir $fac_lman_dir

    # install the current ftp_upload source from local directories
    #
    task="installing Neighborhood Guard software"
    echo "***** $task" | tee /dev/tty
    local our_dir=`dirname $(readlink -e "$0")`
    cp $our_dir/../src/ftp_upload.py $code_dir
    cp $our_dir/../src/ftp_upload_example.conf $config_dir

    cp $our_dir/../tunnel/cktunnel.sh $tun_code_dir/cktunnel
    chmod +x $tun_code_dir/cktunnel
    cp $our_dir/../configupload/utils.sh $tun_code_dir
    cp $our_dir/../tunnel/cktunnel_example.conf $tun_config_dir

    fac=findaxiscam
    cp $our_dir/../findaxiscam/findaxiscam.sh $fac_code_dir/$fac
    chmod 755 $fac_code_dir/$fac
    chown root:root $fac_code_dir/$fac
    ln -sf $fac_code_dir/$fac $fac_link_dir/$fac
    cp $our_dir/../findaxiscam/man/$fac.1 $fac_man_dir
    ln -sf $fac_man_dir/$fac.1 $fac_lman_dir
    mandb

    # install the ftp_upload init script
    #
    service ftp_upload stop || true
    update-rc.d -f ftp_upload remove || true
    local tgt=$initd_dir/ftp_upload
    rm -f $tgt
    cp $our_dir/../initscript/ftp_upload $tgt
    chmod 755 $tgt
    chown root:root $tgt
    update-rc.d ftp_upload defaults 

    # install the cktunnel service file
    #
    systemctl stop cktunnel.service || true
    systemctl disable cktunnel.service || true
    tgt=$systemd_dir/cktunnel.service
    rm -f "$tgt"
    cp $our_dir/../tunnel/cktunnel.service "$tgt"
    # set user that cktunnel will run as
    set_config_value $tgt User `getluser`
    chmod 755 $tgt
    chown root:root $tgt
    systemctl enable cktunnel.service

    # set up the config values for ftp_upload & cktunnel
    #
    task="configuring Neighborhood Guard software"
    echo "***** $task" | tee /dev/tty

    
    # ftp_upload conf
    local conf="$config_dir/ftp_upload.conf"
    cp "$config_dir/ftp_upload_example.conf" "$conf"
    set_config_value $conf ftp_server "`get_config $cfg cs_name`"
    set_config_value $conf ftp_username "`get_config $cfg cs_user`"
    set_config_value $conf ftp_password "`get_config $cfg cs_pass`"
    set_config_value $conf ftp_destination "/`get_config $cfg cs_ftp_dir`"
    set_config_value $conf retain_days "`get_config $cfg um_retain_days`"
    set_config_value $conf incoming_location $inc_dir
    set_config_value $conf processed_location $proc_dir

    # cktunnel conf
    conf="$tun_config_dir/cktunnel.conf"
    cp "$tun_config_dir/cktunnel_example.conf" "$conf"
    local user="`get_config $cfg cs_user`"
    local server="`get_config $cfg cs_name`"
    set_config_value $conf acct "$user@$server"

    # starttunnel conf (we're editing the sh source, here)
    conf="$our_dir/../tunnel/starttunnel.sh"
    set_config_value "$conf" ACCT "$user@$server"

    # configure for camera FTP.  It seems that the only simple way to
    # deny login to the camera user but allow the camera user to connect
    # via FTP is to put the no-login-shell into /etc/shells then set
    # the camera user's shell to it.  If it's not in /etc/shells,
    # vsftpd won't allow the user to connect via FTP
    #
    task="configuring camera FTP access to this machine"
    echo "***** $task" | tee /dev/tty
        if ! grep "^$nologinshell\$" /etc/shells > /dev/null
    then
        echo $nologinshell >> /etc/shells
    fi

    # create the local FTP user account for the camera(s)
    # and give it access to the incoming images dir
    #
    cam_user=`get_config $cfg um_cam_user`
    if id -u $cam_user > /dev/null 2>&1
    then
        deluser --quiet $cam_user 
    fi
    useradd -d $inc_dir -U -s $nologinshell $cam_user
    chown $cam_user:$cam_user $inc_dir    
    chmod 775 $inc_dir
    echo "$cam_user:`get_config $cfg um_cam_pass`" | chpasswd
    
    # limit FTP users to their login directory and below 
    # XXX should be done in an idempotent way
    local cf=/etc/proftpd/proftpd.conf
    if ! grep -E '^DefaultRoot\s+~' "$cf" > /dev/null
    then
        echo \
           "# The configuration below was added by the configupload script" \
            >> $cf
        echo 'DefaultRoot ~' >> $cf
    fi
    
    # set proftpd up to be run on boot and restart it with the new config
    update-rc.d proftpd defaults
    service proftpd restart
    
    task="setting up SSH key pair with cloud server"
    echo "***** $task" | tee /dev/tty
    local luser="`getluser`"
    local cs_user="`get_config $cfg cs_user`"
    local cs_name="`get_config $cfg cs_name`"
    local cs_pass="`get_config $cfg cs_pass`"
    setupkeypair "$luser" "$cs_user@$cs_name" "$cs_pass"
    # create tunnel flags dir on cloud server for cktunnel

    task="creating tunnel-flags directory on cloud server"
    echo "***** $task" | tee /dev/tty
    sudo -u $luser -H ssh "$cs_user@$cs_name" "mkdir -p -m 700 .tunnelflags" 

    task="starting ftp_upload"
    echo "***** $task" | tee /dev/tty
    service ftp_upload start
    
    task="starting cktunnel"
    echo "***** $task" | tee /dev/tty
    systemctl start cktunnel.service
    
    # Turn off error trap
    set +e
    trap - EXIT
    
    echo "***** done" | tee /dev/tty
}


main() {
    # verify that we're root
    #
    if [ `whoami` != root -a "$UI_TESTING" != 1 ]
    then
        echo "$0: You must run this script as root."
        echo "Try sudo $0"
        exit 1
    fi
    
    # start the log
    echo "\n`date --rfc-3339=seconds` Start configupload" >> "$scriptlog"

    
    # get the name of the config file
    local cfile=`find_config`

    # insure the log file's directory exists
    mkdir --parents `dirname "$cfile"`

    # Get the config info from the user.
    # Exit if the user cancels
    #
    if ! get_info "$cfile"
    then
        echo `date --rfc-3339=seconds` "User cancelled configupload" \
            >> "$scriptlog"
        exit 1
    fi
    
    # configure this machine
    configure "$cfile" >> "$scriptlog" 2>&1
    echo `date --rfc-3339=seconds` "Normal exit configupload" >> "$scriptlog"
}
    

if [ ! $UNIT_TEST_IN_PROGRESS ]
then
    main
fi

