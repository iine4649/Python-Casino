import random

class BlackjackGame:
    def __init__(self):
        self.deck = self.generate_deck()
        self.player_cards = []
        self.dealer_cards = []
        self.game_over = False
        self.player_stayed = False


    def generate_deck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def draw_card(self):
        if not self.deck:
            self.deck = self.generate_deck()
        return self.deck.pop()

    def card_value(self, card):
        rank = card[0]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11  # will adjust later if bust
        else:
            return int(rank)

    def calculate_total(self, cards):
        total = sum(self.card_value(card) for card in cards)
        # Adjust Aces from 11 to 1 if total is over 21
        aces = sum(1 for card in cards if card[0] == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def deal_initial_cards(self):
        self.player_cards = [self.draw_card(), self.draw_card()]
        self.dealer_cards = [self.draw_card(), self.draw_card()]
        return self.player_cards, self.dealer_cards


    def hit_player(self):
        if not self.game_over:
            self.player_cards.append(self.draw_card())
            if self.calculate_total(self.player_cards) > 21:
                self.game_over = True
            return self.player_cards
        return None


    def player_stay(self):
        self.player_stayed = True
        self.play_dealer()
        self.game_over = True
        return self.dealer_cards

    def play_dealer(self):
        while self.calculate_total(self.dealer_cards) < 17:
            self.dealer_cards.append(self.draw_card())
        return self.dealer_cards

    def get_player_total(self):
        return self.calculate_total(self.player_cards)

    def get_dealer_total(self):
        return self.calculate_total(self.dealer_cards)

    def get_game_result(self):
        if not self.game_over:
            return None
        player_total = self.get_player_total()
        dealer_total = self.get_dealer_total()

        if player_total > 21:
            return "lose"
        elif dealer_total > 21:
            return "player_wins"
        elif player_total > dealer_total:
            return "player_wins"
        elif player_total < dealer_total:
            return "dealer_wins"
        else:
            return "tie"

    def card_to_string(self, card):
        rank, suit = card
        suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠',
        }
        symbol = suit_symbols.get(suit, suit)
        return f"{rank}{symbol}"



