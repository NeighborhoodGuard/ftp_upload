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

# This file provides the whiptail UI for to allow the user to enter
# configuration values for configupload

# names of the config file and its associated temp file
conf_temp=.uploader.conf

# standard height and width for message boxes
height=13
width=60

# constants for confvalbox() return values
Prev=0
Next=2

# put up a dialog box to request a configuration value from the user.
#
# usage: confvalbox title message value_name [value [box_height]]
#
confvalbox () {
    local title="$1"
    local msg="$2"
    local name="$3"
    local val="$4"
    local hgt="$5"
    if [ "$val" = "" ]
    then
        val=`get_config $conf_temp $name`
    fi
    if [ "$hgt" = "" ]
    then
        hgt="$height"
    fi

    val="`whiptail --title  "$title" \
        --ok-button Next --cancel-button Previous \
        --inputbox -- "$msg" $hgt $width "$val" 3>&1 1>&2 2>&3`"
    local retval=$?
    echo "$val"
    case $retval in
        0)  # Next button
            set_config_value $conf_temp $name "$val"
            return 2
            ;;
        1)  # Previous button
            return 0
            ;;
        *)  # ESC key
            return $retval
    esac
}

# put up the cancel dialog.
# If the first argument is non-empty, offer to save the data entered
#
cancel_dialog() {
    local title="Cancelled"
    local m=""
    if [ "$1" ] # if non-empty, offer to save data
    then
        m="${m}Do you want to save the data you entered (if any) to be used "
        m="${m}as the default values the next time you run this?"
        m="${m}\n\n                   [ESC will discard]"
        whiptail --title  "$title" --yes-button Save --no-button Discard\
            --yesno "$m" 10 $width
    else
        m="You have cancelled installation."
        whiptail --title  "$title" --msgbox "$m" 8 $width
    fi
}

# create the temporary config file.
# If there is an extant config file, use the data in it to populate
# the temporary config file.
#
# usage: create_conftemp config_file
#
create_conftemp() {
    local cfile="$1"
    if [ -r "$cfile" ]
    then
        cp "$cfile" "$conf_temp"
        sed -i "/^#>>/d" "$conf_temp"    # remove old comment header
        sed -i '1{x;p;x;}' "$conf_temp"  # insert blank line at top of file
    else
        echo > "$conf_temp"              # insert blank line at top of file
    fi

    # put the new comment header on the temp file.
    # Note: sed needs at least one line in the file so that 
    # Line 1 can be used as an address
    local cmt="#>> Configuration file created by `getluser`@`hostname`\n"
    cmt="${cmt}#>> on `date`\n#>>"
    sed -i "1s|^|$cmt|" "$conf_temp"
}
    
