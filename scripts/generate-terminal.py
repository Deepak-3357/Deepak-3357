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
               start, type_duration, cycle_duration, weight="400"):
    """
    Type a command, keep it visible, then restart the whole terminal cycle.
    The command itself is hidden until its turn and is revealed character by
    character. Output elements use add_cycle_visibility().
    """
    width = max(10, len(str(value)) * size * 0.61 + 10)
    clip_id = f"typing_{uid}"
    end_type = start + type_duration
    eps = 0.001

    defs.append(
        f'<clipPath id="{clip_id}">'
        f'<rect x="{x}" y="{y - size}" width="0" height="{size + 10}">'
        f'<animate attributeName="width" dur="{cycle_duration:.3f}s" repeatCount="indefinite"'
        f' values="0;0;{width:.1f};{width:.1f};0"'
        f' keyTimes="0;{start/cycle_duration:.6f};{end_type/cycle_duration:.6f};'
        f'{(cycle_duration-eps)/cycle_duration:.6f};1"/>'
        f'</rect></clipPath>'
    )

    body.append(
        f'<text x="{x}" y="{y}" font-family="monospace" '
        f'font-size="{size}px" font-weight="{weight}" fill="{color}" '
        f'clip-path="url(#{clip_id})">{esc(value)}</text>'
    )


def add_cycle_visibility(defs, body, uid, content, start, end, cycle_duration):
    """Show generated output only after its command has finished typing."""
    body.append(f'<g id="{uid}" opacity="0">{content}'
                f'<animate attributeName="opacity" dur="{cycle_duration:.3f}s" '
                f'repeatCount="indefinite" values="0;0;1;1;0" '
                f'keyTimes="0;{start/cycle_duration:.6f};{start/cycle_duration:.6f};'
                f'{end/cycle_duration:.6f};1"/>'
                f'</g>')


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
# Skill Level
# Keep this synchronized with the README Skill Level section.
# -------------------------

skill_groups = [
    (
        "ADVANCED",
        [
            ("Python", 100),
            ("C", 100),
            ("SQL", 100),
        ],
    ),
    (
        "INTERMEDIATE",
        [
            ("C++", 75),
            ("Java", 75),
            ("Power BI", 75),
        ],
    ),
    (
        "CURRENTLY LEARNING",
        [
            ("Machine Learning", 45),
            ("HTML", 45),
            ("CSS", 45),
            ("JavaScript", 45),
            ("React", 45),
        ],
    ),
]

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
skill_bar_x = 250
skill_bar_w = 230

# Position repositories after the complete Skill Level block.
skills_block_height = (
    20
    + sum(25 + (len(group_skills) * 23) + 10
          for _, group_skills in skill_groups)
)

repo_command_y = skills_y + skills_block_height + 25
repo_start_y = repo_command_y + 32

