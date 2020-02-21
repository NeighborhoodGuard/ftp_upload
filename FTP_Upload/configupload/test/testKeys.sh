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

# tell the script under test not to proceed with normal execution 
UNIT_TEST_IN_PROGRESS=1

. ../keys.sh 
. ../utils.sh

# config file for testing
test_conf="test.conf"

test_privkey=$HOME/.ssh/id_rsa
test_user=`whoami`

oneTimeSetUp() {
    # make sure we have a configuration file
    if [ ! -e $test_conf ]
    then
        fail "***** NO TEST CONFIGURATION FILE ($test_conf) PRESENT! *****"
        exit 1
    fi
}

setUp() {
    # get the values from the conf file
    test_ruser=`get_config "$test_conf" test_ruser`
    test_rserver=`get_config "$test_conf" test_rserver`
    test_rpass=`get_config "$test_conf" test_rpass`

    # set up the remote testing account
    if [ -z "$test_ruser" -o -z "$test_rserver" ]
    then
        msg1="Remote server test account not set up in $test_conf."
        msg2="ALL TESTS WILL FAIL."
        fail "$msg1 $msg2"
        # make the ssh errors that will follow more understandable
        test_ruser=remote_user_not_specified
        test_rserver=remote_server_not_specified
        test_rpass=remote_password_not_specified
    fi
    test_racct="$test_ruser@$test_rserver"

    # delete the local host's SSH info.
    # Do this first so that other subsequent ssh operations
    # won't get confused by any test garbage we have
    rm -rf $HOME/.ssh
    ls -d $HOME/.ssh > /dev/null 2>&1
    if [ "$?" -ne 2 ]   # status 2 means ls didn't find .ssh
    then
        fail "setUp's removal of local host's .ssh failed."
    fi

    # add the remote test machine into the local known_hosts file
    # to prevent SSH from complaining
    ssh -o 'PreferredAuthentications=publickey' -o 'StrictHostKeyChecking=no' \
        "$test_racct" true > /dev/null 2>&1

    # delete the remote host's SSH info
    sshpass -p"$test_rpass" ssh "$test_racct" 'rm -rf .ssh'
    sshpass -p"$test_rpass" ssh "$test_racct" 'ls -d .ssh > /dev/null 2>&1'
    lsstatus=$?
    if [ $lsstatus -ne 2 ]   # status 2 means ls didn't find .ssh
    then
        fail "setUp's removal of remote host's .ssh failed; status=$lsstatus"
    fi
}

# run setupkeypair(), check it's return status and also verify that an
# SSH connection can be established with the remote host
#
run_setupkeypair() {
    if ! setupkeypair $test_user "$test_racct" "$test_rpass" > /dev/null 2>&1
    then
        fail "setupkeypair returns failure"
    fi
    if ! ssh "$test_racct" true
    then
        fail "Cannot execute remote command after key pair set up"
    fi
}

test_no_initial_keys() {
    run_setupkeypair
}

test_keypair_already_set_up() {
    run_setupkeypair
    # keypair now already set up
    run_setupkeypair
}

test_bogus_host() {
    # fastest to use a host that's up but not running SSH
    setupkeypair $test_user testuser@10.0.2.1 "$test_rpass" > /dev/null 2>&1
    status=$?
    if [ "$status" -ne 1 ]
    then
        fail "Incorrect status return from bogus host test: $status"
    fi
}

test_existing_key_pair_but_not_set_up() {
    # generate a key pair to be the "existing" one
    echo | ssh-keygen -q -t rsa -f $test_privkey > /dev/null 2>&1

    run_setupkeypair
}

# this is simpulating a keypair owned by someone else
test_existing_key_pair_but_no_read_writre() {
    # generate a key pair to be the "existing" one
    echo | ssh-keygen -q -t rsa -f $test_privkey > /dev/null 2>&1
    chmod 0 $test_privkey
    chmod 0 $test_privkey.pub

    run_setupkeypair
}

test_existing_key_with_passphrase() {
    # create a key pair with a passphrase on the private key
    ssh-keygen -q -t rsa -N testphrase -f "$test_privkey"

    run_setupkeypair
    if [ ! -e "$test_privkey.orig" ]
    then
        fail "Old key file with passphrase $test_privkey.orig does not exist"
    fi
}

test_existing_bad_key() {
    # create a key pair
    ssh-keygen -q -t rsa -f "$test_privkey" < /dev/null > /dev/null 2>&1
    # damage the private key by deleting the second line in the file
    sed --in-place 2d "$test_privkey"

    run_setupkeypair
    if [ ! -e "$test_privkey.orig" ]
    then
        fail "Old, bad key file $test_privkey.orig does not exist"
    fi
}

test_private_but_no_public_key() {
    # create a key pair
    ssh-keygen -q -t rsa -f "$test_privkey" < /dev/null > /dev/null 2>&1
    # remove the public key
    rm "$test_privkey.pub"

    run_setupkeypair
    if [ ! -e "$test_privkey.pub" ]
    then
        fail "Public key file $test_privkey.pub does not exist"
    fi
}

test_private_but_bad_public_key() {
    # create a key pair
    ssh-keygen -q -t rsa -f "$test_privkey" < /dev/null > /dev/null 2>&1
    # damage the public key by deleting a few chars of key data
    sed --in-place 's/ ..../ /' "$test_privkey.pub"

    run_setupkeypair
    if [ ! -e "$test_privkey.pub" ]
    then
        fail "Public key file $test_privkey.pub does not exist"
    fi
    if [ ! -e "$test_privkey.pub.orig" ]
    then
        fail "Old public key not moved aside"
    fi
}


. `which shunit2`    
