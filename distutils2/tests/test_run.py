"""Tests for distutils2.run."""

import os
import sys
from StringIO import StringIO

from distutils2 import install
from distutils2.tests import unittest, support
from distutils2.run import main

from distutils2.tests.support import assert_python_ok

# setup script that uses __file__
setup_using___file__ = """\
__file__

from distutils2.run import setup
setup()
"""

setup_prints_cwd = """\
import os
print os.getcwd()

from distutils2.run import setup
setup()
"""


class RunTestCase(support.TempdirManager,
                  support.LoggingCatcher,
                  unittest.TestCase):

    def setUp(self):
        super(RunTestCase, self).setUp()
        self.old_stdout = sys.stdout
        self.old_argv = sys.argv, sys.argv[:]

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.argv = self.old_argv[0]
        sys.argv[:] = self.old_argv[1]
        super(RunTestCase, self).tearDown()

    # TODO restore the tests removed six months ago and port them to pysetup

    def test_install(self):
        # making sure install returns 0 or 1 exit codes
        project = os.path.join(os.path.dirname(__file__), 'package.tgz')
        install_path = self.mkdtemp()
        old_get_path = install.get_path
        install.get_path = lambda path: install_path
        old_mod = os.stat(install_path).st_mode
        os.chmod(install_path, 0)
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            self.assertFalse(install.install(project))
            self.assertEqual(main(['install', 'blabla']), 1)
        finally:
            sys.stderr = old_stderr
            os.chmod(install_path, old_mod)
            install.get_path = old_get_path

    def test_show_help(self):
        # smoke test, just makes sure some help is displayed
        pythonpath = os.environ.get('PYTHONPATH')
        d2parent = os.path.dirname(os.path.dirname(__file__))
        if pythonpath is not None:
            pythonpath =  os.pathsep.join((pythonpath, d2parent))
        else:
            pythonpath = d2parent

        status, out, err = assert_python_ok(
            '-c', 'from distutils2.run import main; main()', '--help',
            PYTHONPATH=pythonpath)
        self.assertEqual(status, 0)
        self.assertGreater(out, '')
        self.assertEqual(err, '')


def test_suite():
    return unittest.makeSuite(RunTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
