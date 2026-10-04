import os
import json
import base64
import html
import urllib.request
from collections import Counter

USERNAME = "Deepak-3357"
OUTPUT = "assets/github-terminal.svg"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "User-Agent": "Deepak-GitHub-Terminal",
    "Accept": "application/vnd.github+json",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def api(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_bytes(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def esc(value):
    return html.escape(str(value), quote=True)


def svg_text(x, y, value, size=13, color="#dbeafe",
             weight="400", anchor="start", opacity=1):
    return (
        f'<text x="{x}" y="{y}" font-family="monospace" '
        f'font-size="{size}px" font-weight="{weight}" '
        f'fill="{color}" text-anchor="{anchor}" opacity="{opacity}">'
        f'{esc(value)}</text>'
    )


def add_typing(defs, body, uid, x, y, value, size, color,
               delay, duration, weight="400"):
    # SVG SMIL clip animation = typing/reveal effect without JavaScript.
    width = max(10, len(str(value)) * size * 0.61 + 10)
    clip_id = f"typing_{uid}"

    defs.append(
        f'<clipPath id="{clip_id}">'
        f'<rect x="{x}" y="{y - size}" width="0" height="{size + 10}">'
        f'<animate attributeName="width" from="0" to="{width:.1f}" '
        f'begin="{delay:.2f}s" dur="{duration:.2f}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )

    body.append(
        f'<text x="{x}" y="{y}" font-family="monospace" '
        f'font-size="{size}px" font-weight="{weight}" fill="{color}" '
        f'clip-path="url(#{clip_id})">{esc(value)}</text>'
    )


# -------------------------
# GitHub profile
# -------------------------
profile = api(f"https://api.github.com/users/{USERNAME}")

name = profile.get("name") or USERNAME
login = profile.get("login", USERNAME)
followers = profile.get("followers", 0)
following = profile.get("following", 0)
public_gists = profile.get("public_gists", 0)
avatar_url = profile.get("avatar_url", "")

# -------------------------
# ALL public repositories
# Exclude the profile README repository itself.
# -------------------------
repos = []
page = 1

while True:
    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        f"?type=owner&per_page=100&page={page}&sort=updated"
    )
    batch = api(url)

    if not batch:
        break

    repos.extend(batch)

    if len(batch) < 100:
        break

    page += 1

repos = [
    repo for repo in repos
    if not repo.get("fork", False)
    and repo.get("name", "").lower() != USERNAME.lower()
]

# -------------------------
# GitHub language usage
# -------------------------
language_counter = Counter()

for repo in repos:
    try:
        languages = api(repo["languages_url"])
        for language, amount in languages.items():
            language_counter[language] += amount
    except Exception:
        pass

languages = language_counter.most_common(6)

if not languages:
    languages = [
        ("Python", 100),
        ("C++", 80),
        ("Java", 65),
        ("C", 55),
        ("JavaScript", 45),
        ("TypeScript", 35),
    ]

max_language = max(value for _, value in languages)

stars = sum(repo.get("stargazers_count", 0) for repo in repos)
issues = sum(repo.get("open_issues_count", 0) for repo in repos)

# -------------------------
# Download GitHub avatar
# -------------------------
avatar_data = ""

try:
    avatar_bytes = get_bytes(avatar_url)
    avatar_data = (
        "data:image/png;base64,"
        + base64.b64encode(avatar_bytes).decode("ascii")
    )
except Exception:
    pass

# -------------------------
# Layout
# -------------------------
W = 1100
terminal_x = 24
terminal_y = 18
terminal_w = 1052
header_h = 48

photo_x = 55
photo_y = 160
photo_size = 250

stats_x = 355
stats_y = 205

skills_y = 455
skill_bar_x = 290
skill_bar_w = 220

repo_command_y = skills_y + len(languages) * 29 + 50
repo_start_y = repo_command_y + 32

repo_row_h = 27
repo_rows = max(1, (len(repos) + 1) // 2)

height = max(
    730,
    repo_start_y + repo_rows * repo_row_h + 100
)

defs = []
body = []

# -------------------------
# Terminal background
# -------------------------
body.append(
    f'<rect x="{terminal_x}" y="{terminal_y}" '
    f'width="{terminal_w}" height="{height - 36}" rx="10" '
    f'fill="#0b1220" stroke="#334155" stroke-width="1"/>'
)

body.append(
    f'<rect x="{terminal_x}" y="{terminal_y}" '
    f'width="{terminal_w}" height="{header_h}" rx="10" '
    f'fill="#172033"/>'
)

# macOS buttons
body.append('<circle cx="44" cy="42" r="7" fill="#ff5f57"/>')
body.append('<circle cx="68" cy="42" r="7" fill="#febc2e"/>')
body.append('<circle cx="92" cy="42" r="7" fill="#28c840"/>')

body.append(
    svg_text(
        W / 2, 46,
        "deepak@github: ~/profile",
        12, "#bfdbfe",
        anchor="middle"
    )
)

# -------------------------
# whoami
# -------------------------
add_typing(
    defs, body, "whoami",
    55, 90,
    f"{login}@github.com :~$ whoami",
    13, "#a5b4fc", 0.15, 0.75
)

body.append(svg_text(55, 114, name, 13, "#e0e7ff"))

# -------------------------
# neofetch
# -------------------------
add_typing(
    defs, body, "neofetch",
    55, 145,
    f"{login}@github.com :~$ neofetch",
    13, "#a5b4fc", 1.15, 0.8
)

# -------------------------
# Profile photo
# -------------------------
body.append(
    f'<rect x="{photo_x}" y="{photo_y}" '
    f'width="{photo_size}" height="{photo_size}" rx="10" '
    f'fill="#020617" stroke="#1e3a5f"/>'
)

if avatar_data:
    body.append(
        f'<image href="{avatar_data}" '
        f'x="{photo_x + 16}" y="{photo_y + 16}" '
        f'width="{photo_size - 32}" height="{photo_size - 32}" '
        f'preserveAspectRatio="xMidYMid slice"/>'
    )
else:
    body.append(
        svg_text(
            photo_x + photo_size / 2,
            photo_y + photo_size / 2,
            "PROFILE",
            22, "#22d3ee", "700",
            anchor="middle"
        )
    )

# -------------------------
# Profile statistics
# -------------------------
body.append(
    svg_text(
        stats_x, 184,
        f"{login} @github.com",
        15, "#fbbf24", "600"
    )
)

body.append(
    svg_text(
        stats_x, 219,
        "------------------------",
        12, "#64748b"
    )
)

stats = [
    ("OS:", "GitHub Profile"),
    ("Repos:", len(repos)),
    ("Gists:", public_gists),
    ("Stars:", stars),
    ("Followers:", followers),
    ("Following:", following),
    ("Issues:", issues),
]

for index, (label, value) in enumerate(stats):
    y = stats_y + index * 27

    body.append(svg_text(
        stats_x, y,
        label,
        13, "#fbbf24"
    ))

    body.append(svg_text(
        stats_x + 82, y,
        value,
        13, "#c4b5fd"
    ))

# -------------------------
# Skills
# -------------------------
add_typing(
    defs, body, "skills",
    55, skills_y - 20,
    f"{login}@github.com :~$ skills",
    13, "#a5b4fc", 2.15, 0.75
)

for index, (language, amount) in enumerate(languages):
    y = skills_y + index * 29

    percentage = max(
        18,
        min(100, int((amount / max_language) * 100))
    )

    filled = skill_bar_w * percentage / 100

    body.append(svg_text(
        55, y,
        language,
        13, "#67e8f9"
    ))

    body.append(
        f'<rect x="{skill_bar_x}" y="{y - 11}" '
        f'width="{skill_bar_w}" height="12" rx="3" '
        f'fill="#172554"/>'
    )

    body.append(
        f'<rect x="{skill_bar_x}" y="{y - 11}" '
        f'width="{filled:.1f}" height="12" rx="3" '
        f'fill="#22d3ee"/>'
    )

    body.append(svg_text(
        skill_bar_x + skill_bar_w + 12,
        y,
        f"{percentage}%",
        11, "#94a3b8"
    ))

# -------------------------
# ALL repositories
# -------------------------
add_typing(
    defs, body, "repositories",
    55, repo_command_y,
    f"{login}@github.com :~$ ls ~/repositories",
    13, "#a5b4fc", 3.2, 0.9
)

column_x = [155, 515]

for index, repo in enumerate(repos):
    column = index % 2
    row = index // 2

    x = column_x[column]
    y = repo_start_y + row * repo_row_h

    repo_name = repo.get("name", "")

    if len(repo_name) > 40:
        repo_name = repo_name[:37] + "..."

    body.append(
        svg_text(
            x, y,
            "▰ " + repo_name,
            12, "#c4b5fd"
        )
    )

# -------------------------
# exit
# -------------------------
exit_y = height - 58

add_typing(
    defs, body, "exit",
    55, exit_y,
    f"{login}@github.com :~$ exit",
    13, "#a5b4fc", 4.5, 0.8
)

body.append(
    f'<rect x="55" y="{exit_y + 14}" width="8" height="17" '
    f'fill="#c4b5fd">'
    f'<animate attributeName="opacity" values="1;0;1" '
    f'dur="1s" repeatCount="indefinite"/>'
    f'</rect>'
)

# -------------------------
# Final SVG
# -------------------------
svg = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{W}" height="{height}" viewBox="0 0 {W} {height}">'
    '<defs>'
    + "".join(defs)
    + '</defs>'
    + "".join(body)
    + '</svg>'
)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write(svg)

print(f"Generated: {OUTPUT}")
print(f"Repositories displayed: {len(repos)}")
print("Profile repository excluded.")
