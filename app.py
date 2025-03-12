from flask import Flask, request, render_template, jsonify, session
from backend.logic import process_message
from backend.db import get_recent_issues, get_urgent_issues
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

@app.route("/", methods=["GET"])
def home():
    """Render the main chat interface"""
    # Initialize session for new users
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    # Get recent and urgent issues for display
    recent_issues = get_recent_issues(5)
    urgent_issues = get_urgent_issues(3)
    
    return render_template(
        "index.html", 
        messages=session.get('chat_history', []),
        recent_issues=recent_issues,
        urgent_issues=urgent_issues
    )

@app.route("/send", methods=["POST"])
def send_message():
    """Handle message sending via AJAX"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    user_message = request.json.get("message", "")
    
    # Process the message
    bot_response = process_message(user_message, "web", session['user_id'])
    
    # Update chat history
    session['chat_history'].append({"text": user_message, "is_user": True})
    session['chat_history'].append({"text": bot_response, "is_user": False})
    session.modified = True
    
    return jsonify({
        "response": bot_response,
        "issue_data": extract_issue_data(bot_response)
    })

@app.route("/upvote/<issue_id>", methods=["POST"])
def upvote(issue_id):
    """Handle upvote via AJAX"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    # Process the upvote
    response = process_message(f"upvote #{issue_id}", "web", session['user_id'])
    
    # Update chat history
    session['chat_history'].append({"text": f"Upvoted issue #{issue_id}", "is_user": True})
    session['chat_history'].append({"text": response, "is_user": False})
    session.modified = True
    
    return jsonify({"success": True, "message": response})

@app.route("/update/<issue_id>", methods=["GET"])
def get_issue_update(issue_id):
    """Get update for an issue via AJAX"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    # Get the update
    response = process_message(f"update #{issue_id}", "web", session['user_id'])
    
    return jsonify({"success": True, "message": response})

@app.route("/recent", methods=["GET"])
def recent():
    """Get recent issues via AJAX"""
    issues = get_recent_issues(5)
    return jsonify({"success": True, "issues": issues})

@app.route("/urgent", methods=["GET"])
def urgent():
    """Get urgent issues via AJAX"""
    issues = get_urgent_issues(5)
    return jsonify({"success": True, "issues": issues})

def extract_issue_data(response):
    """Extract issue ID from bot response for UI enhancements"""
    if "I've logged it as issue #" in response:
        try:
            issue_id = response.split("issue #")[1].split(".")[0].split()[0]
            return {"issue_id": issue_id, "is_new_issue": True}
        except:
            pass
    return {"is_new_issue": False}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")