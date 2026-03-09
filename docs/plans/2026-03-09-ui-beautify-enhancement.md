# UI美化增强计划 - 左侧栏与字体优化

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 解决左侧栏丑陋和字体大小问题，进一步美化UI细节

**Architecture:** 修改 frontend/app.py 中的 CSS 样式和 HTML 结构，针对侧边栏和字体进行专项优化

**Tech Stack:** Streamlit, CSS3

---

## 任务概览

| 任务 | 内容 |
|------|------|
| 1 | 重新设计侧边栏头部区域（添加 Logo 图标、渐变背景） |
| 2 | 美化侧边栏"新建审核"按钮 |
| 3 | 美化侧边栏会话历史列表（添加图标、日期、更好的间距） |
| 4 | 统一全局字体大小系统 |
| 5 | 优化标题层级字体大小 |
| 6 | 优化卡片和组件内部字体 |
| 7 | 添加深色模式支持（可选） |

---

## 详细任务

### Task 1: 重新设计侧边栏头部

**文件:**
- 修改: `frontend/app.py:700-720`

**Step 1: 添加侧边栏头部 Logo 图标和渐变背景 CSS**

在 CSS 中添加：

```css
/* 侧边栏头部区域 */
.sidebar-header {
    background: linear-gradient(135deg, #FFFDF9 0%, #F5F0E8 100%);
    padding: 1.5rem 1rem;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    text-align: center;
    margin: -1rem -1rem 1rem -1rem;
    border-bottom: 1px solid var(--color-border-light);
}

.sidebar-logo {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    display: block;
}

.sidebar-brand {
    font-family: var(--font-serif);
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #3D405B 0%, #6B705C 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 1px;
}

.sidebar-subtitle {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin-top: 0.25rem;
    font-weight: 400;
}
```

**Step 2: 更新侧边栏 HTML 结构**

```python
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <span class="sidebar-logo">⚖️</span>
        <div class="sidebar-brand">智能合同审核</div>
        <div class="sidebar-subtitle">Smart Contract Review</div>
    </div>
    """, unsafe_allow_html=True)
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign sidebar header with logo and gradient"
```

---

### Task 2: 美化侧边栏新建审核按钮

**文件:**
- 修改: `frontend/app.py:720-740`

**Step 1: 添加按钮 CSS**

```css
/* 侧边栏按钮 */
.sidebar-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: 0.95rem;
    transition: all var(--transition-normal);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.sidebar-btn-primary {
    background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%);
    color: white;
    border: none;
    box-shadow: var(--shadow-sm);
}

.sidebar-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, var(--color-accent-hover) 0%, #B8956A 100%);
}

.sidebar-btn-secondary {
    background: var(--color-bg-card);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}

.sidebar-btn-secondary:hover {
    background: rgba(212, 165, 116, 0.1);
    border-color: var(--color-accent);
}
```

**Step 2: 更新按钮 HTML**

```python
# 新建审核按钮
st.markdown("""
<button class="sidebar-btn sidebar-btn-primary" onclick="window.location.href='?page=home'">
    <span>➕</span> 新建审核
</button>
""", unsafe_allow_html=True)
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: beautify sidebar buttons with gradients"
```

---

### Task 3: 美化侧边栏会话历史列表

**文件:**
- 修改: `frontend/app.py:740-770`

**Step 1: 添加会话列表 CSS**

```css
/* 会话历史列表 */
.session-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--color-border-light);
    margin-bottom: 0.75rem;
}

.session-list-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.session-count {
    background: var(--color-bg-card);
    padding: 2px 8px;
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    color: var(--color-text-muted);
}

.session-item {
    padding: 0.875rem 1rem;
    border-radius: var(--radius-md);
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all var(--transition-fast);
    border: 1px solid transparent;
    background: var(--color-bg-card);
}

.session-item:hover {
    background: rgba(212, 165, 116, 0.08);
    border-color: var(--color-border);
    transform: translateX(4px);
    box-shadow: var(--shadow-sm);
}

.session-item.active {
    background: rgba(212, 165, 116, 0.12);
    border-color: var(--color-accent);
    box-shadow: var(--shadow-sm);
}

.session-title {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--color-text-primary);
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.session-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    color: var(--color-text-muted);
}

.session-date {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.session-empty {
    text-align: center;
    padding: 2rem 1rem;
    color: var(--color-text-muted);
    font-size: 0.85rem;
}
```

**Step 2: 更新会话列表 HTML**

```python
# 会话历史
st.markdown(f"""
<div class="session-list-header">
    <span class="session-list-title">📁 审核历史</span>
    <span class="session-count">{len(sessions)}</span>
</div>
""", unsafe_allow_html=True)

for session in sessions:
    # 显示会话项
    st.markdown(f"""
    <div class="session-item" onclick="window.location.href='?session={session['id']}'">
        <div class="session-title">{session['name']}</div>
        <div class="session-meta">
            <span class="session-date">📅 {session['date']}</span>
            <span class="risk-badge {session['risk_level']}">{session['risk_count']}风险</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: beautify session history list in sidebar"
```

