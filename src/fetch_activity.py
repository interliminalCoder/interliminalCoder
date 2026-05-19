import os
import json
import re
from urllib.request import Request, urlopen
from urllib.error import URLError

GITHUB_TOKEN = os.environ.get("GH_TOKEN")
USERNAME = "interliminalCoder"
README_PATH = "README.md"

EVENT_ICONS = {
    "PushEvent": "📦",
    "CreateEvent": "📁",
    "DeleteEvent": "🗑️",
    "IssuesEvent": "📌",
    "IssueCommentEvent": "💬",
    "PullRequestEvent": "🔀",
    "PullRequestReviewEvent": "👀",
    "PullRequestReviewCommentEvent": "📝",
    "WatchEvent": "⭐",
    "ForkEvent": "🍴",
    "ReleaseEvent": "🏷️",
    "PublicEvent": "🌍",
    "MemberEvent": "👤",
    "GollumEvent": "📖",
}

EVENT_ACTIONS = {
    "created": "creó",
    "opened": "abrió",
    "closed": "cerró",
    "reopened": "reabrió",
    "merged": "fusionó",
    "approved": "aprobó",
    "submitted": "envió",
    "deleted": "eliminó",
    "published": "publicó",
    "started": "empezó a seguir",
    "forked": "hizo fork",
}


def fetch_events():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=10"
    headers = {
        "User-Agent": "interliminalCoder-profile-bot",
        "Accept": "application/vnd.github.v3+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    req = Request(url, headers=headers)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        print(f"Error fetching events: {e}")
        return []


def format_event(event):
    etype = event.get("type", "")
    repo = event.get("repo", {}).get("name", "unknown")
    payload = event.get("payload", {})
    action = payload.get("action", "")

    emoji = EVENT_ICONS.get(etype, "❓")

    if etype == "PushEvent":
        commits = payload.get("commits", [])
        count = len(commits)
        if count == 0:
            return f"{emoji} Push a `{repo}` (sin commits)"
        msg = commits[0].get("message", "").split("\n")[0][:50]
        rest = f" (+{count - 1} más)" if count > 1 else ""
        return f"{emoji} Push a `{repo}` — _{msg}_{rest}"

    if etype == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref", "")
        if ref:
            return f"{emoji} Creó {ref_type} `{ref}` en `{repo}`"
        return f"{emoji} Creó un {ref_type} en `{repo}`"

    if etype == "DeleteEvent":
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref", "")
        return f"{emoji} Eliminó {ref_type} `{ref}` de `{repo}`"

    if etype == "IssuesEvent":
        title = payload.get("issue", {}).get("title", "sin título")
        number = payload.get("issue", {}).get("number", "?")
        act = EVENT_ACTIONS.get(action, action)
        return f"{emoji} {act.title()} issue [#{number}](https://github.com/{repo}/issues/{number}) en `{repo}` — _{title}_"

    if etype == "IssueCommentEvent":
        issue_number = payload.get("issue", {}).get("number", "?")
        return f"{emoji} Comentó en issue [#{issue_number}](https://github.com/{repo}/issues/{issue_number}) de `{repo}`"

    if etype == "PullRequestEvent":
        title = payload.get("pull_request", {}).get("title", "sin título")
        number = payload.get("pull_request", {}).get("number", "?")
        act = EVENT_ACTIONS.get(action, action)
        return f"{emoji} {act.title()} PR [#{number}](https://github.com/{repo}/pull/{number}) en `{repo}` — _{title}_"

    if etype == "PullRequestReviewEvent":
        pr_number = payload.get("pull_request", {}).get("number", "?")
        return f"{emoji} Revisó PR [#{pr_number}](https://github.com/{repo}/pull/{pr_number}) en `{repo}`"

    if etype == "WatchEvent":
        return f"{emoji} Dio estrella a `{repo}`"

    if etype == "ForkEvent":
        forkee = payload.get("forkee", {}).get("full_name", "")
        return f"{emoji} Hizo fork de `{repo}` a `{forkee}`"

    if etype == "ReleaseEvent":
        release = payload.get("release", {}).get("tag_name", "")
        return f"{emoji} Publicó release `{release}` en `{repo}`"

    if etype == "GollumEvent":
        pages = payload.get("pages", [])
        if pages:
            page = pages[0]
            pname = page.get("title", "wiki")
            pact = page.get("action", "actualizó")
            return f"{emoji} {pact.title()} wiki page `{pname}` en `{repo}`"

    return f"{emoji} {etype} en `{repo}`"


def generate_activity_md(events):
    if not events:
        return "No hay actividad reciente aún."

    lines = []
    for event in events:
        lines.append(f"- {format_event(event)}")

    return "\n".join(lines)


def update_readme(activity_md):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- ACTIVITY:start -->.*?<!-- ACTIVITY:end -->"
    replacement = f"<!-- ACTIVITY:start -->\n{activity_md}\n<!-- ACTIVITY:end -->"

    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        content += f"\n\n## Actividad Reciente\n\n{replacement}\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md actualizado con la actividad reciente.")


if __name__ == "__main__":
    events = fetch_events()
    activity = generate_activity_md(events)
    update_readme(activity)

    if events:
        print(f"✅ {len(events)} eventos procesados.")
    else:
        print("⚠️ No se encontraron eventos.")
