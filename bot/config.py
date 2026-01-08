import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Проверь файл .env (он должен лежать рядом с папкой bot).")
def _parse_admin_ids(value: str | None) -> set[int]:
    if not value:
        return set()
    parts = [p.strip() for p in value.split(",")]
    out: set[int] = set()
    for p in parts:
        if p.isdigit():
            out.add(int(p))
    return out

ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS"))