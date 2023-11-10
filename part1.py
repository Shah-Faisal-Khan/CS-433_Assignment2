#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class CustomTopology(Topo):

    def build(self, **_opts):

        ra = self.addNode('ra', cls=LinuxRouter, ip='192.168.1.1/24')
        rb = self.addNode('rb', cls=LinuxRouter, ip='192.168.2.1/24')
        rc = self.addNode('rc', cls=LinuxRouter, ip='192.168.3.1/24')

        s1, s2, s3, s4, s5, s6 = [self.addSwitch(s) for s in ('s1', 's2', 's3', 's4', 's5', 's6')]

        # Existing links
        self.addLink(s1, ra, intfName2='ra-eth1', params2={'ip': '192.168.1.1/24'})
        self.addLink(s2, rb, intfName2='rb-eth2', params2={'ip': '192.168.2.1/24'})
        self.addLink(s3, rc, intfName2='rc-eth3', params2={'ip': '192.168.3.1/24'})

        # Links for s1
        self.addLink(self.addHost('h1', ip='192.168.1.2/24', defaultRoute='via 192.168.1.1'), s1)
        self.addLink(self.addHost('h2', ip='192.168.1.3/24', defaultRoute='via 192.168.1.1'), s1)

        # Links for s2
        self.addLink(self.addHost('h3', ip='192.168.2.2/24', defaultRoute='via 192.168.2.1'), s2)
        self.addLink(self.addHost('h4', ip='192.168.2.3/24', defaultRoute='via 192.168.2.1'), s2)

        # Links for s3
        self.addLink(self.addHost('h5', ip='192.168.3.2/24', defaultRoute='via 192.168.3.1'), s3)
        self.addLink(self.addHost('h6', ip='192.168.3.3/24', defaultRoute='via 192.168.3.1'), s3)

        # Links between routers
        self.addLink(s4, ra, intfName2='ra-eth4', params2={'ip': '192.168.4.1/24'})
        self.addLink(s4, rb, intfName2='rb-eth4', params2={'ip': '192.168.4.2/24'})
        self.addLink(s5, rb, intfName2='rb-eth5', params2={'ip': '192.168.5.1/24'})
        self.addLink(s5, rc, intfName2='rc-eth5', params2={'ip': '192.168.5.2/24'})
        self.addLink(s6, ra, intfName2='ra-eth6', params2={'ip': '192.168.6.1/24'})
        self.addLink(s6, rc, intfName2='rc-eth6', params2={'ip': '192.168.6.2/24'})


def run():
    "Test custom topology"
    topo = CustomTopology()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    
    # Adding routes for inter-subnet communication
    net['ra'].cmd('ip route add 192.168.2.0/24 via 192.168.4.2')
    net['ra'].cmd('ip route add 192.168.3.0/24 via 192.168.6.2')

    net['rb'].cmd('ip route add 192.168.1.0/24 via 192.168.4.1')
    net['rb'].cmd('ip route add 192.168.3.0/24 via 192.168.5.2')

    net['rc'].cmd('ip route add 192.168.1.0/24 via 192.168.6.1')
    net['rc'].cmd('ip route add 192.168.2.0/24 via 192.168.5.1')

    info('*** Routing Table on Routers:\n')
    info(net['ra'].cmd('route'))
    info(net['rb'].cmd('route'))
    info(net['rc'].cmd('route'))
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
