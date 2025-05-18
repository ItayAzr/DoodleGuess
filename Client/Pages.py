import tkinter as tk


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
                request = {
                    'request': 'login',
                    'data': {
                        'username': username,
                        'password': hashlib.sha256(password.encode()).hexdigest(),
                    }
                }
                hash = hashlib.sha256(json.dumps(request).encode()).hexdigest()
                request['Checksum'] = hash
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
            self.error_label = tk.Label(self.frame, bg='lightblue', text=msg, fg='red')
            self.error_label.grid(row=5, column=0, sticky='s')

        self.login_button = tk.Button(self.frame, text='login', pady=5, command=login)
        self.login_button.grid(row=6, column=0, sticky='n')

        self.frame.grid(row=2, column=0, sticky='n')
        self.signup = tk.Button(self, text='sign up', command=lambda: self.controller.show_frame(SignupPage))
        self.signup.grid(row=3, column=0)


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

        # Configure navbar
        self.controller.buttons.grid(sticky='ew')
        if self.controller.User == 'Guest':
            self.controller.login.grid(row=0, column=1)
            self.controller.signup.grid(row=0, column=2)
        else:
            self.controller.logout.grid(row=0, column=1)

        self.label = tk.Label(self, text=f"welcome to DoodleGuess, {self.controller.User}", height=4,
                              background='lightblue', font=('TkDefaultFont', 16))

        self.join_button = tk.Button(self, text="Play", width=2*size1[0], height=2*size1[1],
                                     command=self.join)

        self.label.grid(row=1, column=0, sticky='n')
        self.join_button.grid(row=2, column=0, sticky='n')

    def join(self):
        if self.controller.User == 'Guest':
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

        create_button = tk.Button(self,text='Create Lobby', width=2 * size1[0], height=2 * size1[1],
                                  command=lambda: self.controller.show_frame(LobbyCreate))
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=3)

        self.Title = tk.Label(self, text='Choose lobby Settings', font=('TkDefaultFont', 16))
        self.Title.grid()
        self.mFrame = tk.Frame(self)

        self.label1 = tk.Label(self.mFrame, text='Players:')
        self.label1.grid(row=0, column=0)

        self.select_player = ttk.Combobox(self.mFrame, values=['2', '3', '4', '5', '6', '7', '8', '9', '10'])
        self.select_player.grid(row=0, column=1)

        self.label2 = tk.Label(self.mFrame, text="Time Limit (30 - 90 sec):")
        self.label2.grid(row=1, column=0)

        self.time_entry = tk.Entry(self.mFrame)
        self.time_entry.grid(row=1, column=1)

        self.mFrame.grid(row=1, column=0)

        self.create_lobby_button = tk.Button(self, text='create lobby', width=2 * size1[0], height=2 * size1[1],
                                             command=self.create_lobby)
        self.create_lobby_button.grid(row=2, column=0, sticky='n')

    def create_lobby(self):
        host = self.controller.User
        max_players = self.select_player.get()
        time_limit = self.time_entry.get()

        if not self.select_player.get():
            return False

        if not time_limit:
            return False
        try:
            time_limit = int(time_limit)
            if time_limit < 30 or time_limit > 90:
                return False
        except Exception as e:
            print(e)
            return False

        request = {
            'request': 'create_lobby',
            'data': {
                'host': host,
                'max_players': max_players,
                'time_limit': time_limit
            }
        }
        checksum = hashlib.sha256(json.dumps(request).encode()).hexdigest()
        request['checksum'] = checksum
        result = send_data(client_socket, json.dumps(request).encode())


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
