import base64
import pickle
import threading
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import hashlib
from Client import Client



size1 = [15, 3]  # width, height for login logout and exit buttons


class App(tk.Tk):
    def __init__(self, client: Client):
        super().__init__()
        self.title("DoodleGuess")
        self.geometry("1920x1080")
        self.config(bg='#3f4345')
        self.client = client

        self.client.key_exchange()

        # Container to hold all frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Make the container responsive
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=10)
        self.container.grid_columnconfigure(0, weight=10)

        self.navbar = tk.Frame(self.container, bg='lightblue')
        self.navbar.grid_columnconfigure(0, weight=1)
        self.buttons = tk.Frame(self.navbar, bg='gray')

        self.exit_button = tk.Button(self.buttons, text='Exit', width=size1[0], height=size1[1],
                                command=self.destroy)

        self.home = tk.Button(self.buttons, text='Home', width=size1[0], height=size1[1],
                                command=lambda: self.show_frame(HomePage))

        self.logout = tk.Button(self.buttons, text='logout', width=size1[0], height=size1[1],
                                command=self.log_out)

        self.login = tk.Button(self.buttons, text='login', width=size1[0], height=size1[1],
                                command=lambda: self.show_frame(LoginPage))

        self.signup = tk.Button(self.buttons, text='signup', width=size1[0], height=size1[1],
                                command=lambda: self.show_frame(SignupPage))

        self.navbar.grid(row=0, column=0, sticky='nesw')
        self.frame = tk.Frame(self)
        self.show_frame(HomePage)

    def log_out(self):
        self.client.username = 'Guest'
        self.client.logged_in = False
        self.show_frame(HomePage)

    def refresh_navbar(self):
        for button in self.buttons.winfo_children():
            button.grid_forget()
        self.exit_button.grid()

    def show_frame(self, frame_class):
        """Destroy and recreate the frame every time it's called to ensure a fresh state."""
        # refresh the navbar
        self.refresh_navbar()
        # Create a new instance of the frame
        self.frame = frame_class(self.container, self)
        self.frame.grid(row=1, column=0, sticky="nsew")

        # Bring the new frame to the front
        self.frame.tkraise()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        # Configure navbar
        self.controller.buttons.grid(sticky='ew')
        self.controller.home.grid(row=0, column=1)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=8)

        # Create and place the username label and entry
        self.frame = tk.Frame(self, background='lightblue')

        self.label1 = tk.Label(self, text="welcome to DoodleGuess", height=4, background='lightblue',
                          font=('TkDefaultFont', 16))

        self.label1.grid(row=1, column=0, sticky='n')

        self.username_label = tk.Label(self.frame, text="Username:")
        self.username_label.grid(row=1, column=0, padx=10, pady=5, sticky="sw")
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=2, column=0, padx=10, pady=5, sticky='sw')

        # Create and place the password label and entry
        self.password_label = tk.Label(self.frame, text="Password:")
        self.password_label.grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=4, column=0, padx=10, pady=5, sticky='nw')

        def login():
            username = self.username_entry.get()
            password = self.password_entry.get()
            msg = ''
            if not username:
                msg = 'enter username'
            elif not password:
                msg = 'enter password'
            else:

                data = {
                    'username': username,
                    'password': hashlib.sha256(password.encode()).hexdigest(),
                }
                request = self.controller.client.create_request('login', data)
                result = self.controller.client.send_data(request)
                if result is not None:
                    if result['status'] == 'success':
                        self.controller.client.username = username
                        self.controller.client.logged_in = True
                        self.controller.show_frame(HomePage)
                    elif result['status'] == 'failed':
                        msg = result['data']['msg']
                else:
                    msg = 'something went wrong. please try again'
            self.error_label = tk.Label(self.frame, bg='lightblue', text=msg, fg='red')
            self.error_label.grid(row=5, column=0, sticky='s')

        self.login_button = tk.Button(self.frame, text='login', pady=5, command=login)
        self.login_button.grid(row=6, column=0, sticky='n')

        self.signup = tk.Button(self.frame, text='sign up', command=lambda: self.controller.show_frame(SignupPage))
        self.signup.grid(row=7, column=0, sticky='n')

        self.frame.grid(row=2, column=0, sticky='n')


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

        # Create and place the confirm_password label and entry
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
            msg = 'enter your password again'
        elif confirm_password != password:
            msg = 'passwords not identical'
        else:
            data = {
                'username': username,
                'password': hashlib.sha256(password.encode()).hexdigest(),
            }
            request = self.controller.client.create_request('signup', data)
            result = self.controller.client.send_data(request)
            if result is not None:
                if result['status'] == 'success':
                    self.controller.show_frame(LoginPage)
                elif result['status'] == 'failed':
                    msg = result['data']['msg']
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

        # Configure navbar
        self.controller.buttons.grid(sticky='ew')
        if self.controller.client.username == 'Guest':
            self.controller.login.grid(row=0, column=1)
            self.controller.signup.grid(row=0, column=2)
        else:
            self.controller.logout.grid(row=0, column=1)

        self.label = tk.Label(self, text=f"welcome to DoodleGuess, {self.controller.client.username}", height=4,
                              background='lightblue', font=('TkDefaultFont', 16))

        self.join_button = tk.Button(self, text="Play", width=2*size1[0], height=2*size1[1],
                                     command=self.join)

        self.label.grid(row=1, column=0, sticky='n')
        self.join_button.grid(row=2, column=0, sticky='n')

    def join(self):
        if not self.controller.client.logged_in:
            pass
        else:
            self.controller.show_frame(LobbyActions)


