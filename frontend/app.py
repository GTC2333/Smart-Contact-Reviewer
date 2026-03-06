"""
Streamlit frontend for contract audit system.
Decoupled from main.py, uses API only.
"""
import streamlit as st
import requests
import json
from pathlib import Path
from typing import Dict, Any

from core.config_manager import get_config_manager

# Load configuration
config = get_config_manager()
frontend_cfg = config.get_frontend_config()
backend_cfg = config.get_backend_config()

# Page configuration
st.set_page_config(
    page_title=frontend_cfg.get("title", "智能合同审核系统"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styles
st.markdown(f"""
<style>
    .main {{ background-color: {frontend_cfg.get('theme', {}).get('backgroundColor', '#FFFFFF')}; }}
    .sidebar .sidebar-content {{ background-color: {frontend_cfg.get('theme', {}).get('secondaryBackgroundColor', '#F0F2F6')}; }}
    .css-1d391kg {{ color: {frontend_cfg.get('theme', {}).get('textColor', '#262730')}; }}
    .stButton>button {{
        background-color: {frontend_cfg.get('theme', {}).get('primaryColor', '#FF6B6B')};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
    }}
    .stButton>button:hover {{ opacity: 0.8; }}
    .risk-high {{ background-color: #ffebee; border-left: 5px solid #f44336; padding: 10px; margin: 5px 0; }}
    .risk-medium {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 10px; margin: 5px 0; }}
    .risk-low {{ background-color: #e8f5e9; border-left: 5px solid #4caf50; padding: 10px; margin: 5px 0; }}
</style>
""", unsafe_allow_html=True)


def call_api_audit(file_content: bytes, filename: str) -> Dict:
    """
    Call audit API with file.
    
    Args:
        file_content: File content as bytes
        filename: File name
    
    Returns:
        Audit result dictionary
    """
    endpoint = backend_cfg.get("endpoint_audit", "/audit")
    url = f"http://{backend_cfg.get('host', '127.0.0.1')}:{backend_cfg.get('port', 8000)}{endpoint}"
    files = {"file": (filename, file_content)}
    response = requests.post(url, files=files, timeout=180)
    response.raise_for_status()
    return response.json()


def display_audit_result(result: Dict[str, Any]):
    """Display audit result in the UI."""
    # Update statistics
    annotations = result.get("annotations", [])
    high = len([a for a in annotations if a.get("severity", "").lower() == "high"])
    medium = len([a for a in annotations if a.get("severity", "").lower() == "medium"])
    low = len([a for a in annotations if a.get("severity", "").lower() == "low"])
    
    # Display statistics in sidebar
    with st.sidebar:
        st.metric("高风险", high)
        st.metric("中风险", medium)
        st.metric("低风险", low)
        st.metric("总风险", len(annotations))
    
    # Display parties
    parties = result.get("parties", [])
    if parties:
        st.subheader("👥 合同双方")
        party_cols = st.columns(len(parties))
        for i, party in enumerate(parties):
            with party_cols[i]:
                party_name = party.get("name", "未识别") if isinstance(party, dict) else str(party)
                party_role = party.get("role", "未知") if isinstance(party, dict) else "未知"
                st.markdown(f"**{party_role}**  \n{party_name}")
    
    # Display risk annotations
    if annotations:
        st.subheader("⚠️ 风险明细")
        for anno in annotations:
            severity = anno.get("severity", "low").lower()
            risk_class = {
                "high": "risk-high",
                "medium": "risk-medium",
                "low": "risk-low"
            }.get(severity, "risk-low")
            
            with st.expander(
                f"条款 {anno.get('clause_id', '未知')} | "
                f"{anno.get('party', '双方')} | "
                f"{anno.get('issue_type', '风险')}"
            ):
                st.markdown(f"<div class='{risk_class}'>", unsafe_allow_html=True)
                st.write(f"**问题描述**：{anno.get('description', '无')}")
                if anno.get("law_reference"):
                    st.write(f"**法律依据**：{anno['law_reference']}")
                if anno.get("recommendation"):
                    st.write(f"**修改建议**：{anno['recommendation']}")
                if anno.get("suggested_revision"):
                    st.code(anno["suggested_revision"], language="text")
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 下载完整报告 (JSON)",
        data=json.dumps(result, ensure_ascii=False, indent=2),
        file_name=f"audit_report_{result.get('contract_id', 'unknown')}.json",
        mime="application/json"
    )


# Main interface
st.title("🧠 智能合同审核系统")

# Sidebar: Statistics placeholder
with st.sidebar:
    st.header("📊 统计信息")
    stats_placeholder = st.empty()

# Main area: File upload
st.subheader("📄 上传合同文件")
uploaded_file = st.file_uploader(
    "支持 .txt / .pdf / .docx",
    type=['txt', 'pdf', 'docx'],
    help="拖拽文件至此处或点击浏览"
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    
    with st.spinner("正在处理文件..."):
        try:
            result = call_api_audit(file_bytes, filename)
            st.success("✅ 审核完成！")
            display_audit_result(result)
        
        except requests.exceptions.RequestException as e:
            st.error(f"API 调用失败：{str(e)}")
            st.info("请确保后端 API 服务正在运行")
        except Exception as e:
            st.error(f"处理失败：{str(e)}")
            st.exception(e)

else:
    st.info("👈 请上传合同文件开始审核")
    st.markdown("---")
    st.markdown("### 示例审核报告（默认展示）")
    
    # Load example JSON file
    example_path = config.project_root / "outputs" / "example_annotations.json"
    if example_path.exists():
        with open(example_path, encoding="utf-8") as f:
            example_result = json.load(f)
        
        display_audit_result(example_result)
    else:
        st.warning("示例文件未找到：`outputs/example_annotations.json`")
        st.json({
            "contract_id": "C20250101-DEMO",
            "parties": [{"role": "甲方", "name": "示例公司A"}, {"role": "乙方", "name": "示例公司B"}],
            "annotations": [
                {
                    "clause_id": "3.1",
                    "party": "乙方",
                    "issue_type": "Risk",
                    "description": "付款期限过短，可能导致履约困难。",
                    "severity": "high",
                    "recommendation": "建议延长至10个工作日。",
                    "law_reference": "《民法典》第五百一十条"
                }
            ]
        }, expanded=False)
