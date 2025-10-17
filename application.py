# Elastic Beanstalk entry point - Complete Flask application
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
import json, os, random
from pathlib import Path

# Import our modules
import sys
sys.path.append('src')
from user import User
from game import BlackjackGame
from roulette import RouletteGame

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "userdata.json"
ASSETS_DIR = BASE_DIR / "assets"

app = Flask(__name__, template_folder=str(ASSETS_DIR), static_folder=str(ASSETS_DIR))

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-in-prod"),
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_ENABLED=True,
)

Talisman(app,
    force_https=False,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'style-src': ["'self'", "'unsafe-inline'"],
        'script-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "https:", "data:"]
    })

csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
active_games = {}

# ------------------------------
# User Management
# ------------------------------

def load_users():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("{}", encoding="utf-8")
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8") or "{}")
        if isinstance(data, list):
            return {}
        users = {}
        for username, user_data in data.items():
            if isinstance(user_data, dict) and 'username' in user_data:
                users[username] = User.from_dict(user_data)
            else:
                users[username] = User(
                    username=username,
                    password=user_data.get('password_hash', ''),
                    balance=user_data.get('balance', 500),
                    money_won=user_data.get('money_won', 0),
                    money_lost=user_data.get('money_lost', 0),
                    games_played=user_data.get('games_played', 0)
                )
        return users
    except json.JSONDecodeError:
        return {}

def save_users(users):
    data = {}
    for username, user in users.items():
        if isinstance(user, User):
            data[username] = user.to_dict()
        else:
            data[username] = user
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

# ------------------------------
# Routes
# ------------------------------

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login")
def login():
    return render_template("secure_login.html")

@app.route("/signup")
def signup():
    return render_template("secure_sign_up.html")

@app.route("/lobby")
def lobby():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return redirect(url_for('login'))
    
    return render_template("lobby.html", username=user.username, balance=user.balance)

@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return redirect(url_for('login'))
    
    return render_template("dashboard.html", 
                         username=user.username, 
                         balance=user.balance,
                         money_won=user.money_won,
                         money_lost=user.money_lost,
                         games_played=user.games_played)

@app.route("/deposit")
def deposit():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return redirect(url_for('login'))
    
    return render_template("deposit.html", username=user.username, balance=user.balance)

@app.route("/blackjack")
def blackjack():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return redirect(url_for('login'))
    
    return render_template("blackjack.html", username=user.username, balance=user.balance)

@app.route("/roulette")
def roulette():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return redirect(url_for('login'))
    
    return render_template("roulette.html", username=user.username, balance=user.balance)

# ------------------------------
# API Routes
# ------------------------------

@app.post("/api/sign-up")
@csrf.exempt
def api_sign_up():
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({"ok": False, "error": "Username and password are required"}), 400
    
    users = load_users()
    if username in users:
        return jsonify({"ok": False, "error": "Username already exists"}), 400
    
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        username=username,
        password=password_hash,
        balance=500.0,
        money_won=0.0,
        money_lost=0.0,
        games_played=0
    )
    
    users[username] = new_user
    save_users(users)
    
    session['user_id'] = username
    return jsonify({"ok": True, "redirect": "/lobby"})

@app.post("/api/sign-in")
@csrf.exempt
def api_sign_in():
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({"ok": False, "error": "Username and password are required"}), 400
    
    users = load_users()
    user = users.get(username)
    
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401
    
    session['user_id'] = username
    return jsonify({"ok": True, "redirect": "/lobby"})

@app.post("/api/deposit")
@csrf.exempt
def api_deposit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    amount = float(data.get("amount", 0))
    
    if amount <= 0:
        return jsonify({"ok": False, "error": "Amount must be positive"}), 400
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404
    
    user.balance += amount
    save_users(users)
    
    return jsonify({"ok": True, "new_balance": user.balance})