repo_row_h = 27
repo_rows = max(1, (len(repos) + 1) // 2)

height = max(
    820,
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
CYCLE = 16.5

# Command timeline (seconds). Every cycle restarts from whoami.
WHOAMI_START, WHOAMI_TYPE, WHOAMI_END = 0.20, 0.80, 1.00
NEOFETCH_START, NEOFETCH_TYPE, NEOFETCH_END = 2.20, 0.80, 3.00
SKILLS_START, SKILLS_TYPE, SKILLS_END = 6.20, 0.70, 6.90
REPOS_START, REPOS_TYPE, REPOS_END = 10.20, 0.90, 11.10
EXIT_START, EXIT_TYPE, EXIT_END = 14.70, 0.60, 15.30

add_typing(
    defs, body, "whoami",
    55, 90,
    f"{login}@github.com :~$ whoami",
    13, "#a5b4fc", WHOAMI_START, WHOAMI_TYPE, CYCLE
)

add_cycle_visibility(
    defs, body, "whoami_output",
    svg_text(55, 114, name, 13, "#e0e7ff"),
    WHOAMI_END, NEOFETCH_START - 0.15, CYCLE
)

# -------------------------
# neofetch
# -------------------------
add_typing(
    defs, body, "neofetch",
    55, 145,
    f"{login}@github.com :~$ neofetch",
    13, "#a5b4fc", NEOFETCH_START, NEOFETCH_TYPE, CYCLE
)

# -------------------------
# Profile photo + statistics output
# -------------------------
neofetch_output = []

neofetch_output.append(
    f'<rect x="{photo_x}" y="{photo_y}" '
    f'width="{photo_size}" height="{photo_size}" rx="10" '
    f'fill="#020617" stroke="#1e3a5f"/>'
)

if avatar_data:
    neofetch_output.append(
        f'<image href="{avatar_data}" '
        f'x="{photo_x + 16}" y="{photo_y + 16}" '
        f'width="{photo_size - 32}" height="{photo_size - 32}" '
        f'preserveAspectRatio="xMidYMid slice"/>'
    )
else:
    neofetch_output.append(
        svg_text(
            photo_x + photo_size / 2,
            photo_y + photo_size / 2,
            "PROFILE",
            22, "#22d3ee", "700",
            anchor="middle"
        )
    )

neofetch_output.append(
    svg_text(
        stats_x, 184,
        f"{login} @github.com",
        15, "#fbbf24", "600"
    )
)

neofetch_output.append(
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

    neofetch_output.append(svg_text(
        stats_x, y,
        label,
        13, "#fbbf24"
    ))

    neofetch_output.append(svg_text(
        stats_x + 82, y,
        value,
        13, "#c4b5fd"
    ))


add_cycle_visibility(
    defs, body, "neofetch_output",
    "".join(neofetch_output),
    NEOFETCH_END, SKILLS_START - 0.15, CYCLE
)

# -------------------------
# Skills
# Matches the README Skill Level section exactly.
# -------------------------
add_typing(
    defs, body, "skills",
    55, skills_y - 20,
    f"{login}@github.com :~$ skills",
    13, "#a5b4fc", SKILLS_START, SKILLS_TYPE, CYCLE
)

skills_output = []

current_y = skills_y + 20

for group_name, group_skills in skill_groups:

    # Category heading
    skills_output.append(
        svg_text(
            55,
            current_y,
            group_name,
            13,
            "#fbbf24",
            "700"
        )
    )

    current_y += 25

    for skill_name, percentage in group_skills:

        # Skill name
        skills_output.append(
            svg_text(
                55,
                current_y,
                skill_name,
                12,
                "#67e8f9"
            )
        )

        # Background bar
        skills_output.append(
            f'<rect '
            f'x="{skill_bar_x}" '
            f'y="{current_y - 10}" '
            f'width="{skill_bar_w}" '
            f'height="11" '
            f'rx="3" '
            f'fill="#172554"/>'
        )

        # Progress bar
        filled = skill_bar_w * percentage / 100

        skills_output.append(
            f'<rect '
            f'x="{skill_bar_x}" '
            f'y="{current_y - 10}" '
            f'width="{filled:.1f}" '
            f'height="11" '
            f'rx="3" '
            f'fill="#22d3ee"/>'
        )

        # Percentage
        skills_output.append(
            svg_text(
                skill_bar_x + skill_bar_w + 12,
                current_y,
                f"{percentage}%",
                11,
                "#94a3b8"
            )
        )

        current_y += 23

    current_y += 10

add_cycle_visibility(
    defs, body, "skills_output",
    "".join(skills_output),
    SKILLS_END, REPOS_START - 0.15, CYCLE
)

# -------------------------
# ALL repositories
# -------------------------
add_typing(
    defs, body, "repositories",
    55, repo_command_y,
    f"{login}@github.com :~$ ls ~/repositories",
    13, "#a5b4fc", REPOS_START, REPOS_TYPE, CYCLE
)

repo_output = []

column_x = [155, 515]

for index, repo in enumerate(repos):
    column = index % 2
    row = index // 2

    x = column_x[column]
    y = repo_start_y + row * repo_row_h

    repo_name = repo.get("name", "")

    if len(repo_name) > 40:
        repo_name = repo_name[:37] + "..."

    repo_output.append(
        svg_text(
            x, y,
            "▰ " + repo_name,
            12, "#c4b5fd"
        )
    )


add_cycle_visibility(
    defs, body, "repo_output",
    "".join(repo_output),
    REPOS_END, EXIT_START - 0.15, CYCLE
)

# -------------------------
# exit
# -------------------------
exit_y = height - 58

add_typing(
    defs, body, "exit",
    55, exit_y,
    f"{login}@github.com :~$ exit",
    13, "#a5b4fc", EXIT_START, EXIT_TYPE, CYCLE
)

# Cursor appears after exit finishes, blinks, then disappears when the cycle resets.
body.append(
    f'<g opacity="0">'
    f'<animate attributeName="opacity" dur="{CYCLE:.3f}s" repeatCount="indefinite" '
    f'values="0;0;1;1;0" keyTimes="0;{EXIT_END/CYCLE:.6f};{EXIT_END/CYCLE:.6f};'
    f'{(CYCLE-0.001)/CYCLE:.6f};1"/>'
    f'<rect x="55" y="{exit_y + 14}" width="8" height="17" fill="#c4b5fd">'
    f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
    f'</rect>'
    f'</g>'
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
