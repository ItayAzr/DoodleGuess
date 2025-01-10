# import pygame package
import pygame
import socket
import threading
from Line import Line


def handle_client(conn, address):
    print(f"New connection from {address}")
    while True:
        try:
            data = conn.recv(1024).decode()  # Receive data
            if data == 'exit':
                print("Connection closed by client")
                break  # Connection closed by client

            data = str(data).split("/")
            if data[0] == "line":
                line_txt = data[1]
                print(line_txt)



        except:
            break



def server_program():
    host = "127.0.0.1"  # Localhost
    port = 65432        # Arbitrary non-privileged port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Allow up to 5 pending connections
    print(f"Server listening on {host}:{port}...")

    while True:
        conn, address = server_socket.accept()  # Accept new connection
        thread1 = threading.Thread(target=handle_client, args=(conn, address))
        thread1.start()  # Start the thread to handle the client
        print(f"Active threads: {threading.active_count()}")

if __name__ == "__main__":
    server_program()