#!/bin/sh

# this allows the unit-test code to hijack avahi-browse
if [ -z "$AVAHI_BROWSE" ]
then
    AVAHI_BROWSE=avahi-browse
fi

# Find Axis IP cameras using mDNS-SD.
# Select the relevant parts of the avahi response. 
# Avahi only outputs one of the IP addresses in the mDNS-SD reply. :-P
# Colonize the MAC address shown by Avahi.
# Change the lame backslash escapes in Avahi -p output into
# '|' "escapes" to avoid the shell interpreting the backslashes.
# If the Avahi IP address is not a ZeroConf address, print the result.
# If it is a ZeroConf address, ping the address to try to bring
# the non-ZeroConf address into the ARP table
# then, search through the ARP table and find
# the first IP address for the MAC address that is not a ZeroConf address.
# If we don't find one, print ZeroConf address.
# Finally, filter the (*decimal*!) escape for space out of the description.
#
$AVAHI_BROWSE -t -r -p _axis-video._tcp \
| awk -F ';' '/^=/{print $4, $7, $8, $10}' \
| sed -e \
    's/"macaddress=\(..\)\(..\)\(..\)\(..\)\(..\)\(..\)"/\1:\2:\3:\4:\5:\6/' \
    -e 's/\\/|/g' \
| while read line
do
    set $line
    displayname=$1
    netname=$2
    ipaddr=$3
    hwaddr=$4
    case $ipaddr in
      169.254.*) 
    	zcip=$ipaddr
	ping -c 1 $zcip > /dev/null
        ipaddr=`arp -n | grep -v '^169\.254\.' | grep -i "$hwaddr" \
	        | awk '{print $1; exit}'`
        if [ -z "$ipaddr" ]
        then
            ipaddr=$zcip
        fi
        ;;
    esac
    echo $ipaddr $netname "$displayname" | sed 's/|032/ /g'
done
exit
