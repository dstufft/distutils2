"""Tests for distutils2.manifest."""
import os
import logging
from StringIO import StringIO
from distutils2.manifest import Manifest

from distutils2.tests import unittest, support

_MANIFEST = """\
recursive-include foo *.py   # ok
# nothing here

#

recursive-include bar \\
  *.dat   *.txt
"""

_MANIFEST2 = """\
README
file1
"""


class ManifestTestCase(support.TempdirManager,
                       support.LoggingCatcher,
                       unittest.TestCase):

    def setUp(self):
        super(ManifestTestCase, self).setUp()
        self.cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.cwd)
        super(ManifestTestCase, self).tearDown()

    def test_manifest_reader(self):
        tmpdir = self.mkdtemp()
        MANIFEST = os.path.join(tmpdir, 'MANIFEST.in')
        f = open(MANIFEST, 'w')
        f.write(_MANIFEST)
        f.close()

        manifest = Manifest()
        manifest.read_template(MANIFEST)

        warnings = self.get_logs(logging.WARNING)
        # the manifest should have been read and 3 warnings issued
        # (we didn't provide the files)
        self.assertEqual(3, len(warnings))
        for warning in warnings:
            self.assertIn('no files found matching', warning)

        # manifest also accepts file-like objects
        f = open(MANIFEST)
        manifest.read_template(f)
        f.close()

        # the manifest should have been read and 3 warnings issued
        # (we didn't provide the files)
        self.assertEqual(3, len(warnings))

    def test_default_actions(self):
        tmpdir = self.mkdtemp()
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(tmpdir)
        self.write_file('README', 'xxx')
        self.write_file('file1', 'xxx')
        content = StringIO(_MANIFEST2)
        manifest = Manifest()
        manifest.read_template(content)
        self.assertEqual(['README', 'file1'], manifest.files)


def test_suite():
    return unittest.makeSuite(ManifestTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
