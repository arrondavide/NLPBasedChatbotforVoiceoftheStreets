from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def add_user(platform, platform_user_id):
    user = supabase.table("users").select("*").eq("platform_user_id", platform_user_id).execute()
    if not user.data:
        user = supabase.table("users").insert({
            "platform": platform, 
            "platform_user_id": platform_user_id,
            "created_at": datetime.now().isoformat()
        }).execute()
    return user.data[0]["id"]

def add_issue(description, category, location, sentiment_score, priority=None):
    # Calculate priority if not provided
    if priority is None:
        priority = min(max(abs(sentiment_score) * 10, 1), 10)  # Scale to 1-10
    
    issue = supabase.table("issues").insert({
        "description": description,
        "category": category,
        "location": location,
        "sentiment_score": sentiment_score,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "vote_count": 0,
        "is_urgent": False
    }).execute()
    
    return issue.data[0]["id"]

def add_vote(user_id, issue_id):
    # Check if user already voted for this issue
    existing_vote = supabase.table("votes").select("*").eq("user_id", user_id).eq("issue_id", issue_id).execute()
    
    if not existing_vote.data:
        # Add vote
        supabase.table("votes").insert({
            "user_id": user_id, 
            "issue_id": issue_id,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Count votes and update issue
        vote_count = supabase.table("votes").select("id").eq("issue_id", issue_id).execute()
        vote_count = len(vote_count.data)
        
        # Update issue vote count and urgency flag
        supabase.table("issues").update({
            "vote_count": vote_count, 
            "is_urgent": vote_count >= 50,
            "updated_at": datetime.now().isoformat()
        }).eq("id", issue_id).execute()
        
        return vote_count
    return None

def add_donation_link(issue_id, link, user_id):
    # Validate URL format (basic check)
    if not link.startswith(("http://", "https://")):
        link = "https://" + link
        
    supabase.table("donation_links").insert({
        "issue_id": issue_id, 
        "link": link, 
        "suggested_by": user_id,
        "created_at": datetime.now().isoformat(),
        "status": "pending"  # Links need approval
    }).execute()
    
    return True

def get_update(issue_id):
    update = supabase.table("updates").select("update_text, created_at").eq("issue_id", issue_id).order("created_at", desc=True).limit(1).execute()
    
    if update.data:
        date_str = datetime.fromisoformat(update.data[0]["created_at"].replace("Z", "+00:00")).strftime("%d %b %Y")
        return f"[{date_str}] {update.data[0]['update_text']}"
    return "No updates yet. Be the first to contribute!"

def get_recent_issues(limit=5, category=None, location=None):
    """Get recent or filtered issues"""
    query = supabase.table("issues").select("id, description, category, location, vote_count, is_urgent").order("created_at", desc=True)
    
    if category:
        query = query.eq("category", category)
    if location:
        query = query.eq("location", location)
        
    result = query.limit(limit).execute()
    return result.data

def get_urgent_issues(limit=5):
    """Get urgent issues (50+ votes)"""
    result = supabase.table("issues").select("id, description, category, location, vote_count").eq("is_urgent", True).order("vote_count", desc=True).limit(limit).execute()
    return result.data

def add_update(issue_id, update_text, user_id):
    """Add an update to an issue"""
    supabase.table("updates").insert({
        "issue_id": issue_id,
        "update_text": update_text,
        "updated_by": user_id,
        "created_at": datetime.now().isoformat()
    }).execute()
    
    # Also update the issue's updated_at timestamp
    supabase.table("issues").update({
        "updated_at": datetime.now().isoformat()
    }).eq("id", issue_id).execute()
    
    return True