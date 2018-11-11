#!/usr/bin/python3

import os
import sys
from subprocess import Popen, PIPE

usage = """Usage: hook-file.py antlet_name host_ipaddr portmap1 portmap2 ...
antlet_type:    lxc or kvm
portmap:        enter portmap in the form - hostport:antletport e.g. 8080:80
"""

if len(sys.argv) < 4:
    print(usage)
    sys.exit()


antlet_name = sys.argv[1]
host_ipaddr = sys.argv[2]
host_ports = ""
antlet_ports = ""

for portmap in sys.argv[3:]:
    host_ports += "'{0}' ".format(portmap.split(':')[0])
    antlet_ports += "'{0}' ".format(portmap.split(':')[1])



def antlet_exists(antlet_name):
    for virshcmd in ["virsh -c qemu:///system", "virsh -c lxc:///"]:
        vlist = Popen([ virshcmd + " list --name --all"], stdout=PIPE, shell=True)
        for bytes in vlist.stdout:
            line = bytes.decode().strip()
            if line == antlet_name:
                return True
    return False

def get_antlet_type(antlet_name):
    lxccmd = "virsh -c lxc:///"
    kvmcmd = "virsh -c qemu:///system"

    for antlet_type in ["lxc", "kvm"]:

        if antlet_type == "lxc":
            vlist = Popen([ lxccmd + " list --name --all"], stdout=PIPE, shell=True)
        else:
            vlist = Popen([ kvmcmd + " list --name --all"], stdout=PIPE, shell=True)

        for bytes in vlist.stdout:
            line = bytes.decode().strip()
            if line == antlet_name:
                return antlet_type


def get_antlet_ip(antlet_name):
    lxccmd = "virsh -c lxc:///"
    kvmcmd = "virsh -c qemu:///system"

    baseip = Popen("antsleOS-baseip", stdout=PIPE)
    for line in baseip.stdout:
        baseip = line.decode().strip()

    if get_antlet_type(antlet_name) == "lxc":
        antlet_xml = Popen([ lxccmd + " dumpxml " + antlet_name], stdout=PIPE, shell=True)
    else:
        antlet_xml = Popen([ kvmcmd + " dumpxml " + antlet_name], stdout=PIPE, shell=True)

    for bytes in antlet_xml.stdout:
        line = bytes.decode()
        if line.find('b2:61:6e:73:6c') != -1:
            mac = line.split("'")[1]
            hex_ip = mac.split(":")[-1]
            return "{0}{1}".format(baseip, int(hex_ip, 16))

def create_case_statement():
    pass


if not antlet_exists(antlet_name):
    print("'{0}' does not exist!".format(antlet_name))
    sys.exit()

antlet_type = get_antlet_type(antlet_name)
antlet_ipaddr = get_antlet_ip(antlet_name)

hookfile_path = "/etc/libvirt/hooks/"
if antlet_type == "kvm":
    hook_file = hookfile_path + "qemu"
else:
    hook_file = hookfile_path + "lxc"



head = """#!/bin/bash

antlet_name=$1
antlet_type=`basename "$0"`
trigger=$2

echo `date` hook/${antlet_type} "antlet ${1}" "${2}" >>/var/log/libvirt/hook.log

"""
variables = """
{0})
  antlet_ipaddr={1}
  host_ipaddr={2}
  host_ports=( {3} )
  antlet_ports=( {4} )
""".format(antlet_name, antlet_ipaddr, host_ipaddr, host_ports, antlet_ports)

body = """

# Update iptables
length=$(( ${#host_ports[@]} - 1 ))
if [ "${1}" = "${antlet_name}" ]; then
    if [ "${2}" = "stopped" ] || [ "${2}" = "reconnect" ]; then
        for i in `seq 0 $length`; do
            echo "`date` hook/${antlet_type} antlet $antlet_name Closing port ${host_ports[$i]} -> ${antlet_ports[$i]} " >>/var/log/libvirt/hook.log
            iptables -t nat -D PREROUTING -d ${host_ipaddr} -p udp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
            iptables -D FORWARD -d ${antlet_ipaddr}/32 -p udp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
            iptables -t nat -D PREROUTING -d ${host_ipaddr} -p tcp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
            iptables -D FORWARD -d ${antlet_ipaddr}/32 -p tcp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
        done
    fi
    if [ "${2}" = "start" ] || [ "${2}" = "reconnect" ]; then
        for i in `seq 0 $length`; do
            echo "`date` hook/${antlet_type} antlet $antlet_name Mapping port ${host_ports[$i]} -> ${antlet_ports[$i]} " >>/var/log/libvirt/hook.log
            iptables -t nat -A PREROUTING -d ${host_ipaddr} -p tcp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
            iptables -I FORWARD -d ${antlet_ipaddr}/32 -p tcp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
            iptables -t nat -A PREROUTING -d ${host_ipaddr} -p udp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
            iptables -I FORWARD -d ${antlet_ipaddr}/32 -p udp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
        done
    fi
fi
"""

# check 'hooks' directory exists
if not os.path.exists("/etc/libvirt/hooks"):
    try:
        os.mkdir("/etc/libvirt/hooks")
    except OSError:
        print("Could not create directory!")
        sys.exit()


hook_file_exists = os.path.isfile(hook_file)
try:
    with open(hook_file, "a") as f:
        if not hook_file_exists:
            f.write(head)

        f.write(variables)
        f.write(body)

except Exception:
    print("Problem creating file: {}".format(hook_file))
    sys.exit()

os.chmod(hook_file, 0o755)

