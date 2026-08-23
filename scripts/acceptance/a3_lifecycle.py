"""A3 数据生命周期验收：创建 → 重启可读 → 删除预览 → 删除 → 外部文件保留 → 重复删除 404。"""

import json
import os
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="fm_a3_"))
external_file = tmp / "external.txt"
external_file.write_text("external file should survive", encoding="utf-8")

os.environ["FILEMATE_DB_PATH"] = str(tmp / "a3.db")
os.environ["FILEMATE_DATA_DIR"] = str(tmp / "data")
os.environ["FILEMATE_UPLOAD_DIR"] = str(tmp / "inbox")
os.environ["FILEMATE_ARCHIVE_DIR"] = str(tmp / "archive")

import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

source_id = server._storage.save_source(
    original_name="external.txt",
    source_path=str(external_file),
    raw_text="external content",
    media_type="text/plain",
)
server._storage.save_artifact(
    artifact_type="notes",
    source_id=source_id,
    title="derived artifact",
    content={"text": "derived"},
)

client = TestClient(server.app)
report = {"source_id": source_id, "steps": []}

# 重启可读：用新的存储实例读取同一数据库
from filemate.execution.storage import SQLiteStorage  # noqa: E402

restarted = SQLiteStorage(str(tmp / "a3.db"))
restarted.init_schema()
report["steps"].append(
    {
        "step": "restart_readable",
        "source_exists": restarted.get_source(source_id) is not None,
    }
)

preview = server._storage.preview_source_deletion(source_id)
report["steps"].append({"step": "delete_preview", "affected": preview["affected"]})

delete_resp = client.delete(f"/knowledge/sources/{source_id}")
report["steps"].append(
    {
        "step": "delete_source",
        "status": delete_resp.status_code,
        "success": delete_resp.json()["success"],
    }
)

report["steps"].append(
    {
        "step": "external_file_untouched",
        "exists": external_file.exists(),
    }
)

get_after = client.get(f"/knowledge/sources/{source_id}")
report["steps"].append(
    {
        "step": "get_after_delete",
        "status": get_after.status_code,
    }
)

delete_again = client.delete(f"/knowledge/sources/{source_id}")
report["steps"].append(
    {
        "step": "delete_again",
        "status": delete_again.status_code,
    }
)

out = Path(os.getcwd()) / "_working" / "a3-lifecycle.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
