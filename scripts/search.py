#!/usr/bin/env python3
"""
检索模块 - search.py
用法：
  python search.py --file inspirations.json --keyword "RAG"
  python search.py --file inspirations.json --tag "AI"
  python search.py --file inspirations.json --type paper
  python search.py --file inspirations.json --all
"""

import json
import argparse
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_INSP_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "inspirations.json"


def load_inspirations(file_path: Path) -> dict:
    """加载灵感库"""
    if not file_path.exists():
        print(f"错误：灵感库文件不存在：{file_path}", file=sys.stderr)
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_keyword(entry: dict, keyword: str) -> float:
    """关键词匹配，返回相似度分数"""
    content = entry.get("content", "")
    title = entry.get("title", "")
    tags = " ".join(entry.get("tags", []))
    
    text = f"{title} {content} {tags}".lower()
    keyword_lower = keyword.lower()
    
    # 完全匹配
    if keyword_lower in text:
        return 1.0
    
    # 部分匹配（分词）
    keyword_words = set(re.findall(r'\w+', keyword_lower))
    text_words = set(re.findall(r'\w+', text))
    
    if keyword_words & text_words:
        overlap = len(keyword_words & text_words)
        return min(overlap / len(keyword_words), 1.0)
    
    return 0.0


def search_by_keyword(entries: list, keyword: str, top_k: int = 10) -> list:
    """按关键词检索"""
    scored = []
    for entry in entries:
        if entry.get("status") == "archived" and not keyword.startswith("all"):
            continue
        score = match_keyword(entry, keyword)
        if score > 0:
            scored.append((entry, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"entry": e, "score": s} for e, s in scored[:top_k]]


def search_by_tag(entries: list, tag: str, top_k: int = 10) -> list:
    """按标签检索"""
    results = []
    for entry in entries:
        if entry.get("status") == "archived":
            continue
        tags = [t.lower() for t in entry.get("tags", [])]
        if tag.lower() in tags:
            results.append({"entry": entry, "score": 1.0})
    
    return results[:top_k]


def search_by_type(entries: list, type_: str, top_k: int = 10) -> list:
    """按类型检索"""
    results = []
    for entry in entries:
        if entry.get("status") == "archived":
            continue
        if entry.get("type") == type_:
            results.append({"entry": entry, "score": 1.0})
    
    return results[:top_k]


def search_by_date_range(entries: list, start_date: str, end_date: str = None) -> list:
    """按时间范围检索"""
    results = []
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date) if end_date else datetime.now()
    
    for entry in entries:
        if entry.get("status") == "archived":
            continue
        created = datetime.fromisoformat(entry["created_at"])
        if start <= created <= end:
            results.append({"entry": entry, "score": 1.0})
    
    return results


def format_results(results: list, show_related: bool = True) -> str:
    """格式化输出结果"""
    if not results:
        return "未找到匹配的灵感。"
    
    lines = []
    lines.append(f"找到 {len(results)} 条相关灵感：\n")
    
    for i, r in enumerate(results, 1):
        entry = r["entry"]
        score = r["score"]
        
        # 标题和时间
        created = entry["created_at"][:10]
        lines.append(f"{i}. [{created}] {entry['title']}（关联度 {score:.0%}）")
        
        # 类型和标签
        type_name = {"paper": "论文", "url": "链接", "idea": "灵感", "decision": "决策", "blocker": "困难", "milestone": "里程碑"}.get(entry["type"], entry["type"])
        lines.append(f"   类型：{type_name} | 标签：{' '.join(['#'+t for t in entry.get('tags', [])])}")
        
        # 关联灵感
        if show_related and entry.get("related"):
            lines.append(f"   关联：{len(entry['related'])} 条")
        
        lines.append("")
    
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description="灵感检索模块")
    parser.add_argument("--file", type=str, default=str(DEFAULT_INSP_FILE), help="灵感库文件路径")
    parser.add_argument("--keyword", type=str, help="关键词搜索")
    parser.add_argument("--tag", type=str, help="按标签搜索")
    parser.add_argument("--type", type=str, choices=["paper", "url", "idea", "decision", "blocker", "milestone"], help="按类型搜索")
    parser.add_argument("--start-date", type=str, help="开始日期（YYYY-MM-DD）")
    parser.add_argument("--end-date", type=str, help="结束日期（YYYY-MM-DD）")
    parser.add_argument("--all", action="store_true", help="显示所有灵感（包括已归档）")
    parser.add_argument("--top-k", type=int, default=10, help="最多返回结果数")
    
    args = parser.parse_args()
    
    # 加载数据
    data = load_inspirations(Path(args.file))
    entries = data["entries"]
    
    # 执行检索
    results = []
    
    if args.keyword:
        results = search_by_keyword(entries, args.keyword, args.top_k)
    elif args.tag:
        results = search_by_tag(entries, args.tag, args.top_k)
    elif args.type:
        results = search_by_type(entries, args.type, args.top_k)
    elif args.start_date:
        results = search_by_date_range(entries, args.start_date, args.end_date)
    elif args.all:
        results = [{"entry": e, "score": 1.0} for e in entries if e.get("status") != "archived"] or \
                  [{"entry": e, "score": 1.0} for e in entries]
    else:
        print("请指定检索方式：--keyword / --tag / --type / --start-date / --all")
        sys.exit(1)
    
    # 输出结果
    output = format_results(results)
    print(output)
    
    # 输出 JSON（供程序化处理）
    if len(results) > 0:
        print("\n--- JSON 输出 ---")
        print(json.dumps([{"id": r["entry"]["id"], "title": r["entry"]["title"], "score": r["score"]} for r in results], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
