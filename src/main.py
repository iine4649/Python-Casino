from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from roulette import RouletteGame
import json, os
from pathlib import Path
from user import User
from game import BlackjackGame
from typing import List
from slotmachine import SlotMachineGame
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
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
                    games_played=user_data.get('games_played', 0),
                    nickname=user_data.get('nickname', "")
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
    if session.get('user_id'):
        return redirect(url_for('lobby'))
    return render_template("secure_login.html")

@app.route("/sign-up")
def sign_up():
    return render_template("secure_sign_up.html")

@app.route("/sign-in", methods=["POST"])
@csrf.exempt
def sign_in_form():
    """Handle HTML form-based sign-in."""
    user_id = (request.form.get("user_id") or "").strip().lower()
    password = request.form.get("password") or ""

    users = {k.lower(): v for k, v in load_users().items()}
    user = users.get(user_id)

    if not user:
        return render_template("secure_login.html", error="Invalid username or password")

    password_hash = user.password if isinstance(user, User) else user.get("password_hash", "")
    if not bcrypt.check_password_hash(password_hash, password):
        return render_template("secure_login.html", error="Invalid username or password")

    session['user_id'] = user_id
    return redirect(url_for('lobby'))

@app.route("/lobby")
def lobby():
    user_id = session.get('user_id', 'Guest')
    if user_id in active_games:
        active_games.pop(user_id, None)
    users = load_users()
    user = users.get(user_id)
    balance = user.balance if user else 1000
    display_name = (user.nickname if user and getattr(user, 'nickname', None) else user_id)
    return render_template("lobby.html", username=display_name, balance=balance)

@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    if user and isinstance(user, User):
        balance, money_won, money_lost = user.balance, user.money_won, user.money_lost
        history = getattr(user, 'history', [])
    else:
        balance, money_won, money_lost = 1000, 0, 0
        history = []
    display_name = (user.nickname if user and getattr(user, 'nickname', None) else user_id)
    return render_template("dashboard.html", username=display_name, balance=balance, money_won=money_won, money_lost=money_lost, history=history)

@app.route("/blackjack")
def blackjack():
    user_id = session.get('user_id', 'Guest')
    active_games.pop(user_id, None)
    users = load_users()
    user = users.get(user_id)
    balance = user.balance if user else 1000
    display_name = (user.nickname if user and getattr(user, 'nickname', None) else user_id)
    return render_template("blackjack.html", username=display_name, balance=balance)

 

@app.post("/api/blackjack/deal")
@csrf.exempt
def api_blackjack_deal():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401

    if user_id in active_games:
        return jsonify({"ok": False, "error": "You already have an active round"}), 400

    data = request.get_json(silent=True) or {}
    bet_amount = float(data.get("bet_amount", 100))
    if bet_amount <= 0:
        return jsonify({"ok": False, "error": "Bet must be positive"}), 400
    if bet_amount > 1_000_000_000:
        return jsonify({"ok": False, "error": "Bet exceeds allowed limit"}), 400

    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404

    if user.balance < bet_amount:
        return jsonify({"ok": False, "error": "Insufficient balance"}), 400

    game = BlackjackGame()
    game.deal_initial_cards()
    active_games[user_id] = {"game": game, "bet": bet_amount}

    user.balance -= bet_amount
    save_users(users)

    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(c) for c in game.player_cards],
        "dealer_cards": [game.card_to_string(c) if i > 0 else "?" for i, c in enumerate(game.dealer_cards)],
        "player_total": game.get_player_total(),
        "dealer_total": "?",
        "new_balance": user.balance
    })

