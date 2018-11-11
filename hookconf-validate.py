#!/usr/bin/python3

import os
import re

# config file exists
def config_exists(hook_conf_path="/etc/libvirt/hooks/hooks.conf"):
    if os.path.isfile(hook_conf_path):
        return True
    return False

def check_config_syntax(hook_conf_path="/etc/libvirt/hooks/hooks.conf"):
    valid_syntax = True
    blank_lines_re = re.compile(r'^\s*$')
    keywords = ["antlet_name", "antlet_type", "antlet_ipaddr", "host_ipaddr", "portmap"]
    with open(hook_conf_path, 'r') as f:
        for i, line in enumerate(f):
            line_syntax = False
            blank_line_matches = blank_lines_re.findall(line)
            if len(blank_line_matches) == 1:
                line_syntax = True
                continue
            elif line.startswith("#"):
                line_syntax = True
                continue
            else:
                for kw in keywords:
                    if line.startswith(kw):
                        line_syntax = True
                        break
            if not line_syntax:
                message = "line {}".format(i+1)
                valid_syntax = False
                break
    if valid_syntax:
        message = "Syntax good."

    return (valid_syntax, message)

def main(hook_conf_path):
    print("hooks.conf exists: " + str(config_exists(hook_conf_path)))
    print("Lines start with '#' or keyword or blank: {}".format(check_config_syntax(hook_conf_path)))

if __name__ == '__main__':
    main("./hooks.conf")
