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
