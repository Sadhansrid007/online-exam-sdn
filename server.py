import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

QUESTIONS = [
    {"q": "Which protocol provides reliable, ordered delivery?",
     "options": ["UDP", "TCP", "IP", "ARP"], "answer": 2},
    {"q": "Which device forwards packets using IP addresses?",
     "options": ["Hub", "Switch", "Router", "Repeater"], "answer": 3},
    {"q": "What does DNS translate?",
     "options": ["Names to IP addresses", "MAC to ports",
                 "Files to packets", "TCP to UDP"], "answer": 1}
]

def send_message(conn, data):
    conn.sendall((json.dumps(data) + "\n").encode())

def handle_client(conn, address):
    print(f"[CONNECTED] {address}")
    score = 0

    try:
        reader = conn.makefile("r")
        send_message(conn, {
            "type": "welcome",
            "message": "Welcome to the Online Examination Network!",
            "total": len(QUESTIONS)
        })

        for number, question in enumerate(QUESTIONS, start=1):
            send_message(conn, {
                "type": "question",
                "number": number,
                "total": len(QUESTIONS),
                "question": question["q"],
                "options": question["options"]
            })

            line = reader.readline()
            if not line:
                break

            try:
                response = json.loads(line)
                choice = int(response.get("answer", 0))
            except (ValueError, json.JSONDecodeError, AttributeError):
                choice = 0

            if choice == question["answer"]:
                score += 1

            send_message(conn, {"type": "answer_received"})

        send_message(conn, {
            "type": "result",
            "score": score,
            "total": len(QUESTIONS)
        })

    except (ConnectionError, OSError) as error:
        print(f"[ERROR] {address}: {error}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {address} | Score: {score}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, address = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
