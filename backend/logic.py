from nlp.processor import categorize_issue, extract_location, get_sentiment, detect_intent
from backend.db import add_user, add_issue, add_vote, add_donation_link, get_update

def process_message(message, platform, platform_user_id):
    intent, data = detect_intent(message)
    user_id = add_user(platform, platform_user_id)

    if intent == "report":
        category = categorize_issue(message)
        location = extract_location(message)
        sentiment = get_sentiment(message)
        issue_id = add_issue(message, category, location, sentiment)
        return f"Thanks for letting me know! I’ve logged issue #{issue_id}: {message}. Want to upvote it or suggest a donation link?"
    elif intent == "upvote":
        issue_id = data
        vote_count = add_vote(user_id, issue_id)
        if vote_count:
            return f"Got it! You’ve upvoted issue #{issue_id}. It’s now at {vote_count} votes. Anything else I can help with?"
        return f"Looks like you’ve already upvoted issue #{issue_id}. What’s next?"
    elif intent == "suggest_link":
        issue_id, link = data
        add_donation_link(issue_id, link, user_id)
        return f"Nice one! I’ve added your donation link for issue #{issue_id}. Anything else you’d like to do?"
    elif intent == "update":
        issue_id = data
        update = get_update(issue_id)
        return f"Here’s the latest on issue #{issue_id}: {update}. Need more info?"
    elif intent == "chit_chat":
        return data  # Predefined or dynamic chit-chat response
    elif intent == "unknown":
        return "I’m not quite sure what you mean. You can report an issue like 'Power outage in Colombo', upvote with 'upvote #123', suggest a link with 'suggest link for #123: <url>', or just chat with me!"
    return "Oops, something went wrong. Let’s try that again!"