@app.post("/api/blackjack/hit")
@csrf.exempt
def api_blackjack_hit():
    user_id = session.get('user_id')
    if not user_id or user_id not in active_games:
        return jsonify({"ok": False, "error": "No active game"}), 400

    game = active_games[user_id]["game"]
    bet = active_games[user_id]["bet"]

    game.hit_player()
    player_total = game.get_player_total()

    users = load_users()
    user = users.get(user_id)
    result = None
    game_over = False

    if player_total > 21:
        user.money_lost += bet
        save_users(users)
        del active_games[user_id]
        result = "bust"
        game_over = True

        return jsonify({
            "ok": True,
            "player_cards": [game.card_to_string(c) for c in game.player_cards],
            "dealer_cards": [game.card_to_string(c) for c in game.dealer_cards],
            "player_total": player_total,
            "dealer_total": game.get_dealer_total(),
            "result": result,
            "game_over": game_over,
            "new_balance": user.balance
        })

    save_users(users)
    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(c) for c in game.player_cards],
        "dealer_cards": [game.card_to_string(c) if i > 0 else "?" for i, c in enumerate(game.dealer_cards)],
        "player_total": player_total,
        "dealer_total": "?",
        "result": result,
        "game_over": game_over,
        "new_balance": user.balance
    })

@app.post("/api/blackjack/stand")
@csrf.exempt
def api_blackjack_stand():
    user_id = session.get('user_id')
    if not user_id or user_id not in active_games:
        return jsonify({"ok": False, "error": "No active game"}), 400

    game = active_games[user_id]["game"]
    bet = active_games[user_id]["bet"]

    game.player_stay()
    dealer_total = game.get_dealer_total()
    player_total = game.get_player_total()

    users = load_users()
    user = users.get(user_id)

    result = game.get_game_result()
    if result in ["player_wins", "win"]:
        user.balance += bet * 2
        user.money_won += bet
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "blackjack",
            "result": "win",
            "amount": bet,
        })
    elif result == "tie":
        user.balance += bet
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "blackjack",
            "result": "tie",
            "amount": 0,
        })
    else:
        user.money_lost += bet
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "blackjack",
            "result": "lose",
            "amount": -bet,
        })

    save_users(users)
    del active_games[user_id]

    return jsonify({
        "ok": True,
        "player_cards": [game.card_to_string(c) for c in game.player_cards],
        "dealer_cards": [game.card_to_string(c) for c in game.dealer_cards],
        "player_total": player_total,
        "dealer_total": dealer_total,
        "result": result,
        "game_result": result,
        "bet": bet,
        "game_over": True,
        "new_balance": user.balance
    })

 

@app.route("/deposit")
def deposit():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    display_name = (user.nickname if user and getattr(user, 'nickname', None) else user_id)
    return render_template("deposit.html", username=display_name)

@app.post("/api/deposit")
@csrf.exempt
def api_deposit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"ok": False, "error": "Amount must be positive"}), 400
        if amount > 1_000_000_000:
            return jsonify({"ok": False, "error": "Deposit exceeds allowed limit"}), 400
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "Invalid amount"}), 400

    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404

    user.deposit(amount)
    user.history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "game": "deposit",
        "result": "deposit",
        "amount": amount,
    })
    save_users(users)

    return jsonify({
        "ok": True,
        "new_balance": user.balance,
        "deposited": amount
    })



 

@app.route("/roulette")
def roulette():
    user_id = session.get('user_id', 'Guest')
    active_games.pop(user_id, None)
    users = load_users()
    user = users.get(user_id)
    balance = user.balance if user else 1000
    display_name = (user.nickname if user and getattr(user, 'nickname', None) else user_id)
    return render_template("roulette.html", username=display_name, balance=balance)

