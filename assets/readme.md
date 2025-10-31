# Python Casino

A Flask-based multi-game casino web app for Advanced Topics in Computer Science (Midterm Project).

## Features
- User registration & login with hashed passwords.
- Automatic login function
- Persistent JSON-based data storage.
- Deposit funds system.
- Bet system 
- Playable Blackjack game vs. automated dealer.
- Playable Roulette game of combinations of 3 colors and 36 numbers 
- Playable slot machine with three rows 
- Dashboard showing balance and stats.
- Secure routes with Flask-WTF and Flask-Talisman.


## Setup
1. Clone this repo:
   ```bash
   git clone https://github.com/iine4649/Python-Casino.git
   cd Python-Casino
   ```
2. Install dependencies:
   ```bash
   pip install Flask Flask-Bcrypt Flask-WTF Flask-Talisman
   ```
3. Run the app:
   ```bash
   python main.py
   ```
4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Structure
```
Python-Casino/
├── assets/         # HTML templates & static CSS
├── data/           # JSON data (user balances, etc.)
├── src 
   ├── main.py         # Flask entry point
   ├── roulette.py     # Roulette functions 
   ├── slotmachine.py  # Slotmachine functions  
   ├── user.py         # User model
   ├── utils.py        # JSON helpers
   └── game.py         # Blackjack functions 
```

© 2025 CMP521 Python Casino Team
