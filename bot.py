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
        "PSEUDOCODE: <4-7 lines of clean pseudocode showing the core logic, use | as line separator>\n"
        "HINT 1: <gentle nudge>\n"
        "HINT 2: <key insight>\n"
        "HINT 3: <how to structure the solution>\n"
    )

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 700,
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
        "approach":    fields.get("APPROACH", ""),
        "time":        fields.get("TIME", ""),
        "space":       fields.get("SPACE", ""),
        "pattern":     fields.get("PATTERN", ""),
        "pitfall":     fields.get("PITFALL", ""),
        "pseudocode":  fields.get("PSEUDOCODE", ""),
        "hints":       [h for h in hints if h],
    }


DIFFICULTY_COLOR = {
    "Easy":   "#1EC677",
    "Medium": "#F59E0B",
    "Hard":   "#EF4444",
}


def build_email_html(problem, analysis):
    diff_color = DIFFICULTY_COLOR.get(problem["difficulty"], "#6B7280")
    prereqs = get_prerequisites(problem["tags"])
    date_fmt = datetime.strptime(problem["date"], "%Y-%m-%d").strftime("%B %d, %Y")
    stats = problem["stats"]

    # --- tags ---
    tags_html = ""
    for t in problem["tags"]:
        tags_html += (
            "<span style='display:inline-block;background:#EFF6FF;color:#1D4ED8;"
            "border-radius:20px;padding:4px 13px;font-size:12px;font-weight:600;"
            "margin:3px 4px 3px 0;'>" + t + "</span>"
        )

    # --- stats row ---
    ac_rate  = stats.get("acRate", "N/A")
    total_ac = stats.get("totalAccepted", "N/A")
    total_sub = stats.get("totalSubmission", "N/A")

    def stat_cell(label, value):
        return (
            "<td style='text-align:center;background:#F8FAFC;border-radius:8px;"
            "padding:14px 8px;border:1px solid #E5E7EB;'>"
            "<p style='margin:0;font-size:11px;color:#9CA3AF;letter-spacing:1px;text-transform:uppercase;'>" + label + "</p>"
            "<p style='margin:6px 0 0;font-size:20px;font-weight:700;color:#1E293B;'>" + str(value) + "</p>"
            "</td>"
        )

    stats_html = (
        "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 20px;border-collapse:separate;border-spacing:8px 0;'><tr>"
        + stat_cell("AC Rate", ac_rate)
        + stat_cell("Accepted", total_ac)
        + stat_cell("Submissions", total_sub)
        + "</tr></table>"
    )

    # --- examples ---
    examples_html = ""
    for i, ex in enumerate(problem["examples"], 1):
        examples_html += (
            "<div style='background:#F8FAFC;border-left:3px solid #CBD5E1;"
            "padding:10px 14px;margin:6px 0;border-radius:0 6px 6px 0;"
            "font-family:monospace;font-size:13px;color:#374151;'>"
            "<strong>Case " + str(i) + ":</strong> " + ex + "</div>"
        )

    # --- prerequisites ---
    prereqs_html = ""
    if prereqs:
        for p in prereqs:
            prereqs_html += (
                "<span style='display:inline-block;background:#FEF3C7;color:#92400E;"
                "border-radius:6px;padding:4px 10px;font-size:12px;font-weight:600;"
                "margin:3px 4px 3px 0;'>&#10003; " + p + "</span>"
            )
    else:
        prereqs_html = "<span style='color:#9CA3AF;font-size:13px;'>No specific prerequisites.</span>"

    # --- approach ---
    approach_html = ""
    if analysis.get("approach"):
        approach_html = (
            "<div style='background:#F0F9FF;border-radius:8px;padding:14px 18px;margin:0 0 12px;'>"
            "<p style='margin:0;color:#0C4A6E;font-size:14px;line-height:1.7;'>"
            + analysis["approach"] + "</p></div>"
        )

    # --- complexity ---
    complexity_html = ""
    if analysis.get("time") or analysis.get("space"):
        complexity_html = (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 12px;border-collapse:separate;border-spacing:8px 0;'><tr>"
            "<td style='background:#EFF6FF;border-radius:8px;padding:12px 14px;vertical-align:top;border:1px solid #DBEAFE;'>"
            "<p style='margin:0;font-size:11px;color:#1D4ED8;font-weight:700;letter-spacing:1px;'>TIME</p>"
            "<p style='margin:4px 0 0;font-size:13px;color:#1E293B;line-height:1.5;'>" + analysis.get("time", "N/A") + "</p></td>"
            "<td style='background:#F0FDF4;border-radius:8px;padding:12px 14px;vertical-align:top;border:1px solid #BBF7D0;'>"
            "<p style='margin:0;font-size:11px;color:#166534;font-weight:700;letter-spacing:1px;'>SPACE</p>"
            "<p style='margin:4px 0 0;font-size:13px;color:#1E293B;line-height:1.5;'>" + analysis.get("space", "N/A") + "</p></td>"
            "</tr></table>"
        )

    # --- pattern ---
    pattern_html = ""
    if analysis.get("pattern"):
        pattern_html = (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 12px;'><tr>"
            "<td style='background:#FAF5FF;border-radius:8px;padding:12px 16px;border:1px solid #E9D5FF;'>"
            "<p style='margin:0;font-size:11px;color:#7C3AED;font-weight:700;letter-spacing:1px;'>ALGORITHMIC PATTERN</p>"
            "<p style='margin:4px 0 0;font-size:14px;color:#4C1D95;font-weight:600;'>" + analysis["pattern"] + "</p>"
            "</td></tr></table>"
        )

    # --- pitfall ---
    pitfall_html = ""
    if analysis.get("pitfall"):
        pitfall_html = (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 12px;'><tr>"
            "<td style='background:#FFF7ED;border-radius:8px;padding:12px 16px;border:1px solid #FED7AA;'>"
            "<p style='margin:0;font-size:11px;color:#C2410C;font-weight:700;letter-spacing:1px;'>COMMON PITFALL</p>"
            "<p style='margin:4px 0 0;font-size:13px;color:#7C2D12;line-height:1.6;'>" + analysis["pitfall"] + "</p>"
            "</td></tr></table>"
        )

    # --- pseudocode ---
    pseudocode_html = ""
    if analysis.get("pseudocode"):
        lines = analysis["pseudocode"].split("|")
        lines_html = ""
        for ln in lines:
            ln = ln.strip()
            if ln:
                lines_html += (
                    "<div style='padding:3px 0;color:#E2E8F0;font-family:monospace;font-size:13px;line-height:1.6;'>"
                    + ln + "</div>"
                )
        pseudocode_html = (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 12px;'><tr>"
            "<td style='background:#1E293B;border-radius:8px;padding:16px 20px;'>"
            "<p style='margin:0 0 10px;font-size:11px;color:#64748B;font-weight:700;letter-spacing:1px;'>PSEUDOCODE</p>"
            + lines_html +
            "</td></tr></table>"
        )

    # --- hints ---
    hints_html = ""
    for i, hint in enumerate(analysis.get("hints", []), 1):
        hints_html += (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0 0 10px;'><tr>"
            "<td style='width:32px;vertical-align:top;padding-top:2px;'>"
            "<div style='width:28px;height:28px;background:#0B53A0;color:white;"
            "border-radius:50%;text-align:center;line-height:28px;font-size:12px;font-weight:700;'>"
            + str(i) + "</div></td>"
            "<td style='padding-left:10px;vertical-align:top;'>"
            "<p style='margin:4px 0;color:#374151;font-size:14px;line-height:1.6;'>" + hint + "</p>"
            "</td></tr></table>"
        )

    # --- similar questions ---
    similar_html = ""
    for sq in problem.get("similar_questions", []):
        sq_diff = sq.get("difficulty", "")
        sq_color = DIFFICULTY_COLOR.get(sq_diff, "#6B7280")
        similar_html += (
            "<table cellpadding='0' cellspacing='0' width='100%' style='margin:0;'><tr>"
            "<td style='padding:8px 0;border-bottom:1px solid #F1F5F9;font-size:13px;color:#374151;'>" + sq.get("title", "") + "</td>"
            "<td style='padding:8px 0;border-bottom:1px solid #F1F5F9;text-align:right;font-size:11px;font-weight:700;color:" + sq_color + ";'>" + sq_diff + "</td>"
            "</tr></table>"
        )

    similar_section = ""
    if similar_html:
        similar_section = (
            "<tr><td style='padding:0 32px 4px;'>"
            "<hr style='border:none;border-top:1px solid #E5E7EB;margin:0 0 16px;'>"
            "<p style='margin:0 0 10px;font-size:12px;color:#6B7280;font-weight:700;letter-spacing:1px;'>SIMILAR PROBLEMS</p>"
            + similar_html +
            "</td></tr>"
        )

    # --- full html ---
    html = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'></head>"
        "<body style='margin:0;padding:0;background:#F1F5F9;font-family:Arial,sans-serif;'>"
        "<table width='100%' cellpadding='0' cellspacing='0' style='background:#F1F5F9;padding:32px 16px;'>"
        "<tr><td align='center'>"
        "<table width='600' cellpadding='0' cellspacing='0' style='max-width:600px;width:100%;background:#FFFFFF;border-radius:12px;overflow:hidden;'>"

        # header
        "<tr><td style='background:#0B53A0;padding:28px 32px;'>"
        "<p style='margin:0 0 8px;color:#93C5FD;font-size:11px;letter-spacing:2px;'>DAILY CHALLENGE &middot; " + date_fmt + "</p>"
        "<table cellpadding='0' cellspacing='0'><tr>"
        "<td style='vertical-align:middle;padding-right:10px;'>"
        "<span style='display:inline-block;background:rgba(255,255,255,0.18);color:#E0F2FE;"
        "border-radius:6px;padding:4px 10px;font-size:13px;font-weight:700;white-space:nowrap;'>#" + str(problem["question_id"]) + "</span>"
        "</td>"
        "<td style='vertical-align:middle;'>"
        "<span style='color:#FFFFFF;font-size:20px;font-weight:700;line-height:1.3;'>" + problem["title"] + "</span>"
        "</td></tr></table>"
        "<div style='margin-top:14px;'>"
        "<span style='background:" + diff_color + ";color:white;padding:4px 14px;"
        "border-radius:20px;font-size:12px;font-weight:700;display:inline-block;'>" + problem["difficulty"] + "</span>"
        "</div>"
        "</td></tr>"

        # stats
        "<tr><td style='padding:24px 32px 0;'>" + stats_html + "</td></tr>"

        # topics
        "<tr><td style='padding:0 32px 0;'>"
        "<p style='margin:0 0 8px;font-size:12px;color:#6B7280;font-weight:700;letter-spacing:1px;'>TOPICS</p>"
        "<div style='margin-bottom:20px;'>" + tags_html + "</div>"
        "</td></tr>"

        # prerequisites
        "<tr><td style='padding:0 32px 0;'>"
        "<p style='margin:0 0 8px;font-size:12px;color:#6B7280;font-weight:700;letter-spacing:1px;'>PREREQUISITES</p>"
        "<div style='margin-bottom:20px;'>" + prereqs_html + "</div>"
        "</td></tr>"

        # open problem button
        "<tr><td style='padding:0 32px 20px;'>"
        "<a href='" + problem["link"] + "' style='display:inline-block;background:#0B53A0;color:white;"
        "text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;font-size:15px;'>Open Problem &rarr;</a>"
        "</td></tr>"

        # divider
        "<tr><td style='padding:0 32px;'><hr style='border:none;border-top:1px solid #E5E7EB;margin:0 0 20px;'></td></tr>"

        # example test cases
        "<tr><td style='padding:0 32px 4px;'>"
        "<p style='margin:0 0 8px;font-size:12px;color:#6B7280;font-weight:700;letter-spacing:1px;'>EXAMPLE TEST CASES</p>"
        + examples_html +
        "</td></tr>"

        # divider
        "<tr><td style='padding:0 32px;'><hr style='border:none;border-top:1px solid #E5E7EB;margin:16px 0;'></td></tr>"

        # analysis heading
        "<tr><td style='padding:0 32px 12px;'>"
        "<p style='margin:0;font-size:16px;color:#1E293B;font-weight:700;'>In-Depth Analysis</p>"
        "</td></tr>"

        # approach
        "<tr><td style='padding:0 32px 4px;'>" + approach_html + "</td></tr>"

        # complexity
        "<tr><td style='padding:0 32px 4px;'>" + complexity_html + "</td></tr>"

        # pattern
        "<tr><td style='padding:0 32px 4px;'>" + pattern_html + "</td></tr>"

        # pitfall
        "<tr><td style='padding:0 32px 4px;'>" + pitfall_html + "</td></tr>"

        # pseudocode
        "<tr><td style='padding:0 32px 4px;'>" + pseudocode_html + "</td></tr>"

        # divider
        "<tr><td style='padding:0 32px;'><hr style='border:none;border-top:1px solid #E5E7EB;margin:12px 0;'></td></tr>"

        # hints
        "<tr><td style='padding:0 32px 16px;'>"
        "<p style='margin:0 0 12px;font-size:12px;color:#6B7280;font-weight:700;letter-spacing:1px;'>AI HINTS &mdash; NO SPOILERS</p>"
        + hints_html +
        "</td></tr>"

        + similar_section +

        # footer
        "<tr><td style='background:#F8FAFC;border-top:1px solid #E5E7EB;padding:14px 32px;text-align:center;'>"
        "<p style='margin:0;font-size:12px;color:#9CA3AF;'>LeetCode Daily Bot &middot; FAANG Prep &middot; " + date_fmt + "</p>"
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
