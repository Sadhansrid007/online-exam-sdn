import socket
import json

import os

SERVER = os.environ.get("EXAM_SERVER", "10.0.0.1")
PORT = 5000

def receive_message(reader):
    line = reader.readline()
    if not line:
        raise ConnectionError("Server disconnected")
    return json.loads(line)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER, PORT))
        reader = client.makefile("r")
        welcome = receive_message(reader)
        print("\n" + welcome["message"])
        print("Total questions:", welcome["total"])

        while True:
            message = receive_message(reader)

            if message["type"] == "question":
                print(f"\nQuestion {message['number']}/{message['total']}")
                print(message["question"])

                for i, option in enumerate(message["options"], start=1):
                    print(f"{i}. {option}")

                while True:
                    try:
                        answer = int(input("Your answer (1-4): "))
                        if 1 <= answer <= len(message["options"]):
                            break
                        print("Choose a valid option.")
                    except ValueError:
                        print("Enter a number.")

                client.sendall(
                    (json.dumps({"answer": answer}) + "\n").encode()
                )

                receive_message(reader)  # Acknowledgement

            elif message["type"] == "result":
                print(f"\nEXAM FINISHED! Score: {message['score']}/{message['total']}")
                break

    except (ConnectionError, OSError, json.JSONDecodeError) as error:
        print("Connection error:", error)
    finally:
        client.close()

if __name__ == "__main__":
    main()
