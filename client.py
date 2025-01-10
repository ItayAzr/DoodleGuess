import game_board
import socket
from tkinter import *



def join_game():
    host = "127.0.0.1"  # Server IP address
    port = 65432        # Server port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))  # Connect to server
    print(f"Connected to server at {host}:{port}")
    request = "reqeust/turn"
    client_socket.send(request.encode())  # Send message
    turn = client_socket.recv(1024).decode()  # Receive response


    client_socket.close()  # Close connection
    if turn == "draw":
        game_board.start_drawing("127.0.0.1", 65432)
    elif turn == "guess":
        pass
    else:
        print("instructions unclear: accidentally blew up a hospital")



if __name__ == "__main__":

    root = Tk()
    w = Label(root, text='hello')
    w.pack()
    root.mainloop()