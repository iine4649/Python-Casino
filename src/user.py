from dataclasses import dataclass

@dataclass
class User:
    username: str
    password: str
    balance: int = 500
    money_won: int = 0
    money_lost: int = 0
    games_played: int = 0

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

    @staticmethod
    def from_dict(d):
        return User(
            username=d["username"],
            password=d["password"],
            balance=d.get("balance", 500),
            money_won=d.get("money_won", 0),
            money_lost=d.get("money_lost", 0),
            games_played=d.get("games_played", 0)
        )
