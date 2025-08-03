import requests
import os
import chess.pgn
from io import StringIO

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
    res = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})
    if res.status_code == 200:
        return len(res.json().get("chapters", []))
    else:
        print("Error fetching study details")
        return 0

def split_pgn_games(pgn_text):
    games = []
    while True:
        game = chess.pgn.read_game(StringIO(pgn_text))
        if game is None:
            break
        games.append(game)
        pgn_text = pgn_text[pgn_text.find("1. ", pgn_text.find("1. ") + 1):] if "1. " in pgn_text else ""
    return games

with open(PGN_FILE, "r", encoding="utf-8") as f:
    pgn_text = f.read()

games = split_pgn_games(pgn_text)
existing = get_existing_chapter_count()
available = MAX_CHAPTERS - existing

for i, game in enumerate(games[:available]):
    title = game.headers.get("Event", f"Game {i+1}")
    game_str = str(game)
    data = {
        "pgn": game_str,
        "studyChapter": {
            "name": title,
            "orientation": "white"
        }
    }
    res = requests.post(
        f"https://lichess.org/api/study/{STUDY_ID}/chapter",
        headers=headers,
        data=game_str.encode("utf-8")
    )
    if res.status_code == 201:
        print(f"Uploaded chapter {i+1}: {title}")
    else:
        print(f"Failed to upload chapter {i+1}")
        print("Maximum chapters done")
        print(f"Last PGN title: {title}")
        break
