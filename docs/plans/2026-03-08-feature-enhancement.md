# 功能增强实现计划：历史记录操作 + UI美化 + 流式输出

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 增加历史记录删除功能、美化UI组件、在审核过程中流式显示AI输出

**Architecture:**
1. **历史记录操作**: 在侧边栏会话列表增加删除/重命名按钮，使用确认对话框
2. **UI美化**: 增强CSS样式，增加更多动画效果，优化卡片和按钮设计
3. **流式输出**: 使用Server-Sent Events (SSE)实现实时流式输出，后端推送进度+内容片段，前端EventSource接收

**Tech Stack:**
- Streamlit (前端)
- FastAPI + SSE (后端流式)
- JavaScript EventSource API (前端接收)

---

## Task 1: 侧边栏增加删除按钮

**Files:**
- Modify: `frontend/app.py:540-556`

**Step 1: Add delete button to session items**

```python
# 在现有会话列表循环中，添加删除按钮
for session in st.session_state.sessions[:20]:
    session_id = session.get("session_id", "")
    contract_name = session.get("contract_name", "未命名")
    created_at = session.get("created_at", "")[:10]
    risk_count = session.get("risk_count", 0)

    # Session item container
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if st.button(f"📄 {contract_name[:10]}{'...' if len(contract_name) > 10 else ''}",
                     key=f"session_{session_id}"):
            navigate_to_session(session_id)
    with col2:
        # Delete button with icon
        if st.button("🗑️", key=f"delete_{session_id}", help="删除"):
            # Show confirmation
            pass
    with col3:
        risk_badge = f"<span class='risk-badge' style='font-size: 0.7rem;'>{risk_count}风险</span>"
        st.markdown(risk_badge, unsafe_allow_html=True)

    st.caption(f"{created_at}")
```

**Step 2: Add confirmation dialog CSS and logic**

```python
# Add to CSS section
.confirm-dialog {
    background: #FFFDF9;
    border: 2px solid #E07A5F;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
}
```

**Step 3: Test locally**

Run: `streamlit run frontend/app.py`
Expected: Delete buttons visible in sidebar

**Step 4: Commit**

```bash
git add frontend/app.py
git commit -m "feat: add delete button to session history"
```

---

## Task 2: 添加重命名功能

**Files:**
- Modify: `frontend/app.py:540-556`
- Modify: `api/server.py` (already has rename endpoint)

**Step 1: Add rename button**

```python
# 在删除按钮旁边添加重命名按钮
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    if st.button(...):
        navigate_to_session(session_id)
with col2:
    if st.button("✏️", key=f"rename_{session_id}", help="重命名"):
        # Store session_id to rename
        st.session_state.rename_session_id = session_id
        st.session_state.rename_contract_name = contract_name
with col3:
    if st.button("🗑️", key=f"delete_{session_id}", help="删除"):
        st.session_state.delete_session_id = session_id
with col4:
    st.markdown(...)
```

**Step 2: Add rename input field**

```python
# After the session list, check if rename mode is active
if "rename_session_id" in st.session_state and st.session_state.rename_session_id:
    st.markdown("### 重命名会话")
    new_name = st.text_input("新名称", value=st.session_state.rename_contract_name)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认重命名"):
            call_api_rename_session(st.session_state.rename_session_id, new_name)
            refresh_sessions()
            del st.session_state.rename_session_id
            st.rerun()
    with col2:
        if st.button("取消"):
            del st.session_state.rename_session_id
            st.rerun()
```

**Step 3: Commit**

```bash
git add frontend/app.py
git commit -m "feat: add rename functionality to session history"
```

---

## Task 3: 美化进度界面和动画效果

**Files:**
- Modify: `frontend/app.py:662-688` (progress display)
- Modify: `frontend/app.py:170-513` (CSS)

**Step 1: Enhance progress animation CSS**

