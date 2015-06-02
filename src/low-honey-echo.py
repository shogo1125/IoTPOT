#! /usr/bin/env python
# -*- coding: utf-8 -*-
# last modified : 2015/02/28

import SocketServer
import socket
import datetime
import time
import threading
import binascii
import sys
import subprocess
import struct

loginmes="192.0.0.64.login:\x20"
password="Password:\x20"
incorrect="Login incorrect\x0d\x0a192.0.0.64.login:\x20"
rn="\x0d\x0a"
busybox="\x0d\x0a\x0d\x0a\x0d\x0aBusyBox v1.1.2 (2007.05.09-01:19+0000) Built-in shell (ash)\x0d\x0a" \
        "Enter 'help' for a list of built-in commands.\x0d\x0a\x0d\x0a\x7e\x20\x24\x20"


class Handler(SocketServer.StreamRequestHandler):

    # constracta
    def __init__(self,request,client_address,server):
        self.attackerIP = ""
        self.targetPORT = ""
        self.payload = ""
        self.state = 0
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
        time.sleep(0.2)
        self.request.send(loginmes)
        while True:
            if (datetime.datetime.today() - self.date).seconds > 300:
                break
            # receive response from Attacer
            try:
                self.payload = self.request.recv(8192)
                if len(self.payload) != 0:
                    if self.payload.find(rn) == -1:
                        print "%s" % binascii.hexlify(self.payload)
                        self.payload = ""
                    elif self.state == 0:
                        print "user:%s" % self.payload
                        self.state += 1
                        self.payload += password
                        time.sleep(0.3)
                    elif self.state == 1:
                        print "pass:%s" % self.payload
                        self.state += 1
                        self.payload = busybox
                        time.sleep(0.6)
                    else:
                        pass

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
    print "=== Set up low honeypot(ECHO)  ==="
    server.serve_forever()

