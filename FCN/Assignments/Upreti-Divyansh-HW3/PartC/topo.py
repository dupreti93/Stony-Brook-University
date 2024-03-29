"""
Example topology of Quagga routers
"""

import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService

from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None


class QuaggaTopo(Topo):
    "Creates a topology of Quagga routers"

    def __init__(self):
        """Initialize a Quagga topology with 5 routers, configure their IP
           addresses, loop back interfaces, and paths to their private
           configuration directories."""
        Topo.__init__(self)

        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        quaggaSvc = QuaggaService(autoStop=False)

        # Path configurations for mounts
        quaggaBaseConfigPath = selfPath + '/configs/'

        # List of Quagga host configs
        quaggaHosts = []
        hosts=[]
        quaggaHosts.append(QuaggaHost(name='H1', ip='190.0.1.1/24', loIP=None))
        quaggaHosts.append(QuaggaHost(name='H2', ip='191.0.1.1/24', loIP=None))
        quaggaHosts.append(QuaggaHost(name='R1', ip='190.0.1.2/24', loIP=None))
        quaggaHosts.append(QuaggaHost(name='R2', ip='195.0.1.1/24', loIP=None))
        quaggaHosts.append(QuaggaHost(name='R3', ip='193.0.1.1/24', loIP=None))
        quaggaHosts.append(QuaggaHost(name='R4', ip='191.0.1.2/24', loIP=None))

        # Add switch for IXP fabric
        #ixpfabric = self.addSwitch('fabric-sw1')
        # Setup each Quagga router, add a link between it and the IXP fabric
        for host in quaggaHosts:
            # Create an instance of a host, called a quaggaContainer
            quaggaContainer = self.addHost(name=host.name,
                                           ip=host.ip,
                                           hostname=host.name,
                                           privateLogDir=True,
                                           privateRunDir=True,
                                           inMountNamespace=True,
                                           inPIDNamespace=True,
                                           inUTSNamespace=True)

            # Add a loopback interface with an IP in router's announced range
            self.addNodeLoopbackIntf(node=host.name, ip=host.loIP)

            # Configure and setup the Quagga service for this node
            quaggaSvcConfig ={'quaggaConfigPath': quaggaBaseConfigPath + host.name}
            self.addNodeService(node=host.name, service=quaggaSvc,
                                nodeConfig=quaggaSvcConfig)
            hosts.append(quaggaContainer)
            # Attach the quaggaContainer to the IXP Fabric Switch
            # self.addLink(quaggaContainer,ixpfabrics

        self.addLink(hosts[0], hosts[2])
        self.addLink(hosts[5], hosts[1])
        self.addLink(hosts[3], hosts[5])
        self.addLink(hosts[4], hosts[5])
        self.addLink(hosts[2], hosts[3])
        self.addLink(hosts[2], hosts[4])




