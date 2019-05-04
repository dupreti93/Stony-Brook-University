import socket
import sys
import json

class Solution():
    def __init__(self):
        self.host = sys.argv[1]
        self.filename = sys.argv[1]+".txt"
        self.port = 50005
        self.penultimate = -1
        self.d={}

    def bellmanFord(newNode, curData,updatedVal):
        newVals = {}
        for val in curData:
            if int(updatedVal[val][0]) > (int(updatedVal[newNode][0]) + int(curData[val][0])):
                newVals[val] = [int(updatedVal[newNode][0]) + int(curData[val][0]), updatedVal[val][1]]
            else:
                newVals[val] = [updatedVal[val][0], updatedVal[val][1]]
        return newVals

    def clientMethod(self):
        while True:
            file = open(self.filename, 'r')
            distVect = {}
            neighbours = []
            for line in file:
                content = line.split(',')
                if content[2][:self.penultimate] != "" and content[0] != self.host:
                    neighbours.append((content[2][:self.penultimate],content[0]))
                elif content[1] == 'NA':
                    content[1] = sys.maxsize

                distVect[content[0]] = (int(content[1]),content[2][:self.penultimate])

            for ip in neighbours:
                receivedCont = json.loads(sock.recv(4096))
                old_node = ip[1]
                old_data = {}
                currentData = distVect
                sock = socket.socket()
                sock.connect((ip[0], self.port))
                new_node = self.host
                for val in receivedCont:
                    old_data[str(val)] = receivedCont[str(val)]
                newTable = self.bellmanFord(old_node,old_data,currentData)
                updatedVals = []
                CurrVals = []
                for val in newTable:
                    updatedVals.append(newTable[val][0])
                    CurrVals.append(currentData[val][0])
                if updatedVals != CurrVals:
                    file = open(self.filename,'w')
                    for val in newTable:
                        if newTable[val][0] == sys.maxsize:
                            file.write(val+" NA "+" NA"+"\n")
                        else:
                            #Distance   Cost    Next Hop(Router name)
                            file.write(val+" "+str(newTable[val][0])+" "+self.d[newTable[val][1]]+"\n")
                file.close()
                sock.close()

S = Solution()
S.clientMethod()