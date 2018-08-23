#!/bin/sh

# this allows the unit-test code to hijack avahi-browse
if [ -z "$AVAHI_BROWSE" ]
then
    AVAHI_BROWSE=avahi-browse
fi

# Find Axis IP cameras using mDNS-SD.
# Select the relevant parts of the avahi response. Avahi only outputs
# one of the IP addresses in the mDNS-SD reply. :-P
# Change the lame backslash escapes in Avahi -p output into
# '|' "escapes" to avoid the shell interpreting the backslashes.
# For avahi responses that show a ZeroConf address, ping that address
# to bring the device's addresses into the ARP table (it's not the
# ping, it's the lookup that does it), find the device's MAC address in
# the table, then see if there's a regular IP address associated with it.
# If so, show that address, else the ZeroConf address.
# Filter the (*decimal*!) escape for space out of the description.
#
$AVAHI_BROWSE -t -r -p _axis-video._tcp \
| awk -F ';' '/^=/{print $8, $7, $4}' \
| sed 's/\\/|/g' \
| while read line
do
    set $line
    ipaddr=$1
    case $1 in
      169.254.*) 
        zcip=$1
        ping -c 1 $zcip > /dev/null
        hwaddr=`arp -n | awk /$zcip/'{print $3}'`
        ipaddr=`arp -n | grep -v $zcip | awk /$hwaddr/'{print $1; exit}'`
        if [ -z "$ipaddr" ]
        then
            ipaddr=$zcip
        fi
        ;;
    esac
    echo $ipaddr $2 "$3" | sed 's/|032/ /g'
done

