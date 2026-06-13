import os
import sys
import html
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from renderer import generate_code_image, generate_math_image, detect_code_language

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("CRITICAL ERROR: 'TELEGRAM_BOT_TOKEN' environment variable is missing!")
    sys.exit(1)

# --- BILINGUAL DICTIONARY ---
TEXTS = {
    "en": {
        "welcome": "🎨 *Welcome to Code Picasso!*\n\nI transform your raw source code into clean, beautiful snapshot images.\n\n📥 *How to use me:*\nSimply send or forward any code text directly to this chat.",
        "help": "💡 *Code Picasso Formatting Guide*\n\nJust paste your code snippet. My backend automatically analyzes the structure!",
        "theme_prompt": "🎨 *Choose your preferred syntax highlighting theme:*\n\n(This will be saved for your future snippets)",
        "theme_changed": "🎨 Theme successfully changed to: *{}*",
        "received": "✨ *Snippet received!* How would you like to format this?",
        "btn_img": "🖼️ Image Canvas",
        "btn_txt": "📝 Clean Text",
        "btn_run": "▶️ Run Code (Live)",
        "btn_math": "🧮 Math / LaTeX",
        "btn_gist": "🚀 Push to Gist",
        "btn_explain": "🧠 Explain Code",
        "btn_preview": "🌐 Web Preview",
        "expired": "❌ Snippet expired from memory. Please send the code again.",
        "painting": "🖌️ *Painting your canvas... Please wait.*",
        "executing": "⚙️ *Executing your code in the cloud...*",
        "explaining": "🧠 *Analyzing code structure...*",
        "gist_creating": "🚀 *Pushing your code to GitHub Gist...*",
        "gist_success": "✅ *Gist created successfully!*\n🔗 [View on GitHub]({})",
        "gist_fail": "❌ Failed to create Gist on GitHub. Verify your GITHUB_TOKEN.",
        "fail_render": "❌ Failed to render canvas cleanly.",
        "sys_err": "⚠️ A system framework rendering issue occurred.",
        "exec_reject": "❌ Execution engine rejected the request.",
        "net_err": "⚠️ A network error occurred while reaching the execution engine.",
        "wm_help": "✍️ *Set your watermark!*\nSend `/watermark <your text>` to add a signature to your images.\nExample: `/watermark @meytiii`",
        "wm_set": "✅ Watermark set to: *{}*",
        "wm_clear": "✅ Watermark removed."
    },
    "fa": {
        "welcome": "🎨 *به Code Picasso خوش آمدید!*\n\nمن کدهای خام شما را به تصاویر زیبا و خوانا تبدیل می‌کنم.\n\n📥 *نحوه استفاده:*\nکافیست کد خود را مستقیماً در این چت ارسال یا فوروارد کنید.",
        "help": "💡 *راهنمای استفاده*\n\nکد خود را بفرستید. سرور من زبان آن را به صورت خودکار تشخیص می‌دهد!",
        "theme_prompt": "🎨 *تم رنگی دلخواه خود را انتخاب کنید:*\n\n(این انتخاب برای کدهای بعدی ذخیره می‌شود)",
        "theme_changed": "🎨 تم با موفقیت تغییر کرد به: *{}*",
        "received": "✨ *متن دریافت شد!* دوست دارید چگونه آن را فرمت کنم؟",
        "btn_img": "🖼️ تصویر کد",
        "btn_txt": "📝 متن ساده",
        "btn_run": "▶️ اجرای زنده کد",
        "btn_math": "🧮 فرمول ریاضی",
        "btn_gist": "🚀 ارسال به Gist",
        "btn_explain": "🧠 توضیح کد",
        "btn_preview": "🌐 پیش‌نمایش وب",
        "expired": "❌ داده‌ها از حافظه پاک شده‌اند. لطفاً دوباره ارسال کنید.",
        "painting": "🖌️ *در حال ساخت تصویر... لطفاً صبر کنید.*",
        "executing": "⚙️ *در حال اجرای کد شما در فضای ابری...*",
        "explaining": "🧠 *در حال تحلیل ساختار کد...*",
        "gist_creating": "🚀 *در حال ارسال کد به GitHub Gist...*",
        "gist_success": "✅ *Gist با موفقیت ساخته شد!*\n🔗 [مشاهده در گیت‌هاب]({})",
        "gist_fail": "❌ ساخت Gist با خطا مواجه شد. تنظیمات GITHUB_TOKEN را بررسی کنید.",
        "fail_render": "❌ ساخت تصویر با خطا مواجه شد.",
        "sys_err": "⚠️ خطای سیستمی رخ داد.",
        "exec_reject": "❌ موتور اجرا درخواست را رد کرد.",
        "net_err": "⚠️ خطای شبکه در ارتباط با موتور اجرا.",
        "wm_help": "✍️ *تنظیم واترمارک!*\nبرای افزودن امضا به تصاویر، از دستور `/watermark <متن>` استفاده کنید.\nمثال: `/watermark @meytiii`",
        "wm_set": "✅ واترمارک تنظیم شد: *{}*",
        "wm_clear": "✅ واترمارک حذف شد."
    }
}

