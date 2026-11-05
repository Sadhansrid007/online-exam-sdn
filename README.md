# SDN-Based Online Examination Network

## 1. Project Overview

This project implements an SDN-controlled online examination network using TCP socket programming, Mininet and OpenFlow 1.3.

The system consists of a central examination server and multiple student clients connected through an Open vSwitch controlled by a custom SDN controller.

Students connect to the examination server, receive multiple-choice questions, submit their answers and receive their scores.

## 2. Objectives

- Implement reliable client-server communication using TCP sockets.
- Build and simulate a network topology using Mininet.
- Implement a custom SDN controller supporting OpenFlow 1.3.
- Demonstrate dynamic MAC address learning and flow-rule installation.
- Test communication between multiple student hosts and the examination server.

## 3. System Architecture

The network consists of:

| Component | IP Address | Role |
|---|---|---|
| h1 | 10.0.0.1 | Examination server |
| h2 | 10.0.0.2 | Student client 1 |
| h3 | 10.0.0.3 | Student client 2 |
| h4 | 10.0.0.4 | Student client 3 |
| s1 | — | OpenFlow 1.3 switch |
| c0 | 127.0.0.1:6653 | SDN controller connection |

All four hosts connect to a single Open vSwitch. The switch communicates with the custom SDN controller over OpenFlow 1.3.

## 4. Technologies Used

- Python 3
- TCP Socket Programming
- Mininet
- Open vSwitch
- OpenFlow 1.3
- Ubuntu Linux

## 5. Project Files

| File | Description |
|---|---|
| `topology.py` | Creates and starts the Mininet network topology |
| `raw_controller.py` | Implements the custom OpenFlow 1.3 SDN controller |
| `server.py` | Implements the multithreaded TCP examination server |
| `client.py` | Implements the student examination client |
| `.gitignore` | Excludes temporary files and local environment files |

## 6. Environment Setup

### System Requirements

- Ubuntu Linux or a compatible Ubuntu environment
- Python 3
- Mininet
- Open vSwitch

### Install system dependencies

```bash
sudo apt update
sudo apt install mininet openvswitch-switch python3 python3-venv
```

### Clone the repository

```bash
git clone https://github.com/Sadhansrid007/online-exam-sdn.git
cd online-exam-sdn
```

No third-party Python packages are required by the current socket application or custom controller.

## 7. Running the Project

Use two terminal windows.

### Terminal 1 — Start the SDN Controller

```bash
cd ~/online-exam-sdn
python3 raw_controller.py
The controller listens on port 6653.

### Terminal 2 — Start the Mininet Topology

```bash
cd ~/online-exam-sdn
sudo python3 topology.py
```

The topology starts and enters the Mininet CLI.

### Terminal 3 — Start the Examination Server

From the Mininet CLI in Terminal 2:

```bash
h1 python3 server.py &
```

Verify that the server is running:

```bash
h1 pgrep -af server.py
```

## 8. Running Student Clients

At the Mininet prompt, run:

```bash
h2 python3 client.py
```

```bash
h3 python3 client.py
```

```bash
h4 python3 client.py
```

Each client connects to the examination server, receives three multiple-choice questions, submits answers and displays the final score.

## 9. SDN Flow Verification

To inspect the flow table:

```bash
sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

The controller implements:

- OpenFlow 1.3 handshake.
- Table-miss rule installation.
- Packet-in processing.
- MAC address learning.
- Dynamic flow-rule installation for known destinations.
- Packet flooding for unknown destinations.

## 10. Testing and Initial Results

The following tests have been performed:

| Test | Result |
|---|---|
| Mininet topology startup | Successful |
| OpenFlow 1.3 switch-controller connection | Successful |
| Host connectivity using `pingall` | 0% packet loss |
| TCP examination server startup | Successful |
| Student client h2 | Successful — 3/3 |
| Student client h3 | Successful — 3/3 |
| Student client h4 | Successful — 3/3 |
| Repeated sessions from all three clients | Successful — 3/3 each |
| OpenFlow MAC learning and flow installation | Successful |

## 11. Future Work

The next development phase will focus on:

- Dynamic SDN security and access-control policies.
- Testing challenging network scenarios.
- Performance evaluation and comparison.
- Additional robustness testing.
- Final demonstration and evaluation.

## 12. Authors

Add the names and contributions of all project team members here.
## 13. Additional Documentation

- [Network Architecture](docs/architecture.md)
- [Initial Test Results](docs/test-results.md)
