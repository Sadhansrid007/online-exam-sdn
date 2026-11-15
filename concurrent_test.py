import socket
import json
import sys

SERVER = "10.0.0.1"
PORT = 5000
ANSWERS = [2, 3, 1]

name = sys.argv[1] if len(sys.argv) > 1 else "Student"

try:
    with socket.create_connection((SERVER, PORT), timeout=10) as sock:
        reader = sock.makefile("r")
        print(f"[{name}] Connected")

        while True:
            line = reader.readline()
            if not line:
                break

            message = json.loads(line)

            if message.get("type") == "question":
                answer = ANSWERS[message["number"] - 1]
                sock.sendall(
                    (json.dumps({"answer": answer}) + "\n").encode()
                )

            elif message.get("type") == "result":
                print(f"[{name}] Score: {message['score']}/{message['total']}")
                break

except Exception as error:
    print(f"[{name}] Error: {error}")
