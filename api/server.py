"""
FastAPI server for contract audit system.
Decoupled from main.py, uses service layer.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from core.config_manager import get_config_manager
from core.logger import get_logger
from api.services.audit_service import AuditService

# Initialize services
config = get_config_manager()
backend_cfg = config.get_backend_config()
logger = get_logger(__name__)

app = FastAPI(title="智能合同审核系统 API", version="1.0.0")

# Initialize audit service
audit_service = AuditService()


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
        
        logger.info(f"Audit completed for file: {file.filename}")
        return JSONResponse(content=result)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"审核流程异常: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "contract-audit-api"}


if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host=backend_cfg.get("host", "127.0.0.1"),
        port=backend_cfg.get("port", 8000),
        reload=True
    )
