#!/usr/bin/python3
"""This script will either create the libvirt hooks files, 'lxc' and 'qemu', or return
a json string containing the hook file info derived from the hooks.conf file.

Useage:
    libvirthooks [--return-json]
    
    The user should only edit the hooks.conf file. Not the hook files themselves.

    This script reads the file, 'hooks.conf', located in /etc/libvirt/hooks/.
    Creates a backup of the current 'lxc' and 'qemu' hook files if they exist.
    Then re-writes both the 'lxc' and 'qemu' hook files and makes them executable.
    
    --return-json
            Returns a json string containing the hook file info. Hook files are not created.
"""

import argparse
import json
import os
import re
import shutil
import sys

#For testing
    #hooks_dir = "../testdir/"
    #hooks_conf_path = "../testdir/hooks.conf"
hooks_dir = "/etc/libvirt/hooks/"
hooks_conf_path = "/etc/libvirt/hooks/hooks.conf"


def create_parser():
    parser = argparse.ArgumentParser(description='Parse the hooks configuration file and create the lxc and qemu hooks files. If no arguments are given, the contents of the configuration file for the current hook files are printed to the screen.')
    parser.add_argument('-c', '--create', action='store_true', help='Create the hooks files using /etc/libvirt/hooks/hooks.conf. Specify a different configuration file with the -f option.')
    parser.add_argument('-f', '--file', metavar='path', help='specify different config file path. Default is /etc/libvirt/hooks/hooks.conf.')
    parser.add_argument('-j', '--json', action='store_true', help='return a json string representing the current configuration.')

    return parser


def clean_conf_data():
    """Read 'hooks.conf' flie and remove all comments and blank lines
    
    Returns:
        A list contianing each configuration line from the hooks.conf file
    """
    cleaned_data = []
    empty_line_pattern = re.compile(r'^\s*$')
    
    with open(hooks_conf_path, 'r') as f:
        for line in f:
            # remove comment from line
            config_line, _, comment = line.partition('#')
            if empty_line_pattern.search(config_line) is None:
                k, _, v = config_line.partition('=')
                cleaned_data.extend(["{0}={1}".format(k,v).strip()])

    return cleaned_data


def get_antlet_data(cleaned_data):
    """Creates a list of dictionaries, each of which contains the port forwarding info of each stanza in the hooks.conf file.

    Args:
        cleaned_data: A list of lines of portforwarding info
    
    Returns:
        A list of dictionaries of port forwarding info
        Example dictionary of port forwarding info:
        {
            "antlet_name":"ansible",
            "antlet_type":"kvm", 
            "antlet_ipaddr":"10.1.1.33",
            "host_ipaddr":"192.168.1.3",
            "host_ports":" '3333' '4444' "
            "antlet_ports":" '3333' '4444' "
        }
    """
    list_of_antlets = []
    antlet_info = dict()

    for line in cleaned_data:
        if "antlet_name" in line:
            if len(antlet_info) != 0:
                list_of_antlets.append(antlet_info)

            antlet_info = dict()

            k, _, v = line.partition('=')
            antlet_info[k] = v

        else:
            k, _, v = line.partition('=')

            if "portmap" not in line:
                antlet_info[k] = v
            else:
                hostport, _, antletport = v.partition(':')

                if "host_ports" not in antlet_info:
                    antlet_info["host_ports"] = "'{}' ".format(hostport)
                    #print(antlet_info["host_ports"])
                    antlet_info["antlet_ports"] = "'{}' ".format(antletport)
                else:
                    antlet_info["host_ports"] += "'{}' ".format(hostport)
                   # print(antlet_info["host_ports"])
                    antlet_info["antlet_ports"] += "'{}' ".format(antletport)

    list_of_antlets.append(antlet_info)
    return list_of_antlets


def create_case_statement(list_of_antlets, antlet_type):
    """Creates the case statement used in the hook file.

    Args:
        list_of_antlets: List of dictionaries containing each antlets port forwarding info
        antlet_type: A string - 'lxc' or 'kvm'
    
    Returns:
        A string of the case statement.
    """
    case_statement = "case $antlet_name in\n"
    case_statment_string = ""

    for antlet_dict in list_of_antlets:
        if antlet_dict["antlet_type"] == antlet_type:
            case_statment_string += antlet_dict["antlet_name"] + ")\n"
            case_statment_string += "\thost_ipaddr=" + antlet_dict["host_ipaddr"] + "\n"
            case_statment_string += "\tantlet_ipaddr=" + antlet_dict["antlet_ipaddr"] + "\n"
            case_statment_string += "\thost_ports=(" + antlet_dict["host_ports"] + ")\n"
            case_statment_string += "\tantlet_ports=(" + antlet_dict["antlet_ports"] + ")\n"
            case_statment_string += "\t;;\n"

            case_statement += case_statment_string
            case_statment_string = ""

    case_statement += "*)\n\texit\n\t;;\nesac\n"

    return case_statement


