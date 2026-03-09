# 多智能体合同审核系统 - 后端完善计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完善后端多智能体合同审核功能，修复数据流问题，启用RAG法律检索，增强异步处理和导出功能

**Architecture:** 基于现有的4智能体架构（ContractFormatter → LawSearch → RiskAnnotator → Correction），修复数据流使前端能正确获取条款和修改建议，增加RAG法律检索支持，添加异步任务处理

**Tech Stack:** Python, FastAPI, Streamlit, LLM (DeepSeek/OpenAI/Anthropic), RAG (可选Chroma/Qdrant), SQLAlchemy (可选)

---

## 阶段一：修复数据流问题（关键）

### Task 1: 修复 Pipeline 输出结构

**Files:**
- Modify: `core/pipeline/contract_pipeline.py`
- Test: 直接运行 main.py 测试输出

**Step 1: 读取当前 pipeline 实现**

```bash
cat core/pipeline/contract_pipeline.py
```

**Step 2: 分析问题**

当前 pipeline 输出缺少：
- `clauses` - 结构化的条款列表
- `corrections` - 修改建议列表

**Step 3: 修改 pipeline 添加输出字段**

在 `ContractAuditPipeline.run()` 方法的返回结果中添加：

```python
# 添加到返回结果
result = {
    "contract_id": contract_id,
    "metadata": {...},
    "parties": parties,
    "clauses": clauses,  # 新增：结构化条款列表
    "annotations": annotations,
    "corrections": corrections,  # 新增：修改建议列表
}
```

**Step 4: 测试验证**

```bash
PYTHONPATH=. python main.py
```

检查输出是否包含 `clauses` 和 `corrections` 字段

**Step 5: 提交**

```bash
git add core/pipeline/contract_pipeline.py
git commit -m "fix: pipeline output includes clauses and corrections"
```

---

### Task 2: 修复前端数据访问

**Files:**
- Modify: `frontend/app.py` - 检查数据访问代码
- Test: 访问前端页面验证

**Step 1: 检查前端数据访问**

```bash
grep -n "clauses\|corrections" frontend/app.py
```

**Step 2: 修复前端代码**

确保前端正确访问 `result.get("clauses", [])` 和 `result.get("corrections", [])`

**Step 3: 验证**

启动前端并测试上传合同

**Step 4: 提交**

```bash
git add frontend/app.py
git commit -m "fix: frontend correctly accesses clauses and corrections from pipeline"
```

---

## 阶段二：启用 RAG 法律检索

### Task 3: 配置并启用 RAG

**Files:**
- Modify: `config/settings.yaml` - 启用 RAG
- Modify: `core/rag/` - 检查现有 RAG 实现
- Create: `data/legal_docs/` - 法律文档存储目录

**Step 1: 修改配置启用 RAG**

```yaml
rag:
  enabled: true
  vector_store: chroma  # 或 qdrant
  embedding_model: text-embedding-ada-002
  collection_name: legal_references
```

**Step 2: 检查现有 RAG 实现**

```bash
ls -la core/rag/
cat core/rag/*.py
```

**Step 3: 确保 RAG 组件可用**

如果 RAG 实现不完整，需要补充 `core/rag/retriever.py`

**Step 4: 测试 RAG 检索**

```python
# 测试脚本
from core.rag.retriever import LegalRetriever
retriever = LegalRetriever()
results = retriever.search("合同违约责任")
print(results)
```

**Step 5: 提交**

```bash
git add config/settings.yaml core/rag/
git commit -m "feat: enable RAG for legal reference search"
```

---

## 阶段三：增强异步处理

### Task 4: 添加异步任务处理

**Files:**
- Modify: `api/server.py` - 添加异步端点
- Create: `api/tasks.py` - 任务管理模块

**Step 1: 创建任务管理模块**

```python
# api/tasks.py
import uuid
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}

    def create_task(self, contract_name: str) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "contract_name": contract_name,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None,
        }
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, status: str, result=None, error=None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result:
                self.tasks[task_id]["result"] = result
            if error:
                self.tasks[task_id]["error"] = error

task_manager = TaskManager()
```

**Step 2: 添加异步 API 端点**

```python
# api/server.py 新增
from api.tasks import task_manager

@app.post("/audit/async")
async def audit_contract_async(file: UploadFile = File(...)):
    """异步审核合同"""
    task_id = task_manager.create_task(file.filename)
    # 启动后台任务
    return {"task_id": task_id, "status": "pending"}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
```

**Step 3: 提交**

```bash
git add api/tasks.py api/server.py
git commit -m "feat: add async task processing for long contracts"
```

---

## 阶段四：增强导出功能

### Task 5: 添加 PDF/Word 导出

**Files:**
- Create: `core/exporters/__init__.py`
- Create: `core/exporters/pdf_exporter.py`
- Create: `core/exporters/word_exporter.py`
- Modify: `api/server.py` - 添加导出端点
- Modify: `frontend/app.py` - 添加导出按钮

**Step 1: 安装依赖**

```bash
pip install reportlab python-docx
```

**Step 2: 创建 PDF 导出器**

