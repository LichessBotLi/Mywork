import requests
import os
import sys

STUDY_ID = "MlAhgrv3"
TOKEN = os.environ["TOKEN"]
PGN_PATH = "caro.pgn"
MAX_CHAPTERS = 64

def split_pgns(pgn_text):
    games = []
    current = []
    for line in pgn_text.splitlines():
        if line.strip().startswith("[Event") and current:
            games.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        games.append("\n".join(current))
    return games

def get_game_title(pgn):
    for line in pgn.splitlines():
        if line.startswith("[Event "):
            return line.replace("[Event ", "").strip('[]"')
    return "Untitled Game"

def add_chapter(pgn, index):
    url = f"https://lichess.org/api/study/{STUDY_ID}/chapter"
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    title = get_game_title(pgn) or f"Game {index + 1}"
    data = {
        "name": title,
        "pgn": pgn
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code, title, response.text

def main():
    with open(PGN_PATH, "r", encoding="utf-8") as f:
        full_pgn = f.read()

    games = split_pgns(full_pgn)

    for idx, game in enumerate(games[:MAX_CHAPTERS]):
        status, title, raw = add_chapter(game, idx)
        if status != 200:
            print(f"Error adding chapter {idx+1}: {title}")
            print(raw)
            sys.exit(1)
        print(f"Added Chapter {idx+1}: {title}")

    if len(games) > MAX_CHAPTERS:
        print("Maximum chapters done")
        last_title = get_game_title(games[MAX_CHAPTERS - 1])
        print(f"Last PGN title: {last_title}")

if __name__ == "__main__":
    main()