def backup_hook_files():
    """Create a backup of the existing lxc and qemu files if they exist."""
    # qemu exists
    if os.path.isfile(hooks_dir + "qemu"):
        shutil.copyfile(hooks_dir + 'qemu', hooks_dir + 'qemu.bak')
        os.chmod(hooks_dir + "qemu.bak", 0o755)
    # lxc exists
    if os.path.isfile(hooks_dir + "lxc"):
        shutil.copyfile(hooks_dir + 'lxc', hooks_dir + 'lxc.bak')
        os.chmod(hooks_dir + "lxc.bak", 0o755)


def write_hook_file(case_statement, antlet_type):
    """Create the hook file.

    Args:
        case_statement: String containing the case statement
        antlet_type: String - 'lxc' or 'kvm'
    """
    if antlet_type == "kvm":
        hook_file_path = hooks_dir + "qemu"
    else:
        hook_file_path = hooks_dir + "lxc"

    header_string = '''#!/bin/bash
## CONFIGFILE: {}

# Do not edit this file.
# Edit the hooks.conf configuration file: /etc/libvirt/hooks/hooks.conf
# Then run the libvirthooks script

antlet_name=$1
antlet_type=`basename "$0"`
action=$2

'''.format(hooks_conf_path)

    footer_string = '''
if [ "$action" = "stopped" ] || [ "$action" = "reconnect" ] || [ "$action" = "start" ]; then
    echo `date` hook/${antlet_type} "antlet ${antlet_name}: $action" >>/var/log/libvirt/hook.log
fi

length=$(( ${#host_ports[@]} - 1 ))
if [ "$action" = "stopped" ] || [ "$action" = "reconnect" ]; then
  for i in `seq 0 $length`; do
    echo "`date` hook/${antlet_type} antlet ${antlet_name}: Closing port ${host_ports[$i]} -> ${antlet_ports[$i]} " >>/var/log/libvirt/hook.log
    iptables -t nat -D PREROUTING -d ${host_ipaddr} -p udp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -D FORWARD -d ${antlet_ipaddr}/32 -p udp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
    iptables -t nat -D PREROUTING -d ${host_ipaddr} -p tcp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -D FORWARD -d ${antlet_ipaddr}/32 -p tcp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
  done
fi
if [ "$action" = "start" ] || [ "$action" = "reconnect" ]; then
  for i in `seq 0 $length`; do
    echo "`date` hook/${antlet_type} antlet ${antlet_name}: Mapping port ${host_ports[$i]} -> ${antlet_ports[$i]} " >>/var/log/libvirt/hook.log
    iptables -t nat -A PREROUTING -d ${host_ipaddr} -p tcp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -I FORWARD -d ${antlet_ipaddr}/32 -p tcp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
    iptables -t nat -A PREROUTING -d ${host_ipaddr} -p udp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -I FORWARD -d ${antlet_ipaddr}/32 -p udp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
  done
fi

'''

    try:
        with open(hook_file_path, 'w') as hook_file:
            hook_file.write(header_string + case_statement + footer_string)
        os.chmod(hook_file_path, 0o755)
    except:
        print("Problem with {}".format(hook_file_path))
        sys.exit()


def get_origin_config_file_path():
    """
    """
    regex_config_path_comment = re.compile(r'^## CONFIGFILE: ')
    # qemu exists
    if os.path.isfile(hooks_dir + "lxc"):
        with open(hooks_dir + "lxc", 'r') as f:
            for line in f:
                if regex_config_path_comment.search(line) is not None:
                    return line.partition(':')[2].strip()
                    
    elif os.path.isfile(hooks_dir + "qemu"):
        with open(hooks_dir + "qemu", 'r') as f:
            for line in f:
                if regex_config_path_comment.search(line) is not None:
                    return line.partition(':')[2].strip()
    else:
        return None


def print_current_config():
    config_file = get_origin_config_file_path()
    if config_file is None:
        print("Neither /etc/libvirt/hooks/lxc nor qemu exist. No custom ports currently forwarding.")
    else:
        message = "The existing hook files were created from: {}".format(config_file)
        print('-' * len(message))
        print(message)
        print('-' * len(message) + '\n')
        with open(config_file, 'r') as f:
            print(f.read())


def main():
    """Does one of three things.
    1. Create the hooks files.
    2. Return a json string.
    3. Print the current config file contents
    """
    args = create_parser().parse_args()
    config_file = args.file
    return_json = args.json
    create = args.create

    if return_json:
        config_file = get_origin_config_file_path()
        if config_file is None:
            print('[]')
            sys.exit()

    if config_file:
        global hooks_conf_path
        hooks_conf_path = config_file

    cleaned_data = clean_conf_data()
    antlet_data_list = get_antlet_data(cleaned_data)

    if return_json:
        print(json.dumps(antlet_data_list, separators=(',', ':')))
        return
    elif create:
        lxc_case_statement = create_case_statement(antlet_data_list, "lxc")
        kvm_case_statement = create_case_statement(antlet_data_list, "kvm")
        backup_hook_files()
        write_hook_file(lxc_case_statement, "lxc")
        write_hook_file(kvm_case_statement, "kvm")
    else:
        print_current_config()


if __name__ == "__main__":
    main()
