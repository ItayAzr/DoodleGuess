import threading

import requests
from Server import User
import random
import tkinter as tk


class Lobby:
    def __init__(self, lobby_id: int, host: User, max_players: int, time_limit: int, rounds: int, difficulty: str):
        self.id = lobby_id
        self.host = host
        self.max = max_players
        self.time_limit = time_limit
        self.difficulty = difficulty
        self.rounds = rounds
        self.waiting = True
        self.GIM = False # GIM -> Game In Process
        self.status = 'waiting for players'
        self.playerList = [host]
        self.scores = {
            self.host.data['username']: 0
        }
        self.full = False
        self.player_frame = tk.Frame()  # for the client

    def game_loop(self):
        for round in range(self.rounds):
            for player in self.playerList:
                word = self.get_draw_word()

    def update_player_frame(self):
        for frame in self.player_frame.winfo_children():
            frame.destroy()

        for player in self.playerList:
            frame = tk.Frame(self.player_frame, bg='white')
            if player == self.host:
                frame.config(bg='yellow')
            name = player.data['username']
            player_label = tk.Label(frame, text=f'{name}, score: {self.scores[player]}')
            player_label.grid()
            frame.pack()

    def remove_player(self, player: User):
        if player in self.playerList:
            self.playerList.pop()
        if player.data['username'] in self.scores.keys():
            self.scores.pop(player.data['username'])
        self.update_player_frame()

    def check_user(self, user):
        for player in self.playerList:
            if player == user:
                return player, self.scores[player.data['username']]
        return False

    def add_player(self, player: User) -> bool:
        if not self.full:
            if not self.check_user(player):
                self.playerList.append(player)
                self.scores[player.data['username']] = 0
                if len(self.playerList) >= self.max:
                    self.full = True
                self.update_player_frame()
                return True
        else:
            return False

    def get_draw_word(self):
        # Topics and filters by difficulty level
        difficulty_settings = {
                "easy": {
                    "topics": [
                        "food", "animal", "fruit", "body",
                        "tool", "clothing", "toy", "weather"
                    ],
                    "max_length": 6,
                    "min_freq": 0.7
                },
                "medium": {
                    "topics": [
                        "furniture", "vehicle", "instrument", "sports", "household",
                        "nature", "school", "job", "building", "drink"
                    ],
                    "max_length": 9,
                    "min_freq": 0.4
                },
                "hard": {
                    "topics": [
                        "technology", "machine", "invention", "mythology", "science",
                        "space", "medical", "architecture", "military", "geography"
                    ],
                    "max_length": 100,
                    "min_freq": 0.1
                }
        }

        settings = difficulty_settings.get(self.difficulty, difficulty_settings["easy"])
        topic = random.choice(settings["topics"])

        url = f"https://api.datamuse.com/words?topics={topic}&md=pf&max=1000"  # 'md=pf' gives part of speech and frequency
        try:
            response = requests.get(url)
            if response.status_code == 200:
                words = response.json()

                # gets the frequency of the word
                def get_frequency(tags):
                    for tag in tags:
                        if tag.startswith("f:"):
                            return float(tag.split(":")[1])
                    return 0.0  # Default if no frequency tag

                filtered_words = []
                # Filter to include only nouns and within length and frequency range
                for word in words:
                    if ("tags" in word and "n" in word["tags"] and len(word["word"]) <= settings["max_length"]
                            and get_frequency(word["tags"]) >= settings["min_freq"]):
                        filtered_words.append(word["word"])

                if filtered_words:
                    return random.choice(filtered_words).lower()
                else:
                    return "no_word_found"
            else:
                return "api_error"

        except Exception as e:
            print("Error:", e)
            return "house"



