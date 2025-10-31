from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class User:
    username: str
    password: str
    balance: = 500
    money_won: = 0
    money_lost: = 0
    games_played: = 0

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive.")
        self.balance += amount

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "balance": self.balance,
            "money_won": self.money_won,
            "money_lost": self.money_lost,
            "games_played": self.games_played
        }


@classmethod
def from_dict(cls, data):
    return cls(
        username = data["username"],
        password = data["password"],
        balance = data.get("balance", 500),
        money_won = data.get("money_won", 0),
        money_lost = data.get("money_lost", 0),
        games_played = data.get("games_played", 0),
        history = data.get("history", [])
    )

def update_balance(self, games, result, amount):
    if result == "win":
        self.balance += amount
        self.money_won += amount
    else:
        self.balance -= amount
        self.money_lost += amount
    self.games_played += 1

    self.history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "game": games,
        "result": result,
        "amount": amount,
        "balance now": self.balance
    })

 def to_file(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
