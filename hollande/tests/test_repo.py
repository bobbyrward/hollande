import unittest

from ..repository import parse_repo_string


class TestRepoParsing(unittest.TestCase):
    def test_parsed(self):
        owner, name = parse_repo_string('bobbyrward/hollande')
        self.assertEqual(owner, 'bobbyrward')
        self.assertEqual(name, 'hollande')

    def test_bad_format(self):
        with self.assertRaises(ValueError):
            parse_repo_string('bobbyrward-hollande')