@app.post("/api/roulette/spin")
@csrf.exempt
def roulette_spin():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'ok': False, 'error': 'Not logged in'}), 403

    if user_id in active_games:
        return jsonify({'ok': False, 'error': 'Finish your active round first'}), 400

    data = request.get_json(silent=True) or {}
    bet_color = data.get('bet_color')
    bet_number = data.get('bet_number')
    bet_amount = int(data.get('bet_amount', 100))
    if bet_amount <= 0:
        return jsonify({'ok': False, 'error': 'Bet must be positive'}), 400
    if bet_amount > 1_000_000_000:
        return jsonify({'ok': False, 'error': 'Bet exceeds allowed limit'}), 400

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

    if bet_color == color:
        payout = bet_amount * (14 if color == "green" else 2)
        win = True
        win_type = "color"

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
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "roulette",
            "result": "win",
            "amount": payout - bet_amount,
        })
    else:
        user.balance -= bet_amount
        message = f"You lost ${bet_amount}."
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "roulette",
            "result": "lose",
            "amount": -bet_amount,
        })

    save_users(users)
    active_games.pop(user_id, None)

    return jsonify({
        'ok': True,
        'number': number,
        'color': color,
        'message': message,
        'new_balance': user.balance
    })

@app.route("/slotmachine")
def slotmachine():
    user_id = session.get('user_id', 'Guest')
    users = load_users()
    user = users.get(user_id)
    balance = user.balance if user else 1000
    display_name = (user.nickname if user and getattr(user, 'nickname', None) else user_id)
    return render_template("slotmachine.html", username=display_name, balance=balance)


@app.post("/api/slot/spin")
@csrf.exempt
def api_slot_spin():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"ok": False, "error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    try:
        bet_amount = float(data.get("bet_amount", 100))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid bet amount"}), 400

    users = load_users()
    user = users.get(user_id)
    if not user or not isinstance(user, User):
        return jsonify({"ok": False, "error": "User not found"}), 404

    if bet_amount <= 0:
        return jsonify({"ok": False, "error": "Bet must be positive"}), 400
    if bet_amount > 1_000_000_000:
        return jsonify({"ok": False, "error": "Bet exceeds allowed limit"}), 400

    if user.balance < bet_amount:
        return jsonify({"ok": False, "error": "Insufficient balance"}), 400

    user.balance -= bet_amount

    game = SlotMachineGame()
    result = game.spin(bet_amount)

    if result["multiplier"] > 0:
        user.balance += result["winnings"]
        user.money_won += result["profit"]
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "slotmachine",
            "result": "win",
            "amount": result["profit"],
        })
    else:
        user.money_lost += bet_amount
        user.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": "slotmachine",
            "result": "lose",
            "amount": -bet_amount,
        })

    save_users(users)

    return jsonify({
        "ok": True,
        "reels": result["reels"],
        "multiplier": result["multiplier"],
        "message": result["message"],
        "new_balance": user.balance,
    })

@app.post("/api/sign-up")
@csrf.exempt
def api_sign_up():
    print("Request headers:", dict(request.headers))
    print("Raw data:", request.data)
    data = request.get_json(silent=True) or request.form.to_dict()
    print("Parsed data:", data)
    user_id = (data.get("user_id") or "").strip().lower()
    nickname = (data.get("nickname") or "").strip()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or data.get("password2") or ""
    if not user_id or not password:
        return jsonify({"ok": False, "error": "Missing username or password"}), 400
    if not nickname:
        return jsonify({"ok": False, "error": "Missing nickname"}), 400

    if password != password_confirm:
        return jsonify({"ok": False, "error": "Passwords do not match"}), 400

    users = load_users()

    if user_id in (u.lower() for u in users.keys()):
        return jsonify({"ok": False, "error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=user_id, nickname=nickname, password=hashed_password, balance=10000)
    users[user_id] = new_user
    save_users(users)

    session['user_id'] = user_id

    return jsonify({"ok": True}), 201

@app.post("/api/sign-in")
@csrf.exempt
def api_sign_in():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = (data.get("user_id") or "").strip().lower()
    password = data.get("password") or ""

    users = {k.lower(): v for k, v in load_users().items()}
    user = users.get(user_id)
    if not user:
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    password_hash = user.password if isinstance(user, User) else user.get("password_hash", "")
    if not bcrypt.check_password_hash(password_hash, password):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    session['user_id'] = user_id
    return jsonify({"ok": True})

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

application = app
