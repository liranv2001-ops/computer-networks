import socket
import threading

# Server Configuration
HOST = '127.0.0.1'
PORT = 5555

# Dictionary to store connected clients: {name: socket}
clients = {}

def handle_client(client_socket):
    """Handles a single client connection."""
    name = None
    try:
        # 1. Ask for nickname
        client_socket.send("Welcome! Please enter your name:".encode('utf-8'))
        name = client_socket.recv(1024).decode('utf-8').strip()
        
        # 2. Save client to dictionary
        clients[name] = client_socket
        print(f"[NEW CONNECTION] {name} connected.")
        client_socket.send(f"Hello {name}! To chat, format: TARGET_NAME:MESSAGE".encode('utf-8'))

        # 3. Listen for messages
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            # Protocol: TARGET:MESSAGE
            if ':' in message:
                target_name, msg_content = message.split(':', 1)
                target_name = target_name.strip()
                
                if target_name in clients:
                    target_socket = clients[target_name]
                    full_msg = f"{name} says: {msg_content}"
                    target_socket.send(full_msg.encode('utf-8'))
                    print(f"[LOG] {name} sent message to {target_name}")
                else:
                    client_socket.send(f"[ERROR] User {target_name} not found.".encode('utf-8'))
            else:
                client_socket.send("[ERROR] Invalid format. Use: NAME:MESSAGE".encode('utf-8'))

    except Exception as e:
        print(f"[ERROR] Connection lost with {name}: {e}")
    finally:
        # Cleanup on disconnect
        if name and name in clients:
            del clients[name]
        client_socket.close()

def start_server():
    """Main server loop."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_sock, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock,))
        thread.start()

if __name__ == "__main__":
    start_server()