def get_text(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    """Helper to fetch the correct string based on user's saved language."""
    lang = context.user_data.get('language', 'en')
    return TEXTS[lang].get(key, TEXTS['en'][key])

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts the user to select their interface language."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select your language / لطفاً زبان خود را انتخاب کنید:", 
        reply_markup=reply_markup
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'language' not in context.user_data:
        await language_command(update, context)
    else:
        await update.message.reply_text(get_text(context, "welcome"), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_text(context, "help"), parse_mode="Markdown")

async def theme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🦇 Dracula", callback_data="theme_dracula"),
            InlineKeyboardButton("🌌 Nord", callback_data="theme_nord")
        ],
        [
            InlineKeyboardButton("🎨 Monokai", callback_data="theme_monokai"),
            InlineKeyboardButton("☀️ GitHub", callback_data="theme_github")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(context, "theme_prompt"), reply_markup=reply_markup, parse_mode="Markdown")

async def watermark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'language' not in context.user_data:
        context.user_data['language'] = 'en'
        
    if not context.args:
        await update.message.reply_text(get_text(context, "wm_help"), parse_mode="Markdown")
        return
        
    wm_text = " ".join(context.args)
    if wm_text.lower() in ["off", "none", "clear", "حذف"]:
        context.user_data.pop('watermark', None)
        await update.message.reply_text(get_text(context, "wm_clear"))
    else:
        context.user_data['watermark'] = wm_text
        safe_text = html.escape(wm_text)
        await update.message.reply_text(get_text(context, "wm_set").format(safe_text), parse_mode="HTML")