@app.post("/api/blackjack/deal")
@csrf.exempt
def api_blackjack_deal():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    bet_amount = float(data.get("bet_amount", 100))
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404
    
    if user.balance < bet_amount:
        return jsonify({"ok": False, "error": "Insufficient balance"}), 400
    
    game = BlackjackGame()
    game.deal_initial_cards()
    active_games[user_id] = {
        'game': game,
        'bet': bet_amount,
        'initial_balance': user.balance
    }
    
    user.balance -= bet_amount
    save_users(users)
    
    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(card) for card in game.user],
        "dealer_cards": [game.card_to_string(card) if i > 0 else "?" for i, card in enumerate(game.bot)],
        "player_total": game.get_player_total(),
        "dealer_total": "?" if len(game.bot) > 0 else 0,
        "game_over": game.game_over,
        "new_balance": user.balance
    })

@app.post("/api/blackjack/hit")
@csrf.exempt
def api_blackjack_hit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    
    if user_id not in active_games:
        return jsonify({"ok": False, "error": "No active game"}), 400
    
    game_data = active_games[user_id]
    game = game_data['game']
    
    game.hit_player()
    
    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(card) for card in game.user],
        "dealer_cards": [game.card_to_string(card) if i > 0 else "?" for i, card in enumerate(game.bot)],
        "player_total": game.get_player_total(),
        "dealer_total": "?" if len(game.bot) > 0 else 0,
        "game_over": game.game_over
    })

@app.post("/api/blackjack/stand")
@csrf.exempt
def api_blackjack_stand():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    
    if user_id not in active_games:
        return jsonify({"ok": False, "error": "No active game"}), 400
    
    game_data = active_games[user_id]
    game = game_data['game']
    bet_amount = game_data['bet']
    
    game.player_stay()
    game.play_dealer()
    
    result = game.get_game_result()
    
    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404
    
    if result == "win":
        winnings = bet_amount * 2
        user.balance += winnings
        user.money_won += bet_amount
        message = f"You won ${bet_amount}!"
    elif result == "lose":
        user.money_lost += bet_amount
        message = f"You lost ${bet_amount}."
    else:  # tie
        user.balance += bet_amount
        message = "It's a tie! Your bet is returned."
    
    user.games_played += 1
    save_users(users)
    
    # Clear the active game
    del active_games[user_id]
    
    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(card) for card in game.user],
        "dealer_cards": [game.card_to_string(card) for card in game.bot],
        "player_total": game.get_player_total(),
        "dealer_total": game.get_dealer_total(),
        "game_over": game.game_over,
        "result": result,
        "message": message,
        "new_balance": user.balance
    })

@app.post("/api/roulette/spin")
@csrf.exempt
def roulette_spin():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'ok': False, 'error': 'Not logged in'}), 403

    data = request.get_json(silent=True) or {}
    bet_color = data.get('bet_color')   # red, black, green, or None
    bet_number = data.get('bet_number') # 0–36 or None
    bet_amount = int(data.get('bet_amount', 100))

    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({'ok': False, 'error': 'User not found'}), 404

    if user.balance < bet_amount:
        return jsonify({'ok': False, 'error': 'Insufficient balance'}), 400

    number, color = RouletteGame().spin()
    win = False
    payout = 0
    win_type = None

    # Color bet
    if bet_color == color:
        payout = bet_amount * (14 if color == "green" else 2)
        win = True
        win_type = "color"

    # Number bet
    if bet_number is not None:
        try:
            bet_number = int(bet_number)
            if bet_number == number:
                payout = max(payout, bet_amount * 35)
                win = True
                win_type = "number"
        except ValueError:
            pass

    if win:
        user.balance += payout
        message = f"You won ${payout - bet_amount} on {win_type}!"
    else:
        user.balance -= bet_amount
        message = f"You lost ${bet_amount}."

    save_users(users)

    return jsonify({
        'ok': True,
        'number': number,
        'color': color,
        'message': message,
        'new_balance': user.balance
    })

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

# Elastic Beanstalk entry point
application = app