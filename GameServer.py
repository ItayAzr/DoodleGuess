import socket
import threading

def handle_client(conn, address):
    print(f"New connection from {address}")


def server_program():
    host = "127.0.0.1"  # Localhost
    port = 65632

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)  # Allow up to 5 pending connections
    print(f"Server listening on {host}:{port}...")

    while True:
        conn, address = server_socket.accept() # Accept new connectio
        thread = threading.Thread(target=, args=(conn, address))
        thread.start()  # Start the thread to handle the client
        print(f"Active threads: {threading.active_count()}")

if __name__ == '__main__':
    server_program()