import os, sys, shutil, re
from copy import copy
from os.path import join
from StringIO import StringIO
from distutils2.tests.support import unittest, TempdirManager
from distutils2.command.test import test
import subprocess

try:
    any
except NameError:
    from distutils2._backport import any

EXPECTED_OUTPUT_RE = '''\
FAIL: test_blah \\(myowntestmodule.SomeTest\\)
----------------------------------------------------------------------
Traceback \\(most recent call last\\):
  File ".+/myowntestmodule.py", line \\d+, in test_blah
    self.fail\\("horribly"\\)
AssertionError: horribly
'''

class TestTest(TempdirManager, unittest.TestCase):

    def setUp(self):
        super(TestTest, self).setUp()

        distutils2path = join(__file__, '..', '..', '..')
        distutils2path = os.path.abspath(distutils2path)
        self.old_pythonpath = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = distutils2path + ":" + self.old_pythonpath

    def tearDown(self):
        super(TestTest, self).tearDown()
        os.environ['PYTHONPATH'] = self.old_pythonpath

    def assert_re_match(self, pattern, string):
        def quote(s):
            lines = ['## ' + line for line in s.split('\n')]
            sep = ["#" * 60]
            return [''] + sep + lines + sep
        msg = quote(pattern) + ["didn't match"] + quote(string)
        msg = "\n".join(msg)
        if not re.search(pattern, string):
            self.fail(msg)

    def run_with_dist_cwd(self, pkg_dir):
        cwd = os.getcwd()
        command = [sys.executable, "setup.py", "test"]
        try:
            os.chdir(pkg_dir)
            test_proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            _, errors = test_proc.communicate()
            return errors
        finally:
            os.chdir(cwd)

    def prepare_dist(self, dist_name):
        pkg_dir = join(os.path.dirname(__file__), "dists", dist_name)
        temp_pkg_dir = join(self.mkdtemp(), dist_name)
        shutil.copytree(pkg_dir, temp_pkg_dir)
        return temp_pkg_dir
        
    def test_runs_simple_tests(self):
        self.pkg_dir = self.prepare_dist('simple_test')
        output = self.run_with_dist_cwd(self.pkg_dir)
        self.assert_re_match(EXPECTED_OUTPUT_RE, output)
        self.assertFalse(os.path.exists(join(self.pkg_dir, 'build')))

    def test_builds_extensions(self):
        self.pkg_dir = self.prepare_dist("extensions_test")
        output = self.run_with_dist_cwd(self.pkg_dir)
        self.assert_re_match(EXPECTED_OUTPUT_RE, output)
        self.assertTrue(os.path.exists(join(self.pkg_dir, 'build')))
        self.assertTrue(any(x.startswith('lib') for x in os.listdir(join(self.pkg_dir, 'build'))))

    def test_custom_test_loader(self):
        self.pkg_dir = self.prepare_dist("custom_loader")
        output = self.run_with_dist_cwd(self.pkg_dir)
        self.assert_re_match(EXPECTED_OUTPUT_RE, output)

    def _test_works_with_2to3(self):
        pass

    def _test_downloads_test_requires(self):
        pass

def test_suite():
    suite = [unittest.makeSuite(TestTest)]
    return unittest.TestSuite(suite)
