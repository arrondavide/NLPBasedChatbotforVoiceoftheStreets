import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize classifiers
sia = SentimentIntensityAnalyzer()
zero_shot_classifier = pipeline("zero-shot-classification")
ner_pipeline = pipeline("ner")

CATEGORIES = ["infrastructure", "education", "health", "environment", "safety", "transport", "water", "electricity"]
SRI_LANKA_LOCATIONS = ["Colombo", "Kandy", "Galle", "Jaffna", "Negombo", "Batticaloa", "Trincomalee", 
                      "Anuradhapura", "Matara", "Kurunegala", "Ratnapura", "Badulla", "Puttalam"]

CHIT_CHAT = {
    "hi": "Hello! I'm Voice of the Streets. How can I help your community today?",
    "hello": "Hi there! Ready to make a difference in Sri Lanka? What's happening in your area?",
    "how are you": "I'm here and ready to help! What community issue should we tackle today?",
    "thanks": "Every voice matters! Is there anything else I can help with?",
    "bye": "Take care! Remember, change starts with you. Come back anytime to report issues."
}

def categorize_issue(text):
    """Categorize issue using zero-shot classification"""
    result = zero_shot_classifier(text, CATEGORIES)
    return result["labels"][0]  # Return highest confidence category

def extract_location(text):
    """Extract location using named entity recognition and Sri Lanka location list"""
    # First try NER
    entities = ner_pipeline(text)
    locations = [entity["word"] for entity in entities if entity["entity"].startswith("B-LOC") or entity["entity"].startswith("I-LOC")]
    
    # Then check against known Sri Lanka locations
    for location in SRI_LANKA_LOCATIONS:
        if location.lower() in text.lower():
            return location
    
    # If NER found a location, return the first one
    if locations:
        return locations[0]
    
    return None

def get_sentiment(text):
    """Get sentiment score using VADER"""
    return sia.polarity_scores(text)["compound"]

def get_issue_priority(sentiment, text_length):
    """Calculate priority based on sentiment and message length"""
    # More negative sentiment and longer descriptions might indicate more serious issues
    priority = abs(min(sentiment, 0)) * (min(text_length, 200) / 200)
    return round(priority * 10)  # Scale to 0-10

def detect_intent(text):
    """Detect user intent from message text"""
    text = text.lower().strip()
    
    # Check for chit-chat first
    for phrase, response in CHIT_CHAT.items():
        if phrase in text:
            return "chit_chat", response
            
    # Check for specific commands with issue IDs
    if "upvote #" in text or "upvote issue #" in text:
        try:
            if "upvote #" in text:
                issue_id = text.split("upvote #")[1].split()[0]
            else:
                issue_id = text.split("upvote issue #")[1].split()[0]
            return "upvote", issue_id
        except IndexError:
            return "unknown", None
            
    elif "suggest link for #" in text or "donation for #" in text:
        try:
            if "suggest link for #" in text:
                parts = text.split("suggest link for #")[1].split(":")
            else:
                parts = text.split("donation for #")[1].split(":")
            issue_id, link = parts[0].strip(), parts[1].strip()
            return "suggest_link", (issue_id, link)
        except IndexError:
            return "unknown", None
            
    elif "update #" in text or "status #" in text or "what's happening with #" in text:
        try:
            if "update #" in text:
                issue_id = text.split("update #")[1].split()[0]
            elif "status #" in text:
                issue_id = text.split("status #")[1].split()[0]
            else:
                issue_id = text.split("what's happening with #")[1].split()[0]
            return "update", issue_id
        except IndexError:
            return "unknown", None
    
    # Check if this is likely a report of a new issue
    report_indicators = ["broken", "problem", "issue", "not working", "damaged", "flooding", 
                        "outage", "shortage", "unsafe", "dangerous", "need", "poor", "bad",
                        "leak", "garbage", "waste", "pollution"]
                        
    if any(indicator in text for indicator in report_indicators) or len(text.split()) > 5:
        # Use zero-shot classification to determine if it's actually a report
        result = zero_shot_classifier(text, ["community issue report", "general conversation"])
        if result["labels"][0] == "community issue report" and result["scores"][0] > 0.6:
            return "report", None
            
    # Default to conversation if nothing specific detected
    return "chit_chat", "I'm here to help with community issues in Sri Lanka. You can report something like 'There's a power outage in Colombo' or ask for updates on existing issues."