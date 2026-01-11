import socket
import threading
import sys

# Server Configuration
HOST = '127.0.0.1'
PORT = 5555

def receive_messages(sock):
    """Listens for incoming messages from the server."""
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                break
            # Print message and reprint the prompt
            print(f"\n{msg}\nYour message: ", end='')
        except:
            print("\n[Disconnected from server]")
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print("Could not connect to server. Is it running?")
        return

    # Start a thread to listen for messages
    thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    thread.start()

    # Main loop for sending messages
    while True:
        try:
            msg = input("Your message: ")
            client.send(msg.encode('utf-8'))
        except KeyboardInterrupt:
            break
            
    client.close()

if __name__ == "__main__":
    start_client()