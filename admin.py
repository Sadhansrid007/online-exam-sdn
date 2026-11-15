
import socket
import json
import sys

HOST = "127.0.0.1"
PORT = 6654


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 admin.py BLOCK/UNBLOCK STUDENT_IP")
        return

    action = sys.argv[1].upper()
    student_ip = sys.argv[2]

    if action not in ("BLOCK", "UNBLOCK"):
        print("Invalid action. Use BLOCK or UNBLOCK.")
        return

    request = {
        "action": action,
        "ip": student_ip
    }

    try:
        with socket.create_connection((HOST, PORT), timeout=5) as conn:
            conn.sendall((json.dumps(request) + "\n").encode())

            reader = conn.makefile("r")
            response = reader.readline()

            if not response:
                print("Controller returned no response.")
                return

            result = json.loads(response)
            print(json.dumps(result, indent=4))

    except (OSError, json.JSONDecodeError) as error:
        print("[ERROR]", error)


if __name__ == "__main__":
    main()
