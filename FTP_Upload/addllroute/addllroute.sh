#!/bin/sh
################################################################################
#
# Copyright (C) 2020 Neighborhood Guard, Inc.  All rights reserved.
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

# Add a route to link-local addresses to a (hopefully the only)
# network interface.  This is in support of helping the findaxiscam
# command to find the DHCP (not link-local) address of an Axis IP
# camera.  This is part of a workaround for limitations in avahi-daemon
# and is just plain lame.
# 

# get the name of the first interface in the routing table
iface=`ifconfig -s | egrep -v '^Iface' | awk '{print $1; exit}'`

# add a link-level route to it. If the command fails because
# the route already exists, exit with good status.
# If it fails for some other reason, exit with error status
# 
if errmsg=`route add -net 169.254.0.0/16 dev $iface 2>&1`
then
    exit 0
else
    if echo "$errmsg" | grep -q 'File exists' 
    then
	exit 0
    fi
fi
echo "$errmsg" >&2
exit 1
