# Initial Test Results — D1

## 1. Test Environment

- Network emulator: Mininet 2.3.0
- Virtual switch: Open vSwitch 3.7.1
- OpenFlow version: OpenFlow 1.3
- Controller: Custom Python raw OpenFlow controller
- Server: TCP examination server on h1 (10.0.0.1:5000)
- Clients: h2, h3 and h4

## 2. Test Cases

| Test ID | Test Description | Expected Result | Observed Result | Status |
|---|---|---|---|---|
| TC01 | Start Mininet topology | Hosts and switch start successfully | Topology started successfully | PASS |
| TC02 | OpenFlow controller connection | Switch connects to controller | Controller logged connection and switch features | PASS |
| TC03 | Host connectivity using pingall | All hosts communicate | 0% packet loss (12/12) | PASS |
| TC04 | Start examination server | Server listens on TCP port 5000 | Server process running on h1 (PID 1986 at test time) | PASS |
| TC05 | Client test from h2 | Client connects and completes examination | Score: 3/3 | PASS |
| TC06 | Client test from h3 | Client connects and completes examination | Score: 3/3 | PASS |
| TC07 | Client test from h4 | Client connects and completes examination | Score: 3/3 | PASS |
| TC08 | Repeated client sessions | Server handles repeated connections | Six successful sessions observed across h2, h3 and h4; each scored 3/3 | PASS |
| TC09 | MAC learning and flow-table inspection | Controller learns host MAC addresses and installs forwarding rules | Four learned destination-MAC flows and a table-miss rule observed | PASS |

## 3. Key Observations

- All four hosts were able to communicate through the Mininet network.
- The switch successfully established an OpenFlow 1.3 connection with the custom controller.
- The controller learned host MAC addresses and installed forwarding flows.
- The TCP examination server accepted client connections.
- Clients on h2, h3 and h4 successfully received questions and submitted answers.
- Repeated client sessions completed successfully.

## 4. Limitations of Initial Testing

- The repeated-session test does not establish simultaneous client execution.
- Dynamic security policies and adaptive traffic control are planned for the later implementation phase.
- Performance comparison and challenging-scenario evaluation are not part of these initial tests.

## 5. Conclusion

The initial implementation successfully demonstrates Mininet topology creation, OpenFlow-based switching, MAC learning, TCP socket communication and interaction between the examination application and the SDN network.
