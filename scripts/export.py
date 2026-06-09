#!/usr/bin/env python3
"""
导出模块 - export.py
用法：
  python export.py --file inspirations.json --format markdown --output exports/
  python export.py --file inspirations.json --format json --output exports/
  python export.py --file inspirations.json --format mermaid --output exports/
  python export.py --workflow --output exports/workflow-report.md
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

DEFAULT_INSP_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "inspirations.json"
DEFAULT_WORKFLOW_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "workflow-state.json"


def ensure_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def load_inspirations(file_path: Path) -> dict:
    if not file_path.exists():
        print(f"错误：灵感库文件不存在：{file_path}", file=sys.stderr)
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_workflow(file_path: Path) -> dict:
    if not file_path.exists():
        return {"version": "1.0", "current_task": "", "progress": 0, "history": [], "blockers": [], "next_steps": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def export_markdown(data: dict, output_file: Path):
    """导出为 Markdown 格式（适配 KM / 腾讯学堂）"""
    entries = [e for e in data["entries"] if e.get("status") != "archived"]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# 灵感库导出 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"> 导出时间：{datetime.now().isoformat()}\n")
        f.write(f"> 灵感总数：{len(entries)}\n\n")
        f.write("---\n\n")
        
        # 按类型分组
        type_groups = {}
        for entry in entries:
            type_ = entry.get("type", "idea")
            if type_ not in type_groups:
                type_groups[type_] = []
            type_groups[type_].append(entry)
        
        type_names = {"paper": "📄 论文", "url": "🔗 链接", "idea": "💡 灵感", "decision": "✅ 决策", "blocker": "⚠️ 困难", "milestone": "🏆 里程碑"}
        
        for type_, items in type_groups.items():
            f.write(f"\n## {type_names.get(type_, type_)}（{len(items)} 条）\n\n")
            for entry in items:
                created = entry["created_at"][:10]
                f.write(f"### [{created}] {entry['title']}\n\n")
                f.write(f"{entry['content']}\n\n")
                if entry.get("tags"):
                    tags_str = " ".join([f"#{t}" for t in entry["tags"]])
                    f.write(f"标签：{tags_str}\n\n")
                if entry.get("source_url"):
                    f.write(f"来源：{entry['source_url']}\n\n")
                f.write("---\n\n")
    
    print(f"✅ Markdown 导出完成：{output_file}")


def export_json(data: dict, output_file: Path):
    """导出为 JSON 格式"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 导出完成：{output_file}")


def export_mermaid(data: dict, output_file: Path):
    """导出为 Mermaid 知识图谱"""
    entries = [e for e in data["entries"] if e.get("status") != "archived"]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("```mermaid\ngraph TD\n")
        
        # 按标签分组
        tag_groups = {}
        for entry in entries:
            for tag in entry.get("tags", []):
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(entry["id"])
        
        # 输出节点
        for entry in entries:
            node_id = entry["id"].replace("_", "")
            title = entry["title"][:30]
            f.write(f"    {node_id}[\"{title}\"]\n")
        
        # 输出关联
        for entry in entries:
            node_id = entry["id"].replace("_", "")
            for related_id in entry.get("related", []):
                related_node = related_id.replace("_", "")
                f.write(f"    {node_id} --> {related_node}\n")
        
        # 输出标签分组（用 style 模拟）
        color_map = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#6c5ce7"]
        for i, (tag, entry_ids) in enumerate(tag_groups.items()):
            color = color_map[i % len(color_map)]
            for eid in entry_ids:
                nid = eid.replace("_", "")
                f.write(f"    style {nid} fill:{color},stroke:#333,stroke-width:2px\n")
        
        f.write("```\n")
    
    print(f"✅ Mermaid 图谱导出完成：{output_file}")


def export_workflow_report(data: dict, output_file: Path):
    """导出工作流状态报告"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# 工作流状态报告 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"> 生成时间：{datetime.now().isoformat()}\n\n")
        f.write("---\n\n")
        
        f.write(f"## 📊 当前状态\n\n")
        f.write(f"**当前任务**：{data.get('current_task', '未设置')}\n\n")
        f.write(f"**进度**：{data.get('progress', 0)}%\n\n")
        
        f.write("---\n\n")
        
        f.write(f"## ✅ 已完成的工作\n\n")
        if data.get("history"):
            for h in data["history"][-10:]:  # 最近 10 条
                ts = h["timestamp"][:16]
                f.write(f"### [{ts}] {h['action']}\n\n")
                f.write(f"进度：{h.get('progress', 0)}%\n\n")
                if h.get("blockers"):
                    f.write(f"困难：{', '.join(h['blockers'])}\n\n")
                if h.get("next_steps"):
                    f.write(f"下一步：{', '.join(h['next_steps'])}\n\n")
        else:
            f.write("暂无记录。\n\n")
        
        f.write("---\n\n")
        
        f.write(f"## ⚠️ 当前困难\n\n")
        if data.get("blockers"):
            for b in data["blockers"]:
                f.write(f"- {b}\n")
        else:
            f.write("暂无困难。\n\n")
        
        f.write("---\n\n")
        
        f.write(f"## 🚀 推荐下一步\n\n")
        if data.get("next_steps"):
            for ns in data["next_steps"]:
                f.write(f"- {ns}\n")
        else:
            f.write("暂无推荐。\n\n")
    
    print(f"✅ 工作流报告导出完成：{output_file}")


def main():
    parser = argparse.ArgumentParser(description="灵感库导出模块")
    parser.add_argument("--file", type=str, default=str(DEFAULT_INSP_FILE), help="灵感库文件路径")
    parser.add_argument("--workflow", type=str, help="工作流状态文件路径（如不指定则自动查找）")
    parser.add_argument("--format", type=str, choices=["markdown", "json", "mermaid"], default="markdown", help="导出格式")
    parser.add_argument("--output", type=str, required=True, help="输出文件路径或目录")
    parser.add_argument("--all", action="store_true", help="包含已归档的灵感")
    
    args = parser.parse_args()
    
    if args.workflow or args.format == "workflow":
        # 导出工作流报告
        workflow_file = Path(args.workflow) if args.workflow else DEFAULT_WORKFLOW_FILE
        data = load_workflow(workflow_file)
        output_file = Path(args.output)
        ensure_dirs(output_file.parent)
        export_workflow_report(data, output_file)
    else:
        # 导出灵感库
        data = load_inspirations(Path(args.file))
        
        if not args.all:
            data["entries"] = [e for e in data["entries"] if e.get("status") != "archived"]
        
        output_file = Path(args.output)
        ensure_dirs(output_file.parent)
        
        if args.format == "markdown":
            export_markdown(data, output_file)
        elif args.format == "json":
            export_json(data, output_file)
        elif args.format == "mermaid":
            export_mermaid(data, output_file)


if __name__ == "__main__":
    main()
