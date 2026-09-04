"""汇总多 Agent、多模态面试与学习伙伴对照实验。"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any


def _read_rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name} 缺少字段：{', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name} 尚无真实实验记录")
    return rows


def _number(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"字段 {field} 必须是数字") from exc


def _correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(right) != len(left):
        return None
    left_mean = fmean(left)
    right_mean = fmean(right)
    numerator = sum(
        (first - left_mean) * (second - right_mean)
        for first, second in zip(left, right, strict=True)
    )
    left_scale = math.sqrt(sum((item - left_mean) ** 2 for item in left))
    right_scale = math.sqrt(sum((item - right_mean) ** 2 for item in right))
    if not left_scale or not right_scale:
        return None
    return round(numerator / (left_scale * right_scale), 4)


def _study_status(groups: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    counts = {
        condition: len({row["participant_id"] for row in rows})
        for condition, rows in groups.items()
    }
    sufficient = len(groups) >= 2 and all(count >= 15 for count in counts.values())
    return {
        "status": "sufficient" if sufficient else "pending_more_samples",
        "participant_count_by_condition": counts,
        "minimum_required": "至少两个条件，每个条件 15 名匿名参与者",
    }


def analyze_agent_trials(path: Path) -> dict[str, Any]:
    """比较单 Agent 与按需多 Agent 的任务结果。"""
    required = {
        "participant_id",
        "condition",
        "completed",
        "hallucination_count",
        "reviewed_claim_count",
        "elapsed_seconds",
        "model_calls",
        "estimated_cost_yuan",
    }
    rows = _read_rows(path, required)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)
    metrics = {}
    for condition, items in groups.items():
        reviewed = sum(_number(item, "reviewed_claim_count") for item in items)
        hallucinations = sum(_number(item, "hallucination_count") for item in items)
        metrics[condition] = {
            "trial_count": len(items),
            "task_completion_rate": round(
                fmean(_number(item, "completed") for item in items), 4
            ),
            "hallucination_rate": round(hallucinations / reviewed, 4)
            if reviewed
            else None,
            "mean_elapsed_seconds": round(
                fmean(_number(item, "elapsed_seconds") for item in items), 2
            ),
            "mean_model_calls": round(
                fmean(_number(item, "model_calls") for item in items), 2
            ),
            "mean_estimated_cost_yuan": round(
                fmean(_number(item, "estimated_cost_yuan") for item in items), 4
            ),
        }
    return {**_study_status(groups), "conditions": metrics}


def analyze_interview_trials(path: Path) -> dict[str, Any]:
    """比较文字与多模态面试，并检查系统分与导师盲评分相关性。"""
    required = {
        "participant_id",
        "condition",
        "completed",
        "system_score",
        "expert_score_a",
        "expert_score_b",
        "words_per_minute",
        "long_pause_count",
    }
    rows = _read_rows(path, required)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)
    metrics = {}
    for condition, items in groups.items():
        system_scores = [_number(item, "system_score") for item in items]
        expert_scores = [
            (_number(item, "expert_score_a") + _number(item, "expert_score_b")) / 2
            for item in items
        ]
        metrics[condition] = {
            "trial_count": len(items),
            "completion_rate": round(
                fmean(_number(item, "completed") for item in items), 4
            ),
            "mean_expert_score": round(fmean(expert_scores), 2),
            "system_expert_mae": round(
                fmean(
                    abs(system - expert)
                    for system, expert in zip(
                        system_scores, expert_scores, strict=True
                    )
                ),
                2,
            ),
            "system_expert_correlation": _correlation(
                system_scores, expert_scores
            ),
            "mean_words_per_minute": round(
                fmean(_number(item, "words_per_minute") for item in items), 2
            ),
            "mean_long_pause_count": round(
                fmean(_number(item, "long_pause_count") for item in items), 2
            ),
        }
    return {**_study_status(groups), "conditions": metrics}


def analyze_companion_trials(path: Path) -> dict[str, Any]:
    """比较普通提醒与学习伙伴反馈的执行和次日返回。"""
    required = {
        "participant_id",
        "condition",
        "assigned_tasks",
        "completed_tasks",
        "due_reviews",
        "completed_reviews",
        "returned_next_day",
    }
    rows = _read_rows(path, required)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)
    metrics = {}
    for condition, items in groups.items():
        assigned = sum(_number(item, "assigned_tasks") for item in items)
        completed = sum(_number(item, "completed_tasks") for item in items)
        due = sum(_number(item, "due_reviews") for item in items)
        reviewed = sum(_number(item, "completed_reviews") for item in items)
        metrics[condition] = {
            "participant_count": len({item["participant_id"] for item in items}),
            "task_completion_rate": round(completed / assigned, 4)
            if assigned
            else None,
            "due_review_completion_rate": round(reviewed / due, 4)
            if due
            else None,
            "next_day_return_rate": round(
                fmean(_number(item, "returned_next_day") for item in items), 4
            ),
        }
    return {**_study_status(groups), "conditions": metrics}


def main() -> None:
    """生成机器可读竞赛实验报告。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=Path, required=True)
    parser.add_argument("--interview", type=Path, required=True)
    parser.add_argument("--companion", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "data_kind": "real_anonymous_user_trial",
        "agent_ab": analyze_agent_trials(args.agent),
        "interview_ab": analyze_interview_trials(args.interview),
        "companion_ab": analyze_companion_trials(args.companion),
        "notice": "样本门槛未达到时只能标记为待评测，不得形成效果结论。",
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
