# 知识秘书 Agent — Knowledge Secretary Agent

> **让好想法不再消失，让任务不再卡壳。**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)]()
[![Platform](https://img.shields.io/badge/platform-Box%20%7C%20Claude%20%7C%20CodeBuddy%20%7C%20Codex-green.svg)]()
[![Zero Deps](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![BOX AI 创想大赛](https://img.shields.io/badge/BOX%20AI-创想大赛-orange.svg)]()

---

<!-- DEMO GIF 占位：录屏后替换此行
![演示 GIF](docs/demo.gif)
-->

## 🎯 核心理念

**你正在做 N 件事，每件事都有自己的知识库（秘书）。AI 用这些知识帮你判断下一步。**

| 传统笔记工具 | 知识秘书 Agent |
|---|---|
| 记灵感 → 孤立笔记 | 记灵感 → **绑定到当前任务** |
| 手动打开 → 点击记录 | 对话中识别 → **直接存，零摩擦** |
| AI 推荐 → 通用建议 | AI 推荐 → **引用你的知识库** |
| 单一工具锁定 | **Box / Claude / CodeBuddy 共享数据** |

---

## ✨ 四大技术亮点

### 1️⃣ 知识-任务二维绑定（Task-Anchored Knowledge）
每条知识携带 `task_id`，按任务维度组织，告别孤立笔记碎片。

### 2️⃣ 知识库驱动决策（Personal RAG）
遇到 blocker 或问「下一步」时，AI 主动检索当前任务知识库，引用具体条目给出有依据的建议。

### 3️⃣ 零摩擦捕获
识别即存储，全程无「要记录吗」确认弹窗。唯一需要确认的是压缩（不可逆操作）。

### 4️⃣ 全生命周期闭环 + 跨平台共享
想法捕获 → 任务绑定 → 进度追踪 → 阈值压缩 → 报告导出 → 定时回顾，共享同一份本地数据，换平台不丢上下文。

---

## 🚀 一行安装（Box / WorkBuddy）

```
use_skill("https://github.com/Yanyeoo/inspiration-workflow-skill")
```

安装后**什么都不用做**——正常说话，知识秘书自动在场。  
其他平台 + 定时推送 + 企微接入见 [DAILY_WORKFLOW.md](DAILY_WORKFLOW.md)。

---

## 💬 效果演示

### 场景：遇到 Blocker，AI 引用知识库推荐（核心亮点）

```
用户：卡住了，密集检索模型在领域数据上效果很差

AI：✅ 已记录困难：密集检索模型领域适应差

   根据知识库「稀疏+密集混合检索方案」（06-09），推荐：
   1. 优先用 BM25 保底召回，密集检索做 rerank
   2. 领域微调：用 triplet loss 对 bi-encoder 做 few-shot
   3. 参考知识库中的论文 arxiv:2210.11610 章节 4.2

   当前进度 30% → 解决后说「更新到 X%」
```

### 场景：零摩擦捕获（无需说「记一下」）

```
用户：我想到可以用图数据库替代 JSON 存储知识关联

AI：✅ 已记录到 [RAG 知识库优化]：
   图数据库替代 JSON（idea）
   标签：#图数据库 #知识关联 #架构
   与「知识关联设计」（06-08）相关，已自动关联。
```

### 场景：自动识别论文链接

```
用户：这篇论文很相关 https://arxiv.org/abs/2210.11610

AI：✅ 已记录到 [RAG 知识库优化]：
   arxiv:2210.11610（paper）
   标签：#RAG #检索优化 #论文
```

---

## 📂 文件结构

```
inspiration-workflow-skill/
├── SKILL.md              # Box/WorkBuddy Skill 定义（v2.0）
├── CLAUDE.md             # Claude Code CLI 版本
├── CONTEST.md            # BOX AI 创想大赛参赛说明
├── DEPLOY.md             # 多平台部署指南（Box/Claude/CodeBuddy/Codex/小龙虾）
├── DEMO_SCRIPT.md        # 录屏演示脚本（分场景时间轴）
├── setup.sh              # 一键初始化脚本
├── agent/                # Agent 多文件架构（Box agent-creator 标准）
│   ├── IDENTITY.md       # 身份定位
│   ├── SOUL.md           # 行为准则
│   ├── AGENTS.md         # 子 Agent 配置
│   ├── TOOLS.md          # 工具清单与决策树
│   └── memory/
│       └── MEMORY.md     # 长期记忆模板
└── scripts/
    ├── capture.py        # 灵感捕获模块
    ├── compress.py       # 阈值压缩模块
    ├── search.py         # 检索模块
    ├── export.py         # 导出模块（Markdown / JSON / Mermaid）
    └── tasks.py          # 任务管理模块
```

---

## 🛠️ 安装方式

### 方式一：Box / WorkBuddy（推荐，最丝滑）

在 Box 对话框发送：
```
use_skill("https://github.com/Yanyeoo/inspiration-workflow-skill")
```

### 方式二：一键脚本（全平台初始化）

```bash
curl -fsSL https://raw.githubusercontent.com/Yanyeoo/inspiration-workflow-skill/master/setup.sh | bash
```

### 方式三：Claude Code CLI

```bash
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git
mkdir -p ~/.claude/commands
cp inspiration-workflow-skill/CLAUDE.md ~/.claude/commands/inspiration-workflow.md
# 使用：claude → /inspiration-workflow
```

### 方式四：手动克隆

```bash
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git \
  ~/.workbuddy/skills/inspiration-workflow-skill
```

详细的 CodeBuddy / Codex / 小龙虾安装说明见 [DEPLOY.md](DEPLOY.md)。

---

## 🚀 快速上手

```bash
SCRIPT=~/.workbuddy/skills/inspiration-workflow-skill/scripts

# 1. 创建任务
python $SCRIPT/tasks.py --new "RAG 知识库优化"

# 2. 捕获灵感
python $SCRIPT/capture.py --content "稀疏+密集混合检索方案" --type idea

# 3. 记录进度
python $SCRIPT/capture.py --content "完成 BM25 基线" --type milestone
# 或通过 workflow 脚本（如果存在）
# python $SCRIPT/workflow.py --action "完成 BM25 基线" --progress 30

# 4. 搜索知识
python $SCRIPT/search.py \
  --file ~/.workbuddy/memory/inspirations/inspirations.json \
  --keyword "RAG"

# 5. 导出报告
python $SCRIPT/export.py \
  --file ~/.workbuddy/memory/inspirations/inspirations.json \
  --format markdown --output ~/Desktop/report.md

# 6. 检查压缩阈值
python $SCRIPT/compress.py \
  --file ~/.workbuddy/memory/inspirations/inspirations.json \
  --dry-run
```

---

## 📊 数据存储方案

```
~/.workbuddy/memory/
├── tasks.json                 # 任务列表（核心，v2.0 新增）
├── inspirations/
│   └── inspirations.json     # 知识库（每条绑定 task_id）
├── reviews/                  # 压缩综述（自动生成）
│   └── review-{task}-{date}.md
└── exports/                  # 导出文件
    └── task-report-{date}.md
```

**跨平台共享**：所有平台（Box / Claude CLI / CodeBuddy）均读写此目录，切换工具不丢数据。

---

## 📋 触发词速查

| 说什么 | AI 做什么 |
|---|---|
| 「开始做 X」/ 「新任务：X」 | 创建任务，切换为活跃 |
| 「我想到…」/ 「有个想法…」 | 直接存为 idea，绑定当前任务 |
| `http://` 或 `https://` 链接 | 直接存为 url/paper |
| 「我做了…」/ 「完成了…」 | 更新任务进度 + history |
| 「卡住了」/ 「报错」/ 「不知道怎么」 | 记录 blocker + 知识库推荐 |
| 「接下来干嘛」/ 「下一步」 | 读知识库，输出有依据推荐 |
| 「看所有任务」/ 「任务总览」 | 格式化输出所有任务状态 |
| 「导出总结」/ 「生成报告」 | export.py 生成任务报告 |

---

## ⚙️ 配置项

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `compression_threshold` | 50（全局）/ 30（单任务）| 触发压缩的知识条数 |
| `auto_detect` | true | 自动识别知识（关闭后需手动「记一下」）|
| `confirm_before_compress` | true | 压缩前询问确认（推荐保持开启）|
| `reminder_interval` | 10 | 每 N 条知识提醒一次进度 |

---

## 🔮 未来规划

- [ ] 接入向量数据库（Chroma / FAISS）→ 语义检索
- [ ] 自动生成 Mermaid 知识图谱（可视化任务知识关联）
- [ ] 接入腾讯文档，导出即发布
- [ ] feedly MCP 集成，订阅文章自动归类到任务
- [ ] 多用户隔离（团队协作场景）

---

## 🏆 BOX AI 创想大赛

本项目参加 BOX AI 创想大赛。详细参赛说明见 [CONTEST.md](CONTEST.md)。

---

## 📄 许可证

MIT License — 可自由使用、修改、分发。

---

## 👤 作者

Shayla Deng @ Tencent PCG

如有问题或建议，欢迎提 [Issue](https://github.com/Yanyeoo/inspiration-workflow-skill/issues) 或 PR。
