import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 5555

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        try:
            text = input('')
            if text:
                message = f'{nickname}: {text}'
                client.send(message.encode('utf-8'))
        except:
            break

if __name__ == "__main__":
    nickname = input("Choose a nickname: ")
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print("Could not connect to server.")
        sys.exit()

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()