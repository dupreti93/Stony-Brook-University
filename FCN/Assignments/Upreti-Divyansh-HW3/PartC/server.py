#Libraries to import
import socket
import sys
import json
import os      

#Solution class
class Solution:
    def __init__(self):
        self.host = sys.argv[1]
        self.filename = sys.argv[1] + ".txt"
        self.hostname = self.host
        self.sock = socket.socket()
        self.port = 50005
        self.penultimate = -1

    def serverMethod(self):
        self.sock.bind((self.hostname, self.port))
        self.sock.listen(10)
        try:
            while True:
               file = open(self.filename, 'r')
               connection, ipAddress = self.sock.accept()
               distVector = {}
               for line in file:
                   content = line.split(' ')
                   if content[1] == 'NA':
                       content[1] = sys.maxint
                   distVector[content[0]] = (content[1],content[2][:self.penultimate])

               connection.send(json.dumps(distVector))
               connection.close()
               file.close()
        except:
            self.sock.close()
            file.close()


S=Solution()
S.serverMethod()