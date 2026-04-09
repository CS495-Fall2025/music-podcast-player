"""
make_test_users.py — Create test users with playlists for teammate testing.

HOW TO RUN
──────────
1. Start the backend services from the repo root:
       docker compose up

2. Open a new terminal, go into the backend folder:
       cd backend

3. Run this script (no extra packages needed — stdlib only):
       python seed_teammates.py

WHAT IT CREATES
───────────────
• 3 users (username + password printed clearly at the end)
• 2 playlists per user, each loaded with 4 podcast/RSS feed tracks
• All data goes directly into the DB service (port 5001)
  — no API service or external API keys required

NOTE: Each run generates new usernames with a timestamp suffix so you can run
it multiple times without conflicts.
"""

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

# ── Config ────────────────────────────────────────────────────────────────────
DB_BASE = "http://localhost:5001"
PASSWORD = "TestUser!2026A"

# Public podcast RSS feeds used as playlist tracks.
# These are real feeds — teammates will be able to click through and play them.
FEED_URLS = [
    "https://feeds.npr.org/510289/podcast.xml",           # NPR Alt.Latino
    "https://feed.syntax.fm/rss",                         # Syntax.fm (web dev)
    "https://shoptalkshow.com/feed/podcast/",             # ShopTalk Show
    "https://darknetdiaries.com/feed/podcast/",           # Darknet Diaries
    "https://feeds.transistor.fm/soft-skills-engineering",# Soft Skills Eng.
    "https://changelog.com/podcast/feed",                 # The Changelog
    "https://feeds.megaphone.fm/stuffyoushouldknow",      # Stuff You Should Know
    "https://rss.art19.com/freakonomics-radio",           # Freakonomics Radio
    "https://feeds.npr.org/510019/podcast.xml",           # NPR Pop Culture Happy Hour
    "https://feeds.npr.org/510317/podcast.xml",           # NPR Tiny Desk Concerts
    "https://feeds.simplecast.com/54nAGcIl",              # 99% Invisible
    "https://feeds.feedburner.com/tbtl",                  # TBTL
]

# ── User + playlist definitions ───────────────────────────────────────────────
# Tracks are slices of FEED_URLS; each playlist gets 4 URLs.
USER_SPECS = [
    {
        "label": "dj_alpha",
        "playlists": [
            {
                "title": "Morning Vibes",
                "description": "Chill tracks to start the day",
                "tracks": FEED_URLS[0:4],
            },
            {
                "title": "Late Night Mix",
                "description": "Deep cuts for late nights",
                "tracks": FEED_URLS[4:8],
            },
        ],
    },
    {
        "label": "beatmaker",
        "playlists": [
            {
                "title": "Tech Beats",
                "description": "All things tech and audio",
                "tracks": FEED_URLS[2:6],
            },
            {
                "title": "Coding Playlist",
                "description": "Focus music for the dev grind",
                "tracks": FEED_URLS[6:10],
            },
        ],
    },
    {
        "label": "wavesurfer",
        "playlists": [
            {
                "title": "Indie Picks",
                "description": "Underground gems",
                "tracks": FEED_URLS[0:4],
            },
            {
                "title": "Weekend Roadtrip",
                "description": "Songs for the open road",
                "tracks": FEED_URLS[8:12],
            },
        ],
    },
]


# ── HTTP helpers ──────────────────────────────────────────────────────────────
@dataclass
class UserRecord:
    id: int
    username: str
    email: str


def _post_json(url: str, payload: dict, timeout: int = 20) -> tuple[int, dict]:
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return err.code, parsed


# ── Domain operations ─────────────────────────────────────────────────────────
def create_user(username: str, email: str) -> UserRecord:
    status, payload = _post_json(
        f"{DB_BASE}/users/create",
        {"username": username, "email": email, "password": PASSWORD},
    )
    if status != 201:
        raise RuntimeError(f"Create user failed for {username}: {status} {payload}")

    # Login to retrieve the assigned user ID
    status, payload = _post_json(
        f"{DB_BASE}/users/login",
        {"username": username, "password": PASSWORD},
    )
    if status != 200:
        raise RuntimeError(f"Login failed for {username}: {status} {payload}")

    return UserRecord(
        id=int(payload["id"]),
        username=payload["username"],
        email=email,
    )


def create_playlist(user: UserRecord, title: str, description: str) -> dict:
    status, payload = _post_json(
        f"{DB_BASE}/playlists/create",
        {
            "title": title,
            "description": description,
            "created_by_user_id": user.id,
        },
    )
    if status != 201:
        raise RuntimeError(
            f"Create playlist failed for {user.username!r} ({title!r}): "
            f"{status} {payload}"
        )
    return payload


def add_track(playlist_id: int, user_id: int, track_url: str) -> None:
    status, payload = _post_json(
        f"{DB_BASE}/playlists/{playlist_id}/tracks/add",
        {"track_url": track_url, "created_by_user_id": user_id},
    )
    if status != 201:
        raise RuntimeError(
            f"Add track failed (playlist {playlist_id}): {status} {payload}"
        )


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    stamp = int(time.time())
    created: list[UserRecord] = []

    print()
    print("Creating users and playlists...")
    print()

    for spec in USER_SPECS:
        username = f"{spec['label']}{stamp}"
        email = f"{username}@example.test"

        print(f"  [{spec['label']}]  {username}", end="  ", flush=True)
        user = create_user(username, email)
        print(f"(id={user.id})", flush=True)

        for pl in spec["playlists"]:
            print(f"      playlist: {pl['title']!r}", end="  ", flush=True)
            playlist = create_playlist(user, pl["title"], pl["description"])
            for url in pl["tracks"]:
                add_track(int(playlist["id"]), user.id, url)
            print(f"({len(pl['tracks'])} tracks ✓)", flush=True)

        created.append(user)

    # ── Print credentials summary ─────────────────────────────────────────────
    W = 60
    print()
    print("═" * W)
    print("  TEST ACCOUNT CREDENTIALS")
    print("═" * W)
    print(f"  Shared password:  {PASSWORD}")
    print("─" * W)
    for user in created:
        print(f"  Username : {user.username}")
        print(f"  Email    : {user.email}")
        print(f"  User ID  : {user.id}")
        print()
    print("═" * W)
    print()
    print("  Each account has 2 playlists with 4 tracks each.")
    print("  Log in at http://localhost:5173 (or wherever the frontend is running).")
    print()


if __name__ == "__main__":
    main()

