"""
FastAPI server for contract audit system.
Decoupled from main.py, uses service layer.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from typing import Optional

from core.config_manager import get_config_manager
from core.logger import get_logger
from core.storage import get_session_store
from api.services.audit_service import AuditService

# Initialize services
config = get_config_manager()
backend_cfg = config.get_backend_config()
logger = get_logger(__name__)

app = FastAPI(title="智能合同审核系统 API", version="1.0.0")

# Initialize audit service
audit_service = AuditService()

# Initialize session store
session_store = get_session_store()


@app.post(backend_cfg.get("endpoint_audit", "/audit"))
async def audit_contract(file: UploadFile = File(...)):
    """
    Audit contract from uploaded file.
    
    Args:
        file: Uploaded contract file
    
    Returns:
        Audit result as JSON
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # Validate file type
    if not audit_service.file_handler.validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持格式: {', '.join(audit_service.file_handler.SUPPORTED_EXTENSIONS)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()

        # Audit contract
        result = audit_service.audit_from_file(file_content, file.filename)

        # Save session
        contract_name = file.filename
        session_id = session_store.save_session(contract_name, result)
        result["session_id"] = session_id

        logger.info(f"Audit completed for file: {file.filename}, session: {session_id}")
        return JSONResponse(content=result)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"审核流程异常: {str(e)}")


# ------------------- Session Management Endpoints -------------------

@app.get("/sessions")
async def list_sessions(limit: int = Query(50, ge=1, le=100)):
    """
    List all audit sessions.

    Args:
        limit: Maximum number of sessions to return

    Returns:
        List of session summaries
    """
    sessions = session_store.list_sessions(limit=limit)
    return {"sessions": [s.__dict__ for s in sessions]}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific session by ID.

    Args:
        session_id: Session identifier

    Returns:
        Full session data including audit result
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session.__dict__


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    success = session_store.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "会话已删除"}


@app.get("/sessions/search")
async def search_sessions(keyword: str = Query(..., min_length=1)):
    """
    Search sessions by keyword.

    Args:
        keyword: Search keyword

    Returns:
        List of matching sessions
    """
    sessions = session_store.search_sessions(keyword)
    return {"sessions": [s.__dict__ for s in sessions]}


@app.put("/sessions/{session_id}/rename")
async def rename_session(session_id: str, new_name: str):
    """
    Rename a session.

    Args:
        session_id: Session identifier
        new_name: New contract name

    Returns:
        Success message
    """
    success = session_store.update_session_name(session_id, new_name)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "会话已重命名"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "contract-audit-api"}


# ------------------- Async Task Endpoints -------------------

from api.tasks import task_manager, TaskStatus
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Background executor for running audits
executor = ThreadPoolExecutor(max_workers=2)


def run_audit_task(task_id: str, file_content: bytes, filename: str):
    """Run audit in background thread."""
    try:
        task_manager.update_task(task_id, TaskStatus.PROCESSING.value, progress=10)

        # Audit contract
        result = audit_service.audit_from_file(file_content, filename)
        task_manager.update_task(task_id, TaskStatus.PROCESSING.value, progress=80)

        # Save session
        session_id = session_store.save_session(filename, result)
        result["session_id"] = session_id

        task_manager.update_task(
            task_id,
            TaskStatus.COMPLETED.value,
            result={"session_id": session_id, "result": result},
            progress=100
        )
        logger.info(f"Async audit completed for {filename}, session: {session_id}")

    except Exception as e:
        logger.error(f"Async audit failed: {e}")
        task_manager.update_task(task_id, TaskStatus.FAILED.value, error=str(e))


@app.post("/audit/async")
async def audit_contract_async(file: UploadFile = File(...)):
    """
    Start async contract audit.

    Args:
        file: Uploaded contract file

    Returns:
        Task ID for polling status
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not audit_service.file_handler.validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持格式: {', '.join(audit_service.file_handler.SUPPORTED_EXTENSIONS)}"
        )

    # Create task
    task_id = task_manager.create_task(file.filename)

    # Read file content
    file_content = await file.read()

    # Submit to background executor
    executor.submit(run_audit_task, task_id, file_content, file.filename)

    return {
        "task_id": task_id,
        "status": "pending",
        "message": "审核任务已启动，请使用 task_id 查询进度"
    }


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get async task status.

    Args:
        task_id: Task identifier

    Returns:
        Task status and result if completed
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task


@app.get("/tasks")
async def list_tasks(limit: int = Query(50, ge=1, le=100)):
    """
    List all tasks.

    Args:
        limit: Maximum number of tasks to return

    Returns:
        List of tasks
    """
    tasks = task_manager.list_tasks(limit=limit)
    return {"tasks": tasks}


# ------------------- Export Endpoints -------------------

from core.exporters import PDFExporter, WordExporter
import tempfile
import os


@app.get("/sessions/{session_id}/export/pdf")
async def export_pdf(session_id: str):
    """
    Export session as PDF report.

    Args:
        session_id: Session identifier

    Returns:
        PDF file
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    try:
        exporter = PDFExporter()
        output_path = exporter.export(session.audit_result)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"合同审核报告_{session.contract_name}.pdf"
        )
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF导出失败: {str(e)}")


@app.get("/sessions/{session_id}/export/word")
async def export_word(session_id: str):
    """
    Export session as Word document.

    Args:
        session_id: Session identifier

    Returns:
        Word file
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    try:
        exporter = WordExporter()
        output_path = exporter.export(session.audit_result)

        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"合同审核报告_{session.contract_name}.docx"
        )
    except Exception as e:
        logger.error(f"Word export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Word导出失败: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host=backend_cfg.get("host", "127.0.0.1"),
        port=backend_cfg.get("port", 8000),
        reload=True
    )
