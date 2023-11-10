from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCIntf
from mininet.node import Node
import argparse 

class CustomTopology(Topo):
    def build(self):
        # Adding switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

        # Adding hosts
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')

        # Creating links with default bandwidth
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch1)
        self.addLink(host4, switch2)
        self.addLink(switch1, switch2)

topo = CustomTopology()

# Specify the controller
controller = RemoteController('c0', ip='127.0.0.1', port=6634)

# Start Mininet with the base topology
net = Mininet(topo=topo, controller=controller, waitConnected=True)
net.start()

def config_b():
    # Configuration "b" - h1 as the client and h4 as the server
    # Automatically launch xterm for both h1 and h4
    for node in ['h1', 'h4']:
        host = net.getNodeByName(node)
        host.cmd('xterm &')
        
def config_c():
    # Configuration "c" - h1, h2, h3 as clients and h4 as the server
    # Automatically launch xterm for both h1 and h4
    for node in ['h1','h2', 'h3', 'h4','h4', 'h4']:
        host = net.getNodeByName(node)
        host.cmd('xterm &')
    
def config_d(link_loss_percent):
    # Set loss parameter on the s1-s2 link
    link = net['s1'].connectionsTo(net['s2'])[0]  # Get the link between s1 and s2
    intf1 = link[0]
    intf2 = link[1]

    intf1.config(loss=link_loss_percent)
    intf2.config(loss=link_loss_percent)
    
    # Automatically launch xterm for both h1 and h4
    for node in ['h1', 'h4']:
        host = net.getNodeByName(node)
        host.cmd('xterm &')
    

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--config", required=True, choices=["b", "c", "d"], help="Specify the configuration (b, c, or d)")
parser.add_argument("--loss", type=float, help="Specify the link loss percentage for configuration 'd'")
args = parser.parse_args()

# Determine the desired configuration and apply it
if args.config == "b":
    config_b()
elif args.config == "c":
    config_c()
elif args.config == "d" and args.loss is not None:
    config_d(args.loss)
elif args.config == "d" and args.loss is None:
    print("Error: You must specify the link loss percentage using the --loss argument for configuration 'd'")
    net.stop()
    exit(1)

# Run the Mininet CLI for experiments
CLI(net)

net.stop()
