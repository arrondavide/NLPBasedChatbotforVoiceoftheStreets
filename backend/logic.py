from nlp.processor import categorize_issue, extract_location, get_sentiment, detect_intent, get_issue_priority
from backend.db import (add_user, add_issue, add_vote, add_donation_link, get_update, 
                      get_recent_issues, get_urgent_issues, add_update)

def process_message(message, platform, platform_user_id):
    """Process incoming messages and return appropriate responses"""
    intent, data = detect_intent(message)
    user_id = add_user(platform, platform_user_id)

    if intent == "report":
        # Process new issue report
        category = categorize_issue(message)
        location = extract_location(message)
        sentiment = get_sentiment(message)
        priority = get_issue_priority(sentiment, len(message))
        
        # Add the issue to the database
        issue_id = add_issue(message, category, location, sentiment, priority)
        
        # Generate location text for response
        location_text = f" in {location}" if location else ""
        
        return (f"Thanks for reporting this {category} issue{location_text}! I've logged it as "
                f"issue #{issue_id}. Here's what you can do next:\n"
                f"• Upvote it: 'upvote #{issue_id}'\n"
                f"• Suggest donation: 'suggest link for #{issue_id}: URL'\n"
                f"• Check for updates later: 'update #{issue_id}'")
                
    elif intent == "upvote":
        # Process upvote for an issue
        issue_id = data
        vote_count = add_vote(user_id, issue_id)
        
        if vote_count:
            urgency_msg = ""
            if vote_count >= 50:
                urgency_msg = " This is now flagged as URGENT!"
            elif vote_count >= 40:
                urgency_msg = " Almost at urgent status (50+ votes)!"
                
            return f"Thank you for your vote! Issue #{issue_id} now has {vote_count} votes.{urgency_msg}"
        return f"You've already upvoted issue #{issue_id}. Thanks for your support!"
        
    elif intent == "suggest_link":
        # Process donation link suggestion
        issue_id, link = data
        success = add_donation_link(issue_id, link, user_id)
        
        if success:
            return (f"Thank you for suggesting a donation link for issue #{issue_id}! "
                    f"It will be reviewed shortly. What would you like to do next?")
        return "Sorry, there was a problem adding your donation link. Please try again."
        
    elif intent == "update":
        # Get the latest update for an issue
        issue_id = data
        update = get_update(issue_id)
        
        return f"Update for issue #{issue_id}: {update}"
        
    elif intent == "get_recent":
        # Get recent issues
        issues = get_recent_issues(5)
        
        if not issues:
            return "No issues have been reported yet. Be the first to report one!"
            
        response = "Recent community issues:\n"
        for issue in issues:
            response += f"• #{issue['id']}: {issue['description'][:50]}... ({issue['vote_count']} votes)\n"
        
        return response
        
    elif intent == "get_urgent":
        # Get urgent issues
        issues = get_urgent_issues(5)
        
        if not issues:
            return "There are no urgent issues at the moment. That's good news!"
            
        response = "URGENT community issues:\n"
        for issue in issues:
            response += f"• #{issue['id']}: {issue['description'][:50]}... ({issue['vote_count']} votes)\n"
        
        return response
        
    elif intent == "chit_chat":
        # Handle general conversation
        return data
        
    elif intent == "unknown":
        # Handle unrecognized intent
        return ("I'm not quite sure what you mean. Here's what I can help with:\n"
                "• Report an issue: 'The road near Colombo Hospital has huge potholes'\n"
                "• Upvote an issue: 'upvote #123'\n"
                "• Suggest donation: 'suggest link for #123: https://example.com'\n"
                "• Get updates: 'update #123'\n"
                "• Recent issues: 'show recent issues'\n"
                "• Urgent issues: 'show urgent issues'")
                
    # Fallback response
    return "I didn't catch that. Could you rephrase your message?"