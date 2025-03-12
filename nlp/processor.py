from transformers import pipeline
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure vader_lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize models
classifier = pipeline("text-classification", model="distilbert-base-uncased")
sia = SentimentIntensityAnalyzer()

# Predefined categories and locations
CATEGORIES = ["infrastructure", "education", "health", "environment"]
LOCATIONS = ["Colombo", "Kandy", "Galle", "Jaffna"]

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
    text = text.lower()
    if "upvote #" in text:
        return "upvote", text.split("upvote #")[1].split()[0]
    elif "suggest link for #" in text:
        return "suggest_link", text.split("suggest link for #")[1].split(":")[0], text.split(":")[1].strip()
    elif "update #" in text:
        return "update", text.split("update #")[1].split()[0]
    else:
        return "report", None