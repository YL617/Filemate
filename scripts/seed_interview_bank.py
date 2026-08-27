"""幂等写入面试题库种子数据。"""

from __future__ import annotations

import os
from pathlib import Path

from filemate.execution.storage import SQLiteStorage
from filemate.understanding.interview_bank_seed import SEED_QUESTIONS

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(
    os.getenv(
        "FILEMATE_DB_PATH",
        str(ROOT / ".filemate-data" / "filemate.db"),
    )
).expanduser().resolve()


def main() -> None:
    storage = SQLiteStorage(DB_PATH)
    try:
        storage.init_schema()
        ids = storage.ensure_interview_questions(SEED_QUESTIONS)
        print(f"ENSURED {len(ids)} questions -> {DB_PATH}")
    finally:
        storage.close()


if __name__ == "__main__":
    main()
