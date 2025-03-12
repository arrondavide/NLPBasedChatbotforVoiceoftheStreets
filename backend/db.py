from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def add_user(platform, platform_user_id):
    user = supabase.table("users").select("*").eq("platform_user_id", platform_user_id).execute()
    if not user.data:
        user = supabase.table("users").insert({"platform": platform, "platform_user_id": platform_user_id}).execute()
    return user.data[0]["id"]

def add_issue(description, category, location, sentiment):
    issue = supabase.table("issues").insert({
        "description": description,
        "category": category,
        "location": location,
        "sentiment_score": sentiment
    }).execute()
    return issue.data[0]["id"]

def add_vote(user_id, issue_id):
    if not supabase.table("votes").select("*").eq("user_id", user_id).eq("issue_id", issue_id).execute().data:
        supabase.table("votes").insert({"user_id": user_id, "issue_id": issue_id}).execute()
        vote_count = supabase.table("votes").select("id").eq("issue_id", issue_id).execute().count
        supabase.table("issues").update({"vote_count": vote_count, "is_urgent": vote_count >= 50}).eq("id", issue_id).execute()
        return vote_count
    return None

def add_donation_link(issue_id, link, user_id):
    supabase.table("donation_links").insert({"issue_id": issue_id, "link": link, "suggested_by": user_id}).execute()

def get_update(issue_id):
    update = supabase.table("updates").select("update_text").eq("issue_id", issue_id).order("created_at", desc=True).limit(1).execute()
    return update.data[0]["update_text"] if update.data else "No updates yet."