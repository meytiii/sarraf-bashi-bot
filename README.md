**TL;DR:** Here is your updated, fully tailored `README.md` containing your exact repository URL, GitHub organization name, and official Telegram bot handle.

You can overwrite your current repository file with this text to ensure all paths and installation instructions line up perfectly with your deployment setup.

---

### New `README.md` Code

# 🎨 Code Picasso (@CodePicasso_bot)

`Code Picasso` is an automated, zero-cost Telegram bot that transforms ugly, raw code blocks shared in chats into beautifully syntax-highlighted carbon-copy images. It operates completely locally without external paid APIs, making it highly efficient and lightweight.

---

## ✨ Features
* **Zero API Costs:** Runs completely locally using native Python engines.
* **Smart Auto-Detection:** Automatically infers the programming language of incoming snippets.
* **Beautiful Presentations:** Renders code blocks inside an elegant dark-mode canvas with clean shadow profiling.
* **Mobile Friendly:** Converts low-readability mono text blocks into crisp images optimized for small screens.

---

## 🛠️ Built With
* [Python 3.10+](https://www.python.org/)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Bot API framework
* [Pygments](https://pygments.org/) - Code syntax compiler
* [Playwright](https://playwright.dev/python/) - Headless browser engine for image snapshots

---

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/acantgemini-oss/codepicasso_tgbot.git](https://github.com/acantgemini-oss/codepicasso_tgbot.git)
   cd codepicasso_tgbot



2. **Install requirements & browser binaries:**
```bash
pip install -r requirements.txt
playwright install chromium

```


3. **Set your Environment Token:**
Create an environment variable or place your token directly into your runtime configuration:
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"

```


4. **Run the bot:**
```bash
python bot.py

```



---

## 📦 Cloud Deployment Guide

When deploying to automated container-building hosting services (like your build platform):

1. Link your GitHub repository `acantgemini-oss/codepicasso_tgbot` to the provider.
2. Set the **Build Command** to ensure your headless engine dependencies are pulled down successfully:
```bash
pip install -r requirements.txt && playwright install chromium

```


3. Set the **Start/Runtime Command**:
```bash
python bot.py

```


4. Add your `TELEGRAM_BOT_TOKEN` under the platform's **Environment Variables / Config Vars** section.

---

👨‍💻 Maintained by [@acantgemini-oss](https://github.com/acantgemini-oss) | Try it out on Telegram: [@CodePicasso_bot](https://www.google.com/search?q=https://t.me/CodePicasso_bot)

```

---

Now that the repository profile is updated, are you ready to write the core `bot.py` listener file for **Phase 3**?

```
