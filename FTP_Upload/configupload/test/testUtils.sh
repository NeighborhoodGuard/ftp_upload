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
#
UNIT_TEST_IN_PROGRESS=1

. ../utils.sh

setUp() {
    rm -rf _ttf_* _testingroot uploader.conf # remove the temporary test files
}

# test the functions for setting values in config files
#
test_set_config_value() {
    # set up temporary test files

    ttf_orig=_ttf_configvals_orig.conf
    cat > $ttf_orig << 'END_OF_FILE' 
server_name = examle.com
user_name=example_user
value_with_spaces = value with spaces
number1=999
number2 = 9
END_OF_FILE

    ttf_expected=_ttf_configvals_expected.conf
    cat > $ttf_expected << 'END_OF_FILE' 
server_name = realname.org
user_name=realName
value_with_spaces = new value with spaces
number1=111
number2 = 222
END_OF_FILE
    
    # substitute the values
    set_config_value $ttf_orig server_name realname.org
    set_config_value $ttf_orig user_name realName
    set_config_value $ttf_orig value_with_spaces "new value with spaces"
    set_config_value $ttf_orig number1 111
    set_config_value $ttf_orig number2 222
    
    # check the result
    diff $ttf_expected $ttf_orig
    assertEquals "config values set correctly" 0 $?
}

# test set_config_value when the specified file doesn't exist
test_set_config_value_no_file() {
    set_config_value this_file_doesnt_exist server_name realname.org
    assertNotEquals 0 $?    # return value should be non-zero
}

# test set_config_value when the specified name doesn't exist in the file
test_set_config_value_no_name() {
    ttf_config=_ttf_config.conf
    touch $ttf_config
    set_config_value "$ttf_config" newname newvalue
    assertEquals 0 $?    # set_config_value should return success (zero)
    value=`get_config "$ttf_config" newname`
    assertEquals newvalue "$value"
}

# test the function for returning values from config files
#
test_get_config() {
    ttf_config=_ttf_config.py
    cat > $ttf_config << 'END_OF_FILE'
[default]
cs_name: gooddomain.org
cs_user: theuser
long_one=string with spaces
var_space = wordWithTrailingSpaces   
lastly: string with trailing spaces   
END_OF_FILE

    result=""
    for name in cs_name cs_user long_one var_space lastly
    do
        result="${result}`get_config "$ttf_config" "$name"` "
    done

    expected="\
gooddomain.org \
theuser \
string with spaces \
wordWithTrailingSpaces \
string with trailing spaces "

    assertEquals "get_config results" "$expected" "$result"
}

# test get_config when the name doesn't exist in the config file
# but the caller has supplied a default value
test_get_config_default_value() {
    ttf_config=_ttf_config.conf
    cat > $ttf_config << 'END_OF_FILE'
[default]
cs_name: gooddomain.org
cs_user: theuser
END_OF_FILE

    stdout=`get_config $ttf_config foo defvalue`
    assertEquals 0 $?       # get_config returns zero
    assertEquals defvalue "$stdout"     # stdout is empty string
}

# test get_config when the config file does not exist
test_get_config_no_file() {
    stdout=`get_config this_file_doesnt_exist foo`
    assertNotEquals 0 $?    # get_config returns non-zero
    assertNull "$stdout"    # stdout is empty string
}

# test get_config when the name doesn't exist in the config file
test_get_config_no_name() {
    ttf_config=_ttf_config.conf
    cat > $ttf_config << 'END_OF_FILE'
[default]
cs_name: gooddomain.org
cs_user: theuser
END_OF_FILE

    stdout=`get_config $ttf_config foo`
    assertEquals 0 $?       # get_config returns zero
    assertNull "$stdout"    # stdout is empty string
}

# test get_config when the value doesn't exist in the config file
# but the name does
test_get_config_name_no_value() {
    ttf_config=_ttf_config.conf
    cat > $ttf_config << 'END_OF_FILE'
[default]
cs_name: gooddomain.org
cs_user: 
END_OF_FILE

    stdout=`get_config $ttf_config cs_user`
    assertEquals 0 $?       # get config returns zero
    assertNull "$stdout"    # stdout is empty string
}

# test the function to create directories owned by root
# even if they already exist. Note: we're not testing
# for ownership by root so that the tests don't have to
# be run as root
#
test_create_dir() {
    list="_ttf_dir1 _ttf_dir2 _ttf_dir3"

    create_dir $list
    for d in $list
    do
        test -d $d
        assertTrue "directory $d exists" $?
    done
}

# test the function to find the configuration file
#
test_find_config() {
    local d
    local troot=_testingroot
    TESTING_ROOT=$troot
    local tdirs="/etc /etc/ftp_upload /etc/opt/ftp_upload"
    local tfile=uploader.conf

    # create the testing directories
    for d in $tdirs
    do
        mkdir --parents "$troot$d"
    done

    # test no config file
    local res=`find_config`
    assertEquals "find_config: wrong no-file value retuned" \
        /etc/opt/ftp_upload/$tfile "$res"

    # test config file detection in each standard directory
    for d in $tdirs
    do
        touch "$troot$d/uploader.conf"
        res=`find_config`
        assertEquals "find_config: wrong value returned" "$troot$d/$tfile" "$res"
    done

    # test config file detection in current directory
    touch uploader.conf
    res=`find_config`
    assertEquals "find_config: wrong value returned" "./uploader.conf" "$res"
}


. `which shunit2`    
