"""生成合成问答对评测集种子（明确标记 synthetic=true）。

真实学习资料授权到位后，应替换或扩充为真实问答对，并去掉 synthetic 标记。
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_TOPICS = [
    (
        "操作系统",
        "进程与线程的区别是什么？",
        "进程是资源分配单位，线程是 CPU 调度单位；同进程内线程共享地址空间。",
    ),
    (
        "计算机网络",
        "TCP 与 UDP 的主要区别是什么？",
        "TCP 面向连接、可靠、有序；UDP 无连接、不可靠、开销小。",
    ),
    ("数据库", "ACID 分别指什么？", "原子性、一致性、隔离性、持久性。"),
    ("算法", "稳定排序和不稳定排序有什么区别？", "稳定排序保持相等元素的原始相对顺序。"),
    ("机器学习", "过拟合如何缓解？", "增加数据、正则化、早停、交叉验证。"),
    (
        "软件工程",
        "单元测试和集成测试的区别是什么？",
        "单元测试验证单一模块，集成测试验证模块间协作。",
    ),
    ("数学", "导数的几何意义是什么？", "导数是函数在某点的切线斜率。"),
    ("编译原理", "词法分析和语法分析的区别是什么？", "词法分析生成 token，语法分析构建语法树。"),
    (
        "安全",
        "哈希函数和加密的区别是什么？",
        "哈希不可逆，加密可逆；哈希用于完整性，加密用于机密性。",
    ),
    ("项目管理", "什么是关键路径？", "项目中最长依赖路径，决定最短工期。"),
]


def generate(count: int = 30) -> list[dict]:
    """生成 count 条合成问答对。"""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    pairs: list[dict] = []
    for index in range(count):
        topic, question, reference = _TOPICS[index % len(_TOPICS)]
        pairs.append(
            {
                "id": f"syn-{index + 1:03d}",
                "source_id": "synthetic-source",
                "topic": topic,
                "question": question,
                "gold_chunk_ids": [],
                "reference": reference,
                "synthetic": True,
                "status": "draft",
                "created_at": now,
            }
        )
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "evaluation" / "datasets" / "qa_pairs_v1.synthetic.json",
    )
    args = parser.parse_args()
    data = generate(args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"WROTE {len(data)} pairs -> {args.output}")


if __name__ == "__main__":
    main()
