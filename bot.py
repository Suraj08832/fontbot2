import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from font_generator import generate_consistent_style, get_available_styles
from style_sets import STYLE_SETS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user data
user_data = {}

def create_style_keyboard(text: str, page: int = 0) -> InlineKeyboardMarkup:
    """Create a keyboard with style buttons showing styled text"""
    styles = list(STYLE_SETS.keys())
    styles_per_page = 25
    start_idx = page * styles_per_page
    end_idx = start_idx + styles_per_page
    current_styles = styles[start_idx:end_idx]
    
    keyboard = []
    row = []
    
    for style in current_styles:
        # Generate styled text for the button
        styled_text = generate_consistent_style(text, style)
        # Limit button text length to 20 characters
        button_text = styled_text[:20] + '...' if len(styled_text) > 20 else styled_text
        row.append(InlineKeyboardButton(button_text, callback_data=f"style_{style}"))
        
        if len(row) == 5:  # 5 buttons per row
            keyboard.append(row)
            row = []
    
    if row:  # Add any remaining buttons
        keyboard.append(row)
    
    # Add navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"page_{page-1}"))
    if end_idx < len(styles):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to Stylish Text Generator Bot!\n\n"
        "Send me any text and I'll show you different style options.\n"
        "Tap on any style to copy it directly!"
    )
    await update.message.reply_text(welcome_message)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Store user text and reset page
    user_data[user_id] = {'text': text, 'page': 0}
    
    # Create keyboard with first page of styles
    keyboard = create_style_keyboard(text)
    await update.message.reply_text(
        "Choose a style:",
        reply_markup=keyboard
    )

async def handle_style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle style selection and pagination."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in user_data:
        await query.edit_message_text("Please send a text first!")
        return
    
    data = query.data
    if data.startswith("page_"):
        # Handle pagination
        page = int(data.split("_")[1])
        user_data[user_id]['page'] = page
        keyboard = create_style_keyboard(user_data[user_id]['text'], page)
        await query.edit_message_reply_markup(reply_markup=keyboard)
    else:
        # Handle style selection
        style = data.split("_")[1]
        text = user_data[user_id]['text']
        styled_text = generate_consistent_style(text, style)
        
        # Create back button
        keyboard = [[InlineKeyboardButton("⬅️ Back to Styles", callback_data=f"page_{user_data[user_id]['page']}")]]
        
        # Send styled text with back button
        await query.edit_message_text(
            f"Here's your text in {style} style:\n\n`{styled_text}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

def main() -> None:
    """Start the bot."""
    # Create the Application with hardcoded token
    application = Application.builder().token("7877213016:AAE7cFaUyD8wPFF1PkzNcjvcy9gr0nGuA0c").build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_style_selection))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()