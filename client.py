import game_board
import socket
from tkinter import *


def close_app():
    pass


def login():
    pass


def logout():
    pass


root = Tk()


root.title('DoodleGuess')
root.config(bg='#05303d')
root.geometry("1920x1080")

exit_button = Button(root, text="exit", command=close_app)
login_button = Button(root, text="log in", command=login)
logout_button = Button(root, text='log out', command=logout)

frame = Frame(root, bg='black', bd=3,)

C = Canvas(frame, width=940, height=540, cursor='dot')
frame.pack()
C.pack()


root.mainloop()


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



