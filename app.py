from flask import Flask, request, render_template
from backend.logic import process_message
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Store chat history in memory (for simplicity; use a DB for persistence)
chat_history = []

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_message = request.form["message"]
        response = process_message(user_message, "web", request.remote_addr)
        chat_history.append({"text": user_message, "is_user": True})
        chat_history.append({"text": response, "is_user": False})
    return render_template("index.html", messages=chat_history)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)