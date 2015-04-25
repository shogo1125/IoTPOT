#! /usr/bin/env python
# -*- coding: utf-8 -*-
# last modified : 2015/04/13

import SocketServer
import socket
import datetime
import time
import threading
import binascii
import sys
import subprocess
import struct

status_response="HTTP/1.0 200 OK\x0d\x0a"
date="Date: Mon Apr 13 21:04:03 2015"
header_response="""Server: DVRDVS-Webs
Last-modified: Thu Feb 21 02:41:54 2013
Content-length: 1658
Content-type: text/html
"""


class Handler(SocketServer.StreamRequestHandler):

    # constracta
    def __init__(self,request,client_address,server):
        self.attackerIP = ""
        self.targetPORT = ""
        self.payload = ""
        self.date = datetime.datetime.today()
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)

    def handle(self):
        self.attackerIP = self.client_address[0]
        self.targetPORT = self.server.server_address[1]
        self.receiveQueue = []
        self.binary = ""
        print "%s IP %s.%s > %s.%s : connect" \
        % (self.date,self.attackerIP,self.client_address[1],self.server.server_address[0],self.targetPORT)

        self.request.setblocking(0)
        while True:
            if (datetime.datetime.today() - self.date).seconds > 300:
                break
            # receive response from Attacer
            try:
                self.payload = self.request.recv(8192)
                if len(self.payload) != 0:
                    if self.payload.find("GET") != -1:
			print "find GET"
                        f = open("index.html")
                        html = f.read()
			# date
                        f.close()
                        self.payload = status_response + date +"\x0d\x0a"+ header_response +"\x0d\x0a"+ html
                    else:
                        self.payload = "Error"

                    self.receiveQueue.append(self.payload)

            except socket.error:
                pass

            # check reveice Queue
            if len(self.receiveQueue) != 0:
                sendData = self.receiveQueue.pop(0)
                self.request.send(sendData)
                self.date = datetime.datetime.today()

        self.request.close()
        print "%s : [A] session closed" % self.date


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python %s #port" % sys.argv[0],sys.exit(-1)

    PORT = int(sys.argv[1])
    server = SocketServer.ThreadingTCPServer(('', PORT), Handler)
    print "=== Set up low honeypot(HTTP)  ==="
    server.serve_forever()

