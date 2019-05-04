import dpkt
import sys
import time
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
            self.headerSize = str(struct.unpack(self.getGetFormat("char"), packetData[46:47])[0])
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
    empirical_throughput=[]
    file = open('assignment2.pcap')
    packet = dpkt.pcap.Reader(file)
    packets=[]
    count = 0
    flows=[]
    for i in packet:
        packets.append(Packet(i[0],i[1]))

    transactions = []

    # Find no of flows
    for i in packets:
        if i.synFlag=="1" and i.acknowledgementFlag=="1":
            flows.append(i)
            transactions.append([])
            empirical_throughput.append({})
            empirical_throughput[-1]["mss"]=float(i.maximumSegmentLength)
    print("-----------------------------------------------------------------------------------------")
    print("\n\n")
    print("Number of flows:",len(flows))
    print("\n\n")


    #Store all transactions for these flows
    for i in packets:
        for j in flows:
            if (i.destinationPort == j.destinationPort and i.sourcePort==j.sourcePort):
                transactions[flows.index(j)].append(i)
            elif (i.destinationPort==j.sourcePort and i.sourcePort==j.destinationPort):
                transactions[flows.index(j)].append(i)
    print("-----------------------------------------------------------------------------------------")
    print("\n1.A")
    # Display data for two transactions
    for i in transactions:
        print("For Flow "+str(transactions.index(i)+1)+"(Source Port: "+i[0].sourcePort+", Destination Port: "+i[0].destinationPort+")")
        for j in range(0,2):
            print("\tTransaction "+str(j+1)+":")
            print("\t\tSequence Number:"+ str(i[j].sequenceNumber))
            print("\t\tAcknowledgement Number:"+ str(i[j].acknowledgeNumber))
            print("\t\tReceived Window Size:"+ str(i[j].windowSize))
            print("\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n1.B")
    #Throughput
    d={}
    for i in transactions:
        size = 0
        flag = True
        currentPacket = None
        count=0
        for j in i:
            if j.sourceIp==senderIp and j.sequenceNumber not in d: # Only for sender not counting the lost packets
                    d[j.sequenceNumber]=1
                    count+=1
                    size+=j.packetSize
                    if flag:
                        initialTimestamp = j.timeStamp
                        flag=False
                    currentPacket = j
        print("Throughput for "+ str(transactions.index(i)+1)+" TCP flow" + " (Source Port: "+i[0].sourcePort+", Destination Port: "+i[0].destinationPort+": " +str(size/(currentPacket.timeStamp-initialTimestamp))+" bytes per second")
        empirical_throughput[transactions.index(i)]["throughput"] = size/(currentPacket.timeStamp-initialTimestamp)

    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n1.C")
    #Loss
    d={}
    totalPacketsSent = 0.0
    for i in transactions:
        for j in i:
            if j.sourceIp==senderIp and j.destinationIp==receiverIp:
                totalPacketsSent +=1
                if j.sequenceNumber in d:
                    d[j.sequenceNumber]+=1
                else:
                    d[j.sequenceNumber]=1

        sumOfLostPackets = 0.0
        for j in i:
            if j.sequenceNumber in d:
                if d[j.sequenceNumber]>1:
                    sumOfLostPackets+=d[j.sequenceNumber]-1
        print("\nFlow "+str(transactions.index(i)+1)+" (Source Port: "+i[0].sourcePort+", Destination Port: "+i[0].destinationPort+"):")
        print("\tTotal packets lost = "+str(sumOfLostPackets)+" packets")
        print("\tTotal packets sent from 130.245.145.12 to 128.208.2.19 = "+str(totalPacketsSent)+" packets")
        print("\tLoss rate = "+str(float(sumOfLostPackets/totalPacketsSent)))
        empirical_throughput[transactions.index(i)]["lossrate"]=sumOfLostPackets/totalPacketsSent
    print("\n\n")
    print("-----------------------------------------------------------------------------------------")
    print("\n\n1.D")

    #RTT
    senderToReceiver={}
    receiverToSender={}
    for i in transactions:
        for j in i:
            if j.sourceIp == senderIp and j.destinationIp==receiverIp:
                if j.sequenceNumber not in senderToReceiver:
                    senderToReceiver[j.sequenceNumber]=j.timeStamp
            elif j.sourceIp==receiverIp and j.destinationIp==senderIp:
                if j.acknowledgeNumber not in receiverToSender:
                    receiverToSender[j.acknowledgeNumber] = j.timeStamp

        sum=0
        totalValidInteractions=0
        for j in senderToReceiver:
            if j in receiverToSender:
                sum += receiverToSender[j]-senderToReceiver[j]
                totalValidInteractions+=1

        print("\nAverage RTT for TCP flow "+str(transactions.index(i)+1)+" (Source Port: "+i[0].sourcePort+" ,Destination Port: "+i[0].destinationPort+") : "+str(sum/totalValidInteractions)+" seconds")
        empirical_throughput[transactions.index(i)]["rtt"]=sum/totalValidInteractions
        print("Empirical Throughput for this flow estimated in program: " + str(empirical_throughput[transactions.index(i)]["throughput"])+" bytes per second")
        print("Theoretical Throughput for this flow: "+str((pow(1.5,0.5)*empirical_throughput[transactions.index(i)]["mss"])/((pow(empirical_throughput[transactions.index(i)]["lossrate"],0.5)*empirical_throughput[transactions.index(i)]["rtt"])))+" bytes per second")

    print("\n\n-----------------------------------------------------------------------------------------")
    print("\n\n")


if __name__ == '__main__':
    main()

    

