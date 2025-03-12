from flask import Flask, request, render_template
from backend.logic import process_message
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        message = request.form["message"]
        response = process_message(message, "web", request.remote_addr)
        return render_template("index.html", response=response)
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 for local, use PORT env var for Render
    app.run(host="0.0.0.0", port=port, debug=False)