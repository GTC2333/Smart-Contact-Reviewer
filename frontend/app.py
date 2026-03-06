"""
Streamlit frontend for contract audit system - AI Copilot Workspace.
Features session history management and multi-tab interface.
"""
import streamlit as st
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

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


# ==================== API Functions ====================

def get_api_base() -> str:
    """Get API base URL."""
    return f"http://{backend_cfg.get('host', '127.0.0.1')}:{backend_cfg.get('port', 8000)}"


def call_api_audit(file_content: bytes, filename: str) -> Dict:
    """Call audit API with file."""
    url = f"{get_api_base()}{backend_cfg.get('endpoint_audit', '/audit')}"
    files = {"file": (filename, file_content)}
    response = requests.post(url, files=files, timeout=180)
    response.raise_for_status()
    return response.json()


def call_api_sessions() -> List[Dict]:
    """Get all sessions."""
    url = f"{get_api_base()}/sessions"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json().get("sessions", [])


def call_api_session(session_id: str) -> Dict:
    """Get a specific session."""
    url = f"{get_api_base()}/sessions/{session_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def call_api_delete_session(session_id: str) -> bool:
    """Delete a session."""
    url = f"{get_api_base()}/sessions/{session_id}"
    response = requests.delete(url, timeout=30)
    return response.status_code == 200


def call_api_rename_session(session_id: str, new_name: str) -> bool:
    """Rename a session."""
    url = f"{get_api_base()}/sessions/{session_id}/rename?new_name={requests.utils.quote(new_name)}"
    response = requests.put(url, timeout=30)
    return response.status_code == 200


# ==================== Initialize Session State ====================

if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "audit_result" not in st.session_state:
    st.session_state.audit_result = None


def refresh_sessions():
    """Refresh sessions list from API."""
    try:
        st.session_state.sessions = call_api_sessions()
    except Exception:
        st.session_state.sessions = []


def navigate_to_home():
    """Navigate to home page."""
    st.session_state.current_view = "home"
    st.session_state.current_session_id = None
    st.session_state.audit_result = None
    st.rerun()


def navigate_to_session(session_id: str):
    """Navigate to a specific session."""
    st.session_state.current_view = "session"
    st.session_state.current_session_id = session_id
    # Load session data
    try:
        session = call_api_session(session_id)
        st.session_state.audit_result = session.get("audit_result")
    except Exception:
        st.session_state.audit_result = None
    st.rerun()


def delete_session_and_refresh(session_id: str):
    """Delete a session and refresh the list."""
    try:
        call_api_delete_session(session_id)
        if st.session_state.current_session_id == session_id:
            navigate_to_home()
        else:
            refresh_sessions()
            st.rerun()
    except Exception as e:
        st.error(f"删除失败: {str(e)}")


st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ==================== Custom CSS ====================