# gather the required config info from the user by displaying a series
# of dialog boxes. Return zero if successful or non-zero if user cancels
#
# usage: get_info config_file
#
get_info() {
    local cfile="$1"

    create_conftemp "$cfile"

    local esc="\n\n                [Press ESC to cancel]"
    
    local xstat # exit status of confvalbox
    local rval  # return value from confvalbox (stdout)

    local step=1
    while [ $step -gt 0 ]
    do 
    local m=""
    local title
    case $step in
    1)
        title="Neighborhood Guard Upload Machine Configuration v$version"
        m="${m}This program will configure this machine to receive images "
        m="${m}from a camera and upload them "
        m="${m}to a cloud server running Neighborhood Guard's "
        m="${m}CommunityView software. "
        m="${m}It will ask you for some configuration values, then install and "
        m="${m}configure the software required. "
        m="${m}This program does not use the mouse. "
        m="${m}Move the cursor by using the TAB key or the arrow keys. "
        m="${m}Hit the Enter key when done with each entry."
        m="${m}\n\n"
        m="${m}NOTE: If you have not upgraded this machine in the last "
        m="${m}couple months (or ever), press ESC to cancel and run these two "
        m="${m}commands:\n"
        m="${m}\n  sudo apt-get upgdate"
        m="${m}\n  sudo apt-get upgrade\n\n"
        m="${m}The second command could take a half hour or more to complete. "
        m="${m}Then, run this program again."

        whiptail --title "$title" --msgbox "$m" 21 70
        if [ $? = 0 ]  # OK button
        then
            step=`expr $step + 2`
        else    # user cancelled
            step=`expr $step + 255`
        fi
        ;;
    2)
        title="Name This Computer"
        m="${m}The name of this computer will be set to what you enter here. "
        m="${m}The camera can use "
        m="${m}the name to find this computer on the local network. "
        m="${m}The name must be 1 to 15 characters, and consist only "
        m="${m}of letters, numbers and the hyphen (\"-\") symbol, "
        m="${m}and must not start with a hyphen. "
        m="${m}This machine is currently named '$(hostname)'."
        # if there's no host name in the config file,
        # supply the current host name as the default
        local defname=`get_config $conf_temp um_name`
        if [ "$defname" = "" ]
        then
            defname=`hostname`
        fi
        rval="`confvalbox "$title" "$m$esc" um_name "$defname" 17`"
        xstat=$?
        if [ $xstat = $Next ] # if Next button pressed, validate input
        then
            if ! echo "$rval" | grep -E '^[A-Za-z0-9][-A-Za-z0-9]{1,14}$' \
                > /dev/null
            then
                title="Error in Computer Name"
                m=""
                m="${m}The name must be 1 to 15 characters, and consist only "
                m="${m}of letters, numbers and the hyphen (\"-\") symbol, "
                m="${m}and must not start with a hyphen. "
                whiptail --title "$title" --msgbox "$m" 8 $width
                continue    # repeat this step
            fi
        fi
        step=`expr $step + $xstat`
        ;;
    3)
        title="Camera's FTP User Name For This Machine"
        m="${m}Enter the user name of the account "
        m="${m}the camera will use when connecting to "
        m="${m}this machine via FTP to upload images.  "
        m="${m}If this account does not yet exist on this machine, "
        m="${m}it will be created."
        confvalbox "$title" "$m$esc" um_cam_user > /dev/null
        step=`expr $step + $?`
        ;;
    4)
        title="Camera's FTP Password For This Machine"
        m="${m}Enter the password the camera will use when connecting to "
        m="${m}this machine via FTP to upload images."
        confvalbox "$title" "$m$esc" um_cam_pass > /dev/null
        step=`expr $step + $?`
        ;;
    5)
        title="Number of Days to Save Images On This Machine"
        m="${m}Enter the number of days images should be saved on this machine "
        m="${m}after they have uploaded to the cloud server. This has no "
        m="${m}effect on the number of days the cloud server will save "
        m="${m}the images."
        rval="`confvalbox "$title" "$m$esc" um_retain_days`"
        xstat=$?
        if [ $xstat = $Next ] # if Next button pressed, validate input
        then
            if ! [ "$rval" -gt 0 ]
            then
                title="Error in Number of Days"
                m="Number of days must be a positive integer."
                whiptail --title "$title" --msgbox "$m" 8 $width
                continue    # repeat this step
            fi
        fi
        step=`expr $step + $xstat`
        ;;
    6)
        title="Domain Name of the Cloud Server"
        m="${m}Enter the domain name or the IP address of the cloud server "
        m="${m}that this "
        m="${m}machine will upload images to, e.g., yourneighborhood.org."
        confvalbox "$title" "$m$esc" cs_name > /dev/null
        step=`expr $step + $?`
        ;;
    7)
        title="Cloud Server Account Name"
        m="${m}Enter the user name of the cloud server account to which "
        m="${m}this machine will upload images."
        confvalbox "$title" "$m$esc" cs_user > /dev/null
        step=`expr $step + $?`
        ;;
    8)
        title="Cloud Server Account Password"
        m="${m}Enter the password for the cloud server account to which "
        m="${m}this machine will upload images."
        confvalbox "$title" "$m$esc" cs_pass > /dev/null
        step=`expr $step + $?`
        ;;
    9)
        title="Cloud Server FTP Directory"
        m="${m}Enter the name of the directory within the cloud server "
        m="${m}account into which this machine will upload images. This "
        m="${m}may be a domain name representing the domain portion "
        m="${m}of the URL where the images can be viewed, e.g., "
        m="${m}images.yourneighborhood.org. "
        m="${m}For AWS cloud servers, this is empty."
        confvalbox "$title" "$m$esc" cs_ftp_dir > /dev/null
        step=`expr $step + $?`
        ;;
    10)
        title="Ready to Install"
        m="${m}Ready in install and configure this machine. "
        m="${m}Select Install to proceed or Prev to go back."
        whiptail --title "$title" --yes-button Install --no-button "Prev" \
            --yesno "$m$esc" $height $width
        case $? in
            0)  # Install button
                mv "$conf_temp" "$cfile"
                break
                ;;

            1)  # Prev button
                ;;  # will go back to previous step

            *)  # Esc key
                step=`expr $step + 255`
                ;;
        esac
        ;;
    *)
        # this is a cancellation
        local cancel_step=`expr $step - 254`
        local save_offer=""
        if [ $cancel_step -gt 2 ]
        then
            save_offer=1
        fi

        if cancel_dialog $save_offer
        then
            mv "$conf_temp" "$cfile"
        fi
        return 1
        ;;
    esac
    step=`expr $step - 1`
    done
    return 0
}


