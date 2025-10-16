# roulette.py
import random

class RouletteGame:
    def __init__(self):
        self.number = None
        self.color = None
        self.result = None

    def spin(self):
        self.number = random.randint(0, 36)
        self.color = "red" if self.number % 2 == 1 else "black" if self.number != 0 else "green"
        return self.number, self.color

    def check_result(self, bet_type):
        """bet_type: 'odd', 'even', or 'color_red', 'color_black'"""
        self.spin()

        if bet_type == "odd" and self.number % 2 == 1:
            self.result = "win"
        elif bet_type == "even" and self.number % 2 == 0 and self.number != 0:
            self.result = "win"
        elif bet_type == "color_red" and self.color == "red":
            self.result = "win"
        elif bet_type == "color_black" and self.color == "black":
            self.result = "win"
        else:
            self.result = "lose"
        
        return {
            "number": self.number,
            "color": self.color,
            "result": self.result
        }