st.markdown("""
<style>
    /* ==================== CSS Variables ==================== */
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

    /* Main layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 主背景 */
    [data-testid="stAppViewContainer"] > div:first-child {
        background: var(--color-bg-main);
    }

    /* 内容区背景 */
    .main .block-container {
        background: var(--color-bg-main);
    }

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

    /* Cards */
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

    /* Session item */
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
</style>
""", unsafe_allow_html=True)

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }

    /* Stats */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .stat-card.high { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); }
    .stat-card.medium { background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%); }
    .stat-card.low { background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%); }

    /* Clause card */
    .clause-card {
        background: white;
        border-left: 4px solid #FF6B6B;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
    }
    .clause-card:hover {
        background: #fafafa;
    }
    .clause-card.selected {
        border-left-width: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== Sidebar ====================

with st.sidebar:
    st.markdown('<p class="sidebar-title">🧠 智能合同审核系统</p>')
    st.markdown("---")

    # New audit button
    if st.button("➕ 新建审核", use_container_width=True, key="btn_new_audit"):
        navigate_to_home()

    st.markdown("---")

    # Load sessions
    try:
        refresh_sessions()
    except Exception:
        pass

    # Session history
    st.markdown("### 📋 审核历史")

    if not st.session_state.sessions:
        st.caption("暂无审核记录")
    else:
        for session in st.session_state.sessions[:20]:
            session_id = session.get("session_id", "")
            contract_name = session.get("contract_name", "未命名")
            created_at = session.get("created_at", "")[:10]
            risk_count = session.get("risk_count", 0)

            # Create columns for session item
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<span class='risk-badge' style='font-size: 0.75rem;'>{risk_count}风险</span>", unsafe_allow_html=True)
            with col2:
                is_active = st.session_state.current_session_id == session_id
                if st.button(f"📄 {contract_name[:12]}{'...' if len(contract_name) > 12 else ''}", key=f"session_{session_id}"):
                    navigate_to_session(session_id)

            st.caption(f"📅 {created_at}")
            st.markdown("---")


# ==================== Home Page ====================

if st.session_state.current_view == "home":
    st.markdown("## 欢迎使用智能合同审核系统")

    # Sample contracts directory
    SAMPLES_DIR = config.project_root / "data" / "samples"
    SAMPLE_CONTRACTS = {
        "软件开发服务合同": "软件开发服务合同.txt",
        "房屋租赁合同": "房屋租赁合同.txt",
        "采购合同": "采购合同.txt",
    }

    # Create columns for upload and samples
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📤 上传合同")

        uploaded_file = st.file_uploader(
            "支持 .txt / .pdf / .docx",
            type=['txt', 'pdf', 'docx'],
            help="拖拽文件至此处或点击浏览"
        )

        if uploaded_file is not None:
            with st.spinner("正在审核合同..."):
                try:
                    file_bytes = uploaded_file.read()
                    filename = uploaded_file.name
                    result = call_api_audit(file_bytes, filename)
                    st.session_state.audit_result = result
                    st.session_state.current_session_id = result.get("session_id")
                    st.session_state.current_view = "session"
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"API 调用失败：{str(e)}")
                    st.info("请确保后端 API 服务正在运行")
                except Exception as e:
                    st.error(f"处理失败：{str(e)}")

    with col2:
        st.markdown("### 📁 示例合同")
        st.markdown("点击快速审核示例合同：")

        for name, filename in SAMPLE_CONTRACTS.items():
            sample_path = SAMPLES_DIR / filename
            if sample_path.exists():
                if st.button(f"📄 {name}", use_container_width=True, key=f"sample_{filename}"):
                    with st.spinner(f"正在审核{name}..."):
                        try:
                            file_bytes = sample_path.read_bytes()
                            result = call_api_audit(file_bytes, filename)
                            st.session_state.audit_result = result
                            st.session_state.current_session_id = result.get("session_id")
                            st.session_state.current_view = "session"
                            refresh_sessions()
                            st.rerun()
                        except Exception as e:
                            st.error(f"审核失败：{str(e)}")
            else:
                st.caption(f"文件未找到：{filename}")


# ==================== Session Page ====================

