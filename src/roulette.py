import random

class RouletteGame:
    def __init__(self):
        self.number = None
        self.color = None

    def spin(self):
        """Simulate a roulette spin — returns (number, color)."""
        self.number = random.randint(0, 36)
        if self.number == 0:
            self.color = "green"
        elif self.number % 2 == 1:
            self.color = "red"
        else:
            self.color = "black"
        return self.number, self.color
