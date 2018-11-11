#!/usr/bin/python3
from pprint import pprint as pp
import re

hooks_conf_path = "./hooks.conf"
#hooks_conf_path = "/etc/libvirt/hooks/hooks.conf"
#hooks_conf_path = "e:/_Projects/100/100-days-of-python/Projects/antsle hooks file/hooks.conf"


def clean_conf_data(hooks_conf_path="/etc/libvirt/hooks/hooks.conf"):
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


    '''
    Example of Created Dict
    {
        "antlet_name":"ansible",
        "antlet_type":"kvm", 
        "antlet_ipaddr":"10.1.1.33",
        "host_ipaddr":"192.168.1.3",
        "host_ports":" '3333' '4444' "
        "antlet_ports":" '3333' '4444' "
    }

    '''


def get_antlet_data(cleaned_data):
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


def write_hookfile(header_string, case_statment, footer_string):
    with open("./qemu", "w") as f:
        f.write(header_string + case_statment + footer_string)


def write_hook_file(case_statement, antlet_type):

    hooks_dir = "./"
    #hooks_dir = "/etc/libvirt/hooks/"

    if antlet_type == "kvm":
        hook_file_path = hooks_dir + "qemu"
    else:
        hook_file_path = hooks_dir + "lxc"

    header_string = '''#!/bin/bash

# Do not edit this file.
# Edit the hooks.conf configuration file: /etc/libvirt/hooks/hooks.conf
# Then run the hookconf.py script

antlet_name=$1
antlet_type=`basename "$0"`
action=$2

'''

    footer_string = '''
echo `date` hook/${antlet_type} "antlet ${antlet_name}: $action" >>/var/log/libvirt/hook.log

length=$(( ${#host_ports[@]} - 1 ))
if [ "$action" = "stopped" ] || [ "$action" = "reconnect" ]; then
  for i in `seq 0 $length`; do
    echo "`date` hook/${antlet_type} antlet $antlet_name Closing port ${host_ports[$i]} -> ${antlet_ports[$i]} " >>/var/log/libvirt/hook.log
    iptables -t nat -D PREROUTING -d ${host_ipaddr} -p udp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -D FORWARD -d ${antlet_ipaddr}/32 -p udp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
    iptables -t nat -D PREROUTING -d ${host_ipaddr} -p tcp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -D FORWARD -d ${antlet_ipaddr}/32 -p tcp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
  done
fi
if [ "$action" = "start" ] || [ "$action" = "reconnect" ]; then
  for i in `seq 0 $length`; do
    echo "`date` hook/${antlet_type} antlet $antlet_name Mapping port ${host_ports[$i]} -> ${antlet_ports[$i]} " >>/var/log/libvirt/hook.log
    iptables -t nat -A PREROUTING -d ${host_ipaddr} -p tcp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -I FORWARD -d ${antlet_ipaddr}/32 -p tcp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
    iptables -t nat -A PREROUTING -d ${host_ipaddr} -p udp --dport ${host_ports[$i]} -j DNAT --to ${antlet_ipaddr}:${antlet_ports[$i]}
    iptables -I FORWARD -d ${antlet_ipaddr}/32 -p udp -m state --state NEW,ESTABLISHED,RELATED --dport ${antlet_ports[$i]} -j ACCEPT
  done
fi

'''
    with open(hook_file_path, 'w') as hook_file:
        hook_file.write(header_string + case_statement + footer_string)


def main():

    clean_data = clean_conf_data(hooks_conf_path)
    antlet_data_list = get_antlet_data(clean_data)
    lxc_case_statement = create_case_statement(antlet_data_list, "lxc")
    kvm_case_statement = create_case_statement(antlet_data_list, "kvm")
    write_hook_file(lxc_case_statement, "lxc")
    write_hook_file(kvm_case_statement, "kvm")



# Only run the main() functon if run from the cli. 
# Do not run main() if importing in the REPL 
if __name__ == "__main__":
    main()