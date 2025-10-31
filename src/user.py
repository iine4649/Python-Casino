from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class User:
    username: str
    password: str
    nickname: str = ""
    balance: int = 500
    money_won: int = 0
    money_lost: int = 0
    games_played: int = 0
    history: list = field(default_factory=list)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive.")
        self.balance += amount

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "nickname": self.nickname,
            "balance": self.balance,
            "money_won": self.money_won,
            "money_lost": self.money_lost,
            "games_played": self.games_played,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data.get("username", ""),
            password=data.get("password") or data.get("password_hash", ""),
            nickname=data.get("nickname", data.get("username", "")),
            balance=data.get("balance", 500),
            money_won=data.get("money_won", 0),
            money_lost=data.get("money_lost", 0),
            games_played=data.get("games_played", 0),
            history=data.get("history", []),
        )

    def update_balance(self, game_name, result, amount):
        if result == "win":
            self.balance += amount
            self.money_won += amount
        else:
            self.balance -= amount
            self.money_lost += amount
        self.games_played += 1

        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": game_name,
            "result": result,
            "amount": amount,
            "balance_now": self.balance,
        })

    def to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def from_file(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
