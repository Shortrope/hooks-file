#!/usr/bin/python3

'''
Required args
    antlet_name
    host_ipaddr (or interface name)
    portmap1 - in the form hostport:antletport 8080:80
    [portmapN]

Other derived info
    antlet_type
    antlet_ipaddr

Other application vars
    hook_file_path
    hook_file
    file_head
    file_case
    file_iptables
    saved_cases
    
Checks
    antlet_exists()
    valid_host_ip()
    'hooks' directory exists
    lxc or qemu file exists
'''


# Import statements
import os
import sys
from subprocess import Popen, PIPE
import shutil

# enough args
# create 'usage' var
usage = """Usage: hook-file.py antlet_name host_ipaddr portmap1 portmap2 ...
antlet_type:    lxc or kvm
portmap:        enter portmap in the form - hostport:antletport e.g. 8080:80
"""
# if no - print 'usage'
if len(sys.argv) < 4:
    print(usage)
    sys.exit()

# assign args to vars
antlet_name = sys.argv[1]
host_ipaddr = sys.argv[2]
host_ports = ""
antlet_ports = ""

for portmap in sys.argv[3:]:
    host_ports += "'{0}' ".format(portmap.split(':')[0])
    antlet_ports += "'{0}' ".format(portmap.split(':')[1])


# validate args - quit if no
# antlet_exists
def antlet_exists(antlet_name):
    for virshcmd in ["virsh -c qemu:///system", "virsh -c lxc:///"]:
        vlist = Popen([ virshcmd + " list --name --all"], stdout=PIPE, shell=True)
        for bytes in vlist.stdout:
            line = bytes.decode().strip()
            if line == antlet_name:
                return True
    return False

if not antlet_exists(antlet_name):
    print("'{0}' does not exist!".format(antlet_name))
    sys.exit()

# valid host IP addr

# Get derived antlet info and assign to vars
# antlet_type = get_antlet_type(antlet_name)
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

antlet_type = get_antlet_type(antlet_name)

# antlet_ipaddr = get_antlet_ipaddr(antlet_name)
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

antlet_ipaddr = get_antlet_ip(antlet_name)



# Other application prep work
# create hooks dir if not exists
hook_file_dir = "/etc/libvirt/hooks/"
if antlet_type == "kvm":
    hook_file = hook_file_dir + "qemu"
else:
    hook_file = hook_file_dir + "lxc"

if not os.path.exists(hook_file_dir):
    try:
        os.mkdir(hook_file_dir)
    except OSError:
        print("Could not create 'hooks' directory!")
        sys.exit()

# Does hook file exist?
if os.path.isfile(hook_file):
    # Yes: create backup file
    hook_file_bak = hook_file + ".bak"
    try:
        shutil.copy("{}".format(hook_file), "{}".format(hook_file_bak))
    except Exception:
        print("Could not create backup of {}!".format(hook_file))

    # Yes: get current case statement cases


else:
    # No: create file and chmod it
    print(hook_file + " does not exist!")
    
# create 'head' var
# create 'case' var
# create 'iptables' var

# Write 'head', 'case' and 'iptables' to file


print("antlet_name: " + antlet_name)
print("antlet_type: " + antlet_type)
print("antlet_ipaddr: " + antlet_ipaddr)
print("host_ipaddr: " + host_ipaddr)
print("host_ports: " + host_ports)
print("antlet_ports: " + antlet_ports)
print("hook_file_dir: " + hook_file_dir)
print("hook_file: " + hook_file)
