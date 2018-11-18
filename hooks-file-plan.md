# Create Hooks file for antsle
1. try..catch file operations
1. validate config file syntax
1. validate antlet_name, IPs
1. validate antlet info is complete
1. validate unique host_port
1. reduce info needed. optional antlet_ip, antlet_type and host_ip
1. display current configured host ports
1. specify tcp, udp or both

Done:
1. _create hook files from config file_
1. _backup hook files before writing new files_
1. _comment functions - for help(func_name)_
1. _option to return json string_

## Get Port Forwarding Info
Use a configuration file as the input to create the hooks files.

### Inputs
File: hooks.conf

    antlet_name=mysql-db
    antlet_type=lxc
    antlet_ipaddr=10.1.1.22
    host_ipaddr=192.168.1.3
    portmap=2222:2222
    portmap=...

- antlet_name: must be the first item in the stanza
- antlet_type: kvm or lxc
- host_ipaddr: the IP address of the inbound interface (br0, 1, 2, 3)
- portmappings
    - in the form hostport:antletport e.g. 8080:80
    - must have at least one
    - can have multiple portmap lines
    - the hostport and antletport can be different

The ideal - onle three pieces of info required:

    antlet_name=mysql-db
    host_ipaddr=192.168.1.3  # will default to br0's IP if not present
    portmap=2222:2222

## Auto Input
ToDo:
- get antlet type
- get antlet ip
- get host ip

Done:

## Checks
ToDo:
- /etc/libvirt/hooks/ exists
- lxc or qemu file exists       # we are re-writing the file so is this necessary?
- Valid antlet name
- Duplicate interface/hostport

Done:

## Other functions:
- Backup and rollback hook files
- List host ports already used
- Display all antlet port-mappings
- Display single antlet port-mappings

---

## Help

    # create-hook-file --help  
    Usage: create-hook-files.py [options]
    Only edit the /etc/libvirt/hooks/hooks.conf configuration file. 

    Options:
      -h,  --help           Show this help message
      -v,  --verbose        Display feedback for each step processed
      --hostports           Display used host ports by both lxc and kvm antlets
      --rollback            rollback to previous files
      --show ANTLET         antlet_name or 'all' - Display antlet port mappings
