#!/usr/bin/env python3
"""
自动压缩模块 - compress.py (v2.0)
用法：
  python compress.py                          # 全局压缩（默认阈值 50）
  python compress.py --task-id task_xxx       # 按任务压缩（默认阈值 30）
  python compress.py --task-name "任务名"
  python compress.py --dry-run
  python compress.py --threshold 30
  python compress.py --output reviews/
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
import re

DEFAULT_INSP_DIR = Path.home() / ".workbuddy" / "memory" / "inspirations"
DEFAULT_INSP_FILE = DEFAULT_INSP_DIR / "inspirations.json"
DEFAULT_TASKS_FILE = DEFAULT_INSP_DIR / "tasks.json"

GLOBAL_THRESHOLD = 50
TASK_THRESHOLD = 30


def ensure_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def load_inspirations(file_path: Path) -> dict:
    if not file_path.exists():
        print(f"错误：灵感库文件不存在：{file_path}", file=sys.stderr)
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inspirations(file_path: Path, data: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tasks(file_path: Path) -> dict:
    if not file_path.exists():
        return {"version": "2.0", "active_task_id": None, "tasks": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_task_name(task_id: str) -> str:
    """根据 task_id 获取任务名称（用于命名综述文件）"""
    if not DEFAULT_TASKS_FILE.exists():
        return task_id
    try:
        with open(DEFAULT_TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for t in data.get("tasks", []):
            if t["id"] == task_id:
                # 清理文件名中的特殊字符
                name = re.sub(r'[<>:"/\\|?*]', "_", t["name"])
                return name[:30]  # 限制长度
    except Exception:
        pass
    return task_id


def group_by_tag(entries: list) -> dict:
    tag_groups = {}
    untagged = []
    for entry in entries:
        if entry.get("status") == "archived":
            continue
        tags = entry.get("tags", [])
        if not tags:
            untagged.append(entry)
        else:
            for tag in tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(entry)
    return tag_groups, untagged


def group_by_type(entries: list) -> dict:
    type_groups = {}
    for entry in entries:
        if entry.get("status") == "archived":
            continue
        type_ = entry.get("type", "idea")
        if type_ not in type_groups:
            type_groups[type_] = []
        type_groups[type_].append(entry)
    return type_groups


def generate_review_content(tag_groups: dict, untagged: list, type_groups: dict,
                            data: dict, task_name: str = None) -> str:
    now = datetime.now()
    lines = []
    if task_name:
        lines.append(f"# 任务知识综述 - {task_name} - {now.strftime('%Y-%m-%d')}\n\n")
    else:
        lines.append(f"# 灵感综述 - {now.strftime('%Y-%m-%d')}\n\n")

    lines.append(f"> 自动生成时间：{now.isoformat()}\n\n")

    active_entries = [e for e in data["entries"] if e.get("status") != "archived"]
    if task_name:
        active_entries = [e for e in active_entries if e.get("task_id")]
    lines.append(f"> 已压缩灵感数：{len(active_entries)}\n\n")
    lines.append("\n---\n\n")

    # 按标签分组
    lines.append("## 📊 按标签分组\n\n")
    if not tag_groups:
        lines.append("（无标签分组）\n\n")
    else:
        for tag, entries in sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True):
            lines.append(f"### #{tag}（{len(entries)} 条灵感）\n\n")
            lines.append("**核心洞察**：（待 AI 生成）\n\n")
            lines.append("**关键灵感**：\n\n")
            for entry in entries[:5]:
                lines.append(f"- [{entry['created_at'][:10]}] {entry['title']}\n")
                if entry.get("related"):
                    related_titles = []
                    for rid in entry["related"][:3]:
                        for e in data["entries"]:
                            if e["id"] == rid:
                                related_titles.append(e["title"])
                                break
                    if related_titles:
                        lines.append(f"  - 关联：{', '.join(related_titles)}\n")
            if len(entries) > 5:
                lines.append(f"- ... 还有 {len(entries) - 5} 条\n\n")
            else:
                lines.append("\n")

    # 未标签的灵感
    if untagged:
        lines.append(f"### 未分类（{len(untagged)} 条）\n\n")
        for entry in untagged[:5]:
            lines.append(f"- [{entry['created_at'][:10]}] {entry['title']}\n")
        lines.append("\n")

    # 按类型分组
    lines.append("---\n\n")
    lines.append("## 📂 按类型分组\n\n")
    for type_, entries in type_groups.items():
        type_name = {"paper": "论文", "url": "链接", "idea": "灵感",
                     "decision": "决策", "blocker": "困难", "milestone": "里程碑"}.get(type_, type_)
        lines.append(f"### {type_name}（{len(entries)} 条）\n\n")
        for entry in entries[:3]:
            lines.append(f"- {entry['title']}\n")
        lines.append("\n")

    # 关联分析
    lines.append("---\n\n")
    lines.append("## 🔗 关联分析\n\n")
    lines.append("（待 AI 分析灵感之间的关联关系）\n\n")

    return "".join(lines)


def compress(file_path: Path, output_dir: Path = None, dry_run: bool = False,
             task_id: str = None) -> dict:
    """
    压缩灵感库
    - task_id=None：全局压缩
    - task_id=<id>：仅压缩该任务的灵感
    """
    data = load_inspirations(file_path)
    entries = data["entries"]

    # 筛选需要检查的条目
    if task_id:
        target_entries = [e for e in entries if e.get("task_id") == task_id]
        threshold = TASK_THRESHOLD
        task_name = get_task_name(task_id)
    else:
        target_entries = [e for e in entries if e.get("status") != "archived"]
        threshold = data.get("meta", {}).get("compression_threshold") or GLOBAL_THRESHOLD
        task_name = None

    active_target = [e for e in target_entries if e.get("status") != "archived"]

    # 检查阈值
    if len(active_target) < threshold:
        return {
            "success": False,
            "reason": f"未达到阈值（当前 {len(active_target)} / {threshold}）",
            "should_compress": False,
            "task_id": task_id
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "active_count": len(active_target),
            "threshold": threshold,
            "should_compress": True,
            "task_id": task_id
        }

    # 分组（只对 target_entries 中未归档的做分组）
    to_compress = [e for e in target_entries if e.get("status") != "archived"]
    tag_groups, untagged = group_by_tag(to_compress)
    type_groups = group_by_type(to_compress)

    # 生成综述内容
    review_content = generate_review_content(tag_groups, untagged, type_groups, data, task_name)

    # 确定输出路径
    if output_dir is None:
        output_dir = DEFAULT_INSP_DIR / "reviews"
    ensure_dirs(output_dir)

    now = datetime.now()
    if task_name:
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", task_name)[:30]
        review_file = output_dir / f"review-{safe_name}-{now.strftime('%Y%m%d')}.md"
    else:
        review_file = output_dir / f"review-{now.strftime('%Y%m%d')}.md"

    # 写入综述文档
    with open(review_file, "w", encoding="utf-8") as f:
        f.write(review_content)

    # 标记已压缩的灵感为 archived
    archived_count = 0
    target_ids = {e["id"] for e in to_compress}
    for entry in entries:
        if entry["id"] in target_ids and entry.get("status") != "archived":
            entry["status"] = "archived"
            archived_count += 1

    # 更新 meta（仅全局压缩时更新 last_compressed）
    if not task_id:
        data["meta"]["last_compressed"] = now.isoformat()

    # 保存
    save_inspirations(file_path, data)

    return {
        "success": True,
        "review_file": str(review_file),
        "archived_count": archived_count,
        "active_count": len([e for e in data["entries"] if e.get("status") != "archived"]),
        "threshold": threshold,
        "should_compress": False,
        "task_id": task_id
    }


def main():
    parser = argparse.ArgumentParser(description="自动压缩模块 v2.0")
    parser.add_argument("--file", type=str, default=str(DEFAULT_INSP_FILE), help="灵感库文件路径")
    parser.add_argument("--output", type=str, default=None, help="综述文档输出目录")
    parser.add_argument("--threshold", type=int, default=None, help="覆盖压缩阈值（全局）")
    parser.add_argument("--dry-run", action="store_true", help="只检测不执行")
    parser.add_argument("--task-id", type=str, default=None, help="按任务 ID 压缩")
    parser.add_argument("--task-name", type=str, default=None, help="按任务名称查找并压缩")

    args = parser.parse_args()
    file_path = Path(args.file)

    # --threshold：覆盖全局阈值
    if args.threshold:
        data = load_inspirations(file_path)
        data["meta"]["compression_threshold"] = args.threshold
        save_inspirations(file_path, data)
        print(f"✅ 已更新全局压缩阈值为 {args.threshold}")
        return

    # 解析 task_id（支持 --task-name 模糊匹配）
    task_id = args.task_id
    if args.task_name:
        tasks_data = load_tasks(DEFAULT_TASKS_FILE)
        matched = None
        for t in tasks_data.get("tasks", []):
            if args.task_name in t["name"]:
                matched = t["id"]
                break
        if not matched:
            print(f"⚠️ 找不到任务：{args.task_name}")
            sys.exit(1)
        task_id = matched
        print(f"✅ 匹配到任务：{args.task_name} ({task_id})")

    # 执行压缩
    output_dir = Path(args.output) if args.output else None
    result = compress(file_path, output_dir, args.dry_run, task_id)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["success"] and not result.get("dry_run"):
        print(f"\n✅ 压缩完成！")
        if result.get("task_id"):
            print(f"   任务：{get_task_name(result['task_id'])}")
        print(f"   综述文档：{result['review_file']}")
        print(f"   已归档 {result['archived_count']} 条灵感")
    elif not result["success"]:
        print(f"\n⚠️  {result['reason']}")


if __name__ == "__main__":
    main()