class LobbyActions(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.config(background='lightblue')

        join_button = tk.Button(self, text="Join Lobby", width=2 * size1[0], height=2 * size1[1],
                                command=self.join)
        join_button.grid(row=0, column=0)

        create_button = tk.Button(self, text='Create Lobby', width=2 * size1[0], height=2 * size1[1],
                                  command=lambda: self.controller.show_frame(LobbyCreate))
        create_button.grid(row=0, column=1)

        self.error_label = None

    def join(self):
        request = self.controller.client.create_request('get_lobby_list')
        result = self.controller.client.send_data(request)
        msg = ''
        if result is not None:
            if result['status'] == 'list sent':
                self.controller.show_frame(JoinLobby)
            elif result['status'] == 'error':
                msg = result['data']['msg']
        else:
            msg = 'something went wrong. please try again'
        self.error_label = tk.Label(self, bg='lightblue', text=msg, fg='red', )
        self.error_label.grid(row=3, column=0, padx=10, pady=5, sticky='n')


class JoinLobby(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.grid_rowconfigure(0, weight=4)
        self.grid_rowconfigure(1, weight=1)
        self.lobbies_frame = tk.Frame(self)
        self.refresh()
        self.lobbies_frame.grid(row=0, column=0, sticky='n')

        self.refresh_button = tk.Button(self, text='refresh', command=self.refresh)
        self.refresh_button.grid(row=1, column=0, sticky='n')

    def refresh(self):
        for frame in self.lobbies_frame.winfo_children():
            frame.destroy()

        request = self.controller.client.create_request('get_lobby_list')
        lobby_list = self.controller.client.send_data(request)['data']['lobby_list']

        row = 0
        column = 0
        for lobby in lobby_list:
            print(1)
            frame = tk.Frame(self.lobbies_frame)
            label = tk.Label(frame, text=f'{lobby[1]}\'s lobby, {lobby[2]}/{lobby[3]} players')
            label.grid()
            button = tk.Button(frame, text='join', command=lambda: self.join_lobby(lobby[0]))
            button.grid(row=1, column=0, sticky='n')
            frame.grid(row=row, column=column, sticky='nesw')
            if column < 5:
                column += 1
            elif column >= 5:
                column = 0
                row += 1
            print(2)

    def join_lobby(self, lobby_id):
        data = {
            'lobby_id': lobby_id,
            "action": "update",
            'player': self.controller.client.username
        }
        request = self.controller.client.create_request('join_lobby', data)
        response = self.controller.client.send_data(request)
        if response['status'] == 'failed':
            messagebox.showerror("Error", "couldn't join lobby")
            self.refresh()
        else:
            self.controller.client.set_lobby(base64.b64decode(response['data']['lobby'].encode()))
            self.controller.show_frame(LobbyPage)


class LobbyCreate(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=3)

        self.Title = tk.Label(self, text='Choose lobby Settings', font=('TkDefaultFont', 16))
        self.Title.grid()
        self.label = tk.Label(self, text='default lobby settings: players: 5, time limit: 60 seconds, difficulty: '
                                         'medium')
        self.label.grid(row=1)
        self.mFrame = tk.Frame(self)

        self.label1 = tk.Label(self.mFrame, text='Max Players:')
        self.label1.grid(row=0, column=0)

        self.select_player = ttk.Combobox(self.mFrame, values=['2', '3', '4', '5', '6', '7', '8', '9', '10'])
        self.select_player.grid(row=0, column=1)

        self.label2 = tk.Label(self.mFrame, text="Time Limit:")
        self.label2.grid(row=1, column=0)

        self.select_time = ttk.Combobox(self.mFrame, values=['30', '45', '60', '75', '90', '105', '120'])
        self.select_time.grid(row=1, column=1)

        self.label3 = tk.Label(self.mFrame, text="number of rounds")
        self.label3.grid(row=2, column=0)

        self.select_rounds = ttk.Combobox(self.mFrame, values=['2', '3', '4', '5'])
        self.select_rounds.grid(row=2, column=1)

        self.label4 = tk.Label(self.mFrame, text="difficulty")
        self.label4.grid(row=3, column=0,)

        self.select_difficulty = ttk.Combobox(self.mFrame, values=['easy', 'medium', 'hard'])
        self.select_difficulty.grid(row=3, column=1)

        self.mFrame.grid(row=2, column=0, sticky='n')

        self.create_lobby_button = tk.Button(self, text='create lobby', width=2 * size1[0], height=2 * size1[1],
                                             command=self.create_lobby)
        self.create_lobby_button.grid(row=3, column=0, sticky='n')
        self.error_label = None

    def create_lobby(self):
        max_players = self.select_player.get()
        time_limit = self.select_time.get()
        rounds = self.select_rounds.get()
        difficulty = self.select_difficulty.get()

        if not self.select_player.get():
            max_players = 5
        if not time_limit:
            time_limit = '60'
        if not rounds:
            rounds = '3'
        if not difficulty:
            difficulty = 'medium'

        data = {
            'max_players': max_players,
            'time_limit': time_limit,
            'rounds': rounds,
            'difficulty': difficulty
        }

        request = self.controller.client.create_request('create_lobby', data)
        result = self.controller.client.send_data(request)
        msg = ''
        if result is not None:
            if result['status'] == 'success':
                self.controller.client.set_lobby(base64.b64decode(result['data']['lobby'].encode()))
                self.controller.show_frame(LobbyPage)
            elif result['status'] == 'failed':
                msg = result['data']['msg']
        else:
            msg = 'something went wrong. please try again'
        self.error_label = tk.Label(self, bg='lightblue', text=msg, fg='red',)
        self.error_label.grid(row=3, column=0, padx=10, pady=5, sticky='n')


class LobbyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.grid_rowconfigure(0, weight=4)
        self.grid_rowconfigure(1, weight=1)

        self.start_button = tk.Button(self,  text="Start Game", width=2*size1[0], height=2*size1[1], command=self.start)

        self.f_players = tk.Frame(self)
        self.update_players_frame()
        self.f_players.grid()

        self.controller.client.Lobby.waiting = True

        if self.controller.client.Lobby.host == self.controller.client.username:
            self.start_button.grid(row=1, column=0, sticky='n')

        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print(f'running: {self.controller.client.Lobby.waiting}')

    def update_players_frame(self):
        row = 0
        column = 0
        for player in self.controller.client.Lobby.playerList:
            frame = tk.Frame(self.f_players)
            label = tk.Label(frame, text=player)

            button = tk.Button(frame, text='remove',
                               command=lambda p=player: self.controller.client.Lobby.remove_player(p))
            if self.controller.client.username == self.controller.client.Lobby.host:
                frame.config(bg='yellow')
                label.config(bg='yellow')
                button.grid(row=1, column=0, sticky='n')
            label.grid(row=0, column=0, sticky='nesw')
            frame.grid(row=row, column=column, sticky='nesw')
            if column < 5:
                column += 1
            elif column >= 5:
                column = 0
                row += 1

    def run(self):
        while self.controller.client.Lobby.waiting:
            try:
                message = self.controller.client.game_listen()
                if 'error' in message:
                    print(message['error'])
                    break
                action = message.pop('action')
                if action == 'update':
                    self.controller.client.Lobby.update(message)

                if self.controller.client.Lobby.host == self.controller.client.username:
                    self.start_button.grid(row=1, column=0, sticky='n')

                self.update_players_frame()

                if self.controller.client.Lobby.GIM:
                    self.controller.show_frame(GameBoard)
                    break
            except Exception as e:
                print(e)
        data = {
            'action': 'update',
            'start_game': 'True',
            'skip': 'True'
        }
        request = self.controller.client.create_request('start_game', data)
        print('request sent')
        response = self.controller.client.send_data(request)
        print(f'response: {response}')
        if response['status'] == 'success':
            self.controller.client.Lobby.GIM = True
            self.controller.client.in_game = True
            self.controller.show_frame(GameBoard)

    def start(self):
        self.controller.client.Lobby.waiting = False
        self.controller.client.Lobby.GIM = True
        print('starting game')


class GameBoard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='lightblue')

        self.can_draw = False
        self.word = ''
        self.word_len = 0
        self.guess = ''

        # Default pen settings
        self.pen_color = "black"
        self.pen_width = 3

        # Canvas setup
        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tool panel
        tool_frame = tk.Frame(self, padx=10, pady=10)
        tool_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Color button
        color_btn = tk.Button(tool_frame, text="Pick Color", command=self.pick_color)
        color_btn.pack(pady=5)

        # Pen size slider
        self.size_slider = tk.Scale(tool_frame, from_=1, to=6, orient=tk.HORIZONTAL, label="Pen Size")
        self.size_slider.set(self.pen_width)
        self.size_slider.pack(pady=5)

        self.label = tk.Label(self, text="enter your guess")
        self.label.pack()
        self.guess_entry = tk.Entry(tool_frame)
        self.guess_entry.pack(pady=5)

        self.guess_button = tk.Button(self, text="Submit guess", command=self.set_guess)

        # Clear button
        clear_btn = tk.Button(tool_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_btn.pack(pady=20)

        eraser_button = tk.Button(tool_frame, text="eraser", command=lambda: self.eraser)
        eraser_button.pack(pady=20)

        # Mouse event bindings
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        # Last mouse position
        self.last_x = None
        self.last_y = None

        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        print('game started')
        while True:
            if not self.can_draw:
                message = self.controller.client.game_listen()
                if 'error' in message:
                    print(message['error'])
                    break
                if message['turn'] == 'yes':
                    self.can_draw = True
                    self.word = message['word']
                else:
                    self.can_draw = False
                    self.word_len = message['word_length']

                if message['action'] == 'update':
                    self.controller.client.Lobby.update(message['data'])

                if message['action'] == 'draw':
                    self.canvas.create_line(
                        message['line_data']['x1'], message['line_data']['y1'],
                        message['line_data']['x2'], message['line_data']['y2'],
                        fill=message['line_data']['color'],
                        width=message['line_data']['width']
                    )
                elif message['action'] == 'clear':
                    self.canvas.delete("all")

    def set_guess(self):
        guess = self.guess_entry.get()
        if not guess:
            return None
        self.guess = guess

    def eraser(self):
        self.pen_color = 'white'

    def pick_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.pen_color = color

    def clear_canvas(self):
        self.canvas.delete("all")
        data = {
            "action": "clear"
        }
        request = self.controller.client.create_request('game', data)
        self.controller.client.send_data(request)

    def on_click(self, event):
        if not self.can_draw:
            return
        self.last_x, self.last_y = event.x, event.y

    def on_drag(self, event):
        if not self.can_draw:
            return
        self.pen_width = self.size_slider.get()
        self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                fill=self.pen_color, width=self.pen_width)
        self.last_x, self.last_y = event.x, event.y

        data = {
            "action": "draw",
            'line_data': {
                "x1": self.last_x,
                "y1": self.last_y,
                "x2": event.x,
                "y2": event.y,
                "color": self.pen_color,
                "width": self.pen_width
            }
        }
        request = self.controller.client.create_request('game', data)
        self.controller.client.send_data(request)



