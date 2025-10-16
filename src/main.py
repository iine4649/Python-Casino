from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from roulette import RouletteGame
import json
import os
from pathlib import Path
from user import User
from game import BlackjackGame

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "userdata.json"
ASSETS_DIR = BASE_DIR / "assets"

app = Flask(__name__, template_folder=str(ASSETS_DIR), static_folder=str(ASSETS_DIR))

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-in-prod"),
    SESSION_COOKIE_SECURE=False,  # Set to False for development (HTTP)
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


def save_users(users: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    user_dicts = {}
    for username, user in users.items():
        if isinstance(user, User):
            user_dicts[username] = user.to_dict()
        else:
            user_dicts[username] = user
    DATA_FILE.write_text(json.dumps(user_dicts, ensure_ascii=False, indent=2), encoding="utf-8")


@app.route("/")
def login():
    # If user is already logged in, redirect to lobby
    if session.get('user_id'):
        return redirect(url_for('lobby'))
    return render_template("secure_login.html")


@app.route("/sign-up")
def sign_up():
    return render_template("secure_sign_up.html")

@app.route("/lobby")
def lobby():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    
    if user and isinstance(user, User):
        balance = user.balance
    else:
        balance = 1000  # Default for guest or old format
    
    return render_template("lobby.html", username=user_id, balance=balance)
    
@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    
    if user and isinstance(user, User):
        balance = user.balance
        money_won = user.money_won
        money_lost = user.money_lost
    else:
        balance = 1000 
        money_won = 0
        money_lost = 0
    
    return render_template("dashboard.html", username=user_id, balance=balance, money_won=money_won, money_lost=money_lost)

@app.route("/blackjack")
def blackjack():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    
    if user and isinstance(user, User):
        balance = user.balance
    else:
        balance = 1000

    return render_template("blackjack.html", username=user_id, balance=balance)

@app.route("/deposit")
def deposit():
    user_id = session.get('user_id', 'Guest')
    return render_template("deposit.html", username=user_id)


@app.post("/api/deposit")
@csrf.exempt
def api_deposit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    amount = data.get("amount")
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"ok": False, "error": "Amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "Invalid amount"}), 400
    
    users = load_users()
    user = users.get(user_id)
    
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404
    
    # Add deposit amount to balance
    user.deposit(amount)
    save_users(users)
    
    return jsonify({
        "ok": True,
        "new_balance": user.balance,
        "deposited": amount
    })





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
        "player_cards": [game.card_to_string(card) for card in game.player_cards],
        "dealer_cards": [game.card_to_string(card) if i > 0 else "?" for i, card in enumerate(game.dealer_cards)],
        "player_total": game.get_player_total(),
        "dealer_total": "?" if len(game.dealer_cards) > 0 else 0,
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
    
    result = game.hit_player()
    
    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(card) for card in game.player_cards],
        "dealer_cards": [game.card_to_string(card) if i > 0 else "?" for i, card in enumerate(game.dealer_cards)],
        "player_total": game.get_player_total(),
        "dealer_total": "?" if not game.game_over else game.get_dealer_total(),
        "game_over": game.game_over,
        "result": result,
        "game_result": game.get_game_result() if game.game_over else "playing"
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
    result = game.get_game_result()
    
    users = load_users()
    user = users.get(user_id)
    if user and isinstance(user, User):
        if result == "player_wins" or result == "dealer_bust":
            user.balance += bet_amount * 2
            user.money_won += bet_amount
        elif result == "tie":
            user.balance += bet_amount
        else:
            user.money_lost += bet_amount
        
        user.games_played += 1
        save_users(users)
    
    # Clean up game
    del active_games[user_id]
    
    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(card) for card in game.player_cards],
        "dealer_cards": [game.card_to_string(card) for card in game.dealer_cards],
        "player_total": game.get_player_total(),
        "dealer_total": game.get_dealer_total(),
        "game_over": True,
        "game_result": result,
        "new_balance": user.balance if user and isinstance(user, User) else 0,
        "bet": bet_amount
    })


@app.route("/health")
def health():
    return {"status": "ok"}


@app.post("/api/sign-up")
@csrf.exempt  # If using forms without CSRF token; for production, include token in your form
def api_sign_up():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or data.get("password2") or ""

    if not user_id or not password:
        return jsonify({"ok": False, "error": "Missing user_id or password"}), 400
    if password != password_confirm:
        return jsonify({"ok": False, "error": "Passwords do not match"}), 400

    users = load_users()
    if user_id in users:
        return jsonify({"ok": False, "error": "User already exists"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    # Create new User object with default values
    new_user = User(
        username=user_id,
        password=hashed,
        balance=10000,  # Default starting balance
        money_won=0,
        money_lost=0,
        games_played=0
    )
    users[user_id] = new_user
    save_users(users)
    return jsonify({"ok": True}), 201


@app.post("/api/sign-in")
@csrf.exempt  # If using forms without CSRF token; for production, include token in your form
def api_sign_in():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""

    users = load_users()
    user = users.get(user_id)
    if not user:
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    if isinstance(user, User):
        password_hash = user.password
    else:
        password_hash = user.get("password_hash", "")
    
    if not bcrypt.check_password_hash(password_hash, password):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    session['user_id'] = user_id
    return jsonify({"ok": True})


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route("/debug-session")
def debug_session():
    return jsonify({
        "session": dict(session),
        "user_id": session.get('user_id', 'Not found')
    })

@app.route("/roulette")
def roulette():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    balance = user.balance if user else 1000
    return render_template("roulette.html", username=user_id, balance=balance)

@app.post("/api/roulette/spin")
@csrf.exempt
def api_roulette_spin():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    
    data = request.get_json(silent=True) or {}
    bet_type = data.get("bet_type")
    bet_amount = 100  # fixed for now

    users = load_users()
    user = users.get(user_id)
    if not user:
        return jsonify({"ok": False, "error": "User not found"}), 404
    if user.balance < bet_amount:
        return jsonify({"ok": False, "error": "Insufficient balance"}), 400

    game = RouletteGame()
    outcome = game.check_result(bet_type)

    if outcome["result"] == "win":
        user.balance += bet_amount
        user.money_won += bet_amount
    else:
        user.balance -= bet_amount
        user.money_lost += bet_amount

    user.games_played += 1
    save_users(users)

    return jsonify({
        "ok": True,
        "data": {
            "number": outcome["number"],
            "color": outcome["color"],
            "result": outcome["result"],
            "new_balance": user.balance
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
