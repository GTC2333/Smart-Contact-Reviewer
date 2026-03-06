# UI升级实施计划：极简现代风 + 温暖奶油风

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将智能合同审核系统前端从通用紫色渐变风格升级为温暖奶油色极简现代风格

**Architecture:** 修改 frontend/app.py 中的 CSS 变量和样式定义，添加字体加载和动效，实现温暖专业的法律工作台视觉

**Tech Stack:** Streamlit, CSS3 (CSS Variables, Animations, Transitions)

---

## 任务概览

| 任务 | 内容 |
|------|------|
| 1 | 定义 CSS 变量（配色、字体） |
| 2 | 添加 Google Fonts 字体加载 |
| 3 | 重写侧边栏样式 |
| 4 | 重写统计卡片样式 |
| 5 | 重写风险标签样式 |
| 6 | 重写上传区域样式 |
| 7 | 重写 Tab 切换样式 |
| 8 | 重写条款卡片样式 |
| 9 | 添加页面加载动效 |
| 10 | 添加交互动效 |

---

## 详细任务

### Task 1: 定义 CSS 变量（配色、字体）

**文件:**
- 修改: `frontend/app.py:130-135`

**Step 1: 添加 CSS 变量块**

在 `<style>` 标签开头添加：

```css
:root {
    /* 主色调 - 温暖奶油风 */
    --color-bg-main: #F5F0E8;
    --color-bg-card: #FFFDF9;
    --color-accent: #D4A574;
    --color-accent-hover: #C49565;

    /* 风险色 */
    --color-risk-high: #E07A5F;
    --color-risk-medium: #E9B44C;
    --color-risk-low: #81B29A;

    /* 文字色 */
    --color-text-primary: #3D405B;
    --color-text-secondary: #6B705C;
    --color-text-muted: #9A948A;

    /* 边框色 */
    --color-border: #E8E2D9;
    --color-border-light: #F0EBE3;

    /* 阴影 */
    --shadow-sm: 0 2px 8px rgba(61, 64, 91, 0.06);
    --shadow-md: 0 4px 20px rgba(61, 64, 91, 0.08);
    --shadow-lg: 0 8px 32px rgba(61, 64, 91, 0.12);

    /* 圆角 */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-full: 9999px;

    /* 字体 */
    --font-serif: 'Noto Serif SC', serif;
    --font-sans: 'Noto Sans SC', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    /* 过渡 */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.3s ease;
    --transition-slow: 0.4s ease;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: add CSS variables for warm cream theme"
```

---

### Task 2: 添加 Google Fonts 字体加载

**文件:**
- 修改: `frontend/app.py:130` (在 `<style>` 之前添加)

**Step 1: 添加字体链接**

在 `<style>` 标签之前添加：

```python
# 在 import 之后添加
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: add Google Fonts for typography"
```

---

### Task 3: 重写侧边栏样式

**文件:**
- 修改: `frontend/app.py:135-145` (CSS 部分)

**Step 1: 替换侧边栏 CSS**

```css
/* 侧边栏 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFDF9 0%, #F5F0E8 100%);
    border-right: 1px solid var(--color-border);
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent;
}

/* 侧边栏标题 */
.sidebar-title {
    font-family: var(--font-serif);
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-primary);
    padding: 1rem 0;
    text-align: center;
    background: linear-gradient(135deg, var(--color-accent) 0%, #B8956A 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* 新建按钮 */
.btn-new-audit {
    background: var(--color-accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    transition: all var(--transition-fast) !important;
}

.btn-new-audit:hover {
    background: var(--color-accent-hover) !important;
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* 历史记录项 */
.session-item {
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all var(--transition-fast);
    border: 1px solid transparent;
}

.session-item:hover {
    background: rgba(212, 165, 116, 0.1);
    border-color: var(--color-border);
    transform: translateX(4px);
}

.session-item.active {
    background: rgba(212, 165, 116, 0.15);
    border-color: var(--color-accent);
}
```

**Step 2: 更新侧边栏 HTML**

修改 `frontend/app.py` 中的侧边栏部分：

```python
with st.sidebar:
    st.markdown('<p class="sidebar-title">🧠 智能合同审核系统</p>')
    st.markdown("---")

    # 新建审核按钮
    if st.button("➕ 新建审核", use_container_width=True, key="btn_new_audit"):
        navigate_to_home()
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign sidebar with warm cream theme"
```

---

### Task 4: 重写统计卡片样式

**文件:**
- 修改: `frontend/app.py:213-224`

**Step 1: 替换统计卡片 CSS**

```css
/* 统计卡片 */
.stat-card {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    border-left: 4px solid var(--color-accent);
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-normal);
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}

.stat-card.high { border-left-color: var(--color-risk-high); }
.stat-card.medium { border-left-color: var(--color-risk-medium); }
.stat-card.low { border-left-color: var(--color-risk-low); }

.stat-card .stat-number {
    font-family: var(--font-mono);
    font-size: 2.5rem;
    font-weight: 500;
    color: var(--color-text-primary);
}

.stat-card .stat-label {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    margin-top: 0.25rem;
}
```

**Step 2: 更新 Tab 1 中的统计卡片 HTML**

修改 tab1 中的统计卡片部分，使用新的结构：

```python
# 替换原来的 HTML 统计卡片为：
st.markdown(f"""
<div class="stat-card high">
    <div class="stat-number">{high}</div>
    <div class="stat-label">高风险</div>
</div>
""", unsafe_allow_html=True)
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign stat cards with border accent"
```

