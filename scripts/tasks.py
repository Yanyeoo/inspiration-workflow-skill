#!/usr/bin/env python3
"""
任务管理模块 - tasks.py（v2.0）
用法：
  python tasks.py --new-task "开发灵感库 Skill"
  python tasks.py --switch 1
  python tasks.py --list
  python tasks.py --status
  python tasks.py --action "完成了 XXX" --progress 30
  python tasks.py --blocker "遇到了 XXX 问题"
  python tasks.py --next "接下来应该 XXX"
  python tasks.py --done
  python tasks.py --active-task   # 供 capture.py 读取当前活跃任务
"""

import json
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

DEFAULT_TASKS_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "tasks.json"
DEFAULT_INSP_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "inspirations.json"


def ensure_dirs(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def load_tasks(file_path: Path) -> dict:
    if not file_path.exists():
        return {
            "version": "2.0",
            "active_task_id": None,
            "tasks": []
        }
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 兼容 v1.0：如果是旧格式，迁移
        if "version" not in data or data.get("version") == "1.0":
            return _migrate_v1_to_v2(data, file_path)
        return data


def _migrate_v1_to_v2(old_data: dict, file_path: Path) -> dict:
    """将 v1.0 workflow-state.json 迁移到 v2.0 tasks.json"""
    import time
    tid = f"task_{int(time.time())}"
    new_data = {
        "version": "2.0",
        "active_task_id": tid,
        "tasks": [
            {
                "id": tid,
                "name": old_data.get("current_task", "未命名任务"),
                "status": "active",
                "progress": old_data.get("progress", 0),
                "created_at": datetime.now().isoformat(),
                "done": False,
                "history": old_data.get("history", []),
                "blockers": list(old_data.get("blockers", [])),
                "next_steps": list(old_data.get("next_steps", [])),
                "knowledge_count": 0
            }
        ]
    }
    ensure_dirs(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    return new_data


def save_tasks(file_path: Path, data: dict):
    ensure_dirs(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_active_task(data: dict) -> dict | None:
    tid = data.get("active_task_id")
    if not tid:
        return None
    for t in data["tasks"]:
        if t["id"] == tid:
            return t
    return None


def gen_task_id(data: dict) -> str:
    import time
    return f"task_{int(time.time())}_{len(data['tasks']):03d}"


def cmd_new_task(data: dict, file_path: Path, name: str) -> dict:
    tid = gen_task_id(data)
    now = datetime.now()
    task = {
        "id": tid,
        "name": name,
        "status": "active",
        "progress": 0,
        "created_at": now.isoformat(),
        "done": False,
        "history": [],
        "blockers": [],
        "next_steps": [],
        "knowledge_count": 0
    }
    data["tasks"].append(task)
    data["active_task_id"] = tid
    save_tasks(file_path, data)
    print(f"✅ 已创建任务：[{name}]")
    print(f"   当前活跃任务已切换至此。进度：0% | 知识库：0 条")
    return data


def cmd_switch(data: dict, file_path: Path, arg: str) -> dict:
    # arg 可以是数字索引（从1开始）或 task_id
    tasks = data["tasks"]
    if not tasks:
        print("⚠️ 暂无任务，用 --new-task 创建。")
        return data

    # 按数字索引切换
    if arg.isdigit():
        idx = int(arg) - 1
        if idx < 0 or idx >= len(tasks):
            print(f"⚠️ 编号 {arg} 不存在，当前共 {len(tasks)} 个任务。")
            return data
        tid = tasks[idx]["id"]
    else:
        # 按 task_id 或名称模糊匹配
        tid = None
        for t in tasks:
            if t["id"] == arg:
                tid = arg
                break
            if arg.lower() in t["name"].lower():
                tid = t["id"]
                break
        if not tid:
            print(f"⚠️ 找不到任务：{arg}")
            return data

    data["active_task_id"] = tid
    t = next(t for t in tasks if t["id"] == tid)
    save_tasks(file_path, data)
    status_icon = "✅" if t["done"] else ("🚀" if t["status"] == "active" else "📦")
    print(f"✅ 已切换到：{status_icon} [{t['name']}]")
    print(f"   进度：{t['progress']}% | 知识库：{t['knowledge_count']} 条")
    return data


def cmd_list(data: dict, file_path: Path) -> dict:
    tasks = data["tasks"]
    if not tasks:
        print("暂无任务。用 --new-task 创建第一个任务吧！")
        return data

    active_id = data.get("active_task_id")
    print("📋 任务列表：\n")
    for i, t in enumerate(tasks, 1):
        icon = "✅" if t["done"] else ("🚀" if t["status"] == "active" else "📦")
        active_marker = " ← 活跃" if t["id"] == active_id else ""
        print(f"  {i}. {icon} [{t['name']}]")
        print(f"       进度：{t['progress']}% | 知识库：{t['knowledge_count']} 条{active_marker}")
        if t.get("next_steps"):
            print(f"       下一步：{t['next_steps'][0]}")
        print()
    return data


def cmd_status(data: dict, file_path: Path) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。用 --new-task 创建或 --switch 切换。")
        return data

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"# 任务状态报告 - {now_str}\n")
    print(f"🚀 当前任务：{t['name']}")
    print(f"📊 进度：{t['progress']}%\n")
    print("-" * 40)

    print(f"\n## ✅ 已完成的工作（最近 5 条）\n")
    history = t.get("history", [])
    if history:
        for h in history[-5:]:
            ts = h["timestamp"][:16]
            print(f"  [{ts}] {h['action']}")
            print(f"  进度：{h.get('progress', 0)}%")
            if h.get("blockers"):
                print(f"  困难：{', '.join(h['blockers'])}")
            if h.get("next_steps"):
                print(f"  下一步：{', '.join(h['next_steps'])}")
            print()
    else:
        print("  （暂无记录）\n")

    print("-" * 40)
    print(f"\n## ⚠️ 当前困难\n")
    blockers = t.get("blockers", [])
    if blockers:
        for b in blockers:
            print(f"  - {b}")
    else:
        print("  暂无困难。")

    print(f"\n## 🚀 推荐下一步\n")
    next_steps = t.get("next_steps", [])
    if next_steps:
        for ns in next_steps:
            print(f"  - {ns}")
    else:
        print("  暂无推荐。")

    print(f"\n## 📚 知识库\n")
    print(f"  共 {t.get('knowledge_count', 0)} 条知识")
    print()
    return data


def cmd_action(data: dict, file_path: Path, action: str, progress: int = None) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。先用 --new-task 创建。")
        return data

    now = datetime.now()
    entry = {
        "timestamp": now.isoformat(),
        "action": action,
        "progress": progress if progress is not None else t.get("progress", 0),
        "blockers": list(t.get("blockers", [])),
        "next_steps": list(t.get("next_steps", []))
    }
    t.setdefault("history", []).append(entry)
    if progress is not None:
        t["progress"] = progress
    save_tasks(file_path, data)
    print(f"✅ 已记录到 [{t['name']}]：{action}")
    return data


def cmd_progress(data: dict, file_path: Path, progress: int) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。")
        return data
    t["progress"] = progress
    if t.get("history"):
        t["history"][-1]["progress"] = progress
    save_tasks(file_path, data)
    print(f"✅ [{t['name']}] 进度已更新：{progress}%")
    return data


def cmd_blocker(data: dict, file_path: Path, blocker: str) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。")
        return data
    if blocker not in t["blockers"]:
        t["blockers"].append(blocker)
    if t.get("history"):
        if blocker not in t["history"][-1].get("blockers", []):
            t["history"][-1].setdefault("blockers", []).append(blocker)
    save_tasks(file_path, data)
    print(f"✅ 已记录困难到 [{t['name']}]：{blocker}")
    return data


def cmd_clear_blockers(data: dict, file_path: Path) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。")
        return data
    t["blockers"] = []
    for h in t.get("history", []):
        h["blockers"] = []
    save_tasks(file_path, data)
    print(f"✅ 已清除 [{t['name']}] 的所有困难。")
    return data


def cmd_next(data: dict, file_path: Path, step: str) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。")
        return data
    if step not in t["next_steps"]:
        t["next_steps"].append(step)
    if t.get("history"):
        if step not in t["history"][-1].get("next_steps", []):
            t["history"][-1].setdefault("next_steps", []).append(step)
    save_tasks(file_path, data)
    print(f"✅ 已添加推荐下一步到 [{t['name']}]：{step}")
    return data


def cmd_clear_next(data: dict, file_path: Path) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。")
        return data
    t["next_steps"] = []
    for h in t.get("history", []):
        h["next_steps"] = []
    save_tasks(file_path, data)
    print(f"✅ 已清除 [{t['name']}] 的所有推荐下一步。")
    return data


def cmd_done(data: dict, file_path: Path) -> dict:
    t = get_active_task(data)
    if not t:
        print("⚠️ 暂无活跃任务。")
        return data
    t["done"] = True
    t["status"] = "done"
    t["progress"] = 100
    save_tasks(file_path, data)
    print(f"✅ 任务已完成：[{t['name']}] 🎉")
    return data


def cmd_active_task(data: dict) -> dict:
    """仅输出活跃任务 ID 和名称（供 capture.py 调用）"""
    t = get_active_task(data)
    if not t:
        print("NONE")
    else:
        print(f"{t['id']}|{t['name']}")
    return data


def update_knowledge_count(tasks_file: Path, insp_file: Path):
    """根据 inspirations.json 更新每个任务的 knowledge_count"""
    if not tasks_file.exists() or not insp_file.exists():
        return
    data = load_tasks(tasks_file)
    with open(insp_file, "r", encoding="utf-8") as f:
        insp_data = json.load(f)
    entries = insp_data.get("entries", [])
    # 统计每个 task_id 的数量
    counts = {}
    for e in entries:
        tid = e.get("task_id")
        if tid:
            counts[tid] = counts.get(tid, 0) + 1
    # 更新
    changed = False
    for t in data["tasks"]:
        new_count = counts.get(t["id"], 0)
        if t.get("knowledge_count") != new_count:
            t["knowledge_count"] = new_count
            changed = True
    if changed:
        save_tasks(tasks_file, data)


def main():
    parser = argparse.ArgumentParser(description="任务管理模块 v2.0")
    parser.add_argument("--file", type=str, default=str(DEFAULT_TASKS_FILE), help="tasks.json 文件路径")
    parser.add_argument("--new-task", type=str, help="创建新任务并设为活跃")
    parser.add_argument("--switch", type=str, help="切换活跃任务（编号或名称）")
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--status", action="store_true", help="查看活跃任务状态")
    parser.add_argument("--action", type=str, help="记录做了什么（活跃任务）")
    parser.add_argument("--progress", type=int, help="更新进度（0-100）")
    parser.add_argument("--blocker", type=str, help="记录困难")
    parser.add_argument("--clear-blockers", action="store_true", help="清除所有困难")
    parser.add_argument("--next", type=str, help="添加推荐下一步")
    parser.add_argument("--clear-next", action="store_true", help="清除所有推荐下一步")
    parser.add_argument("--done", action="store_true", help="标记活跃任务为完成")
    parser.add_argument("--active-task", action="store_true", help="输出当前活跃任务（供脚本调用）")
    parser.add_argument("--sync-knowledge-count", action="store_true", help="从 inspirations.json 同步知识库数量")

    args = parser.parse_args()
    file_path = Path(args.file)

    # --sync-knowledge-count 需要同时读 tasks.json 和 inspirations.json
    if args.sync_knowledge_count:
        update_knowledge_count(file_path, DEFAULT_INSP_FILE)
        print("✅ 已同步知识库数量")
        return

    data = load_tasks(file_path)

    # --active-task：纯输出，不修改
    if args.active_task:
        cmd_active_task(data)
        return

    changed = False

    if args.new_task:
        data = cmd_new_task(data, file_path, args.new_task)
        changed = True

    if args.switch:
        data = cmd_switch(data, file_path, args.switch)
        changed = True

    if args.list:
        data = cmd_list(data, file_path)

    if args.status:
        data = cmd_status(data, file_path)

    if args.action:
        data = cmd_action(data, file_path, args.action, args.progress)
        changed = True

    if args.progress is not None and not args.action:
        data = cmd_progress(data, file_path, args.progress)
        changed = True

    if args.blocker:
        data = cmd_blocker(data, file_path, args.blocker)
        changed = True

    if args.clear_blockers:
        data = cmd_clear_blockers(data, file_path)
        changed = True

    if args.next:
        data = cmd_next(data, file_path, args.next)
        changed = True

    if args.clear_next:
        data = cmd_clear_next(data, file_path)
        changed = True

    if args.done:
        data = cmd_done(data, file_path)
        changed = True

    # 如果没有任何参数，默认显示 --list
    if not any([args.new_task, args.switch, args.list, args.status,
                args.action, args.progress is not None,
                args.blocker, args.clear_blockers,
                args.next, args.clear_next, args.done, args.active_task,
                args.sync_knowledge_count]):
        data = cmd_list(data, file_path)


if __name__ == "__main__":
    main()
