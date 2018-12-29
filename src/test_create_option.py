import unittest
from argparse import ArgumentParser
from libvirthooks import *

class TestLibvirthooks(unittest.TestCase):

    def setuUp(self):
        self.default_config = """
# Example:
#    antlet_name=mysql-db
#    antlet_type=lxc
#    antlet_ipaddr=10.1.1.22
#    host_ipaddr=192.168.1.3
#    portmap=3306:3306      # mysql
#    portmap=3333:3333

antlet_name=docker
antlet_type=kvm
antlet_ipaddr=10.1.1.10
host_ipaddr=192.168.1.3
portmap=1000:1001       # funny port
portmap=2000:2002

antlet_name=ansible
antlet_type=lxc
antlet_ipaddr=10.1.1.11
host_ipaddr=192.168.1.3
portmap=1111:1111# wacky port
"""

    #def test_create_uses_default_config_file(self):

    #def test_create_with_different_config_file(self):

    #def test_create_adds_config_file_path_comment_to_hook_files(self):


if __name__ == '__main__':
    unittest.main()