```css
/* 增强进度界面 */
.progress-container {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-md);
    margin: 2rem 0;
}

.progress-header {
    font-family: var(--font-serif);
    font-size: 1.5rem;
    color: var(--color-text-primary);
    text-align: center;
    margin-bottom: 1.5rem;
}

.progress-steps {
    display: flex;
    justify-content: space-between;
    margin: 2rem 0;
    position: relative;
}

.progress-step {
    text-align: center;
    flex: 1;
    position: relative;
    z-index: 1;
}

.progress-step-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--color-border-light);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.5rem;
    transition: all var(--transition-normal);
}

.progress-step.active .progress-step-icon {
    background: var(--color-accent);
    color: white;
    transform: scale(1.1);
}

.progress-step.completed .progress-step-icon {
    background: var(--color-risk-low);
    color: white;
}

/* 脉冲动画 */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(212, 165, 116, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(212, 165, 116, 0); }
    100% { box-shadow: 0 0 0 0 rgba(212, 165, 116, 0); }
}

.progress-step.active .progress-step-icon {
    animation: pulse 2s infinite;
}
```

**Step 2: Update progress display in Python**

```python
# Replace current progress display with enhanced version
st.markdown("""
<div class="progress-container">
    <div class="progress-header">🔄 正在审核合同</div>
</div>
""", unsafe_allow_html=True)

# Show step indicators
steps = [
    ("📝", "解析合同", progress >= 5),
    ("🔍", "检索依据", progress >= 20),
    ("⚠️", "分析风险", progress >= 50),
    ("💡", "生成建议", progress >= 75),
]

step_html = '<div class="progress-steps">'
for icon, label, completed in steps:
    active = not completed
    step_html += f'''
    <div class="progress-step {'active' if active else 'completed'}">
        <div class="progress-step-icon">{icon}</div>
        <div>{label}</div>
    </div>
    '''
step_html += '</div>'
st.markdown(step_html, unsafe_allow_html=True)

st.progress(progress / 100)
```

**Step 3: Commit**

```bash
git add frontend/app.py
git commit -m "feat: enhance progress UI with animations"
```

---

## Task 4: 添加流式输出后端支持 (SSE)

**Files:**
- Modify: `api/server.py:233-266`
- Create: `api/services/stream_service.py`

**Step 1: Create stream service**

```python
# api/services/stream_service.py
"""
Streaming service for real-time audit updates.
"""
import json
from typing import Callable, Optional
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()


async def event_stream(audit_func: Callable, file_content: bytes, filename: str):
    """Generate SSE events for audit progress."""
    result_container = {}
    event_queue = asyncio.Queue()

    def progress_callback(progress: int, message: str):
        """Callback to capture progress updates."""
        event = json.dumps({
            "type": "progress",
            "progress": progress,
            "message": message
        })
        event_queue.put_nowait(f"data: {event}\n\n")

    def content_callback(step: str, content: str):
        """Callback to capture content updates."""
        event = json.dumps({
            "type": "content",
            "step": step,
            "content": content
        })
        event_queue.put_nowait(f"data: {event}\n\n")

    # Start audit in background
    loop = asyncio.get_event_loop()
    audit_task = loop.run_in_executor(
        None,
        lambda: run_audit_with_callbacks(file_content, filename, progress_callback, content_callback, result_container)
    )

    # Yield events as they come
    try:
        while not audit_task.done():
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=1.0)
                yield event
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

        # Get final result
        await audit_task
        while not event_queue.empty():
            event = event_queue.get_nowait()
            yield event

        # Send final result
        if result_container.get("result"):
            yield f"data: {json.dumps({'type': 'complete', 'result': result_container['result']})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


def run_audit_with_callbacks(file_content, filename, progress_callback, content_callback, result_container):
    """Run audit with callbacks."""
    # This would call the audit service with callbacks
    pass
```

**Step 2: Add SSE endpoint to server.py**

```python
from fastapi import BackgroundTasks

@app.post("/audit/stream")
async def audit_contract_stream(file: UploadFile = File(...)):
    """
    Stream contract audit with real-time progress updates.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not audit_service.file_handler.validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式"
        )

    file_content = await file.read()

    # Return streaming response
    return StreamingResponse(
        event_stream_audit(audit_service, file_content, file.filename),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


async def event_stream_audit(audit_svc, file_content, filename):
    """Generate SSE events."""
    import json

    # Progress callback
    async def send_progress(progress, message):
        event = json.dumps({"type": "progress", "progress": progress, "message": message})
        yield f"data: {event}\n\n"

    # Run audit in executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: audit_svc.audit_from_file(file_content, filename)
    )

    # Send completion
    yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"
```

