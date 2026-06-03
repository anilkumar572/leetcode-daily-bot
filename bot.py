import requests
import smtplib
import os
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
      questionFrontendId
      title
      difficulty
      topicTags { name }
      exampleTestcaseList
      content
      hints
      stats
      similarQuestions
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

    import json
    stats = {}
    try:
        stats = json.loads(q.get("stats", "{}"))
    except Exception:
        pass

    similar = []
    try:
        similar = json.loads(q.get("similarQuestions", "[]"))
    except Exception:
        pass

    return {
        "date": data["date"],
        "link": "https://leetcode.com" + data["link"],
        "question_id": q.get("questionFrontendId", ""),
        "title": q["title"],
        "difficulty": q["difficulty"],
        "tags": [t["name"] for t in q["topicTags"]],
        "examples": q["exampleTestcaseList"][:3],
        "content": q["content"],
        "hints": q.get("hints", []),
        "stats": stats,
        "similar_questions": similar[:4],
    }


PREREQ_MAP = {
    "Array":                  ["Index-based iteration", "Two pointers", "Prefix sums"],
    "String":                 ["Character arrays", "String hashing", "Sliding window"],
    "Hash Table":             ["Hash functions", "Collision handling", "Python dict / Java HashMap"],
    "Dynamic Programming":    ["Recursion & memoization", "Subproblem decomposition", "Bottom-up tabulation"],
    "Math":                   ["Modular arithmetic", "GCD / LCM", "Prime sieve"],
    "Sorting":                ["Comparison-based sorts", "Counting sort", "Custom comparators"],
    "Greedy":                 ["Interval scheduling", "Proof of optimality", "Priority queues"],
    "Depth-First Search":     ["Recursion stack", "Graph adjacency list", "Visited tracking"],
    "Breadth-First Search":   ["Queue (deque)", "Level-order traversal", "Shortest path (unweighted)"],
    "Binary Search":          ["Sorted arrays", "Monotonic predicates", "Left / right boundary templates"],
    "Tree":                   ["Recursion on nodes", "In/pre/post-order traversal", "BST properties"],
    "Graph":                  ["Adjacency list/matrix", "Connected components", "Cycle detection"],
    "Stack":                  ["LIFO operations", "Monotonic stack pattern", "Expression evaluation"],
    "Queue":                  ["FIFO operations", "Sliding window maximum", "BFS queue"],
    "Heap (Priority Queue)":  ["Min/max heap ops", "Heapify", "K-th largest element"],
    "Two Pointers":           ["Sorted array techniques", "Fast/slow pointer", "Collision detection"],
    "Sliding Window":         ["Fixed vs variable window", "Character frequency maps", "Max/min in window"],
    "Backtracking":           ["Decision trees", "Pruning conditions", "Permutations / combinations"],
    "Bit Manipulation":       ["AND / OR / XOR / NOT", "Bit shifting", "Bitmask DP"],
    "Linked List":            ["Node & pointer concepts", "Dummy head pattern", "Floyd's cycle detection"],
    "Binary Tree":            ["Tree height & depth", "Lowest common ancestor", "Path problems"],
    "Binary Search Tree":     ["BST insertion/deletion", "Inorder = sorted", "Range queries"],
    "Trie":                   ["Trie node structure", "Insert & search", "Prefix compression"],
    "Segment Tree":           ["Range queries & updates", "Lazy propagation", "Build in O(n)"],
    "Union Find":             ["Root finding with path compression", "Union by rank", "Connected components"],
    "Divide and Conquer":     ["Merge sort template", "Master theorem", "Subproblem merging"],
    "Recursion":              ["Base cases", "Call stack intuition", "Tree/list recursion"],
    "Simulation":             ["Step-by-step state tracking", "Grid navigation", "Modular arithmetic"],
    "Matrix":                 ["2-D indexing", "Spiral/diagonal traversal", "Grid DFS/BFS"],
    "Geometry":               ["Coordinate math", "Convex hull", "Area / distance formulas"],
    "Number Theory":          ["Prime factorization", "Euler's totient", "Modular inverse"],
    "Probability and Statistics": ["Expected value", "Reservoir sampling", "Random algorithms"],
    "Data Stream":            ["Online algorithms", "Running median", "Sliding statistics"],
    "Design":                 ["OOP patterns", "LRU cache internals", "Hash + DLL combo"],
    "Iterator":               ["Lazy evaluation", "Generator pattern", "Pointer advancement"],
    "Monotonic Stack":        ["Next greater element", "Stock span", "Histogram problems"],
    "Monotonic Queue":        ["Deque sliding window", "Max/min in window", "BFS + queue"],
    "String Matching":        ["KMP algorithm", "Rabin-Karp rolling hash", "Z-function"],
    "Topological Sort":       ["DAG properties", "Kahn's BFS algorithm", "DFS post-order"],
    "Shortest Path":          ["Dijkstra's algorithm", "Bellman-Ford", "Floyd-Warshall"],
    "Minimum Spanning Tree":  ["Prim's algorithm", "Kruskal's algorithm", "Union-Find"],
    "Game Theory":            ["Nim game", "Sprague-Grundy theorem", "Minimax"],
    "Concurrency":            ["Thread synchronization", "Semaphore / mutex", "Condition variables"],
    "Interactive":            ["Binary search on hidden value", "Query budgeting", "Adaptive strategy"],
}

