import os
import json
import re
from urllib.request import Request, urlopen
from urllib.error import URLError

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY", "")
LASTFM_USER = os.environ.get("LASTFM_USER", "intercoder")
README_PATH = "README.md"


def fetch_recent_tracks(limit=5):
    if not LASTFM_API_KEY:
        print("WARNING: LASTFM_API_KEY no configurada")
        return []

    url = (
        f"https://ws.audioscrobbler.com/2.0/"
        f"?method=user.getrecenttracks"
        f"&user={LASTFM_USER}"
        f"&api_key={LASTFM_API_KEY}"
        f"&format=json"
        f"&limit={limit}"
    )

    req = Request(url, headers={"User-Agent": "interliminalCoder-profile-bot"})
    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("recenttracks", {}).get("track", [])
    except URLError as e:
        print(f"Error fetching tracks: {e}")
        return []


def generate_tracks_md(tracks):
    if not tracks:
        return "No se pudieron obtener las canciones."

    lines = []

    for i, track in enumerate(tracks):
        artist = track.get("artist", {}).get("#text", "Artista desconocido")
        name = track.get("name", "Canción desconocida")
        album = track.get("album", {}).get("#text", "")
        url = track.get("url", "")
        nowplaying = track.get("@attr", {}).get("nowplaying", "") == "true"

        if nowplaying:
            indicator = "▶️ **Ahora**"
        else:
            indicator = f"🎵"

        track_str = f"- {indicator} **{artist}** — *{name}*"
        if album:
            track_str += f" ({album})"
        if url:
            track_str += f" [[Escuchar]]({url})"

        lines.append(track_str)

    if not nowplaying and lines:
        lines.insert(0, f"📻 Últimas canciones en [Last.fm](https://last.fm/user/{LASTFM_USER}):\n")

    return "\n".join(lines)


def update_readme(tracks_md):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- TIDAL:start -->.*?<!-- TIDAL:end -->"
    replacement = f"<!-- TIDAL:start -->\n{tracks_md}\n<!-- TIDAL:end -->"

    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        section = (
            f"\n\n### 🎵 Últimas canciones\n\n"
            f"<!-- TIDAL:start -->\n{tracks_md}\n<!-- TIDAL:end -->\n"
        )
        content += section

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md actualizado con las últimas canciones.")


if __name__ == "__main__":
    tracks = fetch_recent_tracks()
    md = generate_tracks_md(tracks)
    update_readme(md)

    if tracks:
        print(f"✅ {len(tracks)} canciones procesadas.")
    else:
        print("⚠️ No se encontraron canciones.")
