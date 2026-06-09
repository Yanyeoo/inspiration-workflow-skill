# 📋 BOX AI 创想大赛 — 参赛作品说明

---

## 🏆 作品名称

**知识秘书 Agent（Knowledge Secretary Agent）**

副标题：_让好想法不再消失，让任务不再卡壳_

---

## 📝 作品简介（100 字）

知识秘书 Agent 是一个以「当前任务」为中心的个人知识管理 + 工作流跟踪 AI Agent。它能自动识别对话中的灵感、论文、链接并零摩擦存储，将每条知识绑定到对应任务，在用户遇到困难时主动引用知识库推荐下一步，超过阈值自动生成知识综述，最终导出完整的任务报告。支持 Box、Claude Code CLI、CodeBuddy、Codex CLI 五个平台，数据跨平台共享。

---

## 🎯 使用场景

### 场景 1：研究型工作者的文献管理

**角色**：AI 研究员，同时跟进 3 个研究方向

**痛点**：每天读 5+ 篇论文，灵感散落在各处，复盘时找不到关联

**使用过程**：
```
研究员（对话中）：「这篇 RAG 论文提出的 HyDE 方法挺有意思，
                    适合用在我的知识库项目里」

AI：「✅ 已记录到 [知识库优化] 知识库：
       HyDE 假设文档嵌入方法（paper）
       标签：#HyDE #RAG #检索优化
       与知识库中「稀疏密集混合方案」（昨天）相关，已自动关联。」
```

**价值**：3 个月后写论文 Related Work 时，一键导出 Mermaid 知识图谱，关联脉络一目了然。

---

### 场景 2：独立开发者的项目管理

**角色**：全栈开发者，独自开发 SaaS 产品

**痛点**：一人身兼产品/开发/运营，任务频繁切换，总忘记做到哪

**使用过程**：
```
开发者：「卡住了，用户登录 token 刷新有并发问题」

AI：「✅ 已记录困难：token 刷新并发冲突

     根据知识库「Redis 分布式锁方案」（上周记录），推荐：
     1. 用 SET NX EX 实现原子加锁，防止重复刷新
     2. 参考知识库中「JWT 最佳实践」文档章节 3.2
     
     当前进度 45% → 解决后说「更新到 50%」」
```

**价值**：AI 推荐有出处，不是胡说，直接指向自己记录的解决方案。

---

### 场景 3：参加 AI 大赛的同学

**角色**：你自己 😄

**痛点**：参赛期间灵感频发，同时推进多个作品方向，容易乱

**使用过程**：
```
用户：「开始做 BOX AI 大赛投稿」

AI：「✅ 已创建任务：[BOX AI 大赛投稿]」

用户：「我觉得知识-任务二维绑定是差异化亮点」

AI：「✅ 已记录到 [BOX AI 大赛投稿]：
       知识-任务二维绑定（decision）
       标签：#差异化 #参赛亮点」

用户（一周后）：「生成周报」

AI：「📄 本周进展：
       进度 70%，新增 15 条知识
       完成：SKILL.md、脚本开发、部署指南
       下一步：录制演示视频、提交参赛」
```

---

## ✨ 技术亮点

### 亮点 1：知识-任务二维绑定架构

**现状**：市面上的 AI 笔记工具（Notion AI、Mem.ai）把知识存成孤立的笔记，检索时靠全局搜索，上下文丢失。

**创新**：每条知识携带 `task_id` 字段，强制归属到任务。检索时可按任务过滤，知识不再碎片化。

```json
{
  "id": "insp_20260609_131804_382160",
  "content": "HyDE 方法适合提升 zero-shot 检索",
  "type": "paper",
  "task_id": "task_rag_optimize",   // ← 核心：知识有归属
  "related": ["insp_20260608_..."]  // ← 核心：知识有关联
}
```

**效果**：「任务 A 的所有知识」一次性检索，而不是全局噪音。

---

### 亮点 2：知识库驱动的决策支持（RAG for Personal Workflow）

**现状**：AI 推荐下一步都是通用建议，和用户实际情况无关。

**创新**：遇到 blocker 或问「下一步」时，Agent 先读取当前任务知识库，用已有知识作为 context 生成推荐，相当于**个人版 RAG**。

```
用户遇到 blocker
     ↓
search.py 检索同任务知识库
     ↓
找到相关知识条目（如「3 天前记录的解决方案」）
     ↓
AI 引用具体条目推荐 next_steps
     ↓
「根据知识库『Redis 分布式锁方案』（06-01），推荐...」
```

