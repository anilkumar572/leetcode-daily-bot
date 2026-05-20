# LeetCode Daily Bot 

Sends you the LeetCode Daily Challenge every morning via email with difficulty, tags, example test cases, and AI-generated hints (no spoilers). Completely free to run.

---

## What's inside

```
leetcode-daily-bot/
├── bot.py                       # main script
└── .github/workflows/daily.yml  # GitHub Actions cron job (runs free)
```

---

## Setup (5 minutes)

### 1. Fork this repo

Click the **Fork** button at the top right of this page. No need to clone anything.

### 2. Get your free API keys

| Secret | How to get |
|--------|-----------|
| `GROQ_API_KEY` | Go to [console.groq.com](https://console.groq.com) and sign up for free. No card needed. Then go to API Keys and create one. |
| `EMAIL_SENDER` | Your Gmail address |
| `EMAIL_APP_PASSWORD` | Go to [myaccount.google.com](https://myaccount.google.com) in Chrome. Click Security. Turn on 2-Step Verification if not already on. Search for App Passwords at the top. Create one named "leetcode bot" and copy the 16-character password. |
| `EMAIL_RECIPIENT` | Where you want to receive the email. Can be the same Gmail address. |

### 3. Add GitHub Secrets

Go to your forked repo on GitHub:

Settings -> Secrets and variables -> Actions -> New repository secret

Add all four secrets:
- `GROQ_API_KEY`
- `EMAIL_SENDER`
- `EMAIL_APP_PASSWORD`
- `EMAIL_RECIPIENT`

### 4. Enable GitHub Actions

Go to the Actions tab in your forked repo and click "I understand my workflows, enable them".

### 5. Test it

Actions -> LeetCode Daily Bot -> Run workflow -> Run workflow

Check your inbox. Email should arrive within 30 seconds.

---

## Schedule

Runs every day at 7:00 AM IST automatically. GitHub Actions is free for public repos so there is no cost.

---

## What the email includes

- Problem title with color-coded difficulty badge (green / orange / red)
- Topic tags (Array, DP, Graph, etc.)
- Direct link to open the problem on LeetCode
- Example test cases
- 3 progressive AI hints with no spoilers and no code

---

## Customization

| What to change | Where |
|----------------|-------|
| Send time | Edit the cron value in daily.yml. Use crontab.guru to build your schedule. |
| Hint style | Edit the prompt inside generate_hints() in bot.py |
| AI model | Change the model name in generate_hints(). Groq supports llama-3.3-70b-versatile, mixtral-8x7b-32768, and more. |
| Language for hints | Add "Reply in Hindi" or your preferred language at the end of the prompt |

---

## Stack

- LeetCode GraphQL API for fetching the daily problem
- Groq API (free) with Llama 3.3 70B for AI hints
- Gmail SMTP for sending the email
- GitHub Actions for free daily scheduling

---

## Contributing

Pull requests are welcome. If you find a bug or want to add a feature, open an issue first.

---

## License

MIT
