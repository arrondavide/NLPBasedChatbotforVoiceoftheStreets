from nlp.processor import categorize_issue, extract_location, get_sentiment, detect_intent
from backend.db import add_user, add_issue, add_vote, add_donation_link, get_update

def process_message(message, platform, platform_user_id):
    intent, *args = detect_intent(message)
    user_id = add_user(platform, platform_user_id)

    if intent == "report":
        category = categorize_issue(message)
        location = extract_location(message)
        sentiment = get_sentiment(message)
        issue_id = add_issue(message, category, location, sentiment)
        return f"Thank you for reporting issue #{issue_id}: {message}. You can upvote or suggest donation links using this ID."
    elif intent == "upvote":
        issue_id = args[0]
        vote_count = add_vote(user_id, issue_id)
        if vote_count:
            return f"You’ve upvoted issue #{issue_id}. Current votes: {vote_count}."
        return f"You’ve already upvoted issue #{issue_id}."
    elif intent == "suggest_link":
        issue_id, link = args
        add_donation_link(issue_id, link, user_id)
        return f"Thank you for suggesting a donation link for issue #{issue_id}."
    elif intent == "update":
        issue_id = args[0]
        update = get_update(issue_id)
        return f"Issue #{issue_id}: {update}"
    return "Sorry, I didn’t understand that. Try 'Power outage in Colombo', 'upvote #123', 'suggest link for #123: <url>', or 'update #123'."