
import socket
import struct
import threading
import json
import ipaddress

HOST = "0.0.0.0"
PORT = 6653
ADMIN_HOST = "127.0.0.1"
ADMIN_PORT = 6654
OF_VERSION = 4

NO_BUFFER = 0xffffffff
OFPP_FLOOD = 0xfffffffb
OFPP_CONTROLLER = 0xfffffffd
OFPP_ANY = 0xffffffff
OFPG_ANY = 0xffffffff

mac_tables = {}
switches = {}
switches_lock = threading.Lock()


def message(msg_type, xid, body=b""):
    length = 8 + len(body)
    return struct.pack("!BBHI", OF_VERSION, msg_type, length, xid) + body


def send_switch(state, msg_type, body=b"", xid=None):
    with state["send_lock"]:
        if xid is None:
            xid = state["xid"]
            state["xid"] += 1

        state["conn"].sendall(message(msg_type, xid, body))


def receive_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_table_miss(state):
    fixed = struct.pack(
        "!QQBBHHHIIIH2x",
        0, 0, 0, 0, 0, 0, 0,
        NO_BUFFER, OFPP_ANY, OFPP_ANY, 0
    )

    match = struct.pack("!HH4x", 1, 4)
    instruction = struct.pack("!HH4x", 4, 24)
    action = struct.pack("!HHIH6x", 0, 16, OFPP_CONTROLLER, 65535)

    send_switch(state, 14, fixed + match + instruction + action)


def get_packet_info(body):
    if len(body) < 20:
        return None

    buffer_id = struct.unpack("!I", body[:4])[0]
    match_length = struct.unpack("!H", body[18:20])[0]

    offset = 20
    in_port = None

    while offset + 4 <= 16 + match_length:
        oxm_class, field_mask, length = struct.unpack(
            "!HBB", body[offset:offset + 4]
        )

        value = body[offset + 4:offset + 4 + length]

        if oxm_class == 0x8000 and field_mask == 0 and length == 4:
            in_port = struct.unpack("!I", value)[0]

        offset += 4 + length

    data_offset = 16 + ((match_length + 7) // 8 * 8) + 2
    packet = body[data_offset:]

    if len(packet) < 14 or in_port is None:
        return None

    dst_mac = packet[0:6]
    src_mac = packet[6:12]

    return buffer_id, in_port, src_mac, dst_mac, packet


def send_flow_mod(state, dst_mac, out_port):
    fixed = struct.pack(
        "!QQBBHHHIIIH2x",
        0, 0, 0, 0, 60, 0, 100,
        NO_BUFFER, OFPP_ANY, OFPP_ANY, 0
    )

    match = (
        struct.pack("!HH", 1, 14)
        + struct.pack("!HBB", 0x8000, 3 << 1, 6)
        + dst_mac
        + b"\x00\x00"
    )

    instruction = struct.pack("!HH4x", 4, 24)
    action = struct.pack("!HHIH6x", 0, 16, out_port, 0)

    send_switch(state, 14, fixed + match + instruction + action)


def send_packet_out(state, packet, out_port):
    body = struct.pack("!IIH6x", NO_BUFFER, OFPP_CONTROLLER, 16)
    body += struct.pack("!HHIH6x", 0, 16, out_port, 0)
    body += packet

    send_switch(state, 13, body)


def ipv4_policy_match(student_ip):
    fields = (
        struct.pack("!HBB", 0x8000, 5 << 1, 2)
        + struct.pack("!H", 0x0800)
        + struct.pack("!HBB", 0x8000, 11 << 1, 4)
        + socket.inet_aton(student_ip)
        + struct.pack("!HBB", 0x8000, 12 << 1, 4)
        + socket.inet_aton("10.0.0.1")
    )

    match_length = 4 + len(fields)
    match = struct.pack("!HH", 1, match_length) + fields
    padding = b"\x00" * ((8 - len(match) % 8) % 8)

    return match + padding


def apply_policy(state, action, student_ip):
    command = 0 if action == "BLOCK" else 4

    fixed = struct.pack(
        "!QQBBHHHIIIH2x",
        0xD200000000000001, 0,
        0, command, 0, 0, 200,
        NO_BUFFER, OFPP_ANY, OFPG_ANY, 0
    )

    body = fixed + ipv4_policy_match(student_ip)
    send_switch(state, 14, body)


def handle_admin_client(conn, address):
    print(f"[ADMIN] Connected: {address}")

    try:
        reader = conn.makefile("r")

        for line in reader:
            try:
                request = json.loads(line)
                action = str(request.get("action", "")).upper()
                student_ip = str(request.get("ip", ""))

                if action not in ("BLOCK", "UNBLOCK"):
                    raise ValueError("Action must be BLOCK or UNBLOCK")

                parsed_ip = ipaddress.ip_address(student_ip)

                if parsed_ip.version != 4:
                    raise ValueError("Only IPv4 addresses are supported")

                if student_ip == "10.0.0.1":
                    raise ValueError("Cannot block the examination server")

                with switches_lock:
                    active_switches = list(switches.values())

                if not active_switches:
                    raise RuntimeError("No switch is connected")

                for state in active_switches:
                    apply_policy(state, action, student_ip)

                print(f"[DYNAMIC POLICY] {action} {student_ip}")

                response = {
                    "status": "success",
                    "action": action,
                    "ip": student_ip,
                    "switches_updated": len(active_switches)
                }

            except (ValueError, TypeError, json.JSONDecodeError,
                    RuntimeError, OSError) as error:
                response = {
                    "status": "error",
                    "message": str(error)
                }

            conn.sendall((json.dumps(response) + "\n").encode())

    except (ConnectionError, OSError) as error:
        print("[ADMIN ERROR]", error)

    finally:
        conn.close()


def admin_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ADMIN_HOST, ADMIN_PORT))
    server.listen(5)

    print(f"[ADMIN] Policy interface listening on port {ADMIN_PORT}")

    try:
        while True:
            conn, address = server.accept()
            threading.Thread(
                target=handle_admin_client,
                args=(conn, address),
                daemon=True
            ).start()

    finally:
        server.close()


