import random
import time
class BlackjackGame:
    def __init__(self):
        self.user = []
        self.bot = []
        self.game_over = False
        self.player_stayed = False
        self.round = 1
        self.cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


    def card_value(self, card):
        if card.isdigit():    
            return int(card)
        elif card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 1  

    
    def draw_card(self, who):
        card = random.choice(self.cards)
        value = self.card_value(card)
        print(f"{who.capitalize()} drew a {card}! (value = {value})")

        if who == 'user':
            self.user.append(card)
        else:
            self.bot.append(card)
        return card, value
    
    def calculate_total(self, hand):
        total = sum(self.card_value(card) for card in hand)
        return total
    
    def hit_player(self):
        if not self.game_over:
            self.draw_card('user')
            if self.calculate_total(self.user) > 21:
                self.game_over = True
            return self.user
        return None
    
    def player_stay(self):
        self.player_stayed = True
        print("Dealer's turn...")
        time.sleep(1)
        while self.calculate_total(self.bot) <= 16:
            self.draw_card('bot')
            time.sleep(1)
        self.game_over = True
        return self.bot
    
    def get_game_result(self):
        if not self.game_over:
            return None
        user_total = self.calculate_total(self.user)
        bot_total = self.calculate_total(self.bot)
        
        if user_total > 21:
            return 'lose'
        elif bot_total > 21:
            return 'win'
        elif user_total > bot_total:
            return 'win'
        elif user_total < bot_total:
            return 'lose'
        else:
            return 'tie'