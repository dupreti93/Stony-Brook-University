import dpkt
import sys
import time
import collections
import math
import struct


class Packet:
    def __init__(self, timestamp, packetData):
        try:
            self.timeStamp = timestamp
            self.packetSize = len(packetData)
            self.sourceIp = str(struct.unpack(self.getGetFormat("char"), packetData[26:27])[0])
            for i in range(1, 4):
                self.sourceIp += "." + str(struct.unpack(self.getGetFormat("char"), packetData[26 + i:27 + i])[0])
            self.destinationIp = str(struct.unpack(self.getGetFormat("char"), packetData[30:31])[0])
            for i in range(1, 4):
                self.destinationIp += "." + str(struct.unpack(self.getGetFormat("char"), packetData[30 + i:31 + i])[0])
            self.sourcePort = str(struct.unpack(self.getGetFormat("short"), packetData[34:36])[0])
            self.destinationPort = str(struct.unpack(self.getGetFormat("short"), packetData[36:38])[0])
            flagData = str(struct.unpack(self.getGetFormat("short"), packetData[46:48])[0])
            self.synFlag = "{0:16b}".format(int(flagData))[14]
            self.acknowledgementFlag = "{0:16b}".format(int(flagData))[11]
            self.sequenceNumber = str(struct.unpack(self.getGetFormat("int"), packetData[38:42])[0])
            self.acknowledgeNumber = str(struct.unpack(self.getGetFormat("int"), packetData[42:46])[0])
            self.windowSize = str(struct.unpack(self.getGetFormat("short"), packetData[48:50])[0])
            self.maximumSegmentLength = str(struct.unpack(self.getGetFormat("short"), packetData[56:58])[0])
        except:
            print("Some exception occured in reading a packet")

    def getGetFormat(self, format):
        if format == "int":
            return ">I"
        elif format == "short":
            return ">H"
        elif format == "char":
            return ">B"


def main():
    senderIp = "130.245.145.12"
    receiverIp = "128.208.2.198"
    file = open('assignment2.pcap')
    packet = dpkt.pcap.Reader(file)
    packets = []
    count = 0
    mss=0
    flows = []
    for i in packet:
        packets.append(Packet(i[0], i[1]))

    transactions = []

    # Find no of flows
    for i in packets:
        if i.synFlag == "1" and i.acknowledgementFlag == "1":
            flows.append(i)
            transactions.append([])
            mss= int(i.maximumSegmentLength)

    # Store all transactions for these flows
    for i in packets:
        for j in flows:
            if (i.destinationPort == j.destinationPort and i.sourcePort == j.sourcePort):
                transactions[flows.index(j)].append(i)
            elif (i.destinationPort == j.sourcePort and i.sourcePort == j.destinationPort):
                transactions[flows.index(j)].append(i)

    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n2.A")
    # Congestion Window
    for i in transactions:
        print("\nCongestion window size (First 30 transactions) for flow "+str(transactions.index(i)+1)+" (Source port "+str(i[0].sourcePort)+", Destination port "+str(i[0].destinationPort)+"):")
        '''
            Initially the window size is 1 MSS.
        '''
        cwnd = mss*1.0
        icwnd = mss
        '''
            Dictionary to keep track of duplicate acknowledgements
        '''
        dupAck={}
        count=0
        ssthreshold=None
        rwindSize=None
        for j in i:
            '''
                If an ack is recieved
            '''
            if j.sourceIp == receiverIp and j.destinationIp == senderIp:
                '''
                    If cwnd is greated than ssthreshold:
                        it increases slowly in congestion avoidance phase
                        else
                        it increases faster in congestion control phase
                '''
                if cwnd<ssthreshold:
                    '''
                        Slow start
                    '''
                    cwnd += mss
                else:
                    '''
                        Congestion avoidance
                    '''
                    cwnd+= 1/cwnd
                print("Conegestion window size: " + str(cwnd))
                count = count + 1
                if count == 30:
                    break
                if rwindSize is None:
                    rwindSize = int(j.windowSize)
                    ssthreshold = rwindSize/2
                '''
                    In case of triple duplicate acknowledgementL:
                        ssthreshold goes down by factor of half
                        cwnd becomse initial cwnd
                '''
                if j.acknowledgeNumber in dupAck:
                    dupAck[j.acknowledgeNumber]+=1
                    if dupAck[j.acknowledgeNumber]>2:
                        ssthreshold=ssthreshold/2
                        cwnd = icwnd
                else:
                    dupAck[j.acknowledgeNumber]=1


    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n2.B")
    # Various types of losses:
    senderToReceiver = {}
    receiverToSender = {}
    for i in transactions:
        for j in i:
            if j.sourceIp == senderIp and j.destinationIp == receiverIp:
                if j.sequenceNumber in senderToReceiver:
                    senderToReceiver[j.sequenceNumber] += 1
                else:
                    senderToReceiver[j.sequenceNumber] = 1
            elif j.sourceIp == receiverIp and j.destinationIp == senderIp:
                if j.acknowledgeNumber in receiverToSender:
                    receiverToSender[j.acknowledgeNumber] += 1
                else:
                    receiverToSender[j.acknowledgeNumber] = 1

        lostPackets = 0
        tripleAckLostPackets = 0
        for j in senderToReceiver:
            lostPackets += senderToReceiver[j] - 1
            if j in receiverToSender:
                if receiverToSender[j] > 2:  # Case of triple duplicate acknowledgement
                    tripleAckLostPackets += senderToReceiver[j]


        print("\nFor flow "+str(transactions.index(i)+1)+"(Source port "+str(i[0].sourcePort)+", Destination port "+str(i[0].destinationPort)+"):")
        print("Packets lost due to Triple acknowledgement: "+str(tripleAckLostPackets))
        print("Packets lost due to timeout: "+str(lostPackets-tripleAckLostPackets))

    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
if __name__ == '__main__':
    main()