def handle_switch(conn, address):
    print(f"[CONNECTED] Switch: {address}")

    state = {
        "conn": conn,
        "send_lock": threading.Lock(),
        "xid": 1
    }

    mac_tables[address] = {}

    with switches_lock:
        switches[address] = state

    try:
        while True:
            header = receive_exact(conn, 8)

            if not header:
                break

            version, msg_type, length, received_xid = struct.unpack(
                "!BBHI", header
            )

            if length < 8:
                break

            body = receive_exact(conn, length - 8)

            if body is None:
                break

            if version != OF_VERSION:
                print("[ERROR] Unsupported OpenFlow version")
                break

            if msg_type == 0:
                print("[HELLO] OpenFlow 1.3")
                send_switch(state, 0, xid=received_xid)
                send_switch(state, 5)
                print("[FEATURES REQUEST] Sent to switch")

            elif msg_type == 2:
                send_switch(state, 3, body, xid=received_xid)

            elif msg_type == 6:
                print("[FEATURES REPLY] Received from switch")

                send_switch(state, 9, struct.pack("!HH", 0, 65535))
                send_table_miss(state)

                print("[FEATURES] Switch connected successfully")
                print("[FLOW] Table-miss rule installed")

            elif msg_type == 10:
                info = get_packet_info(body)

                if info is None:
                    continue

                buffer_id, in_port, src_mac, dst_mac, packet = info

                table = mac_tables[address]
                table[src_mac] = in_port

                if dst_mac in table and table[dst_mac] != in_port:
                    out_port = table[dst_mac]

                    send_flow_mod(state, dst_mac, out_port)
                    send_packet_out(state, packet, out_port)

                    print(
                        f"[LEARNED FLOW] {dst_mac.hex(':')} "
                        f"-> port {out_port}"
                    )

                else:
                    send_packet_out(state, packet, OFPP_FLOOD)
                    print(f"[FLOOD] Unknown destination {dst_mac.hex(':')}")

            elif msg_type == 1:
                print("[ERROR] Switch sent an OpenFlow error:", body.hex())

    except (ConnectionError, OSError) as error:
        print("[CONNECTION ERROR]", error)

    finally:
        conn.close()
        mac_tables.pop(address, None)

        with switches_lock:
            if switches.get(address) is state:
                switches.pop(address, None)

        print("[DISCONNECTED]", address)


def main():
    threading.Thread(
        target=admin_server,
        daemon=True
    ).start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Learning SDN Controller listening on port {PORT}")

    try:
        while True:
            conn, address = server.accept()

            threading.Thread(
                target=handle_switch,
                args=(conn, address),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        print("\nController shutting down.")

    finally:
        server.close()


if __name__ == "__main__":
    main()
