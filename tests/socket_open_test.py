#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# vi:ts=4:et

import socket
import pycurl
import unittest
try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib as urllib_parse

from . import app
from . import runwsgi
from . import util

setup_module, teardown_module = runwsgi.app_runner_setup((app.app, 8380))

socket_open_called = False
socket_open_address = None

def socket_open(family, socktype, protocol, address):
    global socket_open_called
    global socket_open_address
    socket_open_called = True
    socket_open_address = address

    #print(family, socktype, protocol, (socket.inet_ntop(family, address[0]), address[1]))
    s = socket.socket(family, socktype, protocol)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    return s

class SocketOpenTest(unittest.TestCase):
    def setUp(self):
        self.curl = pycurl.Curl()
    
    def tearDown(self):
        self.curl.close()
    
    def test_socket_open(self):
        self.curl.setopt(pycurl.OPENSOCKETFUNCTION, socket_open)
        self.curl.setopt(self.curl.URL, 'http://localhost:8380/success')
        sio = util.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, sio.write)
        self.curl.perform()
        
        assert socket_open_called
        self.assertEqual((socket.inet_pton(socket.AF_INET, "127.0.0.1"), 8380), socket_open_address)
        self.assertEqual('success', sio.getvalue())
