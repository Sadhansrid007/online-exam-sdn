
import socket
import struct
import threading

HOST = "0.0.0.0"
PORT = 6653
OF_VERSION = 4

NO_BUFFER = 0xffffffff
OFPP_FLOOD = 0xfffffffb
OFPP_CONTROLLER = 0xfffffffd
OFPP_ANY = 0xffffffff

mac_tables = {}


def message(msg_type, xid, body=b""):
    length = 8 + len(body)
    return struct.pack("!BBHI", OF_VERSION, msg_type, length, xid) + body


def receive_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_table_miss(conn, xid):
    fixed = struct.pack(
        "!QQBBHHHIIIH2x",
        0, 0, 0, 0, 0, 0, 0,
        NO_BUFFER, OFPP_ANY, OFPP_ANY, 0
    )

    match = struct.pack("!HH4x", 1, 4)
    instruction = struct.pack("!HH4x", 4, 24)
    action = struct.pack("!HHIH6x", 0, 16, OFPP_CONTROLLER, 65535)

    conn.sendall(message(14, xid, fixed + match + instruction + action))


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


def send_flow_mod(conn, xid, dst_mac, out_port):
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

    conn.sendall(message(14, xid, fixed + match + instruction + action))


def send_packet_out(conn, xid, packet, out_port):
    body = struct.pack("!IIH6x", NO_BUFFER, OFPP_CONTROLLER, 16)
    body += struct.pack("!HHIH6x", 0, 16, out_port, 0)
    body += packet

    conn.sendall(message(13, xid, body))


def handle_switch(conn, address):
    print(f"[CONNECTED] Switch: {address}")
    xid = 1
    mac_tables[address] = {}

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
                conn.sendall(message(0, received_xid))
                conn.sendall(message(5, xid))
                xid += 1
                print("[FEATURES REQUEST] Sent to switch")

            elif msg_type == 2:
                conn.sendall(message(3, received_xid, body))

            elif msg_type == 6:
                print("[FEATURES REPLY] Received from switch")

                conn.sendall(
                    message(9, xid, struct.pack("!HH", 0, 65535))
                )
                xid += 1

                send_table_miss(conn, xid)
                xid += 1

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

                    send_flow_mod(conn, xid, dst_mac, out_port)
                    xid += 1

                    send_packet_out(conn, xid, packet, out_port)
                    xid += 1

                    print(
                        f"[LEARNED FLOW] {dst_mac.hex(':')} -> port {out_port}"
                    )

                else:
                    send_packet_out(conn, xid, packet, OFPP_FLOOD)
                    xid += 1

                    print(f"[FLOOD] Unknown destination {dst_mac.hex(':')}")

            elif msg_type == 1:
                print("[ERROR] Switch sent an OpenFlow error:", body.hex())

    except (ConnectionError, OSError) as error:
        print("[CONNECTION ERROR]", error)

    finally:
        conn.close()
        mac_tables.pop(address, None)
        print("[DISCONNECTED]", address)


def main():
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
