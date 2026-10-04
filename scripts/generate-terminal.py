import os
import urllib.request
import json
import base64
import html
from collections import Counter

USERNAME = "Deepak-3357"
OUTPUT = "assets/github-terminal.svg"

TOKEN = os.environ.get("GITHUB_TOKEN", "")

headers = {
    "User-Agent": "Deepak-GitHub-Terminal"
}

if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"


def github_api(url):
    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def github_bytes(url):
    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return response.read()


# ---------------------------------------------------------
# GitHub profile
# ---------------------------------------------------------

profile = github_api(
    f"https://api.github.com/users/{USERNAME}"
)

name = profile.get("name") or USERNAME
login = profile.get("login", USERNAME)
followers = profile.get("followers", 0)
following = profile.get("following", 0)
public_repos = profile.get("public_repos", 0)
public_gists = profile.get("public_gists", 0)
avatar_url = profile.get("avatar_url")


# ---------------------------------------------------------
# Repositories
# ---------------------------------------------------------

repos = github_api(
    f"https://api.github.com/users/{USERNAME}/repos"
    "?per_page=100&sort=updated"
)

# Only public repositories
repos = [
    repo for repo in repos
    if not repo.get("fork", False)
]

repos.sort(
    key=lambda repo: repo.get("updated_at", ""),
    reverse=True
)


# ---------------------------------------------------------
# Repository languages
# ---------------------------------------------------------

language_counter = Counter()

for repo in repos:
    try:
        languages = github_api(repo["languages_url"])

        for language, amount in languages.items():
            language_counter[language] += amount

    except Exception:
        pass


# Top languages
top_languages = language_counter.most_common(6)

if not top_languages:
    top_languages = [
        ("Python", 85),
        ("C++", 75),
        ("Java", 65),
        ("C", 60),
        ("JavaScript", 50),
        ("TypeScript", 45),
    ]


max_language_value = max(
    value for _, value in top_languages
)


# ---------------------------------------------------------
# Stars
# ---------------------------------------------------------

stars = sum(
    repo.get("stargazers_count", 0)
    for repo in repos
)

issues = sum(
    repo.get("open_issues_count", 0)
    for repo in repos
)


# ---------------------------------------------------------
# Profile image
# ---------------------------------------------------------

avatar_data = ""

try:
    avatar_bytes = github_bytes(avatar_url)

    avatar_base64 = base64.b64encode(
        avatar_bytes
    ).decode("ascii")

    avatar_data = (
        "data:image/png;base64,"
        + avatar_base64
    )

except Exception:
    avatar_data = ""


# ---------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------

def esc(value):
    return html.escape(str(value))


def text(x, y, value, size=14, color="#dbeafe",
         weight="400", family="monospace"):
    return f'''
    <text
        x="{x}"
        y="{y}"
        font-family="{family}"
        font-size="{size}px"
        font-weight="{weight}"
        fill="{color}">
        {esc(value)}
    </text>
    '''


def bar(x, y, width, percentage):
    filled = int(width * percentage / 100)

    return f'''
    <rect
        x="{x}"
        y="{y}"
        width="{width}"
        height="12"
        rx="3"
        fill="#172554"/>

    <rect
        x="{x}"
        y="{y}"
        width="{filled}"
        height="12"
        rx="3"
        fill="#22d3ee"/>
    '''


# ---------------------------------------------------------
# Build skills
# ---------------------------------------------------------

skills_svg = ""

skill_y = 420

for language, value in top_languages:

    percentage = int(
        (value / max_language_value) * 100
    )

    percentage = max(20, min(100, percentage))

    skills_svg += text(
        165,
        skill_y,
        language,
        14,
        "#67e8f9"
    )

    skills_svg += bar(
        310,
        skill_y - 11,
        240,
        percentage
    )

    skills_svg += text(
        565,
        skill_y,
        f"{percentage}%",
        12,
        "#94a3b8"
    )

    skill_y += 28


# ---------------------------------------------------------
# Repository list
# ---------------------------------------------------------

repo_svg = ""

repo_start_y = skill_y + 42

# Two-column repository layout
column_width = 420

for index, repo in enumerate(repos):

    column = index % 2
    row = index // 2

    x = 165 + (column * column_width)
    y = repo_start_y + (row * 25)

    repo_name = repo.get("name", "")

    if len(repo_name) > 34:
        repo_name = repo_name[:31] + "..."

    repo_svg += text(
        x,
        y,
        "▰ " + repo_name,
        13,
        "#c4b5fd"
    )


# ---------------------------------------------------------
# SVG height
# ---------------------------------------------------------

repo_rows = max(
    1,
    (len(repos) + 1) // 2
)

