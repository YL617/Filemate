"""流程 4 API 闭环验收：出题 → 作答 → 错题 → 今日复习 → 掌握。"""

import json
import os
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="fm_flow4_"))
os.environ["FILEMATE_DB_PATH"] = str(tmp / "flow4.db")
os.environ["FILEMATE_DATA_DIR"] = str(tmp / "data")
os.environ["FILEMATE_UPLOAD_DIR"] = str(tmp / "inbox")
os.environ["FILEMATE_ARCHIVE_DIR"] = str(tmp / "archive")

import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

artifact_id = server._storage.save_artifact(
    artifact_type="questions",
    title="Flow4 Acceptance",
    content=[
        {
            "question": "1+1=?",
            "answer": "2",
            "explanation": "基础加法",
        }
    ],
)

client = TestClient(server.app)
report = {"artifact_id": artifact_id, "steps": []}


def submit(answer: str):
    return client.post(
        "/quiz/attempts",
        json={
            "artifact_id": artifact_id,
            "question_index": 0,
            "user_answer": answer,
        },
    )


def wrongbook(mastered: bool):
    return client.get(f"/wrongbook?mastered={str(mastered).lower()}")


wrong = submit("wrong")
report["steps"].append(
    {"step": "submit_wrong", "status": wrong.status_code, "data": wrong.json()["data"]}
)

book_false_1 = wrongbook(False)
report["steps"].append(
    {
        "step": "wrongbook_after_wrong",
        "status": book_false_1.status_code,
        "count": len(book_false_1.json()["data"]),
        "has_question": any(
            item.get("artifact_id") == artifact_id
            for item in book_false_1.json()["data"]
        ),
    }
)

today = client.get("/review/today")
report["steps"].append(
    {
        "step": "today_review_after_wrong",
        "status": today.status_code,
        "has_wrong_item": any(
            item.get("artifact_id") == artifact_id
            for item in today.json()["data"].get("items", [])
        ),
    }
)

correct_1 = submit("2")
report["steps"].append(
    {
        "step": "submit_correct_1",
        "status": correct_1.status_code,
        "is_correct": correct_1.json()["data"]["is_correct"],
    }
)
book_false_2 = wrongbook(False)
report["steps"].append(
    {
        "step": "wrongbook_after_correct_1",
        "count": len(book_false_2.json()["data"]),
        "still_pending": any(
            item.get("artifact_id") == artifact_id
            for item in book_false_2.json()["data"]
        ),
    }
)

correct_2 = submit("2")
report["steps"].append(
    {
        "step": "submit_correct_2",
        "status": correct_2.status_code,
        "is_correct": correct_2.json()["data"]["is_correct"],
    }
)
book_true = wrongbook(True)
report["steps"].append(
    {
        "step": "wrongbook_mastered",
        "count": len(book_true.json()["data"]),
        "has_question": any(
            item.get("artifact_id") == artifact_id
            for item in book_true.json()["data"]
        ),
    }
)
book_false_3 = wrongbook(False)
report["steps"].append(
    {
        "step": "wrongbook_pending_after_mastered",
        "count": len(book_false_3.json()["data"]),
    }
)

out = Path(os.getcwd()) / "_working" / "flow4-acceptance.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
