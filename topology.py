#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def create_topology():
    net = Mininet(
        controller=None,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )

    info("*** Adding remote SDN controller\n")
    net.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6653
    )

    info("*** Adding examination server and student hosts\n")
    server = net.addHost("h1", ip="10.0.0.1/24")
    student1 = net.addHost("h2", ip="10.0.0.2/24")
    student2 = net.addHost("h3", ip="10.0.0.3/24")
    student3 = net.addHost("h4", ip="10.0.0.4/24")

    info("*** Adding OpenFlow switch\n")
    switch = net.addSwitch("s1", protocols="OpenFlow13")

    info("*** Connecting hosts to switch\n")
    net.addLink(server, switch, bw=10)
    net.addLink(student1, switch, bw=10)
    net.addLink(student2, switch, bw=10)
    net.addLink(student3, switch, bw=10)

    info("*** Starting network\n")
    net.start()

    info("*** Testing connectivity\n")
    net.pingAll()

    info("*** Entering Mininet CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_topology()
