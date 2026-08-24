"""幂等写入面试题库种子数据。"""

from __future__ import annotations

import os
from pathlib import Path

from filemate.execution.storage import SQLiteStorage
from filemate.understanding.interview_bank_seed import SEED_QUESTIONS

ROOT = Path(__file__).resolve().parents[1]
db_path = os.getenv(
    "FILEMATE_DB_PATH",
    str(ROOT / ".filemate-data" / "filemate.db"),
)


def main() -> None:
    storage = SQLiteStorage(db_path)
    storage.init_schema()
    ids = storage.ensure_interview_questions(SEED_QUESTIONS)
    print(f"SEEDED {len(ids)} questions -> {db_path}")


if __name__ == "__main__":
    main()
