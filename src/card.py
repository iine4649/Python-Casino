import random

# standard card combinations
cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
         "Jack", "Queen", "King", "Ace"]
card_suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
suit_colors = {
    "Hearts": "Red",
    "Diamonds": "Red",
    "Clubs": "Black",
    "Spades": "Black"
}

# card dimensions
width = 300
height = 450


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.color = suit_colors[suit]

    def get_value(self):
        if self.rank in ["King", "Queen", "Jack"]:
            return 10
        elif self.rank == "Ace":
            return random.choice([1, 11])
        else:
            return int(self.rank)

    def __str__(self):
        return f"{self.rank} of {self.suit} ({self.color})"


def card_deck():
    """Generate a standard 52-card deck."""
    deck = []
    for suit in card_suits:
        for rank in cards:
            deck.append(Card(rank, suit))
    return deck


def shuffle_cards(deck_count=1):
    """Create and shuffle a deck or multiple decks."""
    deck = card_deck() * deck_count
    random.shuffle(deck)
    return deck


# Debug test
if __name__ == "__main__":
    test_deck = shuffle_cards(2)
    for card in test_deck[:10]:
        print(card)