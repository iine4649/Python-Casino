import copy
import random

cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
         "Jack", "Queen", "King", "Ace"]

card_suits = ["Clubs", "Diamonds", "Hearts", "Spades"]

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_value(self):
        if self.rank in ["King", "Queen", "Jack"]:
            return 10
        elif self.rank == "Ace":
            return 11  # initially; can be adjusted to 1 if needed
        else:
            return int(self.rank)

    def __str__(self):
        return f"{self.rank} of {self.suit}"

def card_deck():
    deck = []
    for suit in card_suits:
        for rank in cards:
            deck.append(Card(rank, suit))
    return deck

def shuffle_cards(deck_count=1):
    reg_deck = card_deck()
    full_deck = copy.deepcopy(reg_deck * deck_count)
    random.shuffle(full_deck)
    return full_deck