**Step 3: Commit**

```bash
git add api/server.py api/services/stream_service.py
git commit -m "feat: add SSE streaming endpoint for real-time audit"
```

---

## Task 5: 前端集成流式输出

**Files:**
- Modify: `frontend/app.py:590-610`

**Step 1: Add streaming API function**

```python
def call_api_audit_stream(file_content: bytes, filename: str):
    """Call streaming audit API."""
    url = f"{get_api_base()}/audit/stream"
    files = {"file": (filename, file_content)}

    # Use requests with stream=True
    response = requests.post(url, files=files, stream=True, timeout=300)
    return response
```

**Step 2: Update progress display to handle streaming**

```python
# Replace current async polling with streaming
if uploaded_file is not None:
    try:
        # Start streaming
        response = call_api_audit_stream(file_bytes, filename)

        st.session_state.current_view = "session"
        st.session_state.stream_response = response
        st.session_state.stream_buffer = ""
        st.rerun()

    except Exception as e:
        st.error(f"审核失败：{str(e)}")

# In session view - handle streaming
elif st.session_state.get("stream_response"):
    response = st.session_state.stream_response

    # Process streaming data
    buffer = st.session_state.get("stream_buffer", "")

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            buffer += chunk.decode("utf-8")

            # Parse events
            while "data:" in buffer:
                start = buffer.find("data:")
                end = buffer.find("\n\n", start)
                if end == -1:
                    break

                event_data = buffer[start:end]
                buffer = buffer[end+2:]

                # Parse JSON
                try:
                    data = json.loads(event_data.replace("data:", ""))

                    if data.get("type") == "progress":
                        progress = data.get("progress", 0)
                        message = data.get("message", "")
                        # Update UI

                    elif data.get("type") == "complete":
                        result = data.get("result")
                        st.session_state.audit_result = result
                        del st.session_state.stream_response
                        st.rerun()

                except:
                    pass

    st.session_state.stream_buffer = buffer
```

**Step 3: Add Streamlit components for streaming display**

```python
# Use st.empty() for real-time updates
progress_placeholder = st.empty()
message_placeholder = st.empty()

# Update in streaming loop
progress_placeholder.progress(progress / 100)
message_placeholder.info(f"**{message}**")
```

**Step 4: Commit**

```bash
git add frontend/app.py
git commit -m "feat: integrate streaming audit in frontend"
```

---

## Task 6: 最终UI美化优化

**Files:**
- Modify: `frontend/app.py:170-513`

**Step 1: Add more sophisticated CSS animations**

```css
/* 渐入动画 */
@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 卡片悬停效果 */
.clause-card {
    position: relative;
    overflow: hidden;
}

.clause-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(212,165,116,0.1) 0%, transparent 100%);
    opacity: 0;
    transition: opacity var(--transition-normal);
}

.clause-card:hover::before {
    opacity: 1;
}

/* 风险卡片渐变背景 */
.risk-card-gradient {
    background: linear-gradient(135deg, #FFFDF9 0%, #F5F0E8 100%);
}
```

**Step 2: Add Toast notifications**

```python
# Add toast helper
def show_toast(message: str, icon: str = "✅"):
    st.toast(f"{icon} {message}")
```

**Step 3: Commit**

```bash
git add frontend/app.py
git commit -m "feat: enhance UI with advanced animations"
```

---

## 验证方案

1. **启动后端**: `PYTHONPATH=. uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload`
2. **启动前端**: `streamlit run frontend/app.py`
3. **测试流程**:
   - [ ] 上传合同 → 审核 → 查看流式输出
   - [ ] 查看侧边栏 → 点击删除按钮 → 确认删除
   - [ ] 点击重命名 → 输入新名称 → 确认重命名
   - [ ] 观察进度界面动画效果
   - [ ] 导出报告功能正常

---

## 执行顺序

1. Task 1: 侧边栏删除按钮
2. Task 2: 重命名功能
3. Task 3: 进度界面美化
4. Task 4: 后端SSE流式支持
5. Task 5: 前端流式输出集成
6. Task 6: 最终UI优化

