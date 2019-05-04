import dpkt
import sys
import time
import math
import struct
import Queue


# sudo tcpdump -i en0 -s 0 -B 544288 -w ~/PycharmProjects/StonyBrook/http_1080.pcap;

class HTTPPacket:
    def __init__(self, timestamp, packetData):
        try:
            self.flag=True
            self.timeStamp = timestamp
            self.packetSize = len(packetData)
            self.sourceIp = str(struct.unpack(self.getGetFormat("char"), packetData[26:27])[0])
            for i in range(1, 4):
                self.sourceIp += "." + str(struct.unpack(self.getGetFormat("char"), packetData[26 + i:27 + i])[0])
            self.destinationIp = str(struct.unpack(self.getGetFormat("char"), packetData[30:31])[0])
            self.sequenceNumber = str(struct.unpack(self.getGetFormat("int"), packetData[38:42])[0])
            self.acknowledgeNumber = str(struct.unpack(self.getGetFormat("int"), packetData[42:46])[0])
            for i in range(1, 4):
                self.destinationIp += "." + str(struct.unpack(self.getGetFormat("char"), packetData[30 + i:31 + i])[0])
            flagData = str(struct.unpack(self.getGetFormat("short"), packetData[46:48])[0])
            self.synFlag = "{0:16b}".format(int(flagData))[14]
            self.acknowledgementFlag = "{0:16b}".format(int(flagData))[11]
            self.request = str(struct.unpack(self.getGetFormat("character"), packetData[66:67])[0])
            for i in range(1, 3):
                self.request += str(struct.unpack(self.getGetFormat("character"), packetData[66 + i: 67 + i])[0])
            self.response = str(struct.unpack(self.getGetFormat("character"), packetData[66:67])[0])
            for i in range(1, 4):
                self.response += str(struct.unpack(self.getGetFormat("character"), packetData[66 + i:67 + i])[0])
        except:
            self.flag=False

    def getGetFormat(self, format):
        if format == "int":
            return ">I"
        elif format == "short":
            return ">H"
        elif format == "char":
            return ">B"
        elif format == "character":
            return ">c"

class Packet:
    def __init__(self, timestamp, packetData):
        try:
            self.timeStamp = timestamp
            self.packetSize = len(packetData)
            self.sourceIp = str(struct.unpack(self.getGetFormat("char"), packetData[26:27])[0])
            for i in range(1, 4):
                self.sourceIp += "." + str(struct.unpack(self.getGetFormat("char"), packetData[26 + i:27 + i])[0])
            self.destinationIp = str(struct.unpack(self.getGetFormat("char"), packetData[30:31])[0])
            self.sequenceNumber = str(struct.unpack(self.getGetFormat("int"), packetData[38:42])[0])
            self.acknowledgeNumber = str(struct.unpack(self.getGetFormat("int"), packetData[42:46])[0])
            for i in range(1, 4):
                self.destinationIp += "." + str(struct.unpack(self.getGetFormat("char"), packetData[30 + i:31 + i])[0])
            flagData = str(struct.unpack(self.getGetFormat("short"), packetData[46:48])[0])
            self.synFlag = "{0:16b}".format(int(flagData))[14]
            self.acknowledgementFlag = "{0:16b}".format(int(flagData))[11]
        except:
            print("Some exception occured")

    def getGetFormat(self, format):
        if format == "int":
            return ">I"
        elif format == "short":
            return ">H"
        elif format == "char":
            return ">B"
        elif format == "character":
            return ">c"


