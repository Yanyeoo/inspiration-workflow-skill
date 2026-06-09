# 灵感库 + 工作流跟踪 Skill

> 自动捕获对话中的灵感/论文/链接，分类存储，超过阈值自动压缩，并随时输出记忆系统或总结。同时跟踪工作流状态（做了什么、进度、困难、AI 推荐下一步）。

## ✨ 核心功能

### 🧠 灵感库（知识存储）
- **自动捕获**：AI 在对话中主动识别灵感/论文/链接
- **分类存储**：自动分类（`paper` / `url` / `idea` / `decision` / `blocker` / `milestone`）
- **自动打标签**：AI 自动提取关键词 + 用户确认
- **自动关联**：存储时自动检索库中相关灵感并询问是否关联
- **阈值压缩**：灵感数 ≥ 阈值（默认 50 条）自动生成综述文档

### 📊 工作流状态跟踪（思路保持）
- **记录做了什么**：用户说「我做了…」→ 自动记录到工作流
- **跟踪进度**：0–100% 进度管理
- **记录困难**：用户说「卡住了」→ 记录困难 + AI 推荐下一步
- **推荐下一步**：AI 基于当前状态推荐下一步行动

### 📤 导出功能
- **Markdown**：适配 KM / 腾讯学堂发文模板
- **JSON**：程序化处理
- **Mermaid**：可视化灵感关联图谱
- **工作流报告**：包含「做了什么 / 进度 / 困难 / 下一步」

---

## 📂 文件结构

```
inspiration-workflow-skill/
├── SKILL.md              # Skill 定义文件（AI 行为规则）
├── scripts/
│   ├── capture.py        # 灵感捕获模块
│   ├── compress.py       # 自动压缩模块
│   ├── search.py         # 检索模块
│   ├── export.py         # 导出模块
│   └── workflow.py       # 工作流状态跟踪模块
└── README.md            # 本文件
```

---

## 🛠️ 安装与使用

### 依赖
- Python 3.8+
- 无额外依赖（仅使用标准库）

### 快速开始

#### 1️⃣ 捕获灵感
```bash
python scripts/capture.py --content "我想到一个点子，可以用 AI 自动生成单元测试" --type idea --tags "AI,测试,自动化"
```

#### 2️⃣ 检索灵感
```bash
# 按关键词搜索
python scripts/search.py --file ~/.workbuddy/memory/inspirations/inspirations.json --keyword "RAG"

# 按标签搜索
python scripts/search.py --file ~/.workbuddy/memory/inspirations/inspirations.json --tag "AI"

# 查看所有灵感
python scripts/search.py --file ~/.workbuddy/memory/inspirations/inspirations.json --all
```

#### 3️⃣ 自动压缩
```bash
# 设置压缩阈值（默认 50 条）
python scripts/compress.py --file ~/.workbuddy/memory/inspirations/inspirations.json --threshold 30

# 执行压缩（达到阈值后自动触发）
python scripts/compress.py --file ~/.workbuddy/memory/inspirations/inspirations.json

# 仅检测不执行
python scripts/compress.py --file ~/.workbuddy/memory/inspirations/inspirations.json --dry-run
```

#### 4️⃣ 工作流状态跟踪
```bash
# 记录做了什么
python scripts/workflow.py --action "完成灵感库 SKILL.md 编写" --progress 30

# 更新进度
python scripts/workflow.py --progress 60

# 记录困难
python scripts/workflow.py --blocker "tai-skill 鉴权脚本有 bug"

# 查看当前状态
python scripts/workflow.py --status --file ~/.workbuddy/memory/inspirations/workflow-state.json
```

#### 5️⃣ 导出
```bash
# 导出为 Markdown（适配 KM / 腾讯学堂）
python scripts/export.py --file ~/.workbuddy/memory/inspirations/inspirations.json --format markdown --output exports/inspirations.md

# 导出为 JSON
python scripts/export.py --file ~/.workbuddy/memory/inspirations/inspirations.json --format json --output exports/inspirations.json

# 导出为 Mermaid 图谱
python scripts/export.py --file ~/.workbuddy/memory/inspirations/inspirations.json --format mermaid --output exports/graph.md

# 导出工作流报告
python scripts/export.py --workflow --output exports/workflow-report.md
```

---

## 📋 SKILL.md 触发词

AI 会基于 `SKILL.md` 自动识别并触发，无需手动调用脚本：

