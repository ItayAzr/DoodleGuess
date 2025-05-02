import socket
import tkinter as tk
import hashlib
import json
import struct


size1 = [15, 3]  # width, height for login logout and exit buttons


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DoodleGuess")
        self.geometry("1920x1080")
        self.config(bg='#3f4345')
        self.User = 'Guest'
        # Container to hold all frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Make the container responsive
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=10)
        self.container.grid_columnconfigure(0, weight=10)

        self.navbar = tk.Frame(self.container, bg='#3f4345')

        self.exit_button = tk.Button(self.navbar, text='Exit', width=size1[0], height=size1[1],
                                command=self.destroy)

        self.home = tk.Button(self.navbar, text='Home', width=size1[0], height=size1[1],
                                command=lambda: self.show_frame(HomePage))

        self.logout = tk.Button(self.navbar, text='logout', width=size1[0], height=size1[1],
                                command=self.log_out)

        self.login = tk.Button(self.navbar, text='login', width=size1[0], height=size1[1],
                                command=lambda: self.show_frame(LoginPage))

        self.signup = tk.Button(self.navbar, text='signup', width=size1[0], height=size1[1],
                                command=lambda: self.show_frame(SignupPage))


        self.navbar.grid(sticky='nesw')

        self.frames = {}
        self.show_frame(HomePage)


    def log_out(self):
        self.User = 'Guest'
        self.show_frame(HomePage)

    def refresh_navbar(self):
        for button in self.navbar.winfo_children():
            button.grid_forget()
        self.exit_button.grid()

    def show_frame(self, frame_class):
        """Destroy and recreate the frame every time it's called to ensure a fresh state."""

        # Destroy the existing frame if it already exists
        if frame_class in self.frames:
            self.frames[frame_class].destroy()
            del self.frames[frame_class]

        # refresh the navbar
        self.refresh_navbar()

        # Create a new instance of the frame
        frame = frame_class(self.container, self)
        self.frames[frame_class] = frame
        frame.grid(row=1, column=0, sticky="nsew")

        # Bring the new frame to the front
        frame.tkraise()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        # Configure navbar buttons
        self.controller.home.grid(row=0, column=1)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=8)


        # Create and place the username label and entry
        frame = tk.Frame(self, background='lightblue')


        label1 = tk.Label(self, text="welcome to DoodleGuess", height=4, background='lightblue',
                          font=('TkDefaultFont', 16))
        label1.grid(row=1, column=0, sticky='n')


        username_label = tk.Label(frame, text="Username:")
        username_label.grid(row=1, column=0, padx=10, pady=5, sticky="sw")
        username_entry = tk.Entry(frame)
        username_entry.grid(row=2, column=0, padx=10, pady=5, sticky='sw')

        # Create and place the password label and entry
        password_label = tk.Label(frame, text="Password:")
        password_label.grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        password_entry = tk.Entry(frame, show="*")
        password_entry.grid(row=4, column=0, padx=10, pady=5, sticky='nw')


        def login():
            username = username_entry.get()
            password = password_entry.get()
            msg = ''
            if not username:
                msg = 'enter username'
            elif not password:
                msg = 'enter password'
            else:
                request = {
                    'request': 'login',
                    'data': {
                        'username': username,
                        'password': hashlib.sha256(password.encode()).hexdigest(),
                    }
                }
                hash = hashlib.sha256(json.dumps(request).encode()).hexdigest()
                request['verify'] = hash
                result = send_data(client_socket, json.dumps(request).encode())
                status = result['status']

                if status == 'success':
                    self.controller.User = username
                    self.controller.show_frame(HomePage)
                elif status == 'error':
                    print('fail')
                    msg = 'username or password is incorrect'
                else:
                    print('fail')
                    msg = 'something went wrong. please try again'
            error_label = tk.Label(frame, bg='lightblue', text=msg, fg='red')
            error_label.grid(row=5, column=0, sticky='s')

        login_button = tk.Button(frame, text='login', command=login)
        login_button.grid(row=6, column=0, sticky='n')
        frame.grid(row=2, column=0, sticky='n')


