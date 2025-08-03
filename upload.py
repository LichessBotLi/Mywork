import requests
import os
import chess.pgn
from io import StringIO
import re

TOKEN = os.environ['TOKEN']
STUDY_ID = "MlAhgrv3"
PGN_FILE = "caro.pgn"
MAX_CHAPTERS = 63

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/x-chess-pgn"
}

def get_existing_chapter_count():
    url = f"https://lichess.org/api/study/{STUDY_ID}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return len(res.json().get("chapters", []))
    else:
        print("Error fetching study details:", res.text)
        return 0

def clean_pgn(raw):
    # Remove comments { ... } and variations ( ... )
    raw = re.sub(r"\{[^}]*\}", "", raw)
    raw = re.sub(r"\([^()]*\)", "", raw)
    return raw

def split_valid_pgn_games(pgn_text):
    games = []
    pgn_io = StringIO(pgn_text)
    while True:
        try:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            games.append(game)
        except Exception as e:
            print(f"Skipping broken PGN: {e}")
            continue
    return games

# Load and clean PGN
with open(PGN_FILE, "r", encoding="utf-8") as f:
    raw_pgn = f.read()

cleaned = clean_pgn(raw_pgn)
games = split_valid_pgn_games(cleaned)
existing = get_existing_chapter_count()
available = MAX_CHAPTERS - existing

if available <= 0:
    print("Maximum chapters done")
    exit()

# Upload each game
for i, game in enumerate(games[:available]):
    title = game.headers.get("Event", f"Game {i+1}")
    pgn_string = str(game)

    res = requests.post(
        f"https://lichess.org/api/study/{STUDY_ID}/chapter",
        headers=headers,
        data=pgn_string.encode("utf-8")
    )

    if res.status_code == 201:
        print(f"✅ Uploaded chapter {existing + i + 1}: {title}")
        last_title = title
    else:
        print(f"❌ Failed at chapter {existing + i + 1}: {res.text}")
        print("Maximum chapters done")
        print(f"Last PGN title: {title}")
        break
