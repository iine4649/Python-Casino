import json
from pathlib import Path
from user import User
DATA_FILE = Path("data") / "userdata.json"
def read_json(file_path):
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding = "utf-8") as f:
        return json.load(f)

def write_json(file_path, data):
    with open(file_path, "w", encoding = "utf-8") as f:
        json.dump(data, f, indent=2)

def format_money(amount):
    return f"${amount:,}"

def verify_if_val_positive(value):
    try:
        return int(value) > 0
    except ValueError:
        return False

def read_users():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
