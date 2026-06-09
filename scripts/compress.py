#!/usr/bin/env python3
"""
自动压缩模块 - compress.py
用法：
  python compress.py --file inspirations.json
  python compress.py --file inspirations.json --threshold 30 --output reviews/
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
import re

DEFAULT_INSP_DIR = Path.home() / ".workbuddy" / "memory" / "inspirations"
DEFAULT_INSP_FILE = DEFAULT_INSP_DIR / "inspirations.json"


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


def group_by_tag(entries: list) -> dict:
    """按标签分组"""
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
    """按类型分组"""
    type_groups = {}
    for entry in entries:
        if entry.get("status") == "archived":
            continue
        type_ = entry.get("type", "idea")
        if type_ not in type_groups:
            type_groups[type_] = []
        type_groups[type_].append(entry)
    return type_groups


def generate_review_content(tag_groups: dict, untagged: list, type_groups: dict, data: dict) -> str:
    """生成综述文档内容"""
    now = datetime.now()
    lines = []
    lines.append(f"# 灵感综述 - {now.strftime('%Y-%m-%d')}\n\n")
    lines.append(f"> 自动生成时间：{now.isoformat()}\n\n")
    active_count = len([e for e in data["entries"] if e.get("status") != "archived"])
    lines.append(f"> 已压缩灵感数：{active_count}\n\n")
    lines.append("\n---\n\n")

    # 按标签分组
    lines.append("## 📊 按标签分组\n\n")
    for tag, entries in sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True):
        lines.append(f"### #{tag}（{len(entries)} 条灵感）\n\n")
        lines.append("**核心洞察**：（待 AI 生成）\n\n")
        lines.append("**关键灵感**：\n\n")
        for entry in entries[:5]:
            lines.append(f"- [{entry['created_at'][:10]}] {entry['title']}\n")
            if entry.get("related"):
                related_titles = []
                for rid in entry["related"]:
                    for e in data["entries"]:
                        if e["id"] == rid:
                            related_titles.append(e["title"])
                            break
                if related_titles:
                    lines.append(f"  - 关联：{', '.join(related_titles[:3])}\n")
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
        type_name = {"paper": "论文", "url": "链接", "idea": "灵感", "decision": "决策", "blocker": "困难", "milestone": "里程碑"}.get(type_, type_)
        lines.append(f"### {type_name}（{len(entries)} 条）\n\n")
        for entry in entries[:3]:
            lines.append(f"- {entry['title']}\n")
        lines.append("\n")

    # 关联分析
    lines.append("---\n\n")
    lines.append("## 🔗 关联分析\n\n")
    lines.append("（待 AI 分析灵感之间的关联关系）\n\n")

    return "".join(lines)


def compress(file_path: Path, output_dir: Path = None, dry_run: bool = False) -> dict:
    """
    压缩灵感库

    Args:
        file_path: 灵感库文件路径
        output_dir: 综述文档输出目录
        dry_run: 是否只检测不执行

    Returns:
        压缩结果
    """
    data = load_inspirations(file_path)
    entries = data["entries"]
    threshold = data["meta"]["compression_threshold"]

    # 检查是否需要压缩
    active_entries = [e for e in entries if e.get("status") != "archived"]
    if len(active_entries) < threshold:
        return {
            "success": False,
            "reason": f"未达到阈值（当前 {len(active_entries)} / {threshold}）",
            "should_compress": False
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "active_count": len(active_entries),
            "threshold": threshold,
            "should_compress": True
        }

    # 分组
    tag_groups, untagged = group_by_tag(entries)
    type_groups = group_by_type(entries)

    # 生成综述内容
    review_content = generate_review_content(tag_groups, untagged, type_groups, data)

    # 确定输出路径
    if output_dir is None:
        output_dir = DEFAULT_INSP_DIR / "reviews"
    ensure_dirs(output_dir)

    now = datetime.now()
    review_file = output_dir / f"review-{now.strftime('%Y-%m-%d')}.md"

    # 写入综述文档
    with open(review_file, "w", encoding="utf-8") as f:
        f.write(review_content)

    # 标记已压缩的灵感为 archived
    archived_count = 0
    for entry in entries:
        if entry.get("status") != "archived":
            entry["status"] = "archived"
            archived_count += 1

    # 更新 meta
    data["meta"]["last_compressed"] = now.isoformat()

    # 保存
    save_inspirations(file_path, data)

    return {
        "success": True,
        "review_file": str(review_file),
        "archived_count": archived_count,
        "active_count": 0,
        "threshold": threshold,
        "should_compress": False
    }


def main():
    parser = argparse.ArgumentParser(description="自动压缩模块")
    parser.add_argument("--file", type=str, default=str(DEFAULT_INSP_FILE), help="灵感库文件路径")
    parser.add_argument("--output", type=str, default=None, help="综述文档输出目录")
    parser.add_argument("--threshold", type=int, default=None, help="覆盖压缩阈值")
    parser.add_argument("--dry-run", action="store_true", help="只检测不执行")

    args = parser.parse_args()

    file_path = Path(args.file)
    output_dir = Path(args.output) if args.output else None

    # 覆盖阈值
    if args.threshold:
        data = load_inspirations(file_path)
        data["meta"]["compression_threshold"] = args.threshold
        save_inspirations(file_path, data)
        print(f"✅ 已更新压缩阈值为 {args.threshold}")
        return

    # 执行压缩
    result = compress(file_path, output_dir, args.dry_run)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["success"] and not result.get("dry_run"):
        print(f"\n✅ 压缩完成！")
        print(f"   综述文档：{result['review_file']}")
        print(f"   已归档 {result['archived_count']} 条灵感")
    elif not result["success"]:
        print(f"\n⚠️  {result['reason']}")


if __name__ == "__main__":
    main()
