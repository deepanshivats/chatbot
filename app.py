from flask import Flask, render_template, request, jsonify
from main import login, chat, logout
import random

app = Flask(__name__)

# ---------------------------
# Helper functions (merged from main.py)
# ---------------------------

GREET_RESPONSES = ["Hello!", "Hi there!", "Hey!", "Welcome back!"]

def greet():
    return random.choice(GREET_RESPONSES)

def is_casual(user_input: str) -> bool:
    casual_words = ["hi", "hello", "hey", "how are you", "what's up"]
    return any(word in user_input.lower() for word in casual_words)

def styled_bot_response(message: str) -> dict:
    return {"bot_response": message}

def check_banking_intents(user_input: str) -> str:
    if "balance" in user_input.lower():
        return "Your current balance is ₹25,000."
    elif "transfer" in user_input.lower():
        return "Sure! Please provide account details for transfer."
    elif "statement" in user_input.lower():
        return "Your last 5 transactions are: 500 debit, 2000 credit, 1000 debit, 1500 debit, 3000 credit."
    return None

def response(user_input: str) -> str:
    if is_casual(user_input):
        return greet()
    intent_response = check_banking_intents(user_input)
    if intent_response:
        return intent_response
    return "I'm not sure I understand. Could you please clarify?"

def login_user(username: str, password: str) -> bool:
    # Dummy login check
    return username == "admin" and password == "password"

def get_account_details(account_number: str) -> dict:
    # Dummy banking data
    return {"account_number": account_number, "balance": "₹25,000"}

# ---------------------------
# Flask Routes
# ---------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    bot_reply = response(user_input)
    return jsonify(styled_bot_response(bot_reply))

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if login_user(username, password):
        return jsonify({"status": "success", "message": "Login successful!"})
    return jsonify({"status": "failure", "message": "Invalid credentials."})

@app.route("/account", methods=["POST"])
def account():
    data = request.json
    account_number = data.get("account_number")
    details = get_account_details(account_number)
    return jsonify(details)

# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)


