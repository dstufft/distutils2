"""Tests for distutils.cmd."""
import os
from distutils2.tests import captured_stdout, run_unittest

from distutils2.command.cmd import Command
from distutils2.dist import Distribution
from distutils2.errors import DistutilsOptionError
from distutils2.tests.support import unittest

class MyCmd(Command):
    def initialize_options(self):
        pass

class CommandTestCase(unittest.TestCase):

    def setUp(self):
        dist = Distribution()
        self.cmd = MyCmd(dist)

    def test_ensure_string_list(self):

        cmd = self.cmd
        cmd.not_string_list = ['one', 2, 'three']
        cmd.yes_string_list = ['one', 'two', 'three']
        cmd.not_string_list2 = object()
        cmd.yes_string_list2 = 'ok'
        cmd.ensure_string_list('yes_string_list')
        cmd.ensure_string_list('yes_string_list2')

        self.assertRaises(DistutilsOptionError,
                          cmd.ensure_string_list, 'not_string_list')

        self.assertRaises(DistutilsOptionError,
                          cmd.ensure_string_list, 'not_string_list2')

    def test_make_file(self):

        cmd = self.cmd

        # making sure it raises when infiles is not a string or a list/tuple
        self.assertRaises(TypeError, cmd.make_file,
                          infiles=1, outfile='', func='func', args=())

        # making sure execute gets called properly
        def _execute(func, args, exec_msg, level):
            self.assertEqual(exec_msg, 'generating out from in')
        cmd.force = True
        cmd.execute = _execute
        cmd.make_file(infiles='in', outfile='out', func='func', args=())

    def test_dump_options(self):

        msgs = []
        def _announce(msg, level):
            msgs.append(msg)
        cmd = self.cmd
        cmd.announce = _announce
        cmd.option1 = 1
        cmd.option2 = 1
        cmd.user_options = [('option1', '', ''), ('option2', '', '')]
        cmd.dump_options()

        wanted = ["command options for 'MyCmd':", '  option1 = 1',
                  '  option2 = 1']
        self.assertEqual(msgs, wanted)

    def test_ensure_string(self):
        cmd = self.cmd
        cmd.option1 = 'ok'
        cmd.ensure_string('option1')

        cmd.option2 = None
        cmd.ensure_string('option2', 'xxx')
        self.assertTrue(hasattr(cmd, 'option2'))

        cmd.option3 = 1
        self.assertRaises(DistutilsOptionError, cmd.ensure_string, 'option3')

    def test_ensure_string_list(self):
        cmd = self.cmd
        cmd.option1 = 'ok,dok'
        cmd.ensure_string_list('option1')
        self.assertEqual(cmd.option1, ['ok', 'dok'])

        cmd.option2 = ['xxx', 'www']
        cmd.ensure_string_list('option2')

        cmd.option3 = ['ok', 2]
        self.assertRaises(DistutilsOptionError, cmd.ensure_string_list,
                          'option3')

    def test_ensure_filename(self):
        cmd = self.cmd
        cmd.option1 = __file__
        cmd.ensure_filename('option1')
        cmd.option2 = 'xxx'
        self.assertRaises(DistutilsOptionError, cmd.ensure_filename, 'option2')

    def test_ensure_dirname(self):
        cmd = self.cmd
        cmd.option1 = os.path.dirname(__file__) or '.'
        cmd.ensure_dirname('option1')
        cmd.option2 = 'xxx'
        self.assertRaises(DistutilsOptionError, cmd.ensure_dirname, 'option2')

def test_suite():
    return unittest.makeSuite(CommandTestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
