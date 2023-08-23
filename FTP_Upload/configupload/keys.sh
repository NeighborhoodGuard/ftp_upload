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

# see if an ssh key pair is already set up between the current user on 
# this machine and the cloud server. If not, set one up now.
# usage: setupkeypair local_user remotuser@remoteserver remote_passwd
#
setupkeypair () {
    local luser="$1"
    local racct="$2"
    local rpass="$3"
    
    # build the sudo prefix to run a command as the local user with a
    # controlling tty, and the su prefix to run as the local user
    # but without a controlling tty
    #
    SUDOLU="sudo -u $luser -H" 

    # see if we have a private key.
    # If we do, see if it's bad or needs a passphrase. If either or these
    # is true, move the key aside and also move any public key aside
    #
    local uhome=`$SUDOLU sh -c 'echo $HOME'`
    local genpubkey
    local privkeyfile=$uhome/.ssh/id_rsa 
    local pubkeyfile=$uhome/.ssh/id_rsa.pub
    if [ -e $privkeyfile ]
    then
        genpubkey=""
        if ! genpubkey="`$SUDOLU ssh-keygen -q -y -f $privkeyfile < /dev/null`"
        then
            echo "Moving bad private key aside"
            mv $privkeyfile $privkeyfile.orig
            if [ -e $pubkeyfile ]
            then
                echo "Moving old public key aside"
                mv $pubkeyfile $pubkeyfile.orig
            fi
        fi
    fi

    # see if a key pair is already set up.
    # This test has the side effect of putting the remote machine's
    # fingerprint in the local user's known_hosts file, if the
    # remote machine can be contacted
    #
    local sshmsg
    if sshmsg="`echo | $SUDOLU ssh \
        -o 'PreferredAuthentications=publickey' \
        -o 'StrictHostKeyChecking=no' $racct exit 2>&1`"
    then
        echo "Key pair IS ALREADY set up with $racct"
        return 0
    fi

    # if the above test failed but we don't see "permission denied" in the
    # output (meaning that we reached the host but don't have a key
    # that it will accept), then some other, non-permission-related
    # failure has occurred, e.g., we can't reach the host
    #
    if ! echo "$sshmsg" | grep -i  "permission denied" > /dev/null
    then
        echo "Unable to connect to $racct"
        echo "$sshmsg"
        return 1
    fi

    echo "No key pair set up with $racct, setting one up now..."

    # if there's an existing private key, then check for a public key.
    # if we have a public key that doesn't match the private key,
    # move it aside.
    # If we don't have a public key, or the one we have doesn't match
    # the private key, generate and save the correct public key
    #
    if genpubkey="`echo | $SUDOLU ssh-keygen -q -y -f $privkeyfile`"
    then
        local pubkey="`sed 's/\([^ ][^ ]*  *[^ ][^ ]*\).*$/\1/' $pubkeyfile`"
        if [ $? != 0 -o "$pubkey" != "$genpubkey" ]
        then
            if [ -e "$pubkeyfile" ]
            then
                echo "(Moving bad public key file aside to $pubkeyfile.orig)" \
                    | tee /dev/tty
                mv "$pubkeyfile" "$pubkeyfile.orig"
            fi
            echo "$genpubkey" "$luser@`hostname`" | \
                $SUDOLU tee $pubkeyfile > /dev/null
        fi

    # otherwise (we don't have a good private key), generate the key pair
    #
    else
        echo "Generating new key pair."
        echo | $SUDOLU ssh-keygen -q -N '' -t rsa -f $privkeyfile
    fi

    echo "Have key pair priv=$privkeyfile pub=$pubkeyfile"

    # copy pub key to cloud server
    #
    $SUDOLU sshpass -p"$rpass" ssh-copy-id -f -i "$pubkeyfile" "$racct" \
        > /dev/null

    # now see if we can log in
    #
    if ! sshmsg="`echo | $SUDOLU ssh \
        -o 'PreferredAuthentications=publickey' \
        -o 'StrictHostKeyChecking=no' $racct exit 2>&1`"
    then
        echo "$sshmsg"
        echo "Cannot ssh to server even though we just set up a key pair!"
        return 1
    fi

    echo "Successfully set up key pair!"
    return 0
}

