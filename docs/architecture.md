# Network Architecture

## SDN-Based Online Examination Network

The network consists of four Mininet hosts connected through a single OpenFlow 1.3 switch. The custom SDN controller manages the switch using the OpenFlow control channel.

```mermaid
flowchart TB
    C["Custom SDN Controller<br/>raw_controller.py<br/>127.0.0.1:6653"]
    S["Open vSwitch<br/>s1 — OpenFlow 1.3"]

    H1["h1 — Examination Server<br/>10.0.0.1<br/>TCP Port 5000"]
    H2["h2 — Student Client 1<br/>10.0.0.2"]
    H3["h3 — Student Client 2<br/>10.0.0.3"]
    H4["h4 — Student Client 3<br/>10.0.0.4"]

    C <-->|"OpenFlow 1.3 Control"| S

    S <-->|"TCP Communication"| H1
    S <-->|"TCP Communication"| H2
    S <-->|"TCP Communication"| H3
    S <-->|"TCP Communication"| H4

    T["Mininet Topology<br/>topology.py"]

    T -. "Creates and manages" .-> S
    T -. "Creates hosts" .-> H1
    T -. "Creates hosts" .-> H2
    T -. "Creates hosts" .-> H3
    T -. "Creates hosts" .-> H4
```

## Component Responsibilities

| Component | Responsibility |
|---|---|
| SDN Controller | Learns MAC addresses and installs forwarding rules |
| Open vSwitch | Forwards packets based on installed flow rules |
| Examination Server | Accepts TCP connections, sends questions and evaluates answers |
| Student Clients | Connect to the server and submit examination answers |
| Mininet | Creates the virtual network topology |

## Communication Workflow

1. The SDN controller establishes an OpenFlow 1.3 connection with the switch.
2. Student clients initiate TCP connections to the examination server at `10.0.0.1:5000`.
3. The switch forwards unknown-destination packets to the controller.
4. The controller learns source MAC addresses and installs forwarding rules for known destinations.
5. The server handles client sessions using multithreading and returns examination results.
