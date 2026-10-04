
    skills_output.append(svg_text(
        skill_bar_x + skill_bar_w + 12,
        y,
        f"{percentage}%",
        11, "#94a3b8"
    ))


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
