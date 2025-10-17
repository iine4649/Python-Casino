from card import Card
from typing import List
from game import BlackjackGame

class Dealer:
    def __init__(self):
        self.hand: List[Card] = []

    def reset_hand(self):
        self.hand = []

    def add_card(self, card: Card):
        self.hand.append(card)

    def get_total(self):
        total = sum(card.get_value() for card in self.hand)
        aces = sum(1 for card in self.hand if card.cards == "Ace")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def dealer_turn(self, deck):
        while self.get_total() < 17:
            card = deck.draw_card()
            self.add_card(card)

    def show_hand(self):
        return [str(card) for card in self.hand]
