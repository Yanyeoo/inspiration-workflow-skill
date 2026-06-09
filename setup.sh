#!/usr/bin/env bash
# setup.sh — 知识秘书 Agent 一键初始化
# 支持 macOS / Linux / Windows WSL
# 用法：curl -fsSL https://raw.githubusercontent.com/Yanyeoo/inspiration-workflow-skill/master/setup.sh | bash

set -e

SKILL_DIR="${HOME}/.workbuddy/skills/inspiration-workflow-skill"
MEMORY_DIR="${HOME}/.workbuddy/memory"
REPO_URL="https://github.com/Yanyeoo/inspiration-workflow-skill.git"

echo ""
echo "🚀 知识秘书 Agent 一键初始化"
echo "================================"

# ── Step 1: 克隆或更新仓库 ───────────────────────────
if [ -d "$SKILL_DIR/.git" ]; then
  echo "📦 检测到已有安装，执行更新..."
  cd "$SKILL_DIR" && git pull --quiet
  echo "✅ 已更新到最新版本"
else
  echo "📦 克隆仓库..."
  git clone --quiet "$REPO_URL" "$SKILL_DIR"
  echo "✅ 仓库克隆完成：$SKILL_DIR"
fi

# ── Step 2: 创建数据目录 ─────────────────────────────
echo "📁 初始化数据目录..."
mkdir -p "$MEMORY_DIR/inspirations"
mkdir -p "$MEMORY_DIR/reviews"
mkdir -p "$MEMORY_DIR/exports"
echo "✅ 数据目录：$MEMORY_DIR"

# ── Step 3: 验证 Python ──────────────────────────────
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  echo "❌ 未找到 Python 3.8+，请先安装 Python"
  exit 1
fi
PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PY_VERSION"

# ── Step 4: 安装到 Claude Code CLI（如果存在）─────────
if command -v claude &>/dev/null; then
  mkdir -p ~/.claude/commands
  cp "$SKILL_DIR/CLAUDE.md" ~/.claude/commands/inspiration-workflow.md
  echo "✅ 已安装到 Claude Code CLI → 使用 /inspiration-workflow 调用"
fi

# ── Step 5: 冒烟测试 ─────────────────────────────────
echo "🧪 运行安装测试..."
$PYTHON "$SKILL_DIR/scripts/capture.py" \
  --content "安装测试：知识秘书 Agent v2.0 已就绪" \
  --type milestone \
  --tags "初始化,测试" \
  --file "$MEMORY_DIR/inspirations/inspirations.json" \
  > /dev/null

echo "✅ 测试通过"

# ── 完成 ─────────────────────────────────────────────
echo ""
echo "================================"
echo "🎉 安装完成！"
echo ""
echo "使用方式："
echo "  Box/WorkBuddy ：use_skill('https://github.com/Yanyeoo/inspiration-workflow-skill')"
echo "  Claude Code   ：claude → /inspiration-workflow"
echo "  手动脚本      ：python $SKILL_DIR/scripts/capture.py --content '你的想法'"
echo ""
echo "详细文档：https://github.com/Yanyeoo/inspiration-workflow-skill/blob/master/DEPLOY.md"
