#!/usr/bin/env python3
"""
灵感捕获模块 - capture.py (v2.0)
用法：
  python capture.py --content "灵感内容"
  python capture.py --content "灵感内容" --type idea --tags "AI,提效"
  python capture.py --content "灵感内容" --task-id "task_xxx"
  python capture.py --file inspirations.json --content "..." --auto-relate
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
import re

# 默认存储路径
DEFAULT_INSP_DIR = Path.home() / ".workbuddy" / "memory" / "inspirations"
DEFAULT_INSP_FILE = DEFAULT_INSP_DIR / "inspirations.json"
DEFAULT_TASKS_FILE = DEFAULT_INSP_DIR / "tasks.json"


def ensure_dirs():
    """确保目录存在"""
    DEFAULT_INSP_DIR.mkdir(parents=True, exist_ok=True)


def get_active_task_id() -> str | None:
    """读取当前活跃任务的 task_id"""
    if not DEFAULT_TASKS_FILE.exists():
        return None
    try:
        with open(DEFAULT_TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("active_task_id")
    except Exception:
        return None


def load_inspirations(file_path: Path) -> dict:
    """加载灵感库"""
    if not file_path.exists():
        return {"version": "2.0", "entries": [], "meta": {"total": 0, "last_compressed": None, "compression_threshold": 50}}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inspirations(file_path: Path, data: dict):
    """保存灵感库"""
    ensure_dirs()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_id() -> str:
    """生成唯一 ID（含微秒，避免并发冲突）"""
    now = datetime.now()
    import time
    micro = int(time.time() * 1_000_000) % 1_000_000
    return f"insp_{now.strftime('%Y%m%d_%H%M%S')}_{micro:06d}"


def detect_type(content: str) -> str:
    """自动检测灵感类型"""
    content_lower = content.lower()
    if "arxiv" in content_lower or "paper" in content_lower or "论文" in content or re.search(r'\d{4}\.\d{4,5}', content):
        return "paper"
    if content.startswith("http://") or content.startswith("https://"):
        return "url"
    if "决定" in content or "decision" in content_lower or "方案" in content:
        return "decision"
    if "卡住" in content or "报错" in content or "blocker" in content_lower:
        return "blocker"
    if "完成" in content or "milestone" in content_lower or "阶段性" in content:
        return "milestone"
    return "idea"


def extract_tags(content: str) -> list:
    """从内容中提取关键词作为标签（简单实现）"""
    tags = []
    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', content)
    tags.extend(chinese_words[:5])
    english_words = re.findall(r'\b[A-Za-z]{3,}\b', content)
    tags.extend([w for w in english_words if w.lower() not in ['the', 'and', 'for', 'with']][:5])
    return list(set(tags))[:8]


def find_related(content: str, entries: list, top_k: int = 3) -> list:
    """查找相关灵感（基于简单关键词匹配）"""
    content_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', content.lower()))
    scored = []
    for entry in entries:
        entry_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', entry["content"].lower()))
        overlap = len(content_words & entry_words)
        if overlap > 0:
            scored.append((entry["id"], entry["title"], overlap))
    scored.sort(key=lambda x: x[2], reverse=True)
    return [{"id": x[0], "title": x[1], "score": x[2]} for x in scored[:top_k]]


def capture(content: str, type_: str = None, tags: list = None, source_url: str = None,
            auto_relate: bool = True, file_path: Path = DEFAULT_INSP_FILE, task_id: str = None) -> dict:
    """
    捕获一条灵感，绑定到指定任务（默认当前活跃任务）
    """
    ensure_dirs()
    data = load_inspirations(file_path)

    # 默认绑定到当前活跃任务
    if task_id is None:
        task_id = get_active_task_id()

    # 自动检测类型
    if type_ is None:
        type_ = detect_type(content)

    # 自动提取标签
    if tags is None:
        tags = extract_tags(content)

    # 生成条目
    now = datetime.now()
    entry = {
        "id": generate_id(),
        "title": content[:50] + ("..." if len(content) > 50 else ""),
        "content": content,
        "type": type_,
        "tags": tags,
        "task_id": task_id,
        "related": [],
        "created_at": now.isoformat(),
        "status": "active",
        "source_url": source_url or ""
    }

    # 自动查找关联（同任务的优先）
    if auto_relate and data["entries"]:
        related = find_related(content, data["entries"])
        # 优先展示同任务的相关知识
        same_task = [r for r in related if next((e for e in data["entries"] if e["id"] == r["id"]), {}).get("task_id") == task_id]
        other_task = [r for r in related if r not in same_task]
        entry["related"] = [r["id"] for r in (same_task + other_task)]
        entry["related_info"] = same_task + other_task

    # 添加到库
    data["entries"].append(entry)
    data["meta"]["total"] = len(data["entries"])
    # 确保 version 是 2.0
    data["version"] = "2.0"

    # 保存
    save_inspirations(file_path, data)

    result = {
        "success": True,
        "entry": entry,
        "total": data["meta"]["total"],
        "threshold": data["meta"]["compression_threshold"],
        "should_compress": data["meta"]["total"] >= data["meta"]["compression_threshold"]
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="灵感捕获模块 v2.0")
    parser.add_argument("--file", type=str, default=str(DEFAULT_INSP_FILE), help="灵感库文件路径")
    parser.add_argument("--content", type=str, required=True, help="灵感内容")
    parser.add_argument("--type", type=str, default=None,
                        choices=["paper", "url", "idea", "decision", "blocker", "milestone"],
                        help="灵感类型")
    parser.add_argument("--tags", type=str, default=None, help="标签（逗号分隔）")
    parser.add_argument("--url", type=str, default=None, help="来源 URL")
    parser.add_argument("--no-auto-relate", action="store_true", help="不自动查找关联")
    parser.add_argument("--task-id", type=str, default=None,
                        help="绑定到指定任务 ID（默认：当前活跃任务，传 'null' 表示全局知识）")

    args = parser.parse_args()

    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]

    # 支持 --task-id null 表示全局知识
    task_id = None
    if args.task_id and args.task_id != "null":
        task_id = args.task_id
    elif args.task_id is None:
        task_id = get_active_task_id()

    result = capture(
        content=args.content,
        type_=args.type,
        tags=tags,
        source_url=args.url,
        auto_relate=not args.no_auto_relate,
        file_path=Path(args.file),
        task_id=task_id
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["should_compress"]:
        print(f"\n⚠️  灵感库已达到 {result['threshold']} 条，建议执行压缩！")
        print(f"   运行：python compress.py --file {args.file}")


if __name__ == "__main__":
    main()
