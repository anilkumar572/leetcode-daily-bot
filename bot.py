import requests
import smtplib
import os
import time
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

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
        "link": "https://leetcode.com" + data["link"],
        "title": q["title"],
        "difficulty": q["difficulty"],
        "tags": [t["name"] for t in q["topicTags"]],
        "examples": q["exampleTestcaseList"][:3],
        "content": q["content"],
    }


def generate_hints(problem):
    plain_content = re.sub(r"<[^>]+>", " ", problem["content"])

    prompt = (
        "You are a DSA mentor helping a developer prepare for FAANG interviews.\n\n"
        "Problem: " + problem["title"] + "\n"
        "Difficulty: " + problem["difficulty"] + "\n"
        "Tags: " + ", ".join(problem["tags"]) + "\n\n"
        "Problem statement:\n"
        + plain_content[:1500] +
        "\n\nGive exactly 3 progressive hints with no code and no spoilers.\n"
        "Format exactly like this:\n"
        "HINT 1: your hint here\n"
        "HINT 2: your hint here\n"
        "HINT 3: your hint here\n\n"
        "Do NOT give the solution or pseudocode."
    )

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
        },
        headers={
            "Authorization": "Bearer " + os.environ["GEMINI_API_KEY"],
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

DIFFICULTY_COLOR = {
    "Easy":   "#1EC677",
    "Medium": "#F59E0B",
    "Hard":   "#EF4444",
}

def build_email_html(problem, hints):
    diff_color = DIFFICULTY_COLOR.get(problem["difficulty"], "#6B7280")

    tags_html = ""
    for t in problem["tags"]:
        tags_html += (
            "<span style=\"display:inline-block;background:#EFF6FF;color:#1D4ED8;"
            "border-radius:20px;padding:3px 12px;font-size:12px;margin:3px 4px 3px 0;\">"
            + t + "</span>"
        )

    examples_html = ""
    for i, ex in enumerate(problem["examples"], 1):
        examples_html += (
            "<div style=\"background:#F8FAFC;border-left:3px solid #CBD5E1;"
            "padding:10px 14px;margin:8px 0;border-radius:0 6px 6px 0;"
            "font-family:monospace;font-size:13px;color:#374151;\">"
            "<strong>Case " + str(i) + ":</strong> " + ex + "</div>"
        )

    hints_html = ""
    for line in hints.split("\n"):
        if line.startswith("HINT"):
            parts = line.split(": ", 1)
            if len(parts) == 2:
                num = parts[0].strip()
                text = parts[1].strip()
                digit = num[-1]
                hints_html += (
                    "<div style=\"display:flex;gap:12px;align-items:flex-start;margin:12px 0;\">"
                    "<div style=\"min-width:28px;height:28px;background:#0B53A0;color:white;"
                    "border-radius:50%;text-align:center;line-height:28px;font-size:12px;font-weight:700;\">"
                    + digit +
                    "</div>"
                    "<p style=\"margin:4px 0;color:#374151;font-size:14px;line-height:1.6;\">" + text + "</p>"
                    "</div>"
                )

    date_fmt = datetime.strptime(problem["date"], "%Y-%m-%d").strftime("%B %d, %Y")

    html = (
        "<!DOCTYPE html><html><head><meta charset=\"UTF-8\"></head>"
        "<body style=\"margin:0;padding:0;background:#F1F5F9;font-family:Arial,sans-serif;\">"
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:#F1F5F9;padding:32px 16px;\">"
        "<tr><td align=\"center\">"
        "<table width=\"600\" cellpadding=\"0\" cellspacing=\"0\" style=\"max-width:600px;width:100%;\">"

        "<tr><td style=\"background:#0B53A0;border-radius:12px 12px 0 0;padding:28px 32px;\">"
        "<p style=\"margin:0;color:#93C5FD;font-size:12px;letter-spacing:2px;\">DAILY CHALLENGE - " + date_fmt + "</p>"
        "<h1 style=\"margin:8px 0 0;color:#FFFFFF;font-size:24px;font-weight:700;\">" + problem["title"] + "</h1>"
        "<div style=\"margin-top:12px;\">"
        "<span style=\"background:" + diff_color + ";color:white;padding:4px 14px;border-radius:20px;"
        "font-size:12px;font-weight:700;\">" + problem["difficulty"] + "</span>"
        "</div></td></tr>"

        "<tr><td style=\"background:#FFFFFF;padding:28px 32px;\">"

        "<h3 style=\"margin:0 0 10px;font-size:13px;color:#6B7280;\">TOPICS</h3>"
        "<div style=\"margin-bottom:24px;\">" + tags_html + "</div>"

        "<a href=\"" + problem["link"] + "\" style=\"display:inline-block;background:#0B53A0;color:white;"
        "text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;"
        "font-size:15px;margin-bottom:28px;\">Open Problem</a>"

        "<h3 style=\"margin:0 0 10px;font-size:13px;color:#6B7280;\">EXAMPLE TEST CASES</h3>"
        + examples_html +

        "<hr style=\"border:none;border-top:1px solid #E5E7EB;margin:24px 0;\">"

        "<h3 style=\"margin:0 0 16px;font-size:13px;color:#6B7280;\">AI HINTS - NO SPOILERS</h3>"
        + hints_html +

        "</td></tr>"

        "<tr><td style=\"background:#F8FAFC;border-radius:0 0 12px 12px;padding:16px 32px;"
        "border-top:1px solid #E5E7EB;text-align:center;\">"
        "<p style=\"margin:0;font-size:12px;color:#9CA3AF;\">LeetCode Daily Bot - Built for FAANG prep</p>"
        "</td></tr>"

        "</table></td></tr></table>"
        "</body></html>"
    )

    return html


def send_email(subject, html):
    sender   = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "LeetCode Daily Bot <" + sender + ">"
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("Email sent to " + recipient)


if __name__ == "__main__":
    print("Fetching daily problem...")
    problem = fetch_daily_problem()
    print("   -> " + problem["title"] + " (" + problem["difficulty"] + ")")

    print("Generating hints...")
    hints = generate_hints(problem)

    html = build_email_html(problem, hints)
    subject = "LeetCode Daily [" + problem["difficulty"] + "] - " + problem["title"]

    print("Sending email...")
    send_email(subject, html)
    print("Done!")
