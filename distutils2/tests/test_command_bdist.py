"""Tests for distutils.command.bdist."""
import os
import sys
from StringIO import StringIO
from distutils2.errors import PackagingPlatformError
from distutils2.command.bdist import bdist, show_formats

from distutils2.tests import unittest, support


class BuildTestCase(support.TempdirManager,
                    support.LoggingCatcher,
                    unittest.TestCase):

    def test_formats(self):
        # let's create a command and make sure
        # we can set the format
        dist = self.create_dist()[1]
        cmd = bdist(dist)
        cmd.formats = ['msi']
        cmd.ensure_finalized()
        self.assertEqual(cmd.formats, ['msi'])

        # what formats does bdist offer?
        # XXX hard-coded lists are not the best way to find available bdist_*
        # commands; we should add a registry
        formats = ['bztar', 'gztar', 'msi', 'tar', 'wininst', 'zip']
        found = sorted(cmd.format_command)
        self.assertEqual(found, formats)

    def test_skip_build(self):
        # bug #10946: bdist --skip-build should trickle down to subcommands
        dist = self.create_dist()[1]
        cmd = bdist(dist)
        cmd.skip_build = True
        cmd.ensure_finalized()
        dist.command_obj['bdist'] = cmd

        names = ['bdist_dumb', 'bdist_wininst']
        if os.name == 'nt':
            names.append('bdist_msi')

        for name in names:
            subcmd = cmd.get_finalized_command(name)
            self.assertTrue(subcmd.skip_build,
                            '%s should take --skip-build from bdist' % name)

    def test_unsupported_platform(self):
        _os_name = os.name
        try:
            os.name = 'some-obscure-os'

            dist = self.create_dist()[1]
            cmd = bdist(dist)
            self.assertRaises(PackagingPlatformError, cmd.ensure_finalized)
        finally:
            os.name = _os_name

    def test_show_formats(self):
        saved = sys.stdout
        sys.stdout = StringIO()
        try:
            show_formats()
            stdout = sys.stdout.getvalue()
        finally:
            sys.stdout = saved

        # the output should be a header line + one line per format
        num_formats = len(bdist.format_commands)
        output = [line for line in stdout.split('\n')
                  if line.strip().startswith('--formats=')]
        self.assertEqual(len(output), num_formats)


def test_suite():
    return unittest.makeSuite(BuildTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
