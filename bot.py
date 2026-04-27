import requests
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ── LeetCode GraphQL ──────────────────────────────────────────────────────────

LEETCODE_GQL = "https://leetcode.com/graphql"

DAILY_QUERY = """
query {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      title
      difficulty
      topicTags { name }
      exampleTestcaseList
      content
    }
  }
}
"""

def fetch_daily_problem():
    resp = requests.post(
        LEETCODE_GQL,
        json={"query": DAILY_QUERY},
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()["data"]["activeDailyCodingChallengeQuestion"]
    q = data["question"]
    return {
        "date": data["date"],
        "link": f"https://leetcode.com{data['link']}",
        "title": q["title"],
        "difficulty": q["difficulty"],
        "tags": [t["name"] for t in q["topicTags"]],
        "examples": q["exampleTestcaseList"][:3],   # first 3 test cases
        "content": q["content"],                    # raw HTML (for hint gen)
    }


# ── Gemini API for hints (free tier) ──────────────────────────────────────────

def generate_hints(problem: dict) -> str:
    import re
    plain_content = re.sub(r"<[^>]+>", " ", problem["content"])   # strip HTML

    prompt = f"""You are a DSA mentor helping a developer prepare for FAANG interviews.

Problem: {problem['title']}
Difficulty: {problem['difficulty']}
Tags: {', '.join(problem['tags'])}

Problem statement (truncated):
{plain_content[:1500]}

Give exactly 3 progressive hints (no code, no spoilers):
1. A high-level intuition nudge (1-2 sentences)
2. The key data structure or algorithm family to consider (1-2 sentences)
3. A subtle edge case or optimization to think about (1-2 sentences)

Format as:
HINT 1: ...
HINT 2: ...
HINT 3: ...

Do NOT give the solution or pseudocode."""

    gemini_key = os.environ["GEMINI_API_KEY"]
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={gemini_key}"
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


# ── Email HTML builder ─────────────────────────────────────────────────────────

DIFFICULTY_COLOR = {
    "Easy":   "#1EC677",
    "Medium": "#F59E0B",
    "Hard":   "#EF4444",
}

def build_email_html(problem: dict, hints: str) -> str:
    diff_color = DIFFICULTY_COLOR.get(problem["difficulty"], "#6B7280")
    tags_html = "".join(
        f'<span style="display:inline-block;background:#EFF6FF;color:#1D4ED8;'
        f'border-radius:20px;padding:3px 12px;font-size:12px;margin:3px 4px 3px 0;'
        f'font-family:\'Courier New\',monospace;">{t}</span>'
        for t in problem["tags"]
    )

    examples_html = ""
    for i, ex in enumerate(problem["examples"], 1):
        examples_html += (
            f'<div style="background:#F8FAFC;border-left:3px solid #CBD5E1;'
            f'padding:10px 14px;margin:8px 0;border-radius:0 6px 6px 0;'
            f'font-family:\'Courier New\',monospace;font-size:13px;color:#374151;">'
            f'<strong>Case {i}:</strong> {ex}</div>'
        )

    hint_lines = hints.split("\n")
    hints_html = ""
    for line in hint_lines:
        if line.startswith("HINT"):
            num, _, text = line.partition(": ")
            hints_html += (
                f'<div style="display:flex;gap:12px;align-items:flex-start;margin:12px 0;">'
                f'<div style="min-width:28px;height:28px;background:#0B53A0;color:white;'
                f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
                f'font-size:12px;font-weight:700;line-height:28px;text-align:center;">'
                f'{num[-1]}</div>'
                f'<p style="margin:4px 0;color:#374151;font-size:14px;line-height:1.6;">{text}</p>'
                f'</div>'
            )

    date_fmt = datetime.strptime(problem["date"], "%Y-%m-%d").strftime("%B %d, %Y")

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;padding:32px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

        <!-- Header -->
        <tr><td style="background:#0B53A0;border-radius:12px 12px 0 0;padding:28px 32px;">
          <p style="margin:0;color:#93C5FD;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Daily Challenge · {date_fmt}</p>
          <h1 style="margin:8px 0 0;color:#FFFFFF;font-size:24px;font-weight:700;">{problem['title']}</h1>
          <div style="margin-top:12px;">
            <span style="background:{diff_color};color:white;padding:4px 14px;border-radius:20px;
              font-size:12px;font-weight:700;letter-spacing:1px;">{problem['difficulty']}</span>
          </div>
        </td></tr>

        <!-- Body -->
        <tr><td style="background:#FFFFFF;padding:28px 32px;">

          <!-- Tags -->
          <h3 style="margin:0 0 10px;font-size:13px;color:#6B7280;text-transform:uppercase;letter-spacing:1px;">Topics</h3>
          <div style="margin-bottom:24px;">{tags_html}</div>

          <!-- CTA -->
          <a href="{problem['link']}" style="display:inline-block;background:#0B53A0;color:white;
            text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;
            font-size:15px;margin-bottom:28px;">Open Problem →</a>

          <!-- Examples -->
          <h3 style="margin:0 0 10px;font-size:13px;color:#6B7280;text-transform:uppercase;letter-spacing:1px;">Example Test Cases</h3>
          {examples_html}

          <!-- Divider -->
          <hr style="border:none;border-top:1px solid #E5E7EB;margin:24px 0;">

          <!-- Hints -->
          <h3 style="margin:0 0 16px;font-size:13px;color:#6B7280;text-transform:uppercase;letter-spacing:1px;">🧠 AI Hints (No Spoilers)</h3>
          {hints_html}

        </td></tr>

        <!-- Footer -->
        <tr><td style="background:#F8FAFC;border-radius:0 0 12px 12px;padding:16px 32px;
          border-top:1px solid #E5E7EB;text-align:center;">
          <p style="margin:0;font-size:12px;color:#9CA3AF;">LeetCode Daily Bot · Built for FAANG prep 🎯</p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Send email ─────────────────────────────────────────────────────────────────

def send_email(subject: str, html: str):
    sender    = os.environ["EMAIL_SENDER"]       # your Gmail
    password  = os.environ["EMAIL_APP_PASSWORD"]  # Gmail App Password
    recipient = os.environ["EMAIL_RECIPIENT"]    # where to receive

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"LeetCode Daily Bot <{sender}>"
    msg["To"]      = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
    print(f" Email sent to {recipient}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching daily problem...")
    problem = fetch_daily_problem()
    print(f"   → {problem['title']} ({problem['difficulty']})")

    print("Generating hints...")
    hints = generate_hints(problem)

    html = build_email_html(problem, hints)
    subject = f" LeetCode Daily [{problem['difficulty']}] — {problem['title']}"

    print(" Sending email...")
    send_email(subject, html)
