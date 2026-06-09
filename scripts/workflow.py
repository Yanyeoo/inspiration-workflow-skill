#!/usr/bin/env python3
"""
工作流状态跟踪模块 - workflow.py
用法：
  python workflow.py --action "完成了 XXX" --progress 30
  python workflow.py --blocker "遇到了 XXX 问题"
  python workflow.py --next "接下来应该 XXX"
  python workflow.py --status
  python workflow.py --clear-blockers
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_WORKFLOW_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "workflow-state.json"


def ensure_dirs(path: Path):
    """确保目录存在"""
    path.parent.mkdir(parents=True, exist_ok=True)


def load_workflow(file_path: Path) -> dict:
    """加载工作流状态"""
    if not file_path.exists():
        return {
            "version": "1.0",
            "current_task": "",
            "progress": 0,
            "history": [],
            "blockers": [],
            "next_steps": []
        }
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_workflow(file_path: Path, data: dict):
    """保存工作流状态"""
    ensure_dirs(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_action(data: dict, action: str, progress: int = None) -> dict:
    """记录用户做了什么"""
    now = datetime.now()
    entry = {
        "timestamp": now.isoformat(),
        "action": action,
        "progress": progress if progress is not None else data.get("progress", 0),
        "blockers": list(data.get("blockers", [])),
        "next_steps": list(data.get("next_steps", []))
    }
    data["history"].append(entry)
    data["current_task"] = action
    if progress is not None:
        data["progress"] = progress
    return data


def update_progress(data: dict, progress: int) -> dict:
    """更新进度"""
    data["progress"] = progress
    if data.get("history"):
        data["history"][-1]["progress"] = progress
    return data


def add_blocker(data: dict, blocker: str) -> dict:
    """记录遇到的困难"""
    if blocker not in data["blockers"]:
        data["blockers"].append(blocker)
    if data.get("history"):
        if blocker not in data["history"][-1]["blockers"]:
            data["history"][-1]["blockers"].append(blocker)
    return data


def remove_blocker(data: dict, blocker: str) -> dict:
    """移除困难（已解决）"""
    if blocker in data["blockers"]:
        data["blockers"].remove(blocker)
    for h in data["history"]:
        if blocker in h["blockers"]:
            h["blockers"].remove(blocker)
    return data


def add_next_step(data: dict, step: str) -> dict:
    """添加 AI 推荐的下一步"""
    if step not in data["next_steps"]:
        data["next_steps"].append(step)
    if data.get("history"):
        if step not in data["history"][-1]["next_steps"]:
            data["history"][-1]["next_steps"].append(step)
    return data


def remove_next_step(data: dict, step: str) -> dict:
    """移除已完成的下一步"""
    if step in data["next_steps"]:
        data["next_steps"].remove(step)
    for h in data["history"]:
        if step in h["next_steps"]:
            h["next_steps"].remove(step)
    return data


def print_status(data: dict):
    """打印当前状态"""
    print(f"# 工作流状态报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print(f"> 当前任务：{data.get('current_task', '未设置')}")
    print(f"> 进度：{data.get('progress', 0)}%\n")
    print("-" * 40)

    print(f"\n## ✅ 已完成的工作（最近 5 条）\n")
    history = data.get("history", [])
    for h in history[-5:]:
        ts = h["timestamp"][:16]
        print(f"### [{ts}] {h['action']}")
        print(f"进度：{h.get('progress', 0)}%")
        if h.get("blockers"):
            print(f"困难：{', '.join(h['blockers'])}")
        if h.get("next_steps"):
            print(f"下一步：{', '.join(h['next_steps'])}")
        print()

    print("-" * 40)

    print(f"\n## ⚠️ 当前困难\n")
    blockers = data.get("blockers", [])
    if blockers:
        for b in blockers:
            print(f"- {b}")
    else:
        print("暂无困难。")

    print(f"\n## 🚀 推荐下一步\n")
    next_steps = data.get("next_steps", [])
    if next_steps:
        for ns in next_steps:
            print(f"- {ns}")
    else:
        print("暂无推荐。")

    print()


def main():
    parser = argparse.ArgumentParser(description="工作流状态跟踪模块")
    parser.add_argument("--file", type=str, default=str(DEFAULT_WORKFLOW_FILE), help="工作流状态文件路径")
    parser.add_argument("--action", type=str, help="记录做了什么")
    parser.add_argument("--progress", type=int, help="更新进度（0-100）")
    parser.add_argument("--blocker", type=str, help="记录遇到的困难")
    parser.add_argument("--clear-blockers", action="store_true", help="清除所有困难")
    parser.add_argument("--next", type=str, help="添加推荐下一步")
    parser.add_argument("--clear-next", action="store_true", help="清除所有推荐下一步")
    parser.add_argument("--status", action="store_true", help="查看当前状态")

    args = parser.parse_args()

    file_path = Path(args.file)
    data = load_workflow(file_path)

    changed = False

    if args.action:
        data = update_action(data, args.action, args.progress)
        print(f"✅ 已记录动作：{args.action}")
        changed = True

    if args.progress is not None and not args.action:
        data = update_progress(data, args.progress)
        print(f"✅ 已更新进度：{args.progress}%")
        changed = True

    if args.blocker:
        data = add_blocker(data, args.blocker)
        print(f"✅ 已记录困难：{args.blocker}")
        changed = True

    if args.clear_blockers:
        data["blockers"] = []
        # 同时清空 history 中的 blockers
        for h in data["history"]:
            h["blockers"] = []
        print("✅ 已清除所有困难")
        changed = True

    if args.next:
        data = add_next_step(data, args.next)
        print(f"✅ 已添加推荐下一步：{args.next}")
        changed = True

    if args.clear_next:
        data["next_steps"] = []
        for h in data["history"]:
            h["next_steps"] = []
        print("✅ 已清除所有推荐下一步")
        changed = True

    # 查看状态（显式指定 --status，或无操作参数时默认显示）
    if args.status or not changed:
        print_status(data)

    # 只有数据变更时才保存
    if changed:
        save_workflow(file_path, data)
        print(f"💾 已保存到 {file_path}")


if __name__ == "__main__":
    main()