| 场景 | 触发词示例 | AI 动作 |
|---|---|---|
| 灵感捕获 | 「我想到…」、「有个想法…」、「记一下…」 | 自动询问是否记录到灵感库 |
| 链接/论文分享 | 包含 `http(s)://` 或「论文」、「paper」 | 自动提取并询问是否存储 |
| 工作流更新 | 「我做了…」、「刚才…」、「现在在…」 | 更新工作流状态 |
| 遇到困难 | 「卡住了」、「不知道怎么办」、「报错」 | 记录困难 + 推荐下一步 |
| 查询灵感 | 「之前想到的…」、「我记录过…」 | 检索灵感库 |
| 查看进度 | 「现在进度如何」、「做到哪了」 | 输出工作流状态总结 |
| 导出总结 | 「导出记忆」、「生成总结」、「写一份报告」 | 导出格式化的记忆/工作流报告 |

---

## 📊 存储方案

### 文件结构
```
~/.workbuddy/memory/inspirations/
├── inspirations.json        # 灵感库（主文件）
├── workflow-state.json      # 工作流状态
├── reviews/                # 综述文档（自动生成）
│   └── review-2026-06-09.md
└── exports/                # 导出文件
    ├── inspirations-export-2026-06-09.md
    └── workflow-report-2026-06-09.md
```

### inspirations.json Schema
```json
{
  "version": "1.0",
  "entries": [
    {
      "id": "insp_20260609_001",
      "title": "RAG 优化论文",
      "content": "刚才看到一篇关于 RAG 优化的论文...",
      "type": "paper",
      "tags": ["RAG", "知识库", "优化"],
      "related": ["insp_20260607_001"],
      "created_at": "2026-06-09T12:30:00+08:00",
      "status": "active",
      "source_url": "https://arxiv.org/..."
    }
  ],
  "meta": {
    "total": 1,
    "last_compressed": null,
    "compression_threshold": 50
  }
}
```

### workflow-state.json Schema
```json
{
  "version": "1.0",
  "current_task": "开发灵感库 Skill",
  "progress": 30,
  "history": [
    {
      "timestamp": "2026-06-09T11:30:00+08:00",
      "action": "完成 SKILL.md 架构设计",
      "progress": 20,
      "blockers": [],
      "next_steps": ["编写 SKILL.md 文件"]
    }
  ],
  "blockers": [],
  "next_steps": ["完成 SKILL.md 编写", "实现 MVP 脚本"]
}
```

---

## ⚙️ 配置项

用户可通过对话修改配置（AI 会识别并执行）：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `compression_threshold` | 50 | 灵感数达到此值触发压缩 |
| `auto_detect` | true | 是否自动识别灵感 |
| `confirm_before_save` | true | 存储前是否询问确认 |
| `reminder_interval` | 10 | 每 N 条灵感提醒一次 |
| `compression_mode` | "confirm" | 压缩模式：`auto` 自动 / `confirm` 确认后 / `manual` 手动 |

**修改示例**（通过对话）：
```
用户：「把压缩阈值改成 30 条」
AI：「✅ 已修改压缩阈值为 30 条」
```

---

## 🧪 测试

### 1️⃣ 测试灵感捕获
```bash
cd inspiration-workflow-skill/scripts
python capture.py --content "测试灵感：可以用 AI 自动生成单元测试" --type idea --tags "AI,测试"
```

### 2️⃣ 测试检索
```bash
python search.py --file ~/.workbuddy/memory/inspirations/inspirations.json --all
```

### 3️⃣ 测试压缩
```bash
# 先添加足够多的测试数据（达到阈值）
for i in {1..50}; do python capture.py --content "测试灵感 $i" --type idea --tags "测试"; done

# 执行压缩
python compress.py --file ~/.workbuddy/memory/inspirations/inspirations.json
```

### 4️⃣ 测试工作流跟踪
```bash
python workflow.py --action "测试工作流跟踪" --progress 50
python workflow.py --blocker "测试困难"
python workflow.py --status
```

---

## 🚀 未来优化方向

1. **接入向量数据库**（Chroma / FAISS）→ 语义检索更精准
2. **支持 Device Code 流鉴权**（无头环境）
3. **多用户隔离**（团队协作）
4. **自动生成 Mermaid 图谱**（可视化灵感关联）
5. **接入腾讯文档**（直接导出到腾讯文档）
6. **AI 自动生成综述**（调用 LLM API 生成高质量综述）

---

## 📄 许可证

MIT License

---

## 👤 作者

Shayla Deng @ Tencent

---

## 📬 反馈

如有问题或建议，请提交 Issue 或 Pull Request。
