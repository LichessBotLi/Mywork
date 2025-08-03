import requests
import os

STUDY_ID = "MlAhgrv3"
TOKEN = os.environ["TOKEN"]
PGN_PATH = "caro.pgn"
MAX_CHAPTERS = 63  # not 64 since 1 chapter already exists

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

def get_title(pgn):
    for line in pgn.splitlines():
        if line.startswith("[Event "):
            return line.replace("[Event ", "").strip('[]"')
    return "Untitled"

def upload_chapter(pgn, index):
    url = f"https://lichess.org/api/study/{STUDY_ID}/chapter"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    title = get_title(pgn)
    data = {"name": title, "pgn": pgn}
    res = requests.post(url, headers=headers, data=data)
    if res.status_code != 200:
        print(f"Error {res.status_code}: {res.text}")
    return res.status_code, title

def main():
    with open(PGN_PATH, encoding="utf-8") as f:
        pgn = f.read()

    games = split_pgns(pgn)

    for i, game in enumerate(games[:MAX_CHAPTERS]):
        code, title = upload_chapter(game, i)
        if code == 200:
            print(f"Chapter {i+1} added: {title}")
        else:
            print(f"Failed at chapter {i+1}")
            exit(1)

    if len(games) > MAX_CHAPTERS:
        print("Maximum chapters done")
        print(f"Last PGN title: {get_title(games[MAX_CHAPTERS - 1])}")

if __name__ == "__main__":
    main()
