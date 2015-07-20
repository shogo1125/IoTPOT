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


option = "\xff\xfd\x01\xff\xfd\x1f\xff\xfd\x21\xff\xfb\x01\xff\xfb\x03"
loginmes = "192.0.0.64.login:\x20"
password = "Password:\x20"
incorrect = "Login incorrect\x0d\x0a"
prompt = "\x7e\x20\x24\x20"
shell_path = "../etc/shell/sh1.txt"
busybox = "\x0d\x0a\x0d\x0a\x0d\x0aBusyBox v1.1.2 (2007.05.09-01:19+0000) Built-in shell (ash)\x0d\x0a" \
          "Enter 'help' for a list of built-in commands.\x0d\x0a\x0d\x0a"
status = """rootfs / rootfs rw 0 0
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

cmd_dict = {}
cmd_dict["./.drop > .nttp\x0d\x0a"] = ""
cmd_dict["rm -f .nttpd\x0d\x0a"] = "rm -f .nttpd\x0d\x0arm: cannot remove `.nttpd': No such file or directory"
cmd_dict["rm -f .drop\x0d\x0a"] = "rm -f .drop\x0d\x0a"
cmd_dict["sh\x0d\x0a"] = busybox
cmd_dict[r"echo -e '\x67\x61\x79\x66\x67\x74'"+"\x0d\x0a"] = r"echo -e '\x67\x61\x79\x66\x67\x74'"+"\x0d\x0agayfgt\x0d\x0a"
cmd_dict[r"/bin/busybox;echo -e '\147\141\171\146\147\164'"+"\x0d\x0a"] = r"/bin/busybox;echo -e '\147\141\171\146\147\164'"+"\x0d\x0agayfgt\x0d\x0a"
cmd_dict["echo welcome\x0d\x0a"] = "welcome\x0d\x0a"  
cmd_dict["echo $?K_O_S_T_Y_P_E\x0d\x0a"] = "0K_O_S_T_Y_P_E\x0d\x0a"
cmd_dict[r"echo -e \\x77\\x65\\x6c\\x63\\x30\\x6d\\x65"+"\x0a\x0a"] = r"echo -e \\x77\\x65\\x6c\\x63\\x30\\x6d\\x65"+"\x0a\x0awelc0me\x0d\x0a"
cmd_dict['echo -n -e "H3lL0WoRlD"'] = "H3lL0WoRlD\x0d\x0a"
cmd_dict["/bin/busybox ZORRO\x0d\x0a"] = "/bin/busybox ZORRO\x0d\x0aZORRO: applet not found\x0d\x0a"
cmd_dict["/bin/busybox wget\x0d\x0a"] = "/bin/busybox wget\x0d\x0awget: applet not found\x0d\x0a"
cmd_dict[r"/bin/busybox echo -e \\x5A\\x4F\\x52\\x52\\x4F"+"\x0d\x0a"] = "/bin/busybox echo -e \\x5A\\x4F\\x52\\x52\\x4F\x0d\x0aZORRO\x0d\x0a"
cmd_dict["cat /proc/mounts && /bin/busybox ZORRO\x0d\x0a"] = "cat /proc/mounts && /bin/busybox ZORRO\x0d\x0a"+status+"\x0d\x0aZORRO: applet not found\x0d\x0a"

path_dict = {}
path_dict["cd /tmp\x0d\x0a"] = "/tmp"
path_dict["cd /\x0d\x0a"] = "/" 
path_dict["cd /var\x0d\x0a"] = "/var"

class Handler(SocketServer.StreamRequestHandler):

    def __init__(self,request,client_address,server):
        self.attackerIP = ""
        self.targetPORT = ""
        self.payload = ""
	self.prompt = prompt
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
                    if self.payload.find("\x0d\x0a") == -1:
                        #print "%s" % binascii.hexlify(self.payload)
                        self.payload = ""
                    elif self.state == 0:
                        print "user:%s" % self.payload
                        self.state += 1
                        self.payload += password
                        time.sleep(0.3)
                    elif self.state == 1:
                        print "pass:%s" % self.payload
                        self.state += 1
                        self.payload = busybox+self.prompt
                        time.sleep(0.6)

                    elif cmd_dict.has_key(self.payload) == True:
                        self.payload = cmd_dict.get(self.payload,"NOT FOUND")+self.prompt
                    elif path_dict.has_key(self.payload) == True:
                        path = path_dict.get(self.payload,"NOT FOUND")
                        self.prompt = path+"\x20\x24\x20"
                        self.payload = self.prompt
                    elif self.payload.find("var") != -1:
                        if self.payload.find("/bin/busybox rm -rf /var/tmp/") != -1:
                          pass
                        elif self.payload.find("bin.sh") != -1:
                          self.payload = self.payload+"binfagt\x0d\x0a"+self.prompt
                        elif self.payload.find("/bin/busybox WOPBOT") != -1:
                          self.payload = self.payload+"WOPBOT: applet not found\x0d\x0a"+self.prompt
                        else:
                          self.payload = self.payload+"ZORRO: applet not found\x0d\x0a"+self.prompt
                    elif self.payload.find("$HOME/.*history") != -1:
                        self.payload = prompt 
                    elif self.payload.find("/bin/busybox cat /bin/sh") != -1:
                        f = open(shell_path)
                        datas = f.read()
                        f.close()
                        data = datas.split(' ')
                        for hexa in data:
                          d = int(hexa,16)
                          self.binary += struct.pack('!L',d)
                        self.payload = "/bin/busybox cat /bin/sh\x0d\x0a"+self.binary
                    elif self.payload.find("echo") != -1:
                        if cmd_dict.has_key(self.payload) == False and  self.payload.find("ZORRO") == -1 and self.payload.find("WOPBOT") == -1:
                            self.payload = self.payload+"\x0d\x0a"+self.prompt
                    else:
                      self.payload = self.payload.replace("\x0d\x0a","")
                      self.payload = "sh: "+ self.payload + ": command not found\x0d\x0a"+self.prompt
                    self.receiveQueue.append(self.payload)

            except socket.error:
                pass

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
    print "=== Set up low honeypot(OPTION)  ==="
    server.serve_forever()

