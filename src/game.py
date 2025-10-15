import random


'''
bot=[]
win=False
dealerstays=False
print("welcome to blackjack! You start with 2 cards, try to get as close to 21 as possible without going over.")


def get_user_deck() -> []:
    user=[]
    user.append(random.randint(1,13))
    return user

def get_bot_deck() -> []:
    bot=[]
    bot.append(random.randint(1,13))
    return bot

def get_user_total() -> int:
    return sum(user)

def get_bot_total() -> int:
    return sum(bot)

    
for i in range(2):   
    user.append(random.randint(1,13))
    bot.append(random.randint(1,13))
    print("your cards:",user)
    print("dealer's cards:",bot)
if sum(user)>=21:
    print("your total is ",sum(user),"bot wins")
while sum(user)<21 and win==False:
    another_round=input("your total is "+str(sum(user))+", do you want another card? (y/n)")
    if another_round=="y":
        user.append(random.randint(1,13))
        print("your cards:",user)
    if sum(user)>21:
        print("you lose! your total is ",sum(user))
        break
    if sum(bot)<sum(user) and sum(bot)<16:
        print("waiting for dealer's turn...")
        time.sleep(2)
        print("dealer draws")
        bot.append(random.randint(1,13))
        print("dealer's cards:",bot, "with a total of",sum(bot))
    elif sum(bot)<sum(user):
        bot.append(random.randint(1,13)) 
        print("waiting for dealer's turn...")
        time.sleep(2)
        print("dealer stays")
        dealerstays=True
    if another_round=="n" and dealerstays==True:
       break
    if sum(user)>sum(bot):
            print("you win!")
            win=True
            break
    elif sum(user)<sum(bot) and sum(bot)<=21 and dealerstays==False:
            print("you lose!")
            break
    elif sum(user)==sum(bot):
            print("it's a tie! go again")
            dealerstays=False
            another_round="y"
    elif sum(bot)>21:
        print("you win!")
        win=True
        break
    elif sum(user)==21:
        print("you win!")
        win=True
        break
    elif sum(bot)==21:
        print("you lose!")
        break
'''
class BlackjackGame:
    def __init__(self):
        self.player_cards = []
        self.dealer_cards = []
        self.game_over = False
        self.player_stayed = False
        
    def deal_initial_cards(self):
    #TODO: deal 2 cards to player and dealer
        
    def draw_card(self):
    #TODO: draw a card from the deck
        
    def hit_player(self):
    #TODO: hit the player
        
    def player_stay(self):
    #TODO: player stays
            
    def play_dealer(self):
    #TODO: play the dealer
        
    def get_player_total(self):
    #TODO: get the player's total

        
    def get_dealer_total(self):
    #TODO: get the dealer's total

        
    def get_game_result(self):
    #TODO: get the game result
            
    def card_to_string(self, card):
    #TODO: convert a card to a string