```python
# core/exporters/pdf_exporter.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from typing import Dict, Any

class PDFExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def export(self, audit_result: Dict[str, Any], output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # 添加标题
        title = Paragraph("合同审核报告", self.styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # 添加风险统计
        annotations = audit_result.get("annotations", [])
        risk_summary = f"<b>风险统计：</b> 共 {len(annotations)} 项风险"
        story.append(Paragraph(risk_summary, self.styles['Normal']))
        story.append(Spacer(1, 12))

        # 添加条款内容
        clauses = audit_result.get("clauses", [])
        if clauses:
            story.append(Paragraph("<b>合同条款：</b>", self.styles['Heading2']))
            for clause in clauses[:10]:  # 限制数量
                story.append(Paragraph(f"{clause.get('title', '')}", self.styles['Heading3']))
                story.append(Paragraph(clause.get('content', '')[:200], self.styles['Normal']))
                story.append(Spacer(1, 6))

        doc.build(story)
```

**Step 3: 创建 Word 导出器**

```python
# core/exporters/word_exporter.py
from docx import Document
from typing import Dict, Any

class WordExporter:
    def export(self, audit_result: Dict[str, Any], output_path: str):
        doc = Document()
        doc.add_heading('合同审核报告', 0)

        # 风险统计
        annotations = audit_result.get("annotations", [])
        doc.add_paragraph(f"风险统计：共 {len(annotations)} 项风险")

        # 条款内容
        clauses = audit_result.get("clauses", [])
        if clauses:
            doc.add_heading('合同条款', level=1)
            for clause in clauses[:10]:
                doc.add_heading(clause.get('title', ''), level=2)
                doc.add_paragraph(clause.get('content', ''))

        doc.save(output_path)
```

**Step 4: 添加 API 端点**

```python
# api/server.py
from core.exporters import PDFExporter, WordExporter

@app.get("/audit/{session_id}/export/pdf")
async def export_pdf(session_id: str):
    """导出 PDF 报告"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 生成 PDF
    exporter = PDFExporter()
    output_path = f"/tmp/report_{session_id}.pdf"
    exporter.export(session.audit_result, output_path)

    return FileResponse(output_path, media_type='application/pdf')
```

**Step 5: 提交**

```bash
git add core/exporters/ api/server.py
git commit -m "feat: add PDF and Word export functionality"
```

---

## 阶段五：增强错误处理和重试

### Task 6: 添加 LLM 调用重试机制

**Files:**
- Modify: `agents/base_agent.py` - 添加重试逻辑
- Modify: `core/llm/factory.py` - 可选

**Step 1: 修改 base_agent.py 添加重试**

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

# 在 _call_llm 方法上应用
@retry_on_failure(max_retries=3, delay=2)
def _call_llm(self, system: str, user: str, response_format=None):
    # 现有逻辑
    pass
```

**Step 2: 测试重试机制**

模拟 LLM 调用失败，验证重试逻辑

**Step 3: 提交**

```bash
git add agents/base_agent.py
git commit -m "feat: add retry mechanism for LLM calls"
```

---

## 阶段六：添加监控和日志

### Task 7: 增强日志和监控

**Files:**
- Modify: `core/logger.py` - 增强日志格式
- Create: `core/metrics.py` - 简单的指标收集

**Step 1: 创建指标收集模块**

```python
# core/metrics.py
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class AuditMetrics:
    timestamp: str
    contract_name: str
    duration_seconds: float
    clause_count: int
    annotation_count: int
    error: str = None

class MetricsCollector:
    def __init__(self):
        self.metrics: List[AuditMetrics] = []

    def record(self, metrics: AuditMetrics):
        self.metrics.append(metrics)

    def get_summary(self) -> Dict:
        total = len(self.metrics)
        if total == 0:
            return {"total_audits": 0}
        return {
            "total_audits": total,
            "avg_duration": sum(m.duration_seconds for m in self.metrics) / total,
        }

metrics_collector = MetricsCollector()
```

**Step 2: 在 pipeline 中集成指标收集**

```python
# core/pipeline/contract_pipeline.py
from core.metrics import metrics_collector, AuditMetrics

# 在 run 方法中
start_time = time.time()
# ... 执行 pipeline ...
duration = time.time() - start_time

metrics_collector.record(AuditMetrics(
    timestamp=datetime.now().isoformat(),
    contract_name=contract_name,
    duration_seconds=duration,
    clause_count=len(clauses),
    annotation_count=len(annotations),
))
```

**Step 3: 添加指标 API 端点**

```python
# api/server.py
from core.metrics import metrics_collector

@app.get("/metrics")
async def get_metrics():
    return metrics_collector.get_summary()
```

**Step 4: 提交**

```bash
git add core/metrics.py api/server.py
git commit -m "feat: add metrics collection for audit pipeline"
```

---

## 验证方案

每个 Task 完成后执行：

```bash
# 1. 启动后端
PYTHONPATH=. uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload

# 2. 启动前端
streamlit run frontend/app.py --server.port 8501

# 3. 测试完整流程
# - 上传合同 → 审核 → 查看结果
# - 检查 clauses 和 corrections 是否显示
# - 测试历史记录功能
# - 测试导出功能

# 4. 验证所有端点
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
```

---

## 任务依赖关系

```
Task 1 (Pipeline输出) ─┬─> Task 2 (前端修复)
                      │
Task 3 (RAG启用) ──────┼─> Task 4 (异步处理)
                      │
Task 5 (导出功能) ────┼─> Task 6 (重试机制)
                      │
Task 7 (监控日志) ─────┘
```

---

## 实施顺序

1. **Task 1-2**: 修复数据流（关键，必须先完成）
2. **Task 3**: 启用 RAG
3. **Task 4**: 异步处理
4. **Task 5**: 导出功能
5. **Task 6-7**: 错误处理和监控
