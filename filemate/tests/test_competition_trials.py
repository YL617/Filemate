"""竞赛对照实验分析工具测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from evaluation.analyze_competition_trials import (
    analyze_agent_trials,
    analyze_companion_trials,
    analyze_interview_trials,
)


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_agent_trial_report_keeps_small_sample_pending(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "agent.csv",
        "participant_id,task_id,condition,completed,hallucination_count,"
        "reviewed_claim_count,elapsed_seconds,model_calls,estimated_cost_yuan\n"
        "P001,T01,single_agent,1,1,10,90,4,0.08\n"
        "P002,T01,multi_agent,1,0,10,80,3,0.06\n",
    )

    report = analyze_agent_trials(path)

    assert report["status"] == "pending_more_samples"
    assert report["conditions"]["single_agent"]["hallucination_rate"] == 0.1
    assert report["conditions"]["multi_agent"]["task_completion_rate"] == 1.0


def test_interview_trial_calculates_expert_alignment(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "interview.csv",
        "participant_id,attempt_id,condition,completed,system_score,"
        "expert_score_a,expert_score_b,words_per_minute,long_pause_count\n"
        "P001,A01,text,1,70,68,72,0,0\n"
        "P002,A02,text,1,80,78,82,0,0\n"
        "P003,A03,multimodal,1,75,73,77,135,2\n"
        "P004,A04,multimodal,1,85,83,87,142,1\n",
    )

    report = analyze_interview_trials(path)

    assert report["status"] == "pending_more_samples"
    assert report["conditions"]["multimodal"]["system_expert_mae"] == 0
    assert report["conditions"]["multimodal"]["system_expert_correlation"] == 1


def test_companion_trial_rejects_header_only_template(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "companion.csv",
        "participant_id,condition,assigned_tasks,completed_tasks,due_reviews,"
        "completed_reviews,returned_next_day\n",
    )

    with pytest.raises(ValueError, match="尚无真实实验记录"):
        analyze_companion_trials(path)
