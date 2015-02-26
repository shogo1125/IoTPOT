#! /usr/bin/python
# -*- coding: utf-8 -*-
# last modified : 2015/02/23
# this script need getdata.sh and datafile to run.

import SocketServer
import sys
import socket
import datetime
import time
import subprocess
import threading
import binascii

option="\xff\xfd\x01\xff\xfd\x1f\xff\xfd\x21\xff\xfb\x01\xff\xfb\x03"
loginmes="192.0.0.64.login:\x20"
password="Password:\x20"
incorrect="Login incorrect\x0d\x0a"
rn="\x0d\x0a"

class Handler(SocketServer.StreamRequestHandler):
# The Handler class for proxy
# Make instance with each connection and override handle() method
# Session from Attacker : self.request

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
        print "%s IP %s.%s > %s.%s : connect" \
            % (self.date,self.attackerIP,self.client_address[1],self.server.server_address[0],self.targetPORT)

        odd = (self.targetPORT % 29) + 1
        cmd = "./getdata.sh %d 1" % odd
        pic = subprocess.Popen(cmd.strip().split(" "),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        option = pic.stdout.read()
        self.request.send(option)
        time.sleep(0.2)

        cmd = "./getdata.sh %d 2" % odd
        pic = subprocess.Popen(cmd.strip().split(" "),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        loginmes = pic.stdout.read()
        self.request.send(loginmes)

        cmd = "./getdata.sh %d 3" % odd
        pic = subprocess.Popen(cmd.strip().split(" "),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        password = pic.stdout.read()

        while True:
            if (datetime.datetime.today() - self.date).seconds > 300:
                break
            # receive response from Attacer
            try:
                self.payload = self.request.recv(8192)
                if len(self.payload) != 0:
                    if self.payload.find(rn) == -1:
                        print "%s" % binascii.hexlify(self.payload)
                    elif self.state == 0:
                        print "user:%s" % self.payload
                        self.state += 1
                        self.payload += password
                        time.sleep(0.3)
                    elif self.state == 1:
                        print "pass:%s" % self.payload
                        self.state = 0 
                        self.payload = incorrect + loginmes
                        time.sleep(1)
                    else:
                        print "ERROR"
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
    print "=== Set up low honeypot(NO)  ==="
    server.serve_forever()

