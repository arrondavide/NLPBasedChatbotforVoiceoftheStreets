from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                         CallbackContext, CallbackQueryHandler)
from backend.logic import process_message
from backend.db import get_recent_issues, get_urgent_issues
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("Report an Issue", callback_data='report')],
        [InlineKeyboardButton("Recent Issues", callback_data='recent'),
         InlineKeyboardButton("Urgent Issues", callback_data='urgent')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Welcome to Voice of the Streets! 🇱🇰\n\n"
        "I help communities in Sri Lanka report and track local issues. "
        "You can report problems, upvote existing ones, and check for updates.\n\n"
        "How can I assist you today?",
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a help message when the command /help is issued."""
    help_text = (
        "🌟 *Voice of the Streets - Help Guide* 🌟\n\n"
        "*How to report an issue:*\n"
        "Simply describe the problem, e.g., 'The street light on Church Road in Colombo is broken'\n\n"
        "*Commands:*\n"
        "• /start - Start the bot\n"
        "• /help - Show this help message\n"
        "• /recent - Show recent issues\n"
        "• /urgent - Show urgent issues\n\n"
        "*Actions:*\n"
        "• Upvote: 'upvote #123'\n"
        "• Suggest donation: 'suggest link for #123: https://example.com'\n"
        "• Get updates: 'update #123'\n\n"
        "Issues with 50+ votes are marked as URGENT ⚠️"
    )
    update.message.reply_text(help_text, parse_mode='Markdown')

def recent_issues(update: Update, context: CallbackContext) -> None:
    """Show recent issues when /recent command is issued."""
    issues = get_recent_issues(5)
    
    if not issues:
        update.message.reply_text("No issues have been reported yet. Be the first!")
        return
        
    response = "📋 *Recent Community Issues:*\n\n"
    
    for issue in issues:
        urgent = "⚠️ URGENT: " if issue.get('is_urgent') else ""
        votes = issue.get('vote_count', 0)
        response += f"{urgent}*#{issue['id']}*: {issue['description'][:50]}... "
        response += f"[{votes} votes]\n\n"
    
    keyboard = []
    for issue in issues:
        keyboard.append([
            InlineKeyboardButton(f"Upvote #{issue['id']}", callback_data=f"vote_{issue['id']}"),
            InlineKeyboardButton(f"Update #{issue['id']}", callback_data=f"update_{issue['id']}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

def urgent_issues(update: Update, context: CallbackContext) -> None:
    """Show urgent issues when /urgent command is issued."""
    issues = get_urgent_issues(5)
    
    if not issues:
        update.message.reply_text("There are no urgent issues at the moment. That's good news!")
        return
        
    response = "⚠️ *URGENT Community Issues:*\n\n"
    
    for issue in issues:
        votes = issue.get('vote_count', 0)
        response += f"*#{issue['id']}*: {issue['description'][:50]}... "
        response += f"[{votes} votes]\n\n"
    
    keyboard = []
    for issue in issues:
        keyboard.append([
            InlineKeyboardButton(f"Upvote #{issue['id']}", callback_data=f"vote_{issue['id']}"),
            InlineKeyboardButton(f"Update #{issue['id']}", callback_data=f"update_{issue['id']}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle button presses from inline keyboards."""
    query = update.callback_query
    query.answer()  # Answer the callback query
    
    data = query.data
    user_id = query.from_user.id
    
    if data == 'report':
        query.edit_message_text(text="Please describe the issue you want to report.")
    
    elif data == 'recent':
        issues = get_recent_issues(5)
        if not issues:
            query.edit_message_text(text="No issues have been reported yet. Be the first!")
            return
        
        response = "📋 *Recent Community Issues:*\n\n"
        for issue in issues:
            urgent = "⚠️ URGENT: " if issue.get('is_urgent') else ""
            votes = issue.get('vote_count', 0)
            response += f"{urgent}*#{issue['id']}*: {issue['description'][:50]}... "
            response += f"[{votes} votes]\n\n"
        
        keyboard = []
        for issue in issues:
            keyboard.append([
                InlineKeyboardButton(f"Upvote #{issue['id']}", callback_data=f"vote_{issue['id']}"),
                InlineKeyboardButton(f"Update #{issue['id']}", callback_data=f"update_{issue['id']}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=response, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif data == 'urgent':
        issues = get_urgent_issues(5)
        if not issues:
            query.edit_message_text(text="There are no urgent issues at the moment. That's good news!")
            return
        
        response = "⚠️ *URGENT Community Issues:*\n\n"
        for issue in issues:
            votes = issue.get('vote_count', 0)
            response += f"*#{issue['id']}*: {issue['description'][:50]}... "
            response += f"[{votes} votes]\n\n"
        
        keyboard = []
        for issue in issues:
            keyboard.append([
                InlineKeyboardButton(f"Upvote #{issue['id']}", callback_data=f"vote_{issue['id']}"),
                InlineKeyboardButton(f"Update #{issue['id']}", callback_data=f"update_{issue['id']}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=response, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif data.startswith('vote_'):
        issue_id = data.split('_')[1]
        response = process_message(f"upvote #{issue_id}", "telegram", str(user_id))
        query.edit_message_text(text=response)
    
    elif data.startswith('update_'):
        issue_id = data.split('_')[1]
        response = process_message(f"update #{issue_id}", "telegram", str(user_id))
        query.edit_message_text(text=response)

def handle_message(update: Update, context: CallbackContext) -> None:
    """Process user messages."""
    message = update.message.text
    user_id = update.message.from_user.id
    
    # Process the message
    response = process_message(message, "telegram", str(user_id))
    
    # Check if this might be a report (for issue reporting UX improvement)
    if "I've logged it as issue #" in response:
        issue_id = response.split("issue #")[1].split(".")[0]
        
        # Add upvote button
        keyboard = [
            [InlineKeyboardButton(f"Upvote Issue #{issue_id}", callback_data=f"vote_{issue_id}")],
            [InlineKeyboardButton("Report Another Issue", callback_data="report")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(response, reply_markup=reply_markup)
    else:
        update.message.reply_text(response)

def main() -> None:
    """Start the bot."""
    # Create the Updater with the bot token
    updater = Updater(os.getenv("TELEGRAM_TOKEN"))
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("recent", recent_issues))
    dp.add_handler(CommandHandler("urgent", urgent_issues))
    
    # Add callback query handler for inline keyboards
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # Add message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()