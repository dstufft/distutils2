"""Tests for distutils.command.build_py."""

import tempfile
import distutils2
from distutils2.tests import support
from distutils2.tests.support import unittest
from distutils2.command.build_py import Mixin2to3

class Mixin2to3TestCase(unittest.TestCase):
    def test_convert_code_only(self):
        # used to check if code gets converted properly.
        code_content = "print 'test'\n"
        code_handle = tempfile.NamedTemporaryFile(delete=True)
        code_name = code_handle.name

        code_handle.write(code_content)
        code_handle.flush()

        mixin2to3 = Mixin2to3() 
        mixin2to3._run_2to3([code_name])
        converted_code_content = "print('test')\n"
        new_code_content = "".join(open(code_name).readlines())

        self.assertEquals(new_code_content, converted_code_content)

    def test_doctests_only(self):
        # used to check if doctests gets converted properly.
        doctest_content = '"""\n>>> print test\ntest\n"""\nprint test\n\n'
        doctest_handle = tempfile.NamedTemporaryFile(delete=True)
        doctest_name = doctest_handle.name

        doctest_handle.write(doctest_content)
        doctest_handle.flush()

        mixin2to3 = Mixin2to3()
        mixin2to3._run_2to3([doctest_name])

        converted_doctest_content = '"""\n>>> print(test)\ntest\n"""\nprint(test)\n\n\n'
        new_doctest_content = "".join(open(doctest_name).readlines())

        self.assertEquals(new_doctest_content, converted_doctest_content)

def test_suite():
    return unittest.makeSuite(Mixin2to3TestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
