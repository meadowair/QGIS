# -*- coding: utf-8 -*-
"""QGIS Unit tests for QgsBlockingNetworkRequest

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import chr
from builtins import str
__author__ = 'Nyall Dawson'
__date__ = '12/11/2018'
__copyright__ = 'Copyright 2018, The QGIS Project'

import qgis  # NOQA

import mockedwebserver
import os
from qgis.testing import unittest, start_app
from qgis.core import QgsBlockingNetworkRequest
from utilities import unitTestDataPath
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtTest import QSignalSpy
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

app = start_app()


class TestQgsBlockingNetworkRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server, cls.port = mockedwebserver.launch()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def testFetchEmptyUrl(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        err = request.get(QNetworkRequest(QUrl()))
        self.assertEqual(len(spy), 1)
        self.assertEqual(err, QgsBlockingNetworkRequest.ServerExceptionError)
        self.assertEqual(request.errorMessage(), 'Protocol "" is unknown')
        reply = request.reply()
        self.assertFalse(reply.content())

    def testFetchBadUrl(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        err = request.get(QNetworkRequest(QUrl('http://x')))
        self.assertEqual(len(spy), 1)
        self.assertEqual(err, QgsBlockingNetworkRequest.ServerExceptionError)
        self.assertEqual(request.errorMessage(), 'Host x not found')
        reply = request.reply()
        self.assertFalse(reply.content())

    def testFetchBadUrl2(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)

        handler = mockedwebserver.SequentialHandler()
        handler.add('GET', '/ffff', 404)
        with mockedwebserver.install_http_handler(handler):
            err = request.get(QNetworkRequest(QUrl('http://localhost:' + str(TestQgsBlockingNetworkRequest.port) + '/ffff')))
        self.assertEqual(len(spy), 1)
        self.assertEqual(err, QgsBlockingNetworkRequest.ServerExceptionError)
        self.assertIn('Not Found', request.errorMessage())
        reply = request.reply()
        self.assertEqual(reply.error(), QNetworkReply.ContentNotFoundError)
        self.assertFalse(reply.content())

    def testGet(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        handler = mockedwebserver.SequentialHandler()
        handler.add('GET', '/test.html', 200, {'Content-type': 'text/html'}, '<html></html>\n')
        with mockedwebserver.install_http_handler(handler):
            err = request.get(QNetworkRequest(QUrl('http://localhost:' + str(TestQgsBlockingNetworkRequest.port) + '/test.html')), True)
        self.assertEqual(len(spy), 1)
        self.assertEqual(err, QgsBlockingNetworkRequest.NoError)
        self.assertEqual(request.errorMessage(), '')
        reply = request.reply()
        self.assertEqual(reply.error(), QNetworkReply.NoError)
        self.assertEqual(reply.content(), '<html></html>\n')
        self.assertEqual(reply.rawHeaderList(), [b'Server',
                                                 b'Date',
                                                 b'Content-type',
                                                 b'Content-Length'])
        self.assertEqual(reply.rawHeader(b'Content-type'), 'text/html')
        self.assertEqual(reply.rawHeader(b'xxxxxxxxx'), '')
        self.assertEqual(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute), 200)
        self.assertEqual(reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute), 'OK')
        self.assertEqual(reply.attribute(QNetworkRequest.RedirectionTargetAttribute), None)

    def testHead(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        handler = mockedwebserver.SequentialHandler()
        handler.add('HEAD', '/test.html', 200, {'Content-type': 'text/html'})
        with mockedwebserver.install_http_handler(handler):
            err = request.head(QNetworkRequest(QUrl('http://localhost:' + str(TestQgsBlockingNetworkRequest.port) + '/test.html')), True)
        self.assertEqual(len(spy), 1)
        self.assertEqual(err, QgsBlockingNetworkRequest.NoError)
        self.assertEqual(request.errorMessage(), '')

    def testPost(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        handler = mockedwebserver.SequentialHandler()
        handler.add('POST', '/test.html', 200, expected_body=b"foo")
        with mockedwebserver.install_http_handler(handler):
            req = QNetworkRequest(QUrl('http://localhost:' + str(TestQgsBlockingNetworkRequest.port) + '/test.html'))
            req.setHeader(QNetworkRequest.ContentTypeHeader, 'text/plain')
            err = request.post(req, b"foo")
        self.assertEqual(err, QgsBlockingNetworkRequest.NoError)
        self.assertEqual(request.errorMessage(), '')

    def testPut(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        handler = mockedwebserver.SequentialHandler()
        handler.add('PUT', '/test.html', 200, expected_body=b"foo")
        with mockedwebserver.install_http_handler(handler):
            req = QNetworkRequest(QUrl('http://localhost:' + str(TestQgsBlockingNetworkRequest.port) + '/test.html'))
            req.setHeader(QNetworkRequest.ContentTypeHeader, 'text/plain')
            err = request.put(req, b"foo")
        self.assertEqual(err, QgsBlockingNetworkRequest.NoError)
        self.assertEqual(request.errorMessage(), '')

    def testDelete(self):
        request = QgsBlockingNetworkRequest()
        spy = QSignalSpy(request.downloadFinished)
        handler = mockedwebserver.SequentialHandler()
        handler.add('DELETE', '/test.html', 200)
        with mockedwebserver.install_http_handler(handler):
            err = request.deleteResource(QNetworkRequest(QUrl('http://localhost:' + str(TestQgsBlockingNetworkRequest.port) + '/test.html')))
        self.assertEqual(len(spy), 1)
        self.assertEqual(err, QgsBlockingNetworkRequest.NoError)
        self.assertEqual(request.errorMessage(), '')


if __name__ == "__main__":
    unittest.main()
