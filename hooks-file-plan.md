# Create Hooks file for antsle

## Get Port Forwarding Info
Use command line arguments to input info

### Inputs
- antlet name
- host interface (br0, 1, 2, 3)
- portmappings
    - space separated
    - in the form hostport:antletport e.g. 8080:80

## Auto Input
ToDo:
- get host ip

Done:
- _get antlet type_
- _get antlet ip_

## Checks
ToDo:
- List host ports already used
- Does the antlet have an entry in the file
- Modify antlet ports
- Remove antlet ports

Done:
- _/etc/libvirt/hooks/ exists_
- _Valid antlet name_
- _lxc or qemu file exists_

Other functions:
- List host ports already used
- Display all antlet port-mappings
- Display single antlet port-mappings
---

## Help
    # create-hook-file --help  
    Usage: hook-file.py [options] antlet_name ingress_interface portmap1 [portmap2 ... portmapN]
    portmap can be in the form of a single port number
      80                    Both the host and antlet port are the same
    or in the form host_port:antlet_port useing a semicolon separator
      8080:80               Differing host and antlet port numbers

    Options:
      -h,  --help           Show this help message
      -v,  --verbose        Display feedback for each step processed
      --hostports           Display used host ports by both lxc and kvm antlets
      --show ANTLET         antlet_name or 'all' - Display antlet port mappings
