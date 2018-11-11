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
# enough args
    # create 'usage' var
    # if no - print 'usage'
    # quit

# assign args to vars

# validate args - quit if no
    # antlet_exists
    # valid host IP addr

# Get antlet info and assign to vars
    # antlet_type = get_antlet_type(antlet_name)
    # antlet_ipaddr = get_antlet_ipaddr(antlet_name)

# Other application prep work
    # create hooks dir if not exists
    # Does hook file exist?
        # Yes: create backup file
        # Yes: Save case statement cases
        # No: create file and chmod it

# create 'head' var
# create 'case' var
# create 'iptables' var

# Write 'head', 'case' and 'iptables' to file

