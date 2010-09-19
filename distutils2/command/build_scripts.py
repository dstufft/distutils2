"""distutils.command.build_scripts

Implements the Distutils 'build_scripts' command."""

__revision__ = "$Id: build_scripts.py 77704 2010-01-23 09:23:15Z tarek.ziade $"

import os, re
from stat import ST_MODE
from distutils2.core import Command
from distutils2.util import convert_path, newer
from distutils2 import log
try:
    import sysconfig
except ImportError:
    from distutils2._backport import sysconfig
from distutils2.compat import Mixin2to3

# check if Python is called on the first line with this expression
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')

class build_scripts (Command, Mixin2to3):

    description = "\"build\" scripts (copy and fixup #! line)"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" (copy) to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ('executable=', 'e', "specify final destination interpreter path"),
        ]

    boolean_options = ['force']


    def initialize_options (self):
        self.build_dir = None
        self.scripts = None
        self.force = None
        self.executable = None
        self.outfiles = None
        self.use_2to3 = False
        self.convert_2to3_doctests = None
        self.use_2to3_fixers = None

    def finalize_options (self):
        self.set_undefined_options('build',
                                   ('build_scripts', 'build_dir'),
                                   'use_2to3', 'use_2to3_fixers',
                                   'convert_2to3_doctests', 'force',
                                   'executable')
        self.scripts = self.distribution.scripts

    def get_source_files(self):
        return self.scripts

    def run (self):
        if not self.scripts:
            return
        copied_files = self.copy_scripts()
        if self.use_2to3 and self.copied_files:
            self._run_2to3(self.copied_files, fixers=self.use_2to3_fixers)

    def copy_scripts (self):
        """Copy each script listed in 'self.scripts'; if it's marked as a
        Python script in the Unix way (first line matches 'first_line_re',
        ie. starts with "\#!" and contains "python"), then adjust the first
        line to refer to the current Python interpreter as we copy.
        """
        self.mkpath(self.build_dir)
        outfiles = []
        for script in self.scripts:
            adjust = 0
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            # Always open the file, but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''

            if adjust:
                log.info("copying and adjusting %s -> %s", script,
                         self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not sysconfig.is_python_build():
                        outf.write("#!%s%s\n" %
                                   (self.executable,
                                    post_interp))
                    else:
                        outf.write("#!%s%s\n" %
                                   (os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                           "python%s%s" % (sysconfig.get_config_var("VERSION"),
                                           sysconfig.get_config_var("EXE"))),
                                    post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                if f:
                    f.close()
                self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 07777
                    newmode = (oldmode | 0555) & 07777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)
        return outfiles
    # copy_scripts ()

# class build_scripts