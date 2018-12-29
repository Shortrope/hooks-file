# Requirements

## config file
### 1. config file exists

### 2. config file has proper syntax and contents
- a line must be blank or start w one of the following strings:
    - "#"
    - "antlet_name"
    - "antlet_type"
    - "antlet_ipaddr"
    - "host_ipaddr"
    - "portmap"
- each antlet stanza has at least 5 lines
- the first line of each antlet stanza begins w the keyword string "antlet_name"
- each stanza must contain exactly one line that begins w each of the following keyword strings
    - "antlet_name"
    - "antlet_type"
    - "antlet_ipaddr"
    - "host_ipaddr"
    - "portmap"
- each stanza can contain more than one line that begins w the string "portmap"
- each line in the stanza must have an "=" after the keyword string with no whitespace between
- each line in the stanza must have a string after the "=" with no whitespace between

## Clean_conf_data

- each line must begin w one of the following keyword strings
    - "antlet_name"
    - "antlet_type"
    - "antlet_ipaddr"
    - "host_ipaddr"
    - "portmap"
- each line in the stanza must have an "=" after the keyword string with no whitespace between
- each line in the stanza must have a string after the "=" with no whitespace between
