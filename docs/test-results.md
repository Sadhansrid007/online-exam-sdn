# Project Test Results — D1 and D2

## 1. Test Environment

- Network emulator: Mininet 2.3.0
- Virtual switch: Open vSwitch 3.7.1
- OpenFlow version: OpenFlow 1.3
- Controller: Custom Python raw OpenFlow controller
- Examination server: h1 (10.0.0.1:5000)
- Student clients: h2 (10.0.0.2), h3 (10.0.0.3), h4 (10.0.0.4)
- Link bandwidth: 10 Mbps
- Dynamic policy interface: TCP port 6654

## 2. D1 — Initial Implementation Tests

| Test ID | Test Description | Expected Result | Observed Result | Status |
|---|---|---|---|---|
| TC01 | Start Mininet topology | Hosts and switch start successfully | Topology started successfully | PASS |
| TC02 | OpenFlow controller connection | Switch connects to controller | Controller logged connection and switch features | PASS |
| TC03 | Host connectivity using pingall | All hosts communicate | 0% packet loss (12/12) | PASS |
| TC04 | Start examination server | Server listens on TCP port 5000 | Server started successfully | PASS |
| TC05 | Client test from h2 | Client connects and completes examination | Score: 3/3 | PASS |
| TC06 | Client test from h3 | Client connects and completes examination | Score: 3/3 | PASS |
| TC07 | Client test from h4 | Client connects and completes examination | Score: 3/3 | PASS |
| TC08 | Repeated client sessions | Server handles repeated connections | Six successful sessions observed; each scored 3/3 | PASS |
| TC09 | MAC learning and flow-table inspection | Controller learns MAC addresses and installs forwarding rules | Learned destination-MAC flows and table-miss rule observed | PASS |

## 3. D2 — Application Functionality and Concurrent Clients

| Test ID | Test Description | Expected Result | Observed Result | Status |
|---|---|---|---|---|
| TC10 | Launch clients from h2, h3 and h4 | All clients connect to the same server | All three hosts connected successfully | PASS |
| TC11 | Complete examinations through separate hosts | Each client receives all questions and submits answers | h2: 3/3, h3: 3/3, h4: 3/3 | PASS |
| TC12 | Multiple client sessions | Multithreaded server handles multiple connections | Three clients launched in rapid succession; all completed successfully | PASS |

## 4. D2 — Dynamic SDN Policy Tests

The controller exposes an administrator policy interface on TCP port 6654. The admin.py utility sends BLOCK and UNBLOCK commands to the controller.

| Test ID | Test Description | Expected Result | Observed Result | Status |
|---|---|---|---|---|
| TC13 | Block student h2 | Controller installs a drop rule for h2 | BLOCK command successful; one switch updated | PASS |
| TC14 | Test blocked student connectivity | h2 cannot reach examination server | 100% ICMP packet loss; TCP connection timed out | PASS |
| TC15 | Test unaffected student h3 | Other students retain connectivity | h3 successfully reached h1 | PASS |
| TC16 | Unblock student h2 | Controller removes the drop rule | UNBLOCK command successful | PASS |
| TC17 | Verify restored connectivity | h2 can reach examination server again | 3/3 ping packets received; 0% loss | PASS |

## 5. D2 — OpenFlow Rule Verification

Observed using ovs-ofctl -O OpenFlow13 dump-flows s1:

- Cookie: 0xd200000000000001
- Source IP: 10.0.0.2 (h2)
- Destination IP: 10.0.0.1 (h1)
- Priority: 200
- Action: DROP
- Packets dropped: 11
- Bytes dropped: 814

## 6. D2 — Performance Evaluation

TCP throughput was measured using iperf with a configured link bandwidth of 10 Mbps.

| Test ID | Scenario | Observed Result |
|---|---|---|
| TC18 | h2 normal TCP throughput | 9.56 Mbps |
| TC19 | h2 TCP connection after BLOCK | Connection timed out |
| TC20 | h3 TCP throughput while h2 was blocked | 9.55 Mbps |
| TC21 | h2 connectivity after UNBLOCK | 0% ping packet loss |

### Performance Observations

- Normal TCP throughput from h2 was 9.56 Mbps.
- After blocking h2, its TCP connection to h1 timed out.
- While h2 was blocked, h3 maintained 9.55 Mbps.
- Unblocking h2 restored network connectivity.

## 7. Overall Observations

- The Mininet topology and OpenFlow 1.3 controller operate successfully.
- The examination application supports multiple TCP clients through multithreading.
- Administrators can dynamically block and unblock individual student IP addresses.
- OpenFlow flow-table inspection confirms switch-level enforcement.
- Throughput measurements demonstrate preservation of connectivity for unaffected students.

## 8. Conclusion

The D1 implementation established the TCP examination application and its integration with the Mininet-based SDN network.

The D2 implementation extends this system with administrator-controlled dynamic SDN policies, selective student blocking, concurrent client testing and quantitative performance evaluation.

The tests demonstrate application functionality, dynamic flow-rule installation and removal, challenging-scenario handling, and preservation of connectivity for unaffected students.
