"""Tests for ``distutils2.command.install_distinfo``. """

import os
import sys
import csv

from distutils2.command.install_distinfo import install_distinfo
from distutils2.core import Command
from distutils2.metadata import DistributionMetadata
from distutils2.tests import unittest, support

try:
    import hashlib
except ImportError:
    from distutils2._backport import hashlib


class DummyInstallCmd(Command):

    def __init__(self, dist=None):
        self.outputs = []
        self.distribution = dist

    def __getattr__(self, name):
            return None

    def ensure_finalized(self):
        pass

    def get_outputs(self):
        return self.outputs + \
               self.get_finalized_command('install_distinfo').get_outputs()


class InstallDistinfoTestCase(support.TempdirManager,
                              support.LoggingCatcher,
                              support.EnvironGuard,
                              unittest.TestCase):

    checkLists = lambda self, x, y: self.assertListEqual(sorted(x), sorted(y))

    def test_empty_install(self):
        pkg_dir, dist = self.create_dist(name='foo',
                                         version='1.0')
        install_dir = self.mkdtemp()

        install = DummyInstallCmd(dist)
        dist.command_obj['install_dist'] = install

        cmd = install_distinfo(dist)
        dist.command_obj['install_distinfo'] = cmd

        cmd.initialize_options()
        cmd.distinfo_dir = install_dir
        cmd.ensure_finalized()
        cmd.run()

        self.checkLists(os.listdir(install_dir), ['foo-1.0.dist-info'])

        dist_info = os.path.join(install_dir, 'foo-1.0.dist-info')
        self.checkLists(os.listdir(dist_info),
                        ['METADATA', 'RECORD', 'REQUESTED', 'INSTALLER'])
        self.assertEqual(open(os.path.join(dist_info, 'INSTALLER')).read(),
                         'distutils')
        self.assertEqual(open(os.path.join(dist_info, 'REQUESTED')).read(),
                         '')
        meta_path = os.path.join(dist_info, 'METADATA')
        self.assertTrue(DistributionMetadata(path=meta_path).check())

    def test_installer(self):
        pkg_dir, dist = self.create_dist(name='foo',
                                         version='1.0')
        install_dir = self.mkdtemp()

        install = DummyInstallCmd(dist)
        dist.command_obj['install_dist'] = install

        cmd = install_distinfo(dist)
        dist.command_obj['install_distinfo'] = cmd

        cmd.initialize_options()
        cmd.distinfo_dir = install_dir
        cmd.installer = 'bacon-python'
        cmd.ensure_finalized()
        cmd.run()

        dist_info = os.path.join(install_dir, 'foo-1.0.dist-info')
        self.assertEqual(open(os.path.join(dist_info, 'INSTALLER')).read(),
                         'bacon-python')

    def test_requested(self):
        pkg_dir, dist = self.create_dist(name='foo',
                                         version='1.0')
        install_dir = self.mkdtemp()

        install = DummyInstallCmd(dist)
        dist.command_obj['install_dist'] = install

        cmd = install_distinfo(dist)
        dist.command_obj['install_distinfo'] = cmd

        cmd.initialize_options()
        cmd.distinfo_dir = install_dir
        cmd.requested = False
        cmd.ensure_finalized()
        cmd.run()

        dist_info = os.path.join(install_dir, 'foo-1.0.dist-info')
        self.checkLists(os.listdir(dist_info),
                        ['METADATA', 'RECORD', 'INSTALLER'])

    def test_no_record(self):
        pkg_dir, dist = self.create_dist(name='foo',
                                         version='1.0')
        install_dir = self.mkdtemp()

        install = DummyInstallCmd(dist)
        dist.command_obj['install_dist'] = install

        cmd = install_distinfo(dist)
        dist.command_obj['install_distinfo'] = cmd

        cmd.initialize_options()
        cmd.distinfo_dir = install_dir
        cmd.no_record = True
        cmd.ensure_finalized()
        cmd.run()

        dist_info = os.path.join(install_dir, 'foo-1.0.dist-info')
        self.checkLists(os.listdir(dist_info),
                        ['METADATA', 'REQUESTED', 'INSTALLER'])

    def test_record(self):
        pkg_dir, dist = self.create_dist(name='foo',
                                         version='1.0')
        install_dir = self.mkdtemp()

        install = DummyInstallCmd(dist)
        dist.command_obj['install_dist'] = install

        fake_dists = os.path.join(os.path.dirname(__file__), '..',
                                  '_backport', 'tests', 'fake_dists')
        fake_dists = os.path.realpath(fake_dists)

        # for testing, we simply add all files from _backport's fake_dists
        dirs = []
        for dir in os.listdir(fake_dists):
                full_path = os.path.join(fake_dists, dir)
                if (not dir.endswith('.egg') or dir.endswith('.egg-info') or
                    dir.endswith('.dist-info')) and os.path.isdir(full_path):
                    dirs.append(full_path)

        for dir in dirs:
            for (path, subdirs, files) in os.walk(dir):
                install.outputs += [os.path.join(path, f) for f in files]
                install.outputs += [os.path.join('path', f + 'c')
                                    for f in files if f.endswith('.py')]


        cmd = install_distinfo(dist)
        dist.command_obj['install_distinfo'] = cmd

        cmd.initialize_options()
        cmd.distinfo_dir = install_dir
        cmd.ensure_finalized()
        cmd.run()

        dist_info = os.path.join(install_dir, 'foo-1.0.dist-info')

        expected = []
        for f in install.get_outputs():
            if f.endswith('.pyc') or \
               f == os.path.join(install_dir, 'foo-1.0.dist-info', 'RECORD'):
                expected.append([f, '', ''])
            else:
                size = os.path.getsize(f)
                md5 = hashlib.md5()
                md5.update(open(f).read())
                hash = md5.hexdigest()
                expected.append([f, hash, str(size)])

        parsed = []
        f = open(os.path.join(dist_info, 'RECORD'), 'rb')
        try:
            reader = csv.reader(f, delimiter=',',
                                   lineterminator=os.linesep,
                                   quotechar='"')
            parsed = list(reader)
        finally:
            f.close()

        self.maxDiff = None
        self.checkLists(parsed, expected)


def test_suite():
    return unittest.makeSuite(InstallDistinfoTestCase)


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")