height = repo_start_y + (repo_rows * 25) + 95


# ---------------------------------------------------------
# Terminal
# ---------------------------------------------------------

svg = f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="1100"
    height="{height}"
    viewBox="0 0 1100 {height}">

    <defs>

        <linearGradient
            id="terminalBg"
            x1="0"
            y1="0"
            x2="1"
            y2="1">

            <stop
                offset="0%"
                stop-color="#0b1220"/>

            <stop
                offset="100%"
                stop-color="#111827"/>

        </linearGradient>

        <filter id="glow">

            <feGaussianBlur
                stdDeviation="3"
                result="blur"/>

            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>

        </filter>

    </defs>


    <!-- Terminal body -->

    <rect
        x="15"
        y="15"
        width="1070"
        height="{height - 30}"
        rx="10"
        fill="url(#terminalBg)"
        stroke="#334155"
        stroke-width="1"/>


    <!-- Header -->

    <rect
        x="15"
        y="15"
        width="1070"
        height="48"
        rx="10"
        fill="#172033"/>


    <!-- macOS buttons -->

    <circle
        cx="38"
        cy="39"
        r="7"
        fill="#ff5f57"/>

    <circle
        cx="62"
        cy="39"
        r="7"
        fill="#febc2e"/>

    <circle
        cx="86"
        cy="39"
        r="7"
        fill="#28c840"/>


    {text(
        450,
        43,
        "deepak@github: ~/profile",
        13,
        "#bfdbfe"
    )}


    <!-- Prompt -->

    {text(
        45,
        95,
        f"{login}@github.com :~$ whoami",
        14,
        "#a5b4fc"
    )}

    {text(
        45,
        119,
        name,
        14,
        "#e0e7ff"
    )}


    <!-- Neofetch -->

    {text(
        45,
        158,
        f"{login}@github.com :~$ neofetch",
        14,
        "#a5b4fc"
    )}


    <!-- Profile image -->

    <rect
        x="45"
        y="180"
        width="260"
        height="260"
        rx="12"
        fill="#020617"
        stroke="#1e3a5f"/>

'''

# Embed avatar
if avatar_data:

    svg += f'''
    <image
        href="{avatar_data}"
        x="65"
        y="200"
        width="220"
        height="220"
        preserveAspectRatio="xMidYMid slice"/>
    '''

else:

    svg += text(
        95,
        315,
        "PROFILE",
        24,
        "#22d3ee",
        "700"
    )


# Right-side statistics

svg += f'''

    {text(
        355,
        205,
        f"{login} @github.com",
        16,
        "#fbbf24",
        "600"
    )}

    {text(
        355,
        250,
        "------------------------",
        13,
        "#64748b"
    )}

    {text(355, 278, "OS:", 14, "#fbbf24")}
    {text(435, 278, "GitHub Profile", 14, "#c4b5fd")}

    {text(355, 305, "Repos:", 14, "#fbbf24")}
    {text(435, 305, public_repos, 14, "#c4b5fd")}

    {text(355, 332, "Gists:", 14, "#fbbf24")}
    {text(435, 332, public_gists, 14, "#c4b5fd")}

    {text(355, 359, "Stars:", 14, "#fbbf24")}
    {text(435, 359, stars, 14, "#c4b5fd")}

    {text(355, 386, "Followers:", 14, "#fbbf24")}
    {text(435, 386, followers, 14, "#c4b5fd")}

    {text(355, 413, "Following:", 14, "#fbbf24")}
    {text(435, 413, following, 14, "#c4b5fd")}

    {text(355, 440, "Issues:", 14, "#fbbf24")}
    {text(435, 440, issues, 14, "#c4b5fd")}


    <!-- Skills -->

    {text(
        45,
        {skill_y - (len(top_languages) * 28) - 10},
        f"{login}@github.com :~$ skills",
        14,
        "#a5b4fc"
    )}

    {skills_svg}


    <!-- Repositories -->

    {text(
        45,
        repo_start_y - 35,
        f"{login}@github.com :~$ ls ~/repositories",
        14,
        "#a5b4fc"
    )}

    {repo_svg}


    <!-- Exit -->

    {text(
        45,
        height - 55,
        f"{login}@github.com :~$ exit",
        14,
        "#a5b4fc"
    )}

    <rect
        x="45"
        y="{height - 38}"
        width="8"
        height="18"
        fill="#c4b5fd">
        <animate
            attributeName="opacity"
            values="1;0;1"
            dur="1s"
            repeatCount="indefinite"/>
    </rect>

</svg>
'''


# ---------------------------------------------------------
# Write file
# ---------------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT),
    exist_ok=True
)

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)

print(f"Generated: {OUTPUT}")