elif st.session_state.current_view == "session":
    result = st.session_state.audit_result

    if not result:
        st.error("无法加载审核结果")
        if st.button("返回首页"):
            navigate_to_home()
        st.stop()

    # Get risk statistics
    annotations = result.get("annotations", [])
    parties = result.get("parties", [])
    clauses = result.get("clauses", [])
    corrections = result.get("corrections", [])

    high = len([a for a in annotations if a.get("severity", "").lower() == "high"])
    medium = len([a for a in annotations if a.get("severity", "").lower() == "medium"])
    low = len([a for a in annotations if a.get("severity", "").lower() == "low"])

    # Header with contract name
    contract_name = result.get("contract_name", "未命名合同")
    st.markdown(f"## 📄 {contract_name}")

    # Tab interface
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 合同概览",
        "📋 合同条款浏览",
        "⚠️ 风险分析",
        "💡 修改建议",
        "📥 导出报告"
    ])

    # ==================== Tab 1: Overview ====================

    with tab1:
        # Stats row
        st.markdown("### 风险统计")
        stats_cols = st.columns(4)
        with stats_cols[0]:
            st.markdown(f"""
            <div class="stat-card high animate-fade-in-up animate-delay-1">
                <div class="stat-number">{high}</div>
                <div class="stat-label">高风险</div>
            </div>
            """, unsafe_allow_html=True)
        with stats_cols[1]:
            st.markdown(f"""
            <div class="stat-card medium animate-fade-in-up animate-delay-2">
                <div class="stat-number">{medium}</div>
                <div class="stat-label">中风险</div>
            </div>
            """, unsafe_allow_html=True)
        with stats_cols[2]:
            st.markdown(f"""
            <div class="stat-card low animate-fade-in-up animate-delay-3">
                <div class="stat-number">{low}</div>
                <div class="stat-label">低风险</div>
            </div>
            """, unsafe_allow_html=True)
        with stats_cols[3]:
            st.markdown(f"""
            <div class="stat-card animate-fade-in-up animate-delay-4">
                <div class="stat-number">{len(annotations)}</div>
                <div class="stat-label">总风险</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Parties
        if parties:
            st.markdown("### 👥 合同双方")
            party_cols = st.columns(len(parties))
            for i, party in enumerate(parties):
                with party_cols[i]:
                    party_name = party.get("name", "未识别") if isinstance(party, dict) else str(party)
                    party_role = party.get("role", "未知") if isinstance(party, dict) else "未知"
                    st.markdown(f"""
                    <div class="card">
                        <div style="color: #666; font-size: 0.9rem;">{party_role}</div>
                        <div style="font-size: 1.1rem; font-weight: 600;">{party_name}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Clauses summary
        if clauses:
            st.markdown(f"### 📑 合同条款 ({len(clauses)}条)")
            for clause in clauses[:5]:
                st.markdown(f"- **{clause.get('title', '条款' + clause.get('id', ''))}**")
            if len(clauses) > 5:
                st.caption(f"还有 {len(clauses) - 5} 条条款...")

    # ==================== Tab 2: Clauses ====================

    with tab2:
        if not clauses:
            st.info("未提取到合同条款")
        else:
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### 条款列表")
                selected_clause_id = st.session_state.get("selected_clause_id", clauses[0].get("id"))

                for clause in clauses:
                    clause_id = clause.get("id", "")
                    clause_title = clause.get("title", f"条款 {clause_id}")
                    is_selected = clause_id == selected_clause_id

                    if st.button(
                        f"📝 {clause_title[:20]}{'...' if len(clause_title) > 20 else ''}",
                        key=f"clause_{clause_id}",
                        use_container_width=True
                    ):
                        st.session_state.selected_clause_id = clause_id
                        st.rerun()

            with col2:
                # Find selected clause
                selected_clause = None
                for c in clauses:
                    if c.get("id") == selected_clause_id:
                        selected_clause = c
                        break

                if selected_clause:
                    st.markdown(f"### {selected_clause.get('title', '条款详情')}")
                    st.text_area("条款内容", selected_clause.get("content", ""), height=200, disabled=True)

                    # Find related annotations
                    related_annos = [a for a in annotations if a.get("clause_id") == selected_clause_id]
                    if related_annos:
                        st.markdown("#### 关联风险")
                        for anno in related_annos:
                            severity = anno.get("severity", "low").lower()
                            risk_class = "risk-high" if severity == "high" else ("risk-medium" if severity == "medium" else "risk-low")
                            st.markdown(f"""
                            <div class="{risk_class}" style="border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;">
                                <strong>{anno.get('issue_type', '风险')}</strong><br>
                                {anno.get('description', '')}
                            </div>
                            """, unsafe_allow_html=True)

    # ==================== Tab 3: Risks ====================

    with tab3:
        if not annotations:
            st.success("✅ 未发现风险")
        else:
            # Filter
            filter_severity = st.selectbox("按风险等级筛选", ["全部", "高", "中", "低"])

            filtered_annos = annotations
            if filter_severity != "全部":
                severity_map = {"高": "high", "中": "medium", "低": "low"}
                filtered_annos = [a for a in annotations if a.get("severity", "").lower() == severity_map[filter_severity]]

            st.markdown(f"共 {len(filtered_annos)} 项风险")

            for anno in filtered_annos:
                severity = anno.get("severity", "low").lower()
                risk_class = "risk-high" if severity == "high" else ("risk-medium" if severity == "medium" else "risk-low")

                with st.expander(f"⚠️ {anno.get('issue_type', '风险')} - {anno.get('clause_id', '')}"):
                    st.markdown(f"""
                    <div class="{risk_class}" style="border-radius: 8px; padding: 1rem;">
                        <p><strong>风险等级：</strong>{anno.get('severity', '低')}</p>
                        <p><strong>涉及方：</strong>{anno.get('party', '双方')}</p>
                        <p><strong>问题描述：</strong>{anno.get('description', '无')}</p>
                        {f"<p><strong>法律依据：</strong>{anno.get('law_reference', '')}</p>" if anno.get('law_reference') else ""}
                        {f"<p><strong>修改建议：</strong>{anno.get('recommendation', '')}</p>" if anno.get('recommendation') else ""}
                    </div>
                    """, unsafe_allow_html=True)

                    if anno.get("suggested_revision"):
                        st.code(anno["suggested_revision"], language="text")

    # ==================== Tab 4: Corrections ====================

    with tab4:
        if not corrections:
            st.info("暂无修改建议")
        else:
            st.markdown(f"共 {len(corrections)} 条修改建议")

            for corr in corrections:
                with st.expander(f"💡 条款 {corr.get('clause_id', '')} 修改建议"):
                    if corr.get("original_text"):
                        st.markdown("**原文：**")
                        st.code(corr["original_text"], language="text")

                    if corr.get("suggested_text"):
                        st.markdown("**建议修改为：**")
                        st.code(corr["suggested_text"], language="text")

            # Copy all suggestions
            all_suggestions = ""
            for corr in corrections:
                if corr.get("suggested_text"):
                    all_suggestions += f"条款 {corr.get('clause_id', '')}:\n{corr['suggested_text']}\n\n"

            if all_suggestions:
                st.markdown("---")
                if st.button("📋 一键复制所有建议", use_container_width=True):
                    st.code(all_suggestions, language="text")
                    st.success("建议已复制到下方，请复制使用")

    # ==================== Tab 5: Export ====================

    with tab5:
        st.markdown("### 📥 导出报告")

        # JSON download
        st.download_button(
            label="📄 下载 JSON 报告",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name=f"audit_report_{result.get('session_id', 'unknown')}.json",
            mime="application/json",
            use_container_width=True
        )

        st.markdown("---")

        # Summary
        st.markdown("### 📊 审核摘要")

        summary = f"""# 合同审核报告

## 合同信息
- 合同名称：{contract_name}
- 审核时间：{result.get('created_at', '')[:19] if result.get('created_at') else '未知'}

## 风险统计
- 高风险：{high}
- 中风险：{medium}
- 低风险：{low}
- 总计：{len(annotations)}

## 合同双方
"""
        for party in parties:
            party_name = party.get("name", "未识别") if isinstance(party, dict) else str(party)
            party_role = party.get("role", "未知") if isinstance(party, dict) else "未知"
            summary += f"- {party_role}：{party_name}\n"

        summary += """
## 主要风险
"""
        for anno in annotations[:10]:
            summary += f"- [{anno.get('severity', '低')}] {anno.get('issue_type', '风险')}：{anno.get('description', '')[:50]}...\n"

        st.text_area("审核摘要", summary, height=300, disabled=True)

        if st.button("📋 复制摘要", use_container_width=True):
            st.success("摘要已复制")

# Footer
st.markdown("---")
st.caption("🧠 智能合同审核系统 v2.0 | AI Copilot Workspace")