class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        # Configure navbar buttons
        self.controller.home.grid(row=0, column=1)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=3)


        self.label1 = tk.Label(self, text="Create a new user", height=4, background='lightblue',
                          font=('TkDefaultFont', 16))
        self.label1.grid(row=0, column=0)

        self.frame = tk.Frame(self, bg='lightblue')

        # Create and place the username label and entry
        self.username_label = tk.Label(self.frame, text="Username:",)
        self.username_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Create and place the password label and entry
        self.password_label = tk.Label(self.frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Create and place the confirm password label and entry
        self.confirm_password_label = tk.Label(self.frame, text="Confirm Password:")
        self.confirm_password_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.confirm_password_entry = tk.Entry(self.frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")


        # Create and place the signup button
        self.signup_button = tk.Button(self.frame, text="Signup", command=self.register_user)
        self.signup_button.grid(row=3, column=0, columnspan=2, pady=20)

        self.error_label = tk.Label
        self.frame.grid(row=1, column=0, stick='n')

    def register_user(self):
        msg = ''
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if not username:
            msg = 'enter username'
        elif not password:
            msg = 'enter password'
        elif not confirm_password:
            msg = 'confirm password'
        elif confirm_password != password:
            msg = 'passwords not identical'
        else:
            request = {
                'request': 'signup',
                'data': {
                    'username': username,
                    'password': hashlib.sha256(password.encode()).hexdigest(),
                }
            }
            hash = hashlib.sha256(json.dumps(request).encode()).hexdigest()
            request['verify'] = hash
            result = send_data(client_socket, json.dumps(request).encode())
            status = result['status']
            if status == 'success':
                self.controller.User = username
                self.controller.show_frame(LoginPage)
            elif status == 'failed':
                msg = 'username is taken'
            else:
                msg = 'something went wrong. please try again'
        self.error_label = tk.Label(self, bg='lightblue', text=msg, fg='red',)
        self.error_label.grid(row=2, column=0, padx=10, pady=5, sticky='n')


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=4)
        self.grid_columnconfigure(0, weight=1)

        # Configure navbar buttons
        if self.controller.Token == -1:
            self.controller.login.grid(row=0, column=1)
            self.controller.signup.grid(row=0, column=2)
        else:
            self.controller.logout.grid(row=0, column=1)

        self.label = tk.Label(self, text=f"welcome to DoodleGuess, {self.controller.User}", height=4, background='lightblue',
                          font=('TkDefaultFont', 16))


        self.join_button = tk.Button(self, text="Play", width=2*size1[0], height=2*size1[1],
                                command=self.join)


        self.label.grid(row=1, column=0, sticky='n')
        self.join_button.grid(row=2, column=0, sticky='n')

    def join(self):
        if self.controller.user == 'Guest':
            pass
        else:
            self.controller.show_frame(Temp1)

class Temp1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        join_button = tk.Button(self, text="Join Lobby", width=2 * size1[0], height=2 * size1[1])
        join_button.grid(row=0, column=0)

        create_button = tk.Button(self,text='Create Lobby', width=2 * size1[0], height=2 * size1[1])
        create_button.grid(row=0, column=1)

    def join(self):
        # clear the page
        for button in self.winfo_children():
            button.grid_forget()

        # add the join stuff
        label = tk.Label(self, text='enter lobby code')
        entry = tk.Entry(self,)

class LobbyCreate(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.Label = tk.Label(self, text='create lobby')


class LobbyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=4)
        self.grid_columnconfigure(0, weight=1)

        start_button = tk.Button(self,  width=2*size1[0], height=2*size1[1])
        start_button.grid()
        waiting = True
        f_players = tk.Frame(self, bg='grey')

class GameBoard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        canvas = tk.Canvas(self,)


# data is json
def send_data(soc, data):

    try:
        # Step 1: Send the message length first (4 bytes)
        soc.send(struct.pack("!I", len(data)))

        # Step 2: Send the actual JSON data
        soc.sendall(data)


        # Receive response length first
        response_length_data = soc.recv(4)
        response_length = struct.unpack("!I", response_length_data)[0]
        print(f"Expecting {response_length} bytes...")

        # Receive full response data
        response_data = b""
        while len(response_data) < response_length:
            chunk = soc.recv(response_length - len(response_data))
            if not chunk:
                break
            response_data += chunk

        response = json.loads(response_data.decode('utf-8'))
        print(response)
        return response
    except Exception as e:
        return {
           'status': 'communication error',
            'data': {
                'msg': 'something went wrong, try again'
            }
        }



if __name__ == '__main__':
    host = "127.0.0.1"  # Server IP address
    port = 65432  # Server port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))  # Connect to server
    print(f"Connected to server at {host}:{port}")

    app = App()
    app.mainloop()

    client_socket.close()