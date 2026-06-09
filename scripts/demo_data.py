#!/usr/bin/env python3
"""
demo_data.py — 预置演示数据脚本
录屏前运行，生成一个有内容的知识库状态，演示效果更好。

用法：
  python scripts/demo_data.py             # 预置演示数据
  python scripts/demo_data.py --clean     # 清空演示数据（恢复干净状态）
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path.home() / ".workbuddy" / "memory"
TASKS_FILE = MEMORY_DIR / "tasks.json"
INSPS_FILE = MEMORY_DIR / "inspirations" / "inspirations.json"


def clean():
    """清空演示数据"""
    for f in [TASKS_FILE, INSPS_FILE]:
        if f.exists():
            f.unlink()
    print("✅ 已清空演示数据，恢复干净状态")


def seed():
    """写入演示数据"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_DIR / "inspirations").mkdir(parents=True, exist_ok=True)

    now = datetime.now()

    # ── tasks.json ────────────────────────────────────
    tasks = {
        "version": "2.0",
        "active_task_id": "task_rag",
        "tasks": [
            {
                "id": "task_rag",
                "name": "RAG 知识库优化",
                "status": "active",
                "progress": 30,
                "created_at": (now - timedelta(days=3)).isoformat(),
                "done": False,
                "history": [
                    {
                        "timestamp": (now - timedelta(days=3)).isoformat(),
                        "action": "完成需求分析与技术选型",
                        "progress": 10
                    },
                    {
                        "timestamp": (now - timedelta(days=2)).isoformat(),
                        "action": "实现 BM25 基线检索",
                        "progress": 30
                    }
                ],
                "blockers": [],
                "next_steps": ["实现密集检索模块", "对比实验"],
                "knowledge_count": 5
            },
            {
                "id": "task_contest",
                "name": "BOX AI 创想大赛",
                "status": "active",
                "progress": 70,
                "created_at": (now - timedelta(days=5)).isoformat(),
                "done": False,
                "history": [
                    {
                        "timestamp": (now - timedelta(days=5)).isoformat(),
                        "action": "完成 SKILL.md 架构设计",
                        "progress": 20
                    },
                    {
                        "timestamp": (now - timedelta(days=4)).isoformat(),
                        "action": "实现全部 Python 脚本",
                        "progress": 60
                    },
                    {
                        "timestamp": (now - timedelta(days=1)).isoformat(),
                        "action": "完成 Agent 多文件架构",
                        "progress": 70
                    }
                ],
                "blockers": [],
                "next_steps": ["录制演示视频", "发布到 GitHub", "提交参赛"],
                "knowledge_count": 3
            }
        ]
    }
    TASKS_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── inspirations.json ─────────────────────────────
    base_id = int(now.timestamp() * 1_000_000)
    entries = [
        {
            "id": f"insp_demo_{base_id + 1}",
            "title": "稀疏+密集混合检索方案",
            "content": "可以用 BM25（稀疏）+ bi-encoder（密集）混合检索，BM25 做初检，bi-encoder 做 rerank，解决长尾 query 召回率低的问题",
            "type": "idea",
            "tags": ["稀疏检索", "密集检索", "混合检索", "召回率"],
            "task_id": "task_rag",
            "related": [f"insp_demo_{base_id + 2}"],
            "created_at": (now - timedelta(days=2, hours=3)).isoformat(),
            "status": "active",
            "source_url": ""
        },
        {
            "id": f"insp_demo_{base_id + 2}",
            "title": "arxiv:2210.11610 RAG 优化论文",
            "content": "REPLUG: Retrieval-Augmented Language Model Pre-Training，提出用检索增强预训练的方式提升 LM 效果",
            "type": "paper",
            "tags": ["RAG", "检索优化", "预训练", "论文"],
            "task_id": "task_rag",
            "related": [f"insp_demo_{base_id + 1}"],
            "created_at": (now - timedelta(days=2, hours=1)).isoformat(),
            "status": "active",
            "source_url": "https://arxiv.org/abs/2210.11610"
        },
        {
            "id": f"insp_demo_{base_id + 3}",
            "title": "BM25 中文分词优化决策",
            "content": "决定用 jieba 分词 + 停用词过滤，而不是按字切分，中文 BM25 效果提升约 15%",
            "type": "decision",
            "tags": ["BM25", "jieba", "中文", "分词"],
            "task_id": "task_rag",
            "related": [],
            "created_at": (now - timedelta(days=1, hours=5)).isoformat(),
            "status": "active",
            "source_url": ""
        },
        {
            "id": f"insp_demo_{base_id + 4}",
            "title": "向量数据库选型：Chroma vs FAISS",
            "content": "对比了 Chroma 和 FAISS：Chroma 有 HTTP API，支持持久化，适合本项目；FAISS 更快但无原生持久化",
            "type": "decision",
            "tags": ["向量数据库", "Chroma", "FAISS", "选型"],
            "task_id": "task_rag",
            "related": [],
            "created_at": (now - timedelta(hours=8)).isoformat(),
            "status": "active",
            "source_url": ""
        },
        {
            "id": f"insp_demo_{base_id + 5}",
            "title": "HyDE 假设文档嵌入方法",
            "content": "Hypothetical Document Embeddings：用 LLM 生成假设答案，再用假设答案的向量做检索，zero-shot 场景效果好",
            "type": "idea",
            "tags": ["HyDE", "零样本", "检索", "LLM"],
            "task_id": "task_rag",
            "related": [f"insp_demo_{base_id + 2}"],
            "created_at": (now - timedelta(hours=2)).isoformat(),
            "status": "active",
            "source_url": ""
        },
        {
            "id": f"insp_demo_{base_id + 6}",
            "title": "知识-任务二维绑定架构（参赛亮点）",
            "content": "区别于传统笔记工具的核心设计：每条知识携带 task_id，按任务维度组织，检索时可过滤，AI 推荐时有上下文",
            "type": "decision",
            "tags": ["架构设计", "差异化", "参赛亮点"],
            "task_id": "task_contest",
            "related": [],
            "created_at": (now - timedelta(days=4)).isoformat(),
            "status": "active",
            "source_url": ""
        },
        {
            "id": f"insp_demo_{base_id + 7}",
            "title": "零摩擦捕获设计原则",
            "content": "去掉所有「要记录吗」确认弹窗，识别即存储，只在压缩（不可逆操作）前询问用户。降低记录摩擦是知识工具成败的关键",
            "type": "decision",
            "tags": ["UX", "零摩擦", "设计原则"],
            "task_id": "task_contest",
            "related": [],
            "created_at": (now - timedelta(days=3)).isoformat(),
            "status": "active",
            "source_url": ""
        },
        {
            "id": f"insp_demo_{base_id + 8}",
            "title": "BOX AI 大赛截止时间",
            "content": "大赛截止日期需要确认，尽快提交演示视频和 GitHub 链接",
            "type": "milestone",
            "tags": ["参赛", "截止", "行动项"],
            "task_id": "task_contest",
            "related": [],
            "created_at": (now - timedelta(hours=1)).isoformat(),
            "status": "active",
            "source_url": ""
        }
    ]

    data = {
        "version": "2.0",
        "entries": entries,
        "meta": {
            "total": len(entries),
            "last_compressed": None,
            "compression_threshold": 50
        }
    }
    INSPS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ 演示数据预置完成！")
    print(f"   任务数：{len(tasks['tasks'])} 个")
    print(f"   知识条数：{len(entries)} 条")
    print(f"   活跃任务：{tasks['active_task_id']}")
    print()
    print("📋 现在可以在 Box/Claude CLI 中演示以下场景：")
    print("   1. 「接下来干嘛」      → AI 引用知识库推荐")
    print("   2. 「卡住了，密集检索效果差」 → blocker + 知识库推荐")
    print("   3. 「我想到用图数据库存知识关联」 → 零摩擦捕获")
    print("   4. 「看看所有任务」    → 多任务总览")
    print("   5. 「导出总结」        → 任务报告生成")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="演示数据预置工具")
    parser.add_argument("--clean", action="store_true", help="清空演示数据")
    args = parser.parse_args()

    if args.clean:
        clean()
    else:
        seed()