**效果**：推荐有据可查，用户信任度高，而不是「可以考虑 A、B、C 方向」的废话建议。

---

### 亮点 3：零摩擦捕获设计（去掉所有不必要确认）

**现状**：大多数知识管理工具需要用户主动打开、点击、填写才能记录。

**创新**：对话中识别到有价值内容后**直接存储**，仅一行轻量反馈，不打断用户思路。唯一需要确认的场景是压缩（不可逆操作）。

```
❌ 传统设计：
用户说「我想到用向量数据库做检索」
→ AI：「要记录到知识库吗？(Y/n)」
→ 用户：「y」
→ AI：「请输入标签：」
→ 用户：「……我已经忘了刚才在说什么了」

✅ 本 Agent 设计：
用户说「我想到用向量数据库做检索」
→ AI：「✅ 已记录：向量数据库做检索（idea）#向量数据库」
→ 用户继续说话，思路不断
```

**效果**：记录摩擦接近零，真正做到「说即记」。

---

### 亮点 4：全生命周期闭环 + 跨平台数据共享

**现状**：工具间数据孤岛——IDE 里写的笔记和对话工具里记的内容不通。

**创新**：
1. **全生命周期**：想法捕获 → 任务绑定 → 进度追踪 → 阈值压缩 → 报告导出 → 定时回顾，在一个 Agent 内完成
2. **跨平台共享**：所有平台共用 `~/.workbuddy/memory/` 数据目录，Box 记的知识，Claude Code CLI 里直接引用

```
Box 对话记录灵感 → 数据写入 ~/.workbuddy/memory/
Claude Code CLI 开发时问「下一步」← 读取同一份数据
CodeBuddy IDE 里触发导出 ← 读取同一份数据
```

**效果**：工具换了，知识还在；平台切了，上下文延续。

---

## 🎬 演示视频脚本概要（完整版见 DEMO_SCRIPT.md）

| 时间段 | 内容 | 重点展示 |
|---|---|---|
| 0:00–0:40 | 开场痛点陈述 | 「好想法会忘」「任务会迷失」 |
| 0:40–1:10 | 一键安装演示 | `use_skill(URL)` 30秒完成 |
| 1:10–2:00 | 零摩擦捕获 | 自然对话 → 自动存储，无确认 |
| 2:00–2:50 | 知识库驱动决策 | Blocker → AI 引用知识库推荐 |
| 2:50–3:30 | 压缩与导出 | 阈值压缩 + 一键导出报告 |
| 3:30–4:00 | 跨平台演示 | Box 记录 → Claude Code CLI 读取 |
| 4:00–4:20 | 结尾 | GitHub 链接 + 致谢 |

---

## 📦 安装步骤

### 方式一：Box（最简单）
```
# 在 Box 对话框中发送：
use_skill("https://github.com/Yanyeoo/inspiration-workflow-skill")
```

### 方式二：一键脚本（全平台初始化）
```bash
curl -fsSL https://raw.githubusercontent.com/Yanyeoo/inspiration-workflow-skill/master/setup.sh | bash
```

### 方式三：手动安装
```bash
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git \
  ~/.workbuddy/skills/inspiration-workflow-skill

# Claude Code CLI
cp ~/.workbuddy/skills/inspiration-workflow-skill/CLAUDE.md \
   ~/.claude/commands/inspiration-workflow.md

# 测试
python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/capture.py \
  --content "安装测试" --type milestone
```

### 系统要求
- Python 3.8+（纯标准库，无需 pip install）
- 支持平台：macOS / Linux / Windows（WSL）

---

## 📊 项目信息

| 项目 | 内容 |
|---|---|
| **GitHub** | https://github.com/Yanyeoo/inspiration-workflow-skill |
| **作者** | Shayla Deng @ Tencent PCG |
| **技术栈** | Python（纯标准库）+ JSON + Box Agent 多文件架构 |
| **开源协议** | MIT |
| **支持平台** | Box、Claude Code CLI、CodeBuddy、Codex CLI、小龙虾 |
| **数据存储** | 本地 JSON（无需云服务，隐私安全） |
| **依赖** | 零外部依赖 |

---

## 🔮 未来规划

- [ ] 接入向量数据库（Chroma/FAISS），实现语义检索
- [ ] 与腾讯文档直接对接，导出即发布
- [ ] 多用户隔离，支持团队协作场景
- [ ] 自动生成 Mermaid 知识图谱，可视化任务知识关联
- [ ] 接入 feedly MCP，自动把订阅文章归类到相关任务
