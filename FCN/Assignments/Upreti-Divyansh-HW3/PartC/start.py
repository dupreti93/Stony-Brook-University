#!/usr/bin/python

"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit

# patch isShellBuiltin
import mininet.util
import mininext.util

mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import OVSController
from mininet.log import setLogLevel, info

from mininext.cli import CLI
from mininext.net import MiniNExT

from topo import QuaggaTopo

net = None

def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"

    info('** Creating Quagga network topology\n')
    topo = QuaggaTopo()

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=OVSController)
    net.start()

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)

    #Setting up our information
    net.get("R1").cmd("sysctl net.ipv4.ip_forward=1")
    net.get("R2").cmd("sysctl net.ipv4.ip_forward=1")
    net.get("R3").cmd("sysctl net.ipv4.ip_forward=1")
    net.get("R4").cmd("sysctl net.ipv4.ip_forward=1")
    net.get("H1").cmd("sysctl net.ipv4.ip_forward=1")
    net.get("H2").cmd("sysctl net.ipv4.ip_forward=1")    


    net.get("R1").cmd("ifconfig R1-eth1 192.0.1.2/24")
    net.get("R1").cmd("ifconfig R1-eth2 194.0.1.1/24")
    net.get("R2").cmd("ifconfig R2-eth1 192.0.1.1/24")
    net.get("R3").cmd("ifconfig R3-eth1 194.0.1.2/24")
    net.get("R4").cmd("ifconfig R4-eth1 195.0.1.2/24")
    net.get("R4").cmd("ifconfig R4-eth2 193.0.1.2/24")

    #net.get("H1").cmd("route add default gw 190.0.1.2")
    #net.get("H2").cmd("route add default gw 191.0.1.2")

    info('** Testing network connectivity\n')
    net.ping(net.hosts)

    info('** Dumping host processes\n')

    for host in net.hosts:
        host.cmdPrint("ps aux")

    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    "stops a network (only called on a forced cleanup)"

    if net is not None:
        info('** Tearing down Quagga network\n')
        net.stop()


if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
