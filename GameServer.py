import socket
import threading


class GameServer:
    def __init__(self, hostname, max_players, time_limit):
        self.host = hostname
        self.max = max_players
        self.time_limit = time_limit
        self.running = True
        self.status = 'waiting for players'
        self.playerList = [hostname]
        self.scores = {
            self.host: 0
        }
        self.full = False

    def check_user(self, username):
        for player in self.playerList:
            if player == username:
                return player, self.scores[player]
            return False

    def add_player(self,username):
        if not self.full:
            if not self.check_user(username):
                self.playerList.append(username)
                self.scores[username] = 0
                if len(self.playerList) >= self.max:
                    self.full = True
        else:
            return 'lobby is full'

    def handle_client(self, conn, address):
        print(f"New connection from {address}")


