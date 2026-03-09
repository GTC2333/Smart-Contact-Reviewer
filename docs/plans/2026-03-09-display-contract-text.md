# 合同审核过程显示全文实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在合同审核过程中（前台上传后开始分析到结果返回的整个阶段），实时显示完整的合同原文文本，让用户可以对照查看审核进度

**Architecture:** 修复当前前端代码中的时序问题 - 合同文本在流式传输开始后才到达，但UI检查在流处理之前；改用placeholder模式在收到第一个SSE事件后显示合同文本；同时完善会话详情页的合同原文Tab

**Tech Stack:** Streamlit, Server-Sent Events (SSE), FastAPI

---

## 任务概览

| 任务 | 内容 |
|------|------|
| 1 | 修复流式审核时合同原文显示的时序问题 |
| 2 | 优化合同原文显示区域的布局和样式 |
| 3 | 确保会话详情页合同原文Tab正确显示 |

---

## 详细任务

### Task 1: 修复流式审核时合同原文显示的时序问题

**文件:**
- 修改: `frontend/app.py:1320-1365`

**Step 1: 使用placeholder模式延迟显示合同原文**

当前代码在第1324行检查 `pending_contract_text`，但此时流处理尚未开始，contract_text 还未到达。修改为使用 Streamlit placeholder 模式：

```python
# 在 progress_bar = st.progress(0) 之后添加
contract_text_placeholder = st.empty()

# 删除原来的即时检查代码（约第1324-1334行）

# 在处理 SSE 事件的循环中，当收到 contract_text 事件时：
for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        buffer += chunk.decode("utf-8")

        while "data:" in buffer:
            start = buffer.find("data:")
            end = buffer.find("\n\n", start)
            if end == -1:
                break

            event_data = buffer[start:end]
            buffer = buffer[end+2:]

            try:
                data = json.loads(event_data.replace("data:", ""))
                event_type = data.get("type")

                if event_type == "contract_text":
                    # 在收到合同文本后，显示原文区域
                    contract_text = data.get("text", "")
                    st.session_state.pending_contract_text = contract_text

                    with contract_text_placeholder.container():
                        st.markdown("### 📄 合同原文")
                        st.text_area(
                            "原始合同文本",
                            value=contract_text,
                            height=250,
                            disabled=True,
                            key="contract_text_during_audit",
                            label_visibility="collapsed"
                        )
                        st.markdown("---")

                elif event_type == "progress":
                    # ... 现有代码

            except json.JSONDecodeError:
                pass
```

**Step 2: 测试验证**

启动前后端，上传一个合同，验证：
- [ ] 合同开始审核后，合同原文区域在进度条下方正确显示
- [ ] 合同原文内容完整无误
- [ ] 用户可以在审核过程中滚动查看合同内容

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "fix: resolve timing issue for contract text display during streaming audit"
```

---

### Task 2: 优化合同原文显示区域的布局和样式

**文件:**
- 修改: `frontend/app.py:185-280` (CSS部分)

**Step 1: 添加合同原文区域的CSS样式**

在 Custom CSS 部分添加：

```css
/* 合同原文显示区域 */
.contract-text-container {
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid var(--color-border-light);
}

.contract-text-header {
    font-family: var(--font-serif);
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.contract-text-area textarea {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    line-height: 1.8;
    background: var(--color-bg-main) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius-sm);
    padding: 1rem;
}
```

**Step 2: 更新HTML结构使用新样式**

```python
# 在显示合同原文时使用新样式
with contract_text_placeholder.container():
    st.markdown("""
    <div class="contract-text-container">
        <div class="contract-text-header">📄 合同原文</div>
    </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "原始合同文本",
        value=contract_text,
        height=300,
        disabled=True,
        key="contract_text_during_audit",
        label_visibility="collapsed"
    )
```

**Step 3: 提交**
```bash
git add frontend/app.py
git commit -m "style: add CSS for contract text display area"
```

---

### Task 3: 确保会话详情页合同原文Tab正确显示

**文件:**
- 修改: `frontend/app.py:1723-1744`

**Step 1: 检查并完善Tab 6的合同原文显示逻辑**

当前代码已存在，但需要确保正确获取合同文本：

```python
# Tab 6: 合同原文
with tab6:
    st.markdown("### 📄 原始合同文本")

    # 优先使用审核过程中的文本，其次使用会话存储的文本
    contract_text = (
        st.session_state.get("pending_contract_text") or
        result.get("contract_text", "")
    )

    if contract_text:
        st.text_area(
            "合同原文",
            value=contract_text,
            height=600,
            disabled=True,
            key="contract_text_viewer",
            label_visibility="collapsed"
        )

        # 添加复制按钮
        if st.button("📋 复制全文", use_container_width=True):
            st.success("已复制到剪贴板")
    else:
        st.warning("⚠️ 无法加载合同原文，请重新上传合同")
        st.info("提示：合同原文会在审核过程中自动保存")
```

**Step 2: 提交**
```bash
git add frontend/app.py
git commit -m "feat: improve contract text tab in session view"
```

---

## 验证步骤

完成所有任务后：

1. **启动后端**: `PYTHONPATH=. uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload`
2. **启动前端**: `streamlit run frontend/app.py`
3. **验证要点**:
   - [ ] 上传新合同后，在审核过程中立即显示合同原文
   - [ ] 合同原文显示在进度条下方，布局合理
   - [ ] 审核过程中可以滚动查看完整合同内容
   - [ ] 审核完成后进入会话详情
   - [ ] 切换到"合同原文"Tab，确认原文完整显示
   - [ ] 确认原文与条款内容对应

---

## 执行选择

**Plan complete and saved to `docs/plans/2026-03-09-display-contract-text.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
