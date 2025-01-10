class User:

    def __init__(self, username, password):
        self.Id = -1
        self.username = username
        self.password = password
        self.wins = 0

    def update_username(self, new_name):
        self.username = new_name

    def update_password(self, new_password):
        self.password = new_password

    def add_win(self):
        self.wins += 1

    def set_id(self, id):
        self.Id = id

