# 知识秘书 Agent — 多平台部署指南

> 一份 Skill，五个平台，零重复配置。

---

## 平台兼容一览

| 平台 | 安装方式 | 触发方式 | 体验等级 |
|---|---|---|---|
| **Box / WorkBuddy** | `use_skill` URL 安装 | 对话自动触发 | ⭐⭐⭐⭐⭐ 最佳 |
| **CodeBuddy（腾讯内网）** | 复制 SKILL.md 到插件目录 | `@knowledge-secretary` | ⭐⭐⭐⭐ |
| **Claude Code CLI** | 复制 CLAUDE.md 到 commands | `/inspiration-workflow` | ⭐⭐⭐⭐ |
| **Codex CLI** | 复制到 `~/.codex/instructions/` | 对话自动读取 | ⭐⭐⭐ |
| **小龙虾 / 其他 CLI** | 通用 system prompt 注入 | 对话自动触发 | ⭐⭐⭐ |

---

## 方式一：Box / WorkBuddy（推荐，最丝滑）

### 一键安装
在 Box 对话框中直接发送：

```
use_skill("https://github.com/Yanyeoo/inspiration-workflow-skill")
```

Agent 级别安装（完整五文件架构）：
```
agent_install("https://github.com/Yanyeoo/inspiration-workflow-skill")
```

### 验证
```
我想到可以用图数据库替代 JSON 存储知识关联
```
**期望**：`✅ 已记录到 [当前任务]：图数据库替代 JSON（idea）`

### 定时任务一键配置
```
use_skill("scheduled-task-creator")
# 然后说：每天晚上 10 点帮我检查知识库阈值，每周一早上生成周报
```

---

## 方式二：CodeBuddy（腾讯内网 IDE 插件）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git

# 复制到 CodeBuddy Skill 目录（根据你的 CodeBuddy 版本调整路径）
cp -r inspiration-workflow-skill ~/.codebuddy/skills/knowledge-secretary
```

### 在 IDE 中使用
在代码编辑器对话框中：
```
@knowledge-secretary 我刚完成了 auth 模块的重构，进度更新到 60%
```

### 与代码关联的特殊用法
```
# 记录代码相关灵感时自动带上文件上下文
@knowledge-secretary 这里的设计模式可以用 Strategy Pattern 优化，记一下
```

---

## 方式三：Claude Code CLI

### 安装步骤

```bash
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git
cd inspiration-workflow-skill

# 安装到 Claude Code commands 目录
mkdir -p ~/.claude/commands
cp CLAUDE.md ~/.claude/commands/inspiration-workflow.md
```

### 使用方式
```bash
# 启动 Claude Code CLI
claude

# 调用知识秘书
/inspiration-workflow

# 或直接对话（CLAUDE.md 作为 system context 自动注入）
> 我想到一个优化点：把压缩阈值改成动态的，基于任务活跃度自动调整
```

### 在项目目录中使用（推荐）
```bash
# 在项目根目录创建 CLAUDE.md 软链，让 Claude Code 自动读取
cd ~/your-project
ln -s ~/.claude/commands/inspiration-workflow.md CLAUDE.md

# 之后在该项目目录启动 claude，知识秘书功能自动激活
claude
```

---

## 方式四：Codex CLI（OpenAI）

### 安装步骤

```bash
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git

# Codex 读取 instructions 目录作为 system prompt
mkdir -p ~/.codex/instructions
cp inspiration-workflow-skill/SKILL.md ~/.codex/instructions/knowledge-secretary.md
```

### 使用方式
```bash
codex
# 对话中自动激活知识秘书行为
> 开始做 RAG 优化项目
> 我想到可以用稀疏检索 + 密集检索混合的方案
```

### 注意事项
- Codex CLI 不支持 frontmatter，使用前去掉 `---` 头部
- Python 脚本路径需手动指定（Codex 不自动执行本地脚本）

---

## 方式五：小龙虾 / 通用 CLI 工具

### 通用 System Prompt 注入方式

```bash
# 提取纯文本版 system prompt
cat inspiration-workflow-skill/SKILL.md | grep -v "^---" > /tmp/ks-prompt.txt

# 小龙虾示例（根据实际命令行参数调整）
xiaolongxia --system-file /tmp/ks-prompt.txt

# 或设置环境变量（部分工具支持）
export SYSTEM_PROMPT=$(cat /tmp/ks-prompt.txt)
```

### 手动触发脚本（任何平台通用）

如果所在平台不能自动调用脚本，可手动运行：

```bash
# 捕获灵感
python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/capture.py \
  --content "你的想法" --type idea

# 更新工作流
python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/workflow.py \
  --action "完成了某件事" --progress 50

# 查看状态
python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/workflow.py --status

# 压缩
python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/compress.py
```

---

## 数据共享：跨平台无缝切换

所有平台共享同一份数据文件（`~/.workbuddy/memory/`），这意味着：

```
在 Box 用对话记录了一个灵感
    ↓
打开 Claude Code CLI 继续开发
    ↓
/inspiration-workflow → 「接下来干嘛」
    ↓
AI 读取同一份知识库，给出有依据的建议
```

**数据路径约定**（统一，避免分裂）：
```
~/.workbuddy/memory/
├── tasks.json
├── inspirations/inspirations.json
├── reviews/
└── exports/
```

---

## 一键脚本（首次环境初始化）

```bash
#!/bin/bash
# setup.sh — 知识秘书一键初始化

set -e

echo "🚀 初始化知识秘书 Agent..."

# 1. 克隆 Skill
git clone https://github.com/Yanyeoo/inspiration-workflow-skill.git \
  ~/.workbuddy/skills/inspiration-workflow-skill

# 2. 创建数据目录
mkdir -p ~/.workbuddy/memory/inspirations
mkdir -p ~/.workbuddy/memory/reviews
mkdir -p ~/.workbuddy/memory/exports

# 3. 安装 Python 依赖（无外部依赖，仅标准库）
echo "✅ 无需额外 pip 安装（纯标准库）"

# 4. 安装到 Claude Code CLI（如果存在）
if command -v claude &> /dev/null; then
  mkdir -p ~/.claude/commands
  cp ~/.workbuddy/skills/inspiration-workflow-skill/CLAUDE.md \
     ~/.claude/commands/inspiration-workflow.md
  echo "✅ 已安装到 Claude Code CLI → /inspiration-workflow"
fi

# 5. 测试
python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/capture.py \
  --content "初始化测试：知识秘书 Agent 已就绪" \
  --type milestone --tags "初始化,测试"

echo ""
echo "✅ 安装完成！"
echo "   Box/WorkBuddy：use_skill('https://github.com/Yanyeoo/inspiration-workflow-skill')"
echo "   Claude Code CLI：/inspiration-workflow"
echo "   手动脚本：python ~/.workbuddy/skills/inspiration-workflow-skill/scripts/capture.py"
```

运行方式：
```bash
curl -fsSL https://raw.githubusercontent.com/Yanyeoo/inspiration-workflow-skill/master/setup.sh | bash
# 或
bash setup.sh
```
