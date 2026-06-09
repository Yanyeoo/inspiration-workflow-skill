# AGENTS.md — 知识秘书 Agent 子 Agent 配置

## 子 Agent 架构说明

知识秘书以**单 Agent + 多 Skill** 为主体，在以下场景引入子 Agent：

---

## 子 Agent 1：知识压缩员（compress-agent）

**触发条件**：任务知识库 ≥ 30 条 OR 全局 ≥ 50 条  
**调用方式**：`mcp_call_tool serverName:"builtin" toolName:"task"`  
**职责**：
1. 读取指定任务的所有 `active` 知识条目
2. 按标签分组，提炼核心洞察
3. 生成 Markdown 综述文档存入 `reviews/`
4. 将已处理条目标记为 `archived`
5. 将核心洞察同步到 `MEMORY.md`

**不允许**：删除原始数据、修改 `created_at` 字段

---

## 子 Agent 2：回顾员（review-agent）

**触发条件**：每周一定时任务 OR 用户说「生成周报」  
**职责**：
1. 读取过去 7 天所有任务的 `history` 字段
2. 汇总「做了什么、遇到什么困难、解决了什么」
3. 对比各任务进度变化
4. 生成可发送到企微的周报摘要

**输出格式**：
```markdown
## 本周任务回顾（{日期范围}）

### 进展最大：{任务名}（{进度变化}）
- 完成：{action列表}
- 知识新增：{n} 条

### 本周困难
- {blocker} → {解决方案}

### 下周优先级
1. {任务名}：{推荐下一步}
```

---

## 子 Agent 3：搜索增强员（search-enhance-agent）

**触发条件**：记录 blocker 时 OR 用户问「有没有关于X的资料」  
**职责**：
1. 从 blocker 内容提取关键词
2. 并行搜索：本地知识库 + isearch 内网
3. 合并结果，排序后返回 Top 3 相关条目
4. 在主 Agent 推荐 next_steps 时作为引用来源

**不允许**：自行修改知识库数据
