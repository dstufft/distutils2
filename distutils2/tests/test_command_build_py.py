"""Tests for distutils.command.build_py."""

import os
import sys

from distutils2.command.build_py import build_py
from distutils2.dist import Distribution
from distutils2.errors import PackagingFileError

from distutils2.tests import unittest, support


class BuildPyTestCase(support.TempdirManager,
                      support.LoggingCatcher,
                      unittest.TestCase):

    def test_package_data(self):
        sources = self.mkdtemp()
        pkg_dir = os.path.join(sources, 'pkg')
        os.mkdir(pkg_dir)
        f = open(os.path.join(pkg_dir, "__init__.py"), "w")
        try:
            f.write("# Pretend this is a package.")
        finally:
            f.close()
        # let's have two files to make sure globbing works
        f = open(os.path.join(pkg_dir, "README.txt"), "w")
        try:
            f.write("Info about this package")
        finally:
            f.close()
        f = open(os.path.join(pkg_dir, "HACKING.txt"), "w")
        try:
            f.write("How to contribute")
        finally:
            f.close()

        destination = self.mkdtemp()

        dist = Distribution({"packages": ["pkg"],
                             "package_dir": sources})

        dist.command_obj["build"] = support.DummyCommand(
            force=False,
            build_lib=destination,
            use_2to3_fixers=None,
            convert_2to3_doctests=None,
            use_2to3=False)
        dist.packages = ["pkg"]
        dist.package_data = {"pkg": ["*.txt"]}
        dist.package_dir = sources

        cmd = build_py(dist)
        cmd.compile = True
        cmd.ensure_finalized()
        self.assertEqual(cmd.package_data, dist.package_data)

        cmd.run()

        # This makes sure the list of outputs includes byte-compiled
        # files for Python modules but not for package data files
        # (there shouldn't *be* byte-code files for those!).
        # FIXME the test below is not doing what the comment above says, and
        # if it did it would show a code bug: if we add a demo.py file to
        # package_data, it gets byte-compiled!
        outputs = cmd.get_outputs()
        self.assertEqual(len(outputs), 4, outputs)
        pkgdest = os.path.join(destination, "pkg")
        files = os.listdir(pkgdest)
        self.assertEqual(sorted(files), ["HACKING.txt", "README.txt",
                                         "__init__.py", "__init__.pyc"])

    def test_empty_package_dir(self):
        # See SF 1668596/1720897.
        # create the distribution files.
        sources = self.mkdtemp()
        pkg = os.path.join(sources, 'pkg')
        os.mkdir(pkg)
        open(os.path.join(pkg, "__init__.py"), "wb").close()
        testdir = os.path.join(pkg, "doc")
        os.mkdir(testdir)
        open(os.path.join(testdir, "testfile"), "wb").close()

        os.chdir(sources)
        dist = Distribution({"packages": ["pkg"],
                             "package_dir": sources,
                             "package_data": {"pkg": ["doc/*"]}})
        dist.script_args = ["build"]
        dist.parse_command_line()

        try:
            dist.run_commands()
        except PackagingFileError:
            self.fail("failed package_data test when package_dir is ''")

    def test_byte_compile(self):
        project_dir, dist = self.create_dist(py_modules=['boiledeggs'])
        os.chdir(project_dir)
        self.write_file('boiledeggs.py', 'import antigravity')
        cmd = build_py(dist)
        cmd.compile = True
        cmd.build_lib = 'here'
        cmd.finalize_options()
        cmd.run()

        found = os.listdir(cmd.build_lib)
        self.assertEqual(sorted(found), ['boiledeggs.py', 'boiledeggs.pyc'])

    def test_byte_compile_optimized(self):
        project_dir, dist = self.create_dist(py_modules=['boiledeggs'])
        os.chdir(project_dir)
        self.write_file('boiledeggs.py', 'import antigravity')
        cmd = build_py(dist)
        cmd.compile = True
        cmd.optimize = 1
        cmd.build_lib = 'here'
        cmd.finalize_options()
        cmd.run()

        found = os.listdir(cmd.build_lib)
        self.assertEqual(sorted(found),
                         ['boiledeggs.py', 'boiledeggs.pyc', 'boiledeggs.pyo'])

    @unittest.skipUnless(hasattr(sys, 'dont_write_bytecode'),
                         'sys.dont_write_bytecode not supported')
    def test_byte_compile_under_B(self):
        # make sure byte compilation works under -B (dont_write_bytecode)
        self.addCleanup(setattr, sys, 'dont_write_bytecode',
                        sys.dont_write_bytecode)
        sys.dont_write_bytecode = True
        self.test_byte_compile()
        self.test_byte_compile_optimized()


def test_suite():
    return unittest.makeSuite(BuildPyTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
