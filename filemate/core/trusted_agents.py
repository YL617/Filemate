"""可信多 Agent 的按需路由与角色目录。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrustedAgentRole:
    """描述一个可审计的后台 Agent 角色。"""

    name: str
    responsibility: str


TRUSTED_AGENT_ROLES = (
    TrustedAgentRole("规划 Agent", "理解目标并拆解任务，不直接改动用户文件"),
    TrustedAgentRole("资料 Agent", "检索本地资料并返回可定位引用"),
    TrustedAgentRole("学习教练 Agent", "把资料转化为学习任务与复习路径"),
    TrustedAgentRole("面试 Agent", "按场景选择问题并组织连续追问"),
    TrustedAgentRole("评价 Agent", "基于作答证据给出评分与改进建议"),
    TrustedAgentRole("安全 Agent", "检查授权、分享范围与高风险操作"),
)

_TASK_ROUTES: dict[str, tuple[str, ...]] = {
    "interview_session": ("面试 Agent", "评价 Agent"),
    "source_rights": ("安全 Agent",),
    "file_confirmation": ("安全 Agent",),
    "memory_deletion": ("安全 Agent",),
    "knowledge_answer": ("资料 Agent", "学习教练 Agent"),
    "study_plan": ("规划 Agent", "学习教练 Agent"),
}


def select_agents(task_type: str) -> list[str]:
    """按任务选择最少必要角色，未知任务不伪造 Agent。"""
    return list(_TASK_ROUTES.get(task_type, ()))


def describe_roles() -> list[dict[str, str]]:
    """返回角色能力目录；该目录不代表角色正在运行。"""
    return [
        {"name": role.name, "responsibility": role.responsibility}
        for role in TRUSTED_AGENT_ROLES
    ]
