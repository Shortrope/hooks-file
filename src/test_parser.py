import unittest
from argparse import ArgumentParser
from libvirthooks import *

class TestLibvirthooks(unittest.TestCase):


    def test_parser_create_option(self):
        parser = create_parser()
        for option in ('-c', '--create'):
            args = parser.parse_args([option])
            self.assertTrue(args.create)


    def test_parser_without_create_option(self):
        parser = create_parser()
        args = parser.parse_args([])
        self.assertFalse(args.create)


    def test_parser_file_option(self):
        parser = create_parser()
        for option in ('-f', '--file'):
            args = parser.parse_args([option, '/path/to/file'])
            self.assertEqual(args.file, '/path/to/file')


    def test_parser_file_option_without_path(self):
        parser = create_parser()
        for option in ('-f', '--file'):
            with self.assertRaises(SystemExit):
                parser.parse_args([option])
                

    def test_parser_json_option(self):
        parser = create_parser()
        for option in ('-j', '--json'):
            args = parser.parse_args([option])
            self.assertTrue(args.json)

    
    def test_parser_without_json_option(self):
        parser = create_parser()
        args = parser.parse_args([])
        self.assertFalse(args.json)


if __name__ == '__main__':
    unittest.main()