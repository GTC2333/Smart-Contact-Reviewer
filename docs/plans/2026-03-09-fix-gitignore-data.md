# Git跟踪文件清理实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复.gitignore缺少data/目录规则的问题，并从git中移除已跟踪的data文件

**Architecture:** 简单的一步修复 - 更新.gitignore并使用git rm --cached移除跟踪

**Tech Stack:** Git, .gitignore

---

## 任务概览

| 任务 | 内容 |
|------|------|
| 1 | 更新.gitignore添加data/忽略规则 |
| 2 | 从git移除已跟踪的data文件 |

---

### Task 1: 更新.gitignore添加data/忽略规则

**文件:**
- 修改: `.gitignore:41-44`

**Step 1: 添加忽略规则**

在 `.gitignore` 文件末尾添加:

```gitignore
# 数据目录
data/           # 数据目录（包含samples和sessions）
```

**Step 2: 验证更改**

Run: `cat .gitignore | tail -10`
Expected: 显示新添加的 data/ 规则

**Step 3: 提交**

```bash
git add .gitignore
git commit -m "chore: add data/ to gitignore"
```

---

### Task 2: 从git移除已跟踪的data文件

**文件:**
- 执行: Git命令

**Step 1: 从git缓存移除data目录（保留本地文件）**

```bash
git rm -r --cached data/
```

Run: `git rm -r --cached data/`
Expected: 显示移除的文件列表，如 `data/samples/xxx.txt` 等

**Step 2: 验证状态**

```bash
git status
```

Expected: 只显示 `.gitignore` 的修改，不显示 data/ 文件

**Step 3: 提交**

```bash
git add .gitignore
git commit -m "chore: remove data/ from git tracking"
```

---

## 验证步骤

完成所有任务后:

1. 运行: `git status`
   - [ ] 只显示 `.gitignore` 修改
   - [ ] 无 data/ 文件在 "Changes" 或 "Untracked files" 中

2. 运行: `git ls-files | grep "^data/"`
   - [ ] 无输出（确认data目录已不被跟踪）

3. 确认本地文件完好:
   - [ ] `ls data/samples/` 文件存在
   - [ ] `ls data/sessions/` 文件存在

---

## 执行选择

**Plan complete and saved to `docs/plans/2026-03-09-fix-gitignore-data.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
