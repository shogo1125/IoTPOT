#! /usr/bin/python
# -*- coding: utf-8 -*-
# last modified : 2015/03/05
# this script need getdata.sh and datafile to run.

import SocketServer
import sys
import socket
import datetime
import time
import subprocess
import threading
import binascii
import struct

option="\xff\xfd\x01\xff\xfd\x1f\xff\xfd\x21\xff\xfb\x01\xff\xfb\x03"
loginmes="192.0.0.64.login:\x20"
password="Password:\x20"
incorrect="Login incorrect\x0d\x0a"
rn="\x0d\x0a"
busybox="\x0d\x0a\x0d\x0a\x0d\x0aBusyBox v1.1.2 (2007.05.09-01:19+0000) Built-in shell (ash)\x0d\x0a" \
        "Enter 'help' for a list of built-in commands.\x0d\x0a\x0d\x0a\x7e\x20\x24\x20"
ZORRO="/bin/busybox ZORRO\x0d\x0a"
wget="/bin/busybox wget\x0d\x0a"
echo_ZORRO="\x5c\x5c\x78\x35\x41\x5c\x5c\x78\x34\x46\x5c\x5c\x78\x35\x32\x5c\x5c\x78\x35\x32\x5c\x5c\x78\x34\x46\x0d\x0a"
echo_gayfgt="\x5c\x78\x36\x37\x5c\x78\x36\x31\x5c\x78\x37\x39\x5c\x78\x36\x36\x5c\x78\x36\x37\x5c\x78\x37\x34"
echo_gayfgt2="\x5c\x31\x34\x37\x5c\x31\x34\x31\x5c\x31\x37\x31\x5c\x31\x34\x36\x5c\x31\x34\x37\x5c\x31\x36\x34"
echo_welcome="\x5c\x5c\x78\x37\x37\x5c\x5c\x78\x36\x35\x5c\x5c\x78\x36\x63\x5c\x5c\x78\x36\x33\x5c\x5c\x78\x33\x30\x5c\x5c\x78\x36\x64\x5c\x5c\x78\x36\x35"
cat_mount="cat /proc/mounts"
status="""rootfs / rootfs rw 0 0
/dev/root / cramfs ro 0 0
proc /proc proc rw,nodiratime 0 0
sysfs /sys sysfs rw 0 0
devfs /dev devfs rw 0 0
devpts /dev/pts devpts rw 0 0
/dev/mtdblock/1 /mnt/custom cramfs ro 0 0
/dev/mtdblock/3 /usr cramfs ro 0 0
/dev/mtdblock/4 /mnt/web cramfs ro 0 0
/dev/mtdblock/6 /mnt/mtd jffs2 rw,noatime 0 0
/dev/ram /var/tmp ramfs rw 0 0
"""
cat_sh="/bin/busybox cat /bin/sh"

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
        self.binary = ""
        self.request.setblocking(0)
        print "%s IP %s.%s > %s.%s : connect" \
            % (self.date,self.attackerIP,self.client_address[1],self.server.server_address[0],self.targetPORT)

        odd = (self.targetPORT % 29) + 1
        cmd = "./getdata.sh %d 1" % odd
        pic = subprocess.Popen(cmd.strip().split(" "),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        option = pic.stdout.read()
        self.request.send(option)
        time.sleep(0.6)

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
                    elif self.payload.find("sh") == 0:
                        self.payload = busybox
                    elif self.payload.find(cat_mount) != -1:
                        self.payload = cat_mount+"\x0d\x0a"+status+"\x0d\x0a"+"ZORRO: applet not found\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find("echo welcome") != -1:
                         self.payload = "welcome"+"\x0d\x0a"+"\x7e\x20\x24\x20"  
                    elif self.payload.find(echo_welcome) != -1: 
                        self.payload = "welc0me"+"\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find(ZORRO) != -1:
                        self.payload = self.payload+"ZORRO: applet not found\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find(wget) != -1:
                        self.payload = wget+"sh: /bin/busybox wget: not found\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find(echo_ZORRO) != -1:
                        self.payload = self.payload+"ZORRO\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find(echo_gayfgt) != -1:
                        self.payload = self.payload+"gayfgt\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find(echo_gayfgt2) != -1:
                        self.payload = self.payload+"gayfgt\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find("var") != -1:
                        if self.payload.find("/bin/busybox rm -rf /var/tmp/") != -1:
                          pass
                        elif self.payload.find("bin.sh") != -1:
                          self.payload = self.payload+"binfagt\x0d\x0a"
                        else:
                          self.payload = self.payload+"ZORRO: applet not found\x0d\x0a"+"\x7e\x20\x24\x20"
                    elif self.payload.find("$HOME/.*history") != -1:
                        self.payload = ""
                    elif self.payload.find(cat_sh) != -1:
                        f = open("output1.txt")
                        datas = f.read()
                        f.close()
                        data = datas.split(' ')
                        for hexa in data:
                          d = int(hexa,16)
                          self.binary += struct.pack('!L',d)
                        self.payload = cat_sh+"\x0d\x0a"+self.binary

                    else:
                      self.payload = self.payload.replace(rn,"")
                      self.payload = "sh: "+ self.payload + ": command not found\x0d\x0a\x7e\x20\x24\x20"
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