async def handle_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code_content = update.message.text or update.message.caption
    if not code_content:
        return

    if 'language' not in context.user_data:
        context.user_data['language'] = 'en'

    piston_lang, lang_badge = await detect_code_language(code_content)
    context.user_data['snippet'] = code_content
    context.user_data['detected_lang'] = piston_lang

    base_received_msg = get_text(context, "received")
    badge_header = f"<b>{lang_badge}</b>\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(get_text(context, "btn_img"), callback_data="render_image"),
            InlineKeyboardButton(get_text(context, "btn_txt"), callback_data="render_text")
        ],
        [
            InlineKeyboardButton(get_text(context, "btn_run"), callback_data="run_code"),
            InlineKeyboardButton(get_text(context, "btn_math"), callback_data="render_math")
        ],
        [
            InlineKeyboardButton(get_text(context, "btn_gist"), callback_data="push_gist"),
            InlineKeyboardButton(get_text(context, "btn_explain"), callback_data="explain_code")
        ],
        [
            InlineKeyboardButton(get_text(context, "btn_preview"), callback_data="preview_web")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"{badge_header}{base_received_msg}", reply_markup=reply_markup, parse_mode="HTML")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("lang_"):
        selected_lang = query.data.split("_")[1]
        context.user_data['language'] = selected_lang
        await query.edit_message_text(get_text(context, "welcome"), parse_mode="Markdown")
        return

    if query.data.startswith("theme_"):
        selected_theme = query.data.split("_")[1]
        context.user_data['theme'] = selected_theme
        msg = get_text(context, "theme_changed").format(selected_theme.capitalize())
        await query.edit_message_text(msg, parse_mode="Markdown")
        return

    code_content = context.user_data.get('snippet')
    
    if not code_content:
        await query.edit_message_text(get_text(context, "expired"))
        return

    if query.data == "render_image":
        await query.edit_message_text(get_text(context, "painting"), parse_mode="Markdown")
        user_theme = context.user_data.get('theme', 'monokai')
        user_wm = context.user_data.get('watermark')
        try:
            image_buffer = await generate_code_image(code_content, theme=user_theme, watermark=user_wm)
            if image_buffer:
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=image_buffer)
                await query.message.delete()
            else:
                await query.edit_message_text(get_text(context, "fail_render"))
        except Exception as e:
            print(f"Error: {e}")
            await query.edit_message_text(get_text(context, "sys_err"))

    elif query.data == "render_math":
        await query.edit_message_text(get_text(context, "painting"), parse_mode="Markdown")
        try:
            image_buffer = await generate_math_image(code_content)
            if image_buffer:
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=image_buffer)
                await query.message.delete()
            else:
                await query.edit_message_text(get_text(context, "fail_render"))
        except Exception as e:
            print(f"Error: {e}")
            await query.edit_message_text(get_text(context, "sys_err"))

    elif query.data == "render_text":
        safe_code = html.escape(code_content)
        await query.edit_message_text(f"<pre><code>{safe_code}</code></pre>", parse_mode="HTML")

    elif query.data == "run_code":
        await query.edit_message_text(get_text(context, "executing"), parse_mode="Markdown")
        
        target_lang = context.user_data.get('detected_lang', 'python')
        
        if target_lang in ["text", "html", "css"]:
            await query.edit_message_text("❌ This format type cannot be executed directly in a terminal console.")
            return

        piston_url = "https://emkc.org/api/v2/piston/execute"
        payload = {"language": target_lang, "version": "*", "files": [{"content": code_content}]}
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(piston_url, json=payload)
            
            if response.status_code == 200:
                output = response.json().get("run", {}).get("output", "")
                if not output.strip():
                    output = "(Executed with no terminal output)"
                
                safe_output = html.escape(output[:3900])
                await query.edit_message_text(f"<b>💻 Terminal Output:</b>\n<pre>{safe_output}</pre>", parse_mode="HTML")
            else:
                await query.edit_message_text(get_text(context, "exec_reject"))
        except Exception as e:
            print(f"Execution Error: {e}")
            await query.edit_message_text(get_text(context, "net_err"))

    elif query.data == "explain_code":
        await query.edit_message_text(get_text(context, "explaining"), parse_mode="Markdown")
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            await query.edit_message_text("⚠️ GEMINI_API_KEY environment variable is missing on the server.")
            return
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            user_lang = context.user_data.get('language', 'en')
            lang_instruction = "Persian (فارسی)" if user_lang == 'fa' else "English"
            
            prompt = f"Explain the following code block clearly and concisely. Keep your explanation under 3 paragraphs. Respond exclusively in {lang_instruction}.\n\nCode:\n{code_content}"
            
            response = model.generate_content(prompt)
            safe_explanation = html.escape(response.text[:3900])
            
            await query.edit_message_text(f"<b>🧠 AI Explanation:</b>\n\n{safe_explanation}", parse_mode="HTML")
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            await query.edit_message_text(get_text(context, "sys_err"))

    elif query.data == "preview_web":
        await query.edit_message_text("🌐 *Rendering webpage preview...*", parse_mode="Markdown")
        try:
            from renderer import generate_web_snapshot
            image_buffer = await generate_web_snapshot(code_content)
            if image_buffer:
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=image_buffer)
                await query.message.delete()
            else:
                await query.edit_message_text(get_text(context, "fail_render"))
        except Exception as e:
            print(f"Error: {e}")
            await query.edit_message_text(get_text(context, "sys_err"))

    elif query.data == "push_gist":
        await query.edit_message_text(get_text(context, "gist_creating"), parse_mode="Markdown")
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            await query.edit_message_text("⚠️ GITHUB_TOKEN environment variable is not configured on the server.")
            return

        gist_payload = {
            "description": "Code Picasso Automated Snippet Shared via Telegram",
            "public": True,
            "files": {
                "snippet.py": {
                    "content": code_content
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post("https://api.github.com/gists", json=gist_payload, headers=headers)
                
            if response.status_code == 201:
                gist_url = response.json().get("html_url", "")
                success_msg = get_text(context, "gist_success").format(gist_url)
                await query.edit_message_text(success_msg, parse_mode="Markdown", disable_web_page_preview=False)
            else:
                print(f"GitHub Error Log: {response.status_code} - {response.text}")
                await query.edit_message_text(get_text(context, "gist_fail"))
        except Exception as e:
            print(f"Gist Exception: {e}")
            await query.edit_message_text(get_text(context, "net_err"))

async def main_async():
    print("Starting Code Picasso Bot runtime...")
    app = Application.builder().token(TOKEN).read_timeout(30.0).write_timeout(30.0).connect_timeout(30.0).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("theme", theme_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("watermark", watermark_command))
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