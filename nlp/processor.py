import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

CATEGORIES = ["infrastructure", "education", "health", "environment"]
LOCATIONS = ["Colombo", "Kandy", "Galle", "Jaffna"]

CHIT_CHAT = {
    "hi": "Hello! How can I assist you today?",
    "how are you": "I’m doing great, thanks for asking! How about you?",
    "thanks": "You’re welcome! Anything else on your mind?",
    "bye": "Take care! Let me know if you need me again."
}

def categorize_issue(text):
    text = text.lower()
    for category in CATEGORIES:
        if category in text or any(keyword in text for keyword in [category[:3]]):
            return category
    return "other"

def extract_location(text):
    text = text.lower()
    for location in LOCATIONS:
        if location.lower() in text:
            return location
    return None

def get_sentiment(text):
    return sia.polarity_scores(text)["compound"]

def detect_intent(text):
    text = text.lower().strip()

    for phrase, response in CHIT_CHAT.items():
        if phrase in text:
            return "chit_chat", response
    if "upvote #" in text:
        issue_id = text.split("upvote #")[1].split()[0]
        return "upvote", issue_id
    elif "suggest link for #" in text:
        parts = text.split("suggest link for #")[1].split(":")
        issue_id, link = parts[0].strip(), parts[1].strip()
        return "suggest_link", (issue_id, link)
    elif "update #" in text:
        issue_id = text.split("update #")[1].split()[0]
        return "update", issue_id
    elif any(cat in text.lower() for cat in CATEGORIES) or any(loc in text.lower() for loc in LOCATIONS):
        return "report", None
    return "chit_chat", "Hmm, let’s chat! What’s on your mind?"