def get_prerequisites(tags):
    seen = set()
    prereqs = []
    for tag in tags:
        for p in PREREQ_MAP.get(tag, []):
            if p not in seen:
                seen.add(p)
                prereqs.append(p)
    return prereqs[:9]


def generate_ai_analysis(problem):
    plain_content = re.sub(r"<[^>]+>", " ", problem["content"])

    prompt = (
        "You are a senior FAANG engineer and DSA coach.\n\n"
        "Problem #" + problem["question_id"] + ": " + problem["title"] + "\n"
        "Difficulty: " + problem["difficulty"] + "\n"
        "Tags: " + ", ".join(problem["tags"]) + "\n\n"
        "Problem statement:\n" + plain_content[:2000] + "\n\n"
        "Respond in EXACTLY this format (no markdown, no extra text):\n\n"
        "APPROACH: <2-3 sentences on the optimal approach>\n"
        "TIME: <time complexity with brief reason>\n"
        "SPACE: <space complexity with brief reason>\n"
        "PATTERN: <the algorithmic pattern this represents>\n"
        "PITFALL: <one common mistake to avoid>\n"
        "HINT 1: <gentle nudge>\n"
        "HINT 2: <key insight>\n"
        "HINT 3: <how to structure the solution>\n"
    )

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
        },
        headers={
            "Authorization": "Bearer " + os.environ["GROQ_API_KEY"],
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()

    fields = {}
    for line in raw.split("\n"):
        if ": " in line:
            key, _, val = line.partition(": ")
            fields[key.strip()] = val.strip()

    hints = [fields.get("HINT 1", ""), fields.get("HINT 2", ""), fields.get("HINT 3", "")]

    return {
        "approach":  fields.get("APPROACH", ""),
        "time":      fields.get("TIME", ""),
        "space":     fields.get("SPACE", ""),
        "pattern":   fields.get("PATTERN", ""),
        "pitfall":   fields.get("PITFALL", ""),
        "hints":     [h for h in hints if h],
    }


DIFFICULTY_COLOR = {
    "Easy":   "#1EC677",
    "Medium": "#F59E0B",
    "Hard":   "#EF4444",
}

DIFFICULTY_BG = {
    "Easy":   "rgba(30,198,119,0.12)",
    "Medium": "rgba(245,158,11,0.12)",
    "Hard":   "rgba(239,68,68,0.12)",
}


def build_email_html(problem, analysis):
    diff_color = DIFFICULTY_COLOR.get(problem["difficulty"], "#6B7280")
    prereqs = get_prerequisites(problem["tags"])
    date_fmt = datetime.strptime(problem["date"], "%Y-%m-%d").strftime("%B %d, %Y")
    stats = problem["stats"]

    tags_html = ""
    for t in problem["tags"]:
        tags_html += (
            "<span style='display:inline-block;background:#EFF6FF;color:#1D4ED8;"
            "border-radius:20px;padding:3px 12px;font-size:12px;margin:3px 4px 3px 0;'>"
            + t + "</span>"
        )

    ac_rate = stats.get("acRate", "N/A")
    total_ac = stats.get("totalAccepted", "N/A")
    total_sub = stats.get("totalSubmission", "N/A")

    stats_html = (
        "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 24px;'><tr>"
        + "<td style='text-align:center;background:#F8FAFC;border-radius:8px;padding:12px 8px;border:1px solid #E5E7EB;'>"
        + "<p style='margin:0;font-size:11px;color:#9CA3AF;letter-spacing:1px;'>AC Rate</p>"
        + "<p style='margin:4px 0 0;font-size:18px;font-weight:700;color:#1E293B;'>" + str(ac_rate) + "</p></td>"
        + "<td style='width:8px;'></td>"
        + "<td style='text-align:center;background:#F8FAFC;border-radius:8px;padding:12px 8px;border:1px solid #E5E7EB;'>"
        + "<p style='margin:0;font-size:11px;color:#9CA3AF;letter-spacing:1px;'>Accepted</p>"
        + "<p style='margin:4px 0 0;font-size:18px;font-weight:700;color:#1E293B;'>" + str(total_ac) + "</p></td>"
        + "<td style='width:8px;'></td>"
        + "<td style='text-align:center;background:#F8FAFC;border-radius:8px;padding:12px 8px;border:1px solid #E5E7EB;'>"
        + "<p style='margin:0;font-size:11px;color:#9CA3AF;letter-spacing:1px;'>Submissions</p>"
        + "<p style='margin:4px 0 0;font-size:18px;font-weight:700;color:#1E293B;'>" + str(total_sub) + "</p></td>"
        + "</tr></table>"
    )

    examples_html = ""
    for i, ex in enumerate(problem["examples"], 1):
        examples_html += (
            "<div style='background:#F8FAFC;border-left:3px solid #CBD5E1;"
            "padding:10px 14px;margin:8px 0;border-radius:0 6px 6px 0;"
            "font-family:monospace;font-size:13px;color:#374151;'>"
            "<strong>Case " + str(i) + ":</strong> " + ex + "</div>"
        )

    prereqs_html = ""
    if prereqs:
        for p in prereqs:
            prereqs_html += (
                "<span style='display:inline-block;background:#FEF3C7;color:#92400E;"
                "border-radius:6px;padding:4px 10px;font-size:12px;margin:3px 4px 3px 0;'>"
                "&#10003; " + p + "</span>"
            )
    else:
        prereqs_html = "<span style='color:#9CA3AF;font-size:13px;'>No specific prerequisites.</span>"

    approach_html = ""
    if analysis.get("approach"):
        approach_html = (
            "<div style='background:#F0F9FF;border-radius:8px;padding:16px 20px;margin:0 0 16px;'>"
            "<p style='margin:0;color:#0C4A6E;font-size:14px;line-height:1.7;'>"
            + analysis["approach"] + "</p></div>"
        )

    complexity_html = ""
    if analysis.get("time") or analysis.get("space"):
        complexity_html = (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 20px;'><tr>"
            + "<td style='background:#EFF6FF;border-radius:8px;padding:12px 14px;vertical-align:top;border:1px solid rgba(0,0,0,0.04);'>"
            + "<p style='margin:0;font-size:11px;color:#1D4ED8;font-weight:700;letter-spacing:1px;'>&#9201; Time</p>"
            + "<p style='margin:4px 0 0;font-size:13px;color:#1E293B;line-height:1.5;'>" + analysis.get("time", "N/A") + "</p></td>"
            + "<td style='width:8px;'></td>"
            + "<td style='background:#F0FDF4;border-radius:8px;padding:12px 14px;vertical-align:top;border:1px solid rgba(0,0,0,0.04);'>"
            + "<p style='margin:0;font-size:11px;color:#166534;font-weight:700;letter-spacing:1px;'>&#129504; Space</p>"
            + "<p style='margin:4px 0 0;font-size:13px;color:#1E293B;line-height:1.5;'>" + analysis.get("space", "N/A") + "</p></td>"
            + "</tr></table>"
        )

    pattern_html = ""
    if analysis.get("pattern"):
        pattern_html = (
            "<div style='display:flex;align-items:center;gap:10px;margin:0 0 20px;"
            "background:#FAF5FF;border-radius:8px;padding:12px 16px;'>"
            "<span style='font-size:18px;'>&#128260;</span>"
            "<div><p style='margin:0;font-size:11px;color:#7C3AED;font-weight:700;"
            "letter-spacing:1px;'>ALGORITHMIC PATTERN</p>"
            "<p style='margin:2px 0 0;font-size:14px;color:#4C1D95;font-weight:600;'>"
            + analysis["pattern"] + "</p></div></div>"
        )

    pitfall_html = ""
    if analysis.get("pitfall"):
        pitfall_html = (
            "<div style='display:flex;align-items:flex-start;gap:10px;margin:0 0 20px;"
            "background:#FFF7ED;border-radius:8px;padding:12px 16px;'>"
            "<span style='font-size:18px;'>&#9888;&#65039;</span>"
            "<div><p style='margin:0;font-size:11px;color:#C2410C;font-weight:700;"
            "letter-spacing:1px;'>COMMON PITFALL</p>"
            "<p style='margin:4px 0 0;font-size:13px;color:#7C2D12;line-height:1.6;'>"
            + analysis["pitfall"] + "</p></div></div>"
        )

    hints_html = ""
    for i, hint in enumerate(analysis.get("hints", []), 1):
        hints_html += (
            "<div style='display:flex;gap:12px;align-items:flex-start;margin:12px 0;'>"
            "<div style='min-width:28px;height:28px;background:#0B53A0;color:white;"
            "border-radius:50%;text-align:center;line-height:28px;font-size:12px;font-weight:700;'>"
            + str(i) +
            "</div>"
            "<p style='margin:4px 0;color:#374151;font-size:14px;line-height:1.6;'>" + hint + "</p>"
            "</div>"
        )

    similar_html = ""
    for sq in problem.get("similar_questions", []):
        sq_diff = sq.get("difficulty", "")
        sq_color = DIFFICULTY_COLOR.get(sq_diff, "#6B7280")
        similar_html += (
            "<div style='display:flex;justify-content:space-between;align-items:center;"
            "padding:8px 0;border-bottom:1px solid #F1F5F9;'>"
            "<span style='font-size:13px;color:#374151;'>" + sq.get("title", "") + "</span>"
            "<span style='font-size:11px;font-weight:700;color:" + sq_color + ";'>"
            + sq_diff + "</span></div>"
        )

    similar_section = ""
    if similar_html:
        similar_section = (
            "<hr style='border:none;border-top:1px solid #E5E7EB;margin:24px 0;'>"
            "<h3 style='margin:0 0 12px;font-size:13px;color:#6B7280;letter-spacing:1px;'>SIMILAR PROBLEMS</h3>"
            + similar_html
        )

    html = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'></head>"
        "<body style='margin:0;padding:0;background:#F1F5F9;font-family:Arial,sans-serif;'>"
        "<table width='100%' cellpadding='0' cellspacing='0' style='background:#F1F5F9;padding:32px 16px;'>"
        "<tr><td align='center'>"
        "<table width='600' cellpadding='0' cellspacing='0' style='max-width:600px;width:100%;'>"

        "<tr><td style='background:#0B53A0;border-radius:12px 12px 0 0;padding:28px 32px;'>"
        "<p style='margin:0;color:#93C5FD;font-size:11px;letter-spacing:2px;'>DAILY CHALLENGE &#183; " + date_fmt + "</p>"
        "<div style='display:flex;align-items:baseline;gap:10px;margin-top:6px;'>"
        "<span style='background:rgba(255,255,255,0.15);color:#E0F2FE;border-radius:6px;"
        "padding:2px 10px;font-size:13px;font-weight:700;'>#" + str(problem["question_id"]) + "</span>"
        "<h1 style='margin:0;color:#FFFFFF;font-size:22px;font-weight:700;'>" + problem["title"] + "</h1>"
        "</div>"
        "<div style='margin-top:12px;display:flex;gap:8px;align-items:center;'>"
        "<span style='background:" + diff_color + ";color:white;padding:4px 14px;"
        "border-radius:20px;font-size:12px;font-weight:700;'>" + problem["difficulty"] + "</span>"
        "</div>"
        "</td></tr>"

        "<tr><td style='background:#FFFFFF;padding:28px 32px;'>"

        + stats_html +

        "<h3 style='margin:0 0 10px;font-size:12px;color:#6B7280;letter-spacing:1px;'>TOPICS</h3>"
        "<div style='margin-bottom:24px;'>" + tags_html + "</div>"

        "<h3 style='margin:0 0 10px;font-size:12px;color:#6B7280;letter-spacing:1px;'>PREREQUISITES</h3>"
        "<div style='margin-bottom:24px;'>" + prereqs_html + "</div>"

        "<a href='" + problem["link"] + "' style='display:inline-block;background:#0B53A0;color:white;"
        "text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;"
        "font-size:15px;margin-bottom:28px;'>Open Problem &#8594;</a>"

        "<h3 style='margin:0 0 10px;font-size:12px;color:#6B7280;letter-spacing:1px;'>EXAMPLE TEST CASES</h3>"
        + examples_html +

        "<hr style='border:none;border-top:1px solid #E5E7EB;margin:24px 0;'>"

        "<h2 style='margin:0 0 16px;font-size:16px;color:#1E293B;font-weight:700;'>&#129513; In-Depth Analysis</h2>"

        + approach_html +
        + complexity_html +
        + pattern_html +
        + pitfall_html +

        "<hr style='border:none;border-top:1px solid #E5E7EB;margin:24px 0;'>"

        "<h3 style='margin:0 0 16px;font-size:12px;color:#6B7280;letter-spacing:1px;'>AI HINTS &#8212; NO SPOILERS</h3>"
        + hints_html +

        + similar_section +

        "</td></tr>"

        "<tr><td style='background:#F8FAFC;border-radius:0 0 12px 12px;padding:16px 32px;"
        "border-top:1px solid #E5E7EB;text-align:center;'>"
        "<p style='margin:0;font-size:12px;color:#9CA3AF;'>LeetCode Daily Bot &#183; FAANG Prep &#183; " + date_fmt + "</p>"
        "</td></tr>"

        "</table></td></tr></table>"
        "</body></html>"
    )

    return html


def send_email(subject, html):
    sender = os.environ["EMAIL_SENDER"]
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
    print("  -> #" + problem["question_id"] + " " + problem["title"] + " (" + problem["difficulty"] + ")")

    print("Generating AI analysis...")
    analysis = generate_ai_analysis(problem)

    html = build_email_html(problem, analysis)
    subject = ("LeetCode #" + problem["question_id"] + " [" + problem["difficulty"] + "] " + problem["title"])

    print("Sending email...")
    send_email(subject, html)
    print("Done!")
