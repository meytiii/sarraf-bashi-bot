import os
import sys
import html
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from renderer import generate_code_image

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("CRITICAL ERROR: 'TELEGRAM_BOT_TOKEN' environment variable is missing!")
    sys.exit(1)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎨 *Welcome to Code Picasso!*\n\n"
        "I transform your raw source code into clean, beautiful, syntax-highlighted snapshot images.\n\n"
        "📥 *How to use me:*\n"
        "Simply send or forward any code text directly to this chat. "
        "Normal plain text or markdown blocks work flawlessly!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💡 *Code Picasso Formatting Guide*\n\n"
        "Just paste your code snippet. My backend automatically analyzes the structure to detect the correct language style!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def theme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🦇 Dracula", callback_data="theme_dracula"),
            InlineKeyboardButton("🌌 Nord", callback_data="theme_nord")
        ],
        [
            InlineKeyboardButton("🎨 Monokai", callback_data="theme_monokai"),
            InlineKeyboardButton("☀️ GitHub Light", callback_data="theme_github")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Choose your preferred syntax highlighting theme:*\n\n"
        "(This will be saved for your future snippets)", 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code_content = update.message.text or update.message.caption
    if not code_content:
        return

    context.user_data['snippet'] = code_content

    keyboard = [
        [
            InlineKeyboardButton("🖼️ Image Canvas", callback_data="render_image"),
            InlineKeyboardButton("📝 Clean Text", callback_data="render_text")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✨ *Snippet received!* How would you like to format this?", 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Listens for button clicks and processes the saved snippet accordingly."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("theme_"):
        selected_theme = query.data.split("_")[1]
        context.user_data['theme'] = selected_theme
        await query.edit_message_text(f"🎨 Theme successfully changed to: *{selected_theme.capitalize()}*", parse_mode="Markdown")
        return

    code_content = context.user_data.get('snippet')
    
    if not code_content:
        await query.edit_message_text("❌ Snippet expired from memory. Please send the code again.")
        return

    if query.data == "render_image":
        await query.edit_message_text("🖌️ *Painting your code canvas... Please wait.*", parse_mode="Markdown")
        
        user_theme = context.user_data.get('theme', 'monokai')
        
        try:
            image_buffer = await generate_code_image(code_content, theme=user_theme)
            
            if image_buffer:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=image_buffer, 
                    caption="✨ *Rendered by Code Picasso* (@CodePicasso\\_bot)",
                    parse_mode="Markdown"
                )
                await query.message.delete()
            else:
                await query.edit_message_text("❌ Failed to render code block canvas cleanly.")
        except Exception as e:
            print(f"Error handling request: {e}")
            await query.edit_message_text("⚠️ A system framework rendering issue occurred.")

    elif query.data == "render_text":
        safe_code = html.escape(code_content)
        formatted_text = f"<pre><code>{safe_code}</code></pre>"
        await query.edit_message_text(formatted_text, parse_mode="HTML")

async def main_async():
    print("Starting Code Picasso Bot runtime...")
    app = Application.builder().token(TOKEN).read_timeout(30.0).write_timeout(30.0).connect_timeout(30.0).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("theme", theme_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Code Picasso is live and listening...")
    
    await app.initialize()
    await app.updater.start_polling()
    await app.start()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        print("Stopping bot...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()