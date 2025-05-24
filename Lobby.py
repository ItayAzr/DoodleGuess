import threading

import requests
import random
import tkinter as tk


class Lobby:
    def __init__(self, lobby_id: int, host: str, max_players: int, time_limit: int, rounds: int, difficulty: str):
        self.id = lobby_id
        self.host = host

        self.max = max_players
        self.time_limit = time_limit
        self.difficulty = difficulty
        self.rounds = rounds

        self.in_round = False
        self.waiting = False
        self.GIM = False  # GIM -> Game In Process

        self.playerList = [host]
        self.guessed_correct = []
        self.scores = {
            self.host: 0
        }

        self.word = ''
        self.full = False

    def update_player_frame(self) -> tk.Frame:
        player_frame = tk.Frame()
        for player in self.playerList:
            frame = tk.Frame(player_frame, bg='white')
            if player == self.host:
                frame.config(bg='yellow')
            name = player
            player_label = tk.Label(frame, text=f'{name}, score: {self.scores[player]}')
            player_label.pack()
            frame.pack()
        return player_frame

    def remove_player(self, username):
        for player in self.playerList:
            if player == username:
                self.playerList.pop()
            if player in self.scores:
                self.scores.pop(player)
            if player == self.host:
                return self.update_host()
        self.update_player_frame()
        return None

    def check_user(self, user):
        for player in self.playerList:
            if player == user:
                return player, self.scores[player]
        return False

    def add_player(self, player) -> bool:
        if not self.full:
            if not self.check_user(player):
                self.playerList.append(player)
                self.scores[player] = 0
                if len(self.playerList) >= self.max:
                    self.full = True
                self.update_player_frame()
                return True
        else:
            return False

    def update(self, data: dict):
        for key in data:
            if key == 'host':
                for player in self.playerList:
                    if player == data[key]:
                        self.host = player
            if key == 'scores':
                for score in self.scores:
                    self.scores[score] += data['scores'][score]
            if key == 'remove_player':
                self.remove_player(data[key])
            if key == 'start_game':
                self.GIM = True

    def update_host(self):
        self.playerList.remove(self.host)
        new_host = random.choice(self.playerList)
        self.host = new_host
        return new_host

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

        url = f"https://api.datamuse.com/words?topics={topic}&md=pf&max=100"  # 'md=pf' gives part of speech and frequency
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
                    self.word = random.choice(filtered_words).lower()
                else:
                    self.word = 'house'
            else:
                self.word = 'house'
        except Exception as e:
            print("Error:", e)
            self.word = 'house'


