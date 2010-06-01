"""Tests for distutils.command.bdist."""
import unittest2, urllib, urllib2
from distutils2.tests.pypi_server import PyPIServer, PYPI_DEFAULT_STATIC_PATH
import os.path

class PyPIServerTest(unittest2.TestCase):

    def test_records_requests(self):
        """We expect that PyPIServer can log our requests"""
        server = PyPIServer()
        server.start()
        self.assertEqual(len(server.requests), 0)

        data = "Rock Around The Bunker"
        headers = {"X-test-header": "Mister Iceberg"}

        request = urllib2.Request(server.full_address, data, headers)
        urllib2.urlopen(request)
        self.assertEqual(len(server.requests), 1)
        environ, request_data = server.requests[-1]
        self.assertIn("Rock Around The Bunker", request_data)
        self.assertEqual(environ["HTTP_X_TEST_HEADER"], "Mister Iceberg")
        server.stop()

    def test_serve_static_content(self):
        """PYPI Mocked server can serve static content from disk.
        """

        def uses_local_files_for(server, url_path):
            """Test that files are served statically (eg. the output from the
            server is the same than the one made by a simple file read.
            """
            url = server.full_address + url_path 
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            file = open(PYPI_DEFAULT_STATIC_PATH + url_path)
            return response.read() == file.read()

        server = PyPIServer(static_uri_paths=["simple", "external"])
        server.start()
        
        # the file does not exists on the disc, so it might not be served
        url = server.full_address + "/simple/unexisting_page"
        request = urllib2.Request(url)
        try:
            urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self.assertEqual(e.getcode(), 404)

        # now try serving a content that do exists
        self.assertTrue(uses_local_files_for(server, "/simple/index.html"))

        # and another one in another root path
        self.assertTrue(uses_local_files_for(server, "/external/index.html"))

def test_suite():
    return unittest2.makeSuite(PyPIServerTest)

if __name__ == '__main__':
    unittest2.main(defaultTest="test_suite")
