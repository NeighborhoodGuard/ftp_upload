#!/bin/sh

AVAHI_BROWSE=avahi_browse
export AVAHI_BROWSE

findaxiscam() {
    . ../findaxiscam.sh
}

# mock ping
ping() {
    echo -n
}

# mock arp
arp() {
    printf "%s" "$arpout"
}

# mock avahi-browse
avahi_browse() {
    printf "%s" "$about"
}

arp1=`cat << StopHere
Address                  HWtype  HWaddress           Flags Mask            Iface
169.254.119.131          ether   00:40:8c:ef:e2:f1   C                     enp3s0
169.254.119.132          ether   00:40:8c:ef:e2:f2   C                     enp3s0
169.254.119.133          ether   00:40:8c:ef:e2:f3   C                     enp3s0
192.168.1.128            ether   f4:5c:89:89:89:63   C                     enp3s0
192.168.1.1              ether   60:a4:4c:d2:a4:b8   C                     enp3s0
192.168.1.22             ether   18:5e:0f:92:11:a2   C                     enp3s0
192.168.1.81             ether   00:40:8c:ef:e2:f1   C                     enp3s0
192.168.1.82             ether   00:40:8c:ef:e2:f2   C                     enp3s0
192.168.1.83             ether   00:40:8c:ef:e2:f3   C                     enp3s0
StopHere
`
ab1=`cat << StopHere
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local;axis-00408cefe2f1.local;169.254.119.131;80;"macaddress=00408CEFE2F1"
StopHere
`

ab2=`cat << StopHere
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local;axis-00408cefe2f1.local;169.254.119.131;80;"macaddress=00408CEFE2F1"
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F2;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F2;_axis-video._tcp;local;axis-00408cefe2f2.local;169.254.119.132;80;"macaddress=00408CEFE2F2"
StopHere
`

ab3=`cat << StopHere
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local;axis-00408cefe2f1.local;169.254.119.131;80;"macaddress=00408CEFE2F1"
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F2;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F2;_axis-video._tcp;local;axis-00408cefe2f2.local;169.254.119.132;80;"macaddress=00408CEFE2F2"
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F3;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F3;_axis-video._tcp;local;axis-00408cefe2f3.local;169.254.119.133;80;"macaddress=00408CEFE2F3"
StopHere
`
ab1_dhcp=`cat << StopHere
+;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local
=;enp3s0;IPv4;AXIS\032P1357\032-\03200408CEFE2F1;_axis-video._tcp;local;axis-00408cefe2f1.local;192.168.1.81;80;"macaddress=00408CEFE2F1"
StopHere
`

expected1=`cat << StopHere
192.168.1.81 axis-00408cefe2f1.local AXIS P1357 - 00408CEFE2F1
StopHere
`

expected2=`cat << StopHere
192.168.1.81 axis-00408cefe2f1.local AXIS P1357 - 00408CEFE2F1
192.168.1.82 axis-00408cefe2f2.local AXIS P1357 - 00408CEFE2F2
StopHere
`

expected3=`cat << StopHere
192.168.1.81 axis-00408cefe2f1.local AXIS P1357 - 00408CEFE2F1
192.168.1.82 axis-00408cefe2f2.local AXIS P1357 - 00408CEFE2F2
192.168.1.83 axis-00408cefe2f3.local AXIS P1357 - 00408CEFE2F3
StopHere
`

expected_no_arp_dhcp_ipaddr=`cat << StopHere
169.254.119.131 axis-00408cefe2f1.local AXIS P1357 - 00408CEFE2F1
StopHere
`

test_one_cam_ab_zconf_ipaddr() {
    about="$ab1"
    arpout="$arp1"
    actual=`findaxiscam`
    assertEquals "$expected1" "$actual"
}

test_two_cams_ab_zconf_ipaddr() {
    about="$ab2"
    arpout="$arp1"
    actual=`findaxiscam`
    assertEquals "$expected2" "$actual"
}

test_three_cams_ab_zconf_ipaddr() {
    about="$ab3"
    arpout="$arp1"
    actual=`findaxiscam`
    assertEquals "$expected3" "$actual"
}

test_no_arp_dhcp_ipaddr() {
    about="$ab1"
    arpout=`printf "%s" "$arp1" | grep -v 192.168.1.81`
    actual=`findaxiscam`
    assertEquals "$expected_no_arp_dhcp_ipaddr" "$actual"
}

test_ab_dhcp_ipaddr() {
    about="$ab1_dhcp"
    arpout="$arp1"
    actual=`findaxiscam`
    assertEquals "$expected1" "$actual"
}

. `which shunit2`
