# 🧩 LeetCode Daily Bot

Sends you the LeetCode Daily Challenge every morning via email — with difficulty, tags, example test cases, and AI-generated hints (no spoilers).

---

## 📦 What's inside

```
leetcode-daily-bot/
├── bot.py                        # main script
└── .github/workflows/daily.yml  # GitHub Actions cron job
```

---

## 🚀 Setup (5 minutes)

### 1. Fork / push to GitHub
Create a new GitHub repo and push this folder to it.

### 2. Get your API keys

| Key | How to get |
|-----|-----------|
| `GEMINI_API_KEY` | https://aistudio.google.com → **Get API Key** → free, no card needed |
| `EMAIL_SENDER` | Your Gmail address |
| `EMAIL_APP_PASSWORD` | Gmail → Settings → Security → **2-Step Verification ON** → **App Passwords** → create one for "Mail" |
| `EMAIL_RECIPIENT` | Where you want to receive emails (can be same Gmail) |

> ⚠️ Use an **App Password**, not your real Gmail password.

### 3. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add all four secrets:
- `GEMINI_API_KEY`
- `EMAIL_SENDER`
- `EMAIL_APP_PASSWORD`
- `EMAIL_RECIPIENT`

### 4. Enable GitHub Actions

Go to the **Actions** tab in your repo and enable workflows if prompted.

---

## ⏰ Schedule

The bot runs every day at **7:00 AM IST** automatically.

To test it manually: **Actions → LeetCode Daily Bot → Run workflow**

---

## ✉️ What the email looks like

- 📌 Problem title + difficulty badge (color-coded)
- 🏷️ Topic tags
- 🔗 Direct link to problem
- 🧪 Example test cases
- 🧠 3 progressive AI hints (no code, no spoilers)

---

## 🛠️ Customization

| What | Where |
|------|-------|
| Change send time | Edit `cron` in `daily.yml` (use [crontab.guru](https://crontab.guru)) |
| Change hint style | Edit the prompt inside `generate_hints()` in `bot.py` |
| Add Java boilerplate | Extend `build_email_html()` to fetch starter code |
