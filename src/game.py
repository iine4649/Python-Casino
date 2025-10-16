import random


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