---

### Task 5: 重写风险标签样式

**文件:**
- 修改: `frontend/app.py:159-170`

**Step 1: 替换风险标签 CSS**

```css
/* 风险标签 - 柔和风格 */
.risk-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    font-weight: 500;
    border: 1px solid transparent;
    transition: all var(--transition-fast);
}

.risk-high {
    background: rgba(224, 122, 95, 0.12);
    color: var(--color-risk-high);
    border-color: rgba(224, 122, 95, 0.3);
}

.risk-medium {
    background: rgba(233, 180, 76, 0.12);
    color: var(--color-risk-medium);
    border-color: rgba(233, 180, 76, 0.3);
}

.risk-low {
    background: rgba(129, 178, 154, 0.12);
    color: var(--color-risk-low);
    border-color: rgba(129, 178, 154, 0.3);
}

.risk-badge:hover {
    border-width: 2px;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign risk badges with soft borders"
```

---

### Task 6: 重写上传区域样式

**文件:**
- 修改: `frontend/app.py:195-210`

**Step 1: 替换上传区域 CSS**

```css
/* 上传区域 */
.upload-area {
    background: var(--color-bg-card);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 3rem 2rem;
    text-align: center;
    transition: all var(--transition-normal);
    cursor: pointer;
}

.upload-area:hover {
    border-color: var(--color-accent);
    background: rgba(212, 165, 116, 0.03);
    box-shadow: var(--shadow-sm);
}

.upload-area [data-testid="stFileUploader"] {
    padding: 1rem;
}

/* Streamlit 文件上传器样式覆盖 */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    background: transparent !important;
    border: none !important;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign upload area with hover effects"
```

---

### Task 7: 重写 Tab 切换样式

**文件:**
- 修改: `frontend/app.py:186-194`

**Step 1: 替换 Tab CSS**

```css
/* Tab 切换 - 底部指示器风格 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid var(--color-border-light);
    padding-bottom: 0;
}

.stTabs [data-baseweb="tab"] {
    padding: 12px 24px;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    color: var(--color-text-secondary);
    font-weight: 500;
    transition: all var(--transition-fast);
    position: relative;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--color-accent);
    background: rgba(212, 165, 116, 0.05);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--color-accent);
    background: transparent;
}

.stTabs [data-baseweb="tab"][aria-selected="true"]::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--color-accent);
    border-radius: 3px 3px 0 0;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign tabs with animated underline"
```

---

### Task 8: 重写条款卡片样式

**文件:**
- 修改: `frontend/app.py:225-240`

**Step 1: 替换条款卡片 CSS**

```css
/* 条款卡片 */
.clause-card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border-light);
    border-left: 3px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 1rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: all var(--transition-normal);
}

.clause-card:hover {
    background: rgba(212, 165, 116, 0.03);
    border-left-color: var(--color-accent);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
}

.clause-card.selected {
    border-left-width: 5px;
    border-left-color: var(--color-accent);
    box-shadow: var(--shadow-md);
    background: rgba(212, 165, 116, 0.05);
}

/* 普通卡片 */
.card {
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
    border: 1px solid var(--color-border-light);
    transition: all var(--transition-normal);
}

.card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: redesign clause cards with hover lift"
```

---

### Task 9: 添加页面加载动效

**文件:**
- 修改: `frontend/app.py` (在 CSS 变量后添加)

**Step 1: 添加动画 keyframes**

```css
/* 页面加载动画 */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* 动画类 */
.animate-fade-in-up {
    animation: fadeInUp 0.5s ease forwards;
    opacity: 0;
}

.animate-delay-1 { animation-delay: 0.1s; }
.animate-delay-2 { animation-delay: 0.2s; }
.animate-delay-3 { animation-delay: 0.3s; }
.animate-delay-4 { animation-delay: 0.4s; }

/* 主内容区动效 */
.main-content {
    animation: fadeIn 0.4s ease;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: add page load animations"
```

---

### Task 10: 添加交互动效

**文件:**
- 修改: `frontend/app.py` (CSS 部分末尾)

**Step 1: 添加通用交互样式**

```css
/* 按钮动效 */
.stButton > button {
    transition: all var(--transition-fast) !important;
}

.stButton > button:hover {
    transform: scale(1.02);
}

.stButton > button:active {
    transform: scale(0.98);
}

/* 下拉菜单 */
[data-baseweb="select"] {
    border-radius: var(--radius-sm) !important;
}

/* 进度条 */
[data-testid="stProgress"] > div > div {
    background: var(--color-accent) !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--color-bg-main);
}

::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--color-accent);
}

/* 主背景 */
[data-testid="stAppViewContainer"] > div:first-child {
    background: var(--color-bg-main);
}

/* 内容区背景 */
.main .block-container {
    background: var(--color-bg-main);
    padding-top: 2rem;
    padding-bottom: 2rem;
}
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "style: add interaction animations and scrollbar"
```

---

## 验证步骤

完成所有任务后：

1. **启动后端**: `PYTHONPATH=. uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload`
2. **启动前端**: `streamlit run frontend/app.py`
3. **验证要点**:
   - [ ] 配色是否为温暖奶油色
   - [ ] 字体是否加载成功
   - [ ] 统计卡片是否有彩色左边框
   - [ ] Tab 切换是否有底部指示器
   - [ ] 条款卡片悬停是否有上浮效果
   - [ ] 滚动条是否美化

---

## 执行选择

**Plan complete and saved to `docs/plans/2026-03-06-ui-upgrade-plan.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