---

### Task 4: 统一全局字体大小系统

**文件:**
- 修改: `frontend/app.py:184-230` (CSS Variables)

**Step 1: 添加字体大小变量**

在 `:root` 中添加：

```css
/* 字体大小系统 */
--font-size-xs: 0.7rem;
--font-size-sm: 0.8rem;
--font-size-base: 0.9rem;
--font-size-md: 1rem;
--font-size-lg: 1.1rem;
--font-size-xl: 1.25rem;
--font-size-2xl: 1.5rem;
--font-size-3xl: 2rem;
```

**Step 2: 添加全局字体样式**

```css
/* 全局字体 */
html, body, .stApp {
    font-family: var(--font-sans);
    font-size: var(--font-size-base);
    color: var(--color-text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* 所有文字元素基础字体大小 */
p, span, div {
    font-size: var(--font-size-base);
    line-height: 1.6;
}
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: add unified font size system"
```

---

### Task 5: 优化标题层级字体大小

**文件:**
- 修改: `frontend/app.py` (CSS 部分)

**Step 1: 添加标题样式**

```css
/* 标题层级 */
h1, .h1 {
    font-family: var(--font-serif);
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: 1rem;
    letter-spacing: -0.5px;
}

h2, .h2 {
    font-family: var(--font-serif);
    font-size: var(--font-size-2xl);
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 0.75rem;
}

h3, .h3 {
    font-family: var(--font-sans);
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 0.5rem;
}

h4, .h4 {
    font-family: var(--font-sans);
    font-size: var(--font-size-lg);
    font-weight: 500;
    color: var(--color-text-secondary);
    margin-bottom: 0.5rem;
}

/* Streamlit 标题覆盖 */
.stMarkdown h1 {
    font-family: var(--font-serif);
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--color-text-primary);
}

.stMarkdown h2 {
    font-family: var(--font-serif);
    font-size: var(--font-size-2xl);
    font-weight: 600;
}

.stMarkdown h3 {
    font-family: var(--font-sans);
    font-size: var(--font-size-xl);
    font-weight: 600;
}

.stMarkdown h4 {
    font-family: var(--font-sans);
    font-size: var(--font-size-lg);
    font-weight: 500;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: optimize heading font sizes with hierarchy"
```

---

### Task 6: 优化卡片和组件内部字体

**文件:**
- 修改: `frontend/app.py` (CSS 部分)

**Step 1: 优化各组件字体**

```css
/* 卡片内部字体 */
.card {
    font-size: var(--font-size-base);
}

.card-title {
    font-size: var(--font-size-lg);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.card-text {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    line-height: 1.6;
}

/* 条款卡片 */
.clause-card {
    font-size: var(--font-size-base);
}

.clause-title {
    font-size: var(--font-size-md);
    font-weight: 600;
    color: var(--color-text-primary);
}

.clause-content {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    line-height: 1.5;
    margin-top: 0.5rem;
}

/* 风险详情 */
.risk-detail {
    font-size: var(--font-size-sm);
}

.risk-issue {
    font-weight: 500;
    font-size: var(--font-size-base);
}

.risk-suggestion {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
}

/* 统计数字 */
.stat-number {
    font-family: var(--font-mono);
    font-size: var(--font-size-3xl);
    font-weight: 500;
}

.stat-label {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
}

/* 按钮文字 */
.stButton > button {
    font-size: var(--font-size-base);
    font-weight: 500;
}

/* 输入框 */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    font-size: var(--font-size-base);
}

/* 下拉菜单 */
.stSelectbox > div > div > div {
    font-size: var(--font-size-base);
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: optimize component internal font sizes"
```

---

### Task 7: 添加深色模式支持（可选）

**文件:**
- 修改: `frontend/app.py` (CSS 部分)

**Step 1: 添加深色模式媒体查询**

```css
/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
    :root {
        --color-bg-main: #1A1A2E;
        --color-bg-card: #242438;
        --color-text-primary: #E8E8E8;
        --color-text-secondary: #A0A0A0;
        --color-text-muted: #707070;
        --color-border: #3A3A4A;
        --color-border-light: #2A2A3A;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #242438 0%, #1A1A2E 100%);
    }

    .sidebar-header {
        background: linear-gradient(135deg, #242438 0%, #1A1A2E 100%);
    }
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: add dark mode support"
```

---

## 验证步骤

完成所有任务后：

1. **启动前端**: `streamlit run frontend/app.py`
2. **验证要点**:
   - [ ] 侧边栏头部是否有 Logo 图标和渐变背景
   - [ ] 新建审核按钮是否有渐变色和悬停动效
   - [ ] 会话历史列表是否有更好的视觉层次
   - [ ] 全局字体大小是否统一（base: 0.9rem）
   - [ ] 标题是否有正确的层级大小
   - [ ] 卡片、条款、风险详情等组件字体是否协调

---

## 执行选择

**Plan complete and saved to `docs/plans/2026-03-09-ui-beautify-enhancement.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
