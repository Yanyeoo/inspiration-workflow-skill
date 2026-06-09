# TOOLS — 知识秘书 Agent 工具配置

## 一、核心 Skill（必须加载）

### inspiration-workflow（你开发的 Skill）
- **来源**：`https://github.com/Yanyeoo/inspiration-workflow-skill`
- **安装**：`use_skill("https://github.com/Yanyeoo/inspiration-workflow-skill")`
- **提供能力**：
  - `capture.py` — 灵感捕获 + 自动关联
  - `workflow.py` — 任务进度跟踪
  - `compress.py` — 阈值压缩 + 综述生成
  - `search.py` — 关键词检索
  - `export.py` — Markdown/JSON/Mermaid 导出

---

## 二、MCP 工具（必须配置）

### 2.1 文件系统（核心，必须）
| 工具 | 用途 |
|---|---|
| `read_file` | 读取 `tasks.json` / `inspirations.json` |
| `write_to_file` | 更新任务状态 / 存储新知识 |
| `list_files` | 列出 `reviews/` 和 `exports/` 目录 |
| `search_content` | 跨文件全文检索知识库 |

**数据目录约定**：
```
~/.workbuddy/memory/
├── tasks.json
├── inspirations/
│   └── inspirations.json
├── reviews/
└── exports/
```

### 2.2 定时任务（压缩与回顾，强烈推荐）
- MCP Server：`scheduled_task`
- 用途：
  - **每日晚 22:00**：自动检测各任务知识库是否达到压缩阈值
  - **每周一 09:00**：生成上周任务回顾摘要，推送企微
  - **每次新建任务时**：自动创建对应的压缩检查定时任务

**定时任务示例配置**：
```yaml
- name: "知识库阈值检查"
  cron: "0 22 * * *"
  action: "python compress.py --dry-run --all-tasks"
  
- name: "每周任务回顾"
  cron: "0 9 * * 1"
  action: "python export.py --all-tasks --format markdown --weekly-review"
```

### 2.3 企微推送（异步通知，推荐）
- MCP Server：`wecom_push`
- 用途：
  - 压缩综述生成后推送通知
  - 每周回顾摘要推送
  - 任务进度超过 3 天无更新时提醒
  - Blocker 记录后推送提醒「已记录困难，随时说下一步」

### 2.4 内网搜索（知识增强，推荐）
- MCP Server：`isearch`
- 用途：
  - 记录 blocker 时，自动搜索内网知识库中是否有解决方案
  - 记录 paper/url 时，检索相关内网文档补充背景

### 2.5 浏览器自动化（链接内容提取，可选）
- MCP Server：`playwright`
- 用途：
  - 用户分享链接时，自动抓取页面标题 + 摘要存入知识库
  - 不只存 URL，存有意义的内容摘要

---

## 三、可集成的其他 Skills

### 优先级 P0（显著提升体验）

#### `scheduled-task-creator`
- 触发时机：用户说「每周帮我生成回顾」、「定时压缩」
- 作用：引导式创建定时任务，接管 scheduled_task MCP 配置

#### `xlsx`
- 触发时机：用户说「导出任务看板」、「生成进度表格」
- 作用：将 `tasks.json` 导出为带格式的 Excel，包含进度条、甘特图样式

#### `pdf`
- 触发时机：用户说「生成项目报告」、「打印本周综述」
- 作用：将 Markdown 综述渲染为精美 PDF，适合分享/归档

### 优先级 P1（锦上添花）

#### `workflow-orchestrator`
- 触发时机：任务流程固化后
- 作用：将高频工作流（如「每次创建任务时的初始化步骤」）封装为可复用 YAML 模板

#### `docx`
- 触发时机：导出需要兼容 Word 格式时
- 作用：生成可编辑的 .docx 格式任务报告

#### `feedly`（通过 MCP）
- 触发时机：用户订阅了信息源且想关联到任务知识库
- 作用：自动把 feedly 日报中的相关文章捕获为 paper 类型知识

---

## 四、工具调用决策树

```
用户消息到来
│
├─ 包含「http」/ 「论文」/ 「arxiv」?
│   └─ capture.py --type paper/url + playwright 抓取摘要
│
├─ 包含「想到」/ 「点子」/ 「可以用」?
│   └─ capture.py --type idea
│
├─ 包含「做了」/ 「完成了」/ 「进度」?
│   └─ workflow.py --action ... --progress ...
│
├─ 包含「卡住」/ 「报错」/ 「不知道怎么」?
│   └─ workflow.py --blocker ... 
│   └─ isearch 搜索内网解决方案
│   └─ 读 tasks.json 当前知识库推荐 next_steps
│
├─ 包含「下一步」/ 「接下来干嘛」?
│   └─ 读 tasks.json（active_task + knowledge）
│   └─ search.py --task-id {active} 检索相关知识
│   └─ 综合生成推荐
│
├─ 包含「压缩」/ 「综述」/ 达到阈值?
│   └─ 确认后执行 compress.py
│
└─ 包含「导出」/ 「报告」/ 「总结」?
    └─ export.py + 可选 pdf/xlsx skill
```
