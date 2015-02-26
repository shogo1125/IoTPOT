#! /usr/bin/python
# -*- coding: utf-8 -*-
# last modified : 2015/01/21

import SocketServer
import sys
import socket
import datetime
import time
import subprocess
import threading

class Handler(SocketServer.StreamRequestHandler):
# The Handler class for proxy
# Make instance with each connection and override handle() method
# Session from Attacker : self.request
    
    # constracta
    def __init__(self,request,client_address,server):
        self.attackerIP = ""
        self.targetPORT = ""
        self.payload = ""
        self.date = datetime.datetime.today()
        self.proxySocket = None
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)
    
    def handle(self):
        self.receiveQueue = []
        self.attackerIP = self.client_address[0]
        self.targetPORT = self.server.server_address[1] 
        print "%s IP %s.%s > %s.%s : connect" \
                 % (self.date,self.attackerIP,self.client_address[1],self.server.server_address[0],self.targetPORT)
        th = QemuThread(self.attackerIP,self.targetPORT,self.request,self.receiveQueue)
        th.start()

        self.request.setblocking(0)
        while True:
            if (datetime.datetime.today() - self.date).seconds > 300:
                break

            # receive response from Attacer
            try:
                self.payload = self.request.recv(8192)
                if len(self.payload) != 0:
                    #if self.payload.find("wget") != -1:
                      # send mail
                      iself.payload = self.payload.replace(" ","_")
                      #cmd = "python send_mail.py '%s'" % self.payload
                      #print "FOUND MALWARE !!"  
                      #subprocess.call(cmd.strip().split(" "))
                      self.payload = self.payload.replace("wget","WGOT")

                    if self.payload.find("exit") != -1:
                      self.payload="EXIT" 
                    self.receiveQueue.append(self.payload)
            except socket.error:
                pass

            # check reveice Queue
            if len(th.receiveQueue) != 0:
                sendData = th.receiveQueue.pop(0)
                self.request.send(sendData)
                self.date = datetime.datetime.today()

        self.request.close()
        print "%s IP %s.%s > %s.%s : session closed" \
                 % (self.date,self.attackerIP,self.client_address[1],self.server.server_address[0],self.targetPORT)


class QemuThread(threading.Thread):
# The Thread class for Qemu
# Make instance with each connection from Attacker

    def __init__(self,attackerIP,targetPORT,proxyThreadRequest,proxyThreadQueue):
        self.proxyThreadQueue = proxyThreadQueue
        self.receiveQueue = []
        self.proxyThreadRequest = proxyThreadRequest
###############################################################
        self.attackerIP = attackerIP
###############################################################
        self.targetPORT = targetPORT
        self.responce = ""
        self.date = datetime.datetime.today()
        self.qemuSocket = None
        threading.Thread.__init__(self)

        if not self.qemuSocket:
          # make Client socket
          self.qemuSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
          try:
            # socket connect
            self.qemuSocket.connect((self.attackerIP,int(self.targetPORT)))
          except IndexError: 
            print "Error Connection to Qemu"
    
    def run(self):
        self.qemuSocket.setblocking(0)
        while True:
            if ( datetime.datetime.today() - self.date).seconds > 300:
                break

            try:
                # receive responce from Qemu
                self.responce = self.qemuSocket.recv(8192)
                if len(self.responce) != 0:
                    self.receiveQueue.append(self.responce)
            except:
                pass
            # check receive Queue
            if len(self.proxyThreadQueue) != 0:
                sendData = self.proxyThreadQueue.pop(0)
                self.qemuSocket.send(sendData)
                self.date = datetime.datetime.today()

        print "%s : Qemu session closed" % self.date

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python %s #port " % sys.argv[0],sys.exit(-1)

    PORT = int(sys.argv[1])
    server = SocketServer.ThreadingTCPServer(('', PORT), Handler)
    print "=== Set up proxy ==="
    server.serve_forever()

