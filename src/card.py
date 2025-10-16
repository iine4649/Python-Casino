import copy
import random
import game

cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
         "Jack", "Queen ", "King", "Ace"]
card_color = ["Red", "Black"]
card_suits = ["Club", "Diamond", "Heart", "Spades"]
suit_colors = {
    "Hearts": "Red",
    "Diamonds": "Red",
    "Clubs": "Black",
    "Spades": "Black"
}


class Card:
    def __init__(self, cards, card_types, card_color):
        self.cards = cards
        self.card_types = card_type
        self.card_color = card_color
    def get_value(self):
        if self.cards = ["King", "Queen", "Jack"]:
            return 10
        elif self.cards == "Ace"
            return.random(1, 11)
        else:
            return int(self.card_rank)
    def __str__(self):
        return f"{self.cards} or {self.type}"





