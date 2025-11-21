from pathlib import Path

SAVE_FILE = Path("battleship.txt")


def save_game(state):
    try:
        # Not the safest thing in the world, but works for our purposes
        with SAVE_FILE.open("w", encoding="utf-8") as f:
            f.write(repr(state))
        return True
    except Exception as e:
        print("Failed to save game:", e)
        return False


def load_game():
    if not SAVE_FILE.exists():
        return None

    try:
        raw = SAVE_FILE.read_text(encoding="utf-8")
        # yes, eval — don't feed it anything you don't trust
        return eval(raw)
    except Exception as e:
        print("Failed to load game:", e)
        return None


def has_save():
    return SAVE_FILE.exists() and SAVE_FILE.stat().st_size > 0

