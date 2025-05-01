from flask import Flask, render_template, request, redirect, session, url_for
import random
from main import (
    greet, is_casual, styled_bot_response, check_banking_intents,
    response, login_user, get_account_details, GREET_RESPONSES
)

app = Flask(__name__, static_folder='static')
app.secret_key = 'secret123'  # Session key


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form.get("login_id")
        password = request.form.get("password")
        user = login_user(login_id, password)

        if user:
            session["user"] = {
                "id": user[0],
                "login_id": user[1],
                "name": user[3]
            }
            session["chat_history"] = []  # Reset chat on new login
            return redirect("/chat")
        else:
            return render_template("login.html",
                                   error="❌ Invalid login ID or password.")

    return render_template("login.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        user_msg = request.form.get("message", "").strip()
        if user_msg:
            chat_history = session.get("chat_history", [])
            casual = is_casual(user_msg)
            chat_history.append(f"You: {user_msg}")

            replies = []

            # 🚪 Exit check
            if user_msg.lower() in ['bye', 'exit', 'quit']:
                styled_reply = styled_bot_response("👋 Goodbye! Take care bhai!", casual)
                chat_history.append(f"Bot: {styled_reply}")
                session["chat_history"] = chat_history
                return styled_reply

            # 💬 Normalize, split and remove duplicate queries
            queries = [query.strip() for query in user_msg.replace('?', '.').split('.') if query.strip()]
            queries = list(dict.fromkeys(queries))  # Remove duplicates

            seen_replies = set()

            for query in queries:
                response_found = False

                # Greeting detection
                if greet(query):
                    if "Greeting detected" not in seen_replies:
                        replies.append(random.choice(GREET_RESPONSES))
                        seen_replies.add("Greeting detected")
                        response_found = True
                    continue

                # Check for account-related keywords
                if "account" in query.lower() or "balance" in query.lower():
                    result = get_account_details(session["user"]["login_id"])
                    if result and result not in seen_replies:
                        replies.append(result)
                        seen_replies.add(result)
                        response_found = True
                    continue

                # Check banking intents
                intent_reply = check_banking_intents(query)
                if intent_reply and intent_reply not in seen_replies:
                    replies.append(intent_reply)
                    seen_replies.add(intent_reply)
                    response_found = True
                    continue

                # Fallback response
                if not response_found:
                    fallback_reply = response(query)
                    if fallback_reply and fallback_reply not in seen_replies:
                        replies.append(fallback_reply)
                        seen_replies.add(fallback_reply)

            # Format response
            if replies:
                combined_reply = "\n\n".join(replies)
                styled_reply = styled_bot_response(combined_reply, casual)
            else:
                styled_reply = styled_bot_response("❓ I'm not sure I understood that.", casual)

            chat_history.append(f"Bot: {styled_reply}")
            session["chat_history"] = chat_history

            return styled_reply

    # GET request — render chat UI
    return render_template("chat.html",
                           chat_history=session.get("chat_history", []),
                           name=session["user"]["name"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
