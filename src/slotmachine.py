import random
from typing import List


class SlotMachineGame:
    def __init__(self):
        self.symbols: List[str] = ['🍒', '🍋', '🔔', '⭐', '7️⃣', '💎']
        # simple weights: common to rare
        self.weights: List[float] = [28, 26, 20, 16, 8, 2]
        self.payout_multipliers = {
            '🍋': 4,
            '🍒': 5,
            '🔔': 10,
            '⭐': 15,
            '7️⃣': 50,
            '💎': 100,
        }

    def spin(self, bet_amount: float) -> dict:
        """Simulate a slot machine spin — returns game result dict."""
        reels: List[str] = random.choices(self.symbols, weights=self.weights, k=3)
        
        multiplier = 0
        if reels[0] == reels[1] == reels[2]:
            multiplier = self.payout_multipliers.get(reels[0], 0)

        winnings = bet_amount * multiplier
        profit = winnings - bet_amount
        
        if multiplier > 0:
            message = f"Jackpot {reels[0]} x3! You won ${int(profit)} (x{int(multiplier)})."
        else:
            message = f"You lost ${int(bet_amount)}."

        return {
            "reels": reels,
            "multiplier": multiplier,
            "winnings": winnings,
            "profit": profit,
            "message": message,
        }