def main():
    # HTTP file
    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n3.A")
    file = open("http_1080.pcap")
    packet = dpkt.pcap.Reader(file)
    packets = []
    for i in packet:
        item= HTTPPacket(i[0], i[1])
        if item.flag:
            packets.append(item)
    q = Queue.Queue()
    response = {}
    for i in packets:
        if i.request == "GET":
            q.put(i)
        elif i.response == "HTTP":
            item = q.get()
            #Dequeu from queue and dequeued request belongs to response item
            response[i] = item
    counter=1
    for i in response:
        print(counter)
        counter+=1
        print("REQUEST : TCP TUPLE: <src,dest,seq,ack> :"+response[i].sourceIp+"  "+response[i].destinationIp+"  "+response[i].sequenceNumber+"  "+response[i].acknowledgeNumber)
        print("RESPNONSE: TCP TUPLE: <src,dest,seq,ack> :"+ i.sourceIp+ "  "+i.destinationIp+ "  "+i.sequenceNumber+"  "+i.acknowledgeNumber)



    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n3.B")

    # Three files to analyze
    file = open("http_1080.pcap")
    packet = dpkt.pcap.Reader(file)
    packets = []
    for i in packet:
        item= HTTPPacket(i[0], i[1])
        if item.flag:
            packets.append(item)
    totalPackets=0
    tcpConnections=0
    time=0
    size=0
    for i in packets:
        totalPackets += 1
        size += i.packetSize
        if i.synFlag == "1" and i.acknowledgementFlag == "1":
            tcpConnections += 1

    time = packets[-1].timeStamp-packets[0].timeStamp

    if tcpConnections>6:
        print("HTTP protocol: HTTP 1.0")
    elif tcpConnections<=6 and tcpConnections>2:
        print("HTTP protocol: HTTP 1.1")
    else:
        print("HTTP protocol: HTTP 2.0")

    print("Number of connections ",tcpConnections)
    print("Total number of packets sent: ",totalPackets)
    print("Total time taken:",time)
    print("Raw bytes size:",size)
    print("\n")


    file = open("tcp_1081.pcap")
    packet = dpkt.pcap.Reader(file)
    packets = []
    for i in packet:
        packets.append(Packet(i[0], i[1]))
    totalPackets = 0
    tcpConnections = 0
    size = 0
    for i in packets:
        totalPackets += 1
        size += i.packetSize
        if i.synFlag == "1" and i.acknowledgementFlag == "1":
            tcpConnections += 1
    time = packets[-1].timeStamp - packets[0].timeStamp

    if tcpConnections>6:
        print("HTTP protocol: HTTP 1.0")
    elif tcpConnections<=6 and tcpConnections>2:
        print("HTTP protocol: HTTP 1.1")
    else:
        print("HTTP protocol: HTTP 2.0")

    print("Number of connections ",tcpConnections)
    print("Total number of packets sent: ", totalPackets)
    print("Total time taken:", time)
    print("Raw bytes size:", size)
    print("\n")



    file = open("tcp_1082.pcap")
    packet = dpkt.pcap.Reader(file)
    packets = []
    for i in packet:
        packets.append(Packet(i[0], i[1]))
    totalPackets = 0
    tcpConnections = 0
    size = 0
    for i in packets:
        totalPackets += 1
        size += i.packetSize
        if i.synFlag == "1" and i.acknowledgementFlag == "1":
            tcpConnections += 1

    time = packets[-1].timeStamp - packets[0].timeStamp
    if tcpConnections>6:
        print("HTTP protocol: HTTP 1.0")
    elif tcpConnections<=6 and tcpConnections>2:
        print("HTTP protocol: HTTP 1.1")
    else:
        print("HTTP protocol: HTTP 2.0")

    print("Number of connections ",tcpConnections)
    print("Total number of packets sent: ", totalPackets)
    print("Total time taken:", time)
    print("Raw bytes size:", size)
    print("\n")

    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n3.C")

    print("HTTP 2.0 performs fastest and sends least packets as expected because it makes least number of connections")
    print("In the above results, the correct packet count and size of HTTP 1.0 is not present as some packets were invalidated because")
    print("each packet cannot be of HTTP protocol. Also, the time spent is largest in HTTP 1.0.")
    print("HTTP 1.1 comes in between HTTP 1.0 and HTTP 2.0 in performance. HTTP 2.0 is fastest and most efficient.")
    print("HTTP 1.1 comes second and least performance is of HTTP 1.0")

    print("\n\n")
    print("-----------------------------------------------------------------------------------------")

if __name__ == '__main__':
    main()



