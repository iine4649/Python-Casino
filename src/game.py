import random
<<<<<<< Updated upstream

=======
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
        elif card == 'A' and self.calculate_total(self.user)<=10:
            return 11
        elif card == 'A' and self.calculate_total(self.user)>10:
            return 1

    
    def draw_card(self, who):
        card = random.choice(self.cards)
        value = self.card_value(card)
        print(f"{who.capitalize()} drew a {card}")

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
    def get_game_result(self):
        user_total = self.calculate_total(self.user)
        bot_total = self.calculate_total(self.bot)
        
        if user_total ==21:
            return 'win'
        elif bot_total ==21:
            return 'lose'
        elif user_total > 21:
            return 'lose'
        elif bot_total > 21:
            return 'win'
        elif user_total > bot_total:
            return 'win'
        elif user_total < bot_total:
            return 'lose'
        else:
            return 'tie'
>>>>>>> Stashed changes

'''
bot=[]
win=False
dealerstays=False
Round=1
print("welcome to blackjack! You start with 2 cards, try to get as close to 21 as possible without going over.")
time.sleep(1)
print("Aces are worth 1, face cards are worth 10. Good luck!")
Bet=int(input("how much do you want to bet?"))
for i in range(2):
    user.append(random.randint(1,10))
    bot.append(random.randint(1,10))
print("your cards:",user)
print("dealer's cards is:",bot)
while sum(user)<21 and sum(bot)<21:
    choice=input("do you want to hit or stay? (h/s)")
    if choice=="h":
        user.append(random.randint(1,10))
    if sum(bot)<=16:
        time.sleep(2)
        print("dealer hits")
        bot.append(random.randint(1,10))
    elif sum(bot)>16:
        dealerstays=True
    if choice=="s" and dealerstays:
        break
    print("your cards:",user, "total:", sum(user))
    print("dealer's cards:",bot, "total:", sum(bot))
if sum(user)==21:
    win=True
elif sum(bot)==21:
    win=False
elif sum(user)>21:
    win=False
elif sum(bot)>21:
    win=True
elif sum(user)>sum(bot):
    win=True
elif sum(user)==sum(bot):
    print("it's a tie! with a total of", sum(user), "you now have",Bet,"dollars")
if win==True:
    print("you win! with a total of", sum(user), "you now have",Bet*2,"dollars")
else:
    print("you lose. with a total of", sum(user), "you now have 0 dollars")
