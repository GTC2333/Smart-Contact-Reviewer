"""
Streamlit frontend for contract audit system - AI Copilot Workspace.
Features session history management and multi-tab interface.
"""
import streamlit as st
import requests
import json
import time
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


def check_api_available() -> bool:
    """Check if API is available."""
    try:
        url = f"{get_api_base()}/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def call_api_audit(file_content: bytes, filename: str) -> Dict:
    """Call audit API with file."""
    url = f"{get_api_base()}{backend_cfg.get('endpoint_audit', '/audit')}"
    files = {"file": (filename, file_content)}
    response = requests.post(url, files=files, timeout=300)
    response.raise_for_status()
    return response.json()


def call_api_audit_async(file_content: bytes, filename: str) -> Dict:
    """Call async audit API."""
    url = f"{get_api_base()}/audit/async"
    files = {"file": (filename, file_content)}
    response = requests.post(url, files=files, timeout=30)
    response.raise_for_status()
    return response.json()


def call_api_audit_stream(file_content: bytes, filename: str):
    """Call streaming audit API."""
    url = f"{get_api_base()}/audit/stream"
    files = {"file": (filename, file_content)}
    response = requests.post(url, files=files, stream=True, timeout=300)
    return response


def call_api_task_status(task_id: str) -> Dict:
    """Get task status."""
    url = f"{get_api_base()}/tasks/{task_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def call_api_sessions() -> List[Dict]:
    """Get all sessions."""
    url = f"{get_api_base()}/sessions"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json().get("sessions", [])


def call_api_session(session_id: str) -> Dict:
    """Get a specific session."""
    url = f"{get_api_base()}/sessions/{session_id}"
    response = requests.get(url, timeout=10)
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

if "sessions_loaded" not in st.session_state:
    st.session_state.sessions_loaded = False

if "task_id" not in st.session_state:
    st.session_state.task_id = None

if "pending_rename_session_id" not in st.session_state:
    st.session_state.pending_rename_session_id = None

if "pending_rename_contract_name" not in st.session_state:
    st.session_state.pending_rename_contract_name = None


def refresh_sessions():
    """Refresh sessions list from API."""
    try:
        st.session_state.sessions = call_api_sessions()
        st.session_state.sessions_loaded = True
    except Exception:
        st.session_state.sessions = []
        st.session_state.sessions_loaded = False


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

        /* 字体大小系统 */
        --font-size-xs: 0.7rem;
        --font-size-sm: 0.8rem;
        --font-size-base: 0.9rem;
        --font-size-md: 1rem;
        --font-size-lg: 1.1rem;
        --font-size-xl: 1.25rem;
        --font-size-2xl: 1.5rem;
        --font-size-3xl: 2rem;

        /* 过渡 */
        --transition-fast: 0.2s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.4s ease;
    }

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

    /* ==================== 组件字体样式 ==================== */
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
        font-size: 1.4rem;
        font-weight: 700;
        color: #3D405B;
        padding: 1rem 0;
        text-align: center;
        letter-spacing: 2px;
    }

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

    /* Streamlit 按钮美化为侧边栏按钮样式 */
    .sidebar-btn-container .stButton > button {
        width: 100%;
        padding: 0.75rem 1rem;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all var(--transition-normal) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        margin-bottom: 1rem !important;
        background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .sidebar-btn-container .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
        background: linear-gradient(135deg, var(--color-accent-hover) 0%, #B8956A 100%) !important;
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

    /* 侧边栏项目滑入动画 */
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

    /* 卡片悬停效果增强 */
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

    /* 按钮波纹效果 */
    .stButton > button {
        position: relative;
        overflow: hidden;
    }

    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s;
    }

    .stButton > button:active::after {
        width: 200px;
        height: 200px;
    }

    /* 上传区域动画 */
    .upload-area {
        position: relative;
    }

    .upload-area::after {
        content: '';
        position: absolute;
        inset: 0;
        border: 2px dashed var(--color-accent);
        border-radius: var(--radius-lg);
        opacity: 0;
        transition: opacity var(--transition-normal);
    }

    .upload-area:hover::after {
        opacity: 1;
    }

    /* 成功/错误提示增强 */
    .stSuccess, .stError {
        animation: slideIn 0.3s ease;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Tab 选中动画 */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        transition: all 0.2s ease;
    }

    /* 会话项动画类 */
    .session-item-animated {
        animation: slideInLeft 0.3s ease forwards;
    }

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

    /* 会话项内的按钮容器 */
    .session-actions {
        display: flex;
        gap: 0.25rem;
    }

    .session-actions button {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
    }

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

            /* Accent colors - lighter for dark mode */
            --color-accent: #E0B88A;
            --color-accent-hover: #D4A574;

            /* Risk colors - adjusted for dark mode */
            --color-risk-high: #E89080;
            --color-risk-medium: #F0C060;
            --color-risk-low: #90C0A8;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #242438 0%, #1A1A2E 100%);
        }

        .sidebar-header {
            background: linear-gradient(135deg, #242438 0%, #1A1A2E 100%);
        }
    }

    /* 合同原文显示区域 */
    .contract-text-viewer label {
        font-family: var(--font-serif);
        font-weight: 600;
        color: var(--color-text-primary);
    }

    .contract-text-viewer textarea {
        font-family: var(--font-mono);
        font-size: var(--font-size-sm);
        line-height: 1.8;
        background: var(--color-bg-card) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-sm);
    }

    /* 审核过程中显示的合同原文区域 */
    .contract-text-during-audit {
        background: var(--color-bg-card);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid var(--color-border-light);
    }

    .contract-text-during-audit .stMarkdown {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================== Sidebar ====================

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <span class="sidebar-logo">⚖️</span>
        <div class="sidebar-brand">智能合同审核</div>
        <div class="sidebar-subtitle">Smart Contract Review</div>
    </div>
    """, unsafe_allow_html=True)

    # New audit button
    st.markdown('<div class="sidebar-btn-container">', unsafe_allow_html=True)
    if st.button("➕ 新建审核", use_container_width=True, key="btn_new_audit_sidebar"):
        navigate_to_home()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Session history - 只在需要时加载
    # Session history header
    session_count = len(st.session_state.sessions) if st.session_state.sessions else 0
    st.markdown(f"""
    <div class="session-list-header">
        <span class="session-list-title">📁 审核历史</span>
        <span class="session-count">{session_count}</span>
    </div>
    """, unsafe_allow_html=True)

    # Refresh button (styled smaller)
    if st.button("🔄 刷新", key="btn_refresh_sessions", help="刷新会话列表"):
        refresh_sessions()
        st.session_state.sessions_loaded = True

    if not st.session_state.sessions_loaded:
        st.markdown('<div class="session-empty">点击刷新按钮加载历史记录</div>', unsafe_allow_html=True)
    elif not st.session_state.sessions:
        st.markdown('<div class="session-empty">暂无审核记录</div>', unsafe_allow_html=True)
    else:
        for idx, session in enumerate(st.session_state.sessions[:20]):
            session_id = session.get("session_id", "")
            contract_name = session.get("contract_name", "未命名")
            created_at = session.get("created_at", "")[:10]
            risk_count = session.get("risk_count", 0)

            # Determine risk level class
            if risk_count >= 5:
                risk_class = "risk-high"
            elif risk_count >= 2:
                risk_class = "risk-medium"
            else:
                risk_class = "risk-low"

            # Session item with inline actions
            st.markdown(f"""
            <div class="session-item">
                <div class="session-title">{contract_name}</div>
                <div class="session-meta">
                    <span class="session-date">📅 {created_at}</span>
                    <span class="risk-badge {risk_class}">{risk_count}风险</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons in columns
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("打开", key=f"open_{session_id}", help="打开此会话"):
                    navigate_to_session(session_id)
            with col2:
                if st.button("🗑️", key=f"delete_{session_id}", help="删除"):
                    st.session_state.pending_delete_session_id = session_id
                    st.session_state.pending_delete_contract_name = contract_name
                    st.rerun()

            # Add rename button
            if st.button("✏️ 重命名", key=f"rename_{session_id}", help="重命名此会话"):
                st.session_state.pending_rename_session_id = session_id
                st.session_state.pending_rename_contract_name = contract_name
                st.rerun()

        # Confirmation dialog for delete
        if "pending_delete_session_id" in st.session_state and st.session_state.pending_delete_session_id:
            st.markdown("### 确认删除")
            st.warning(f"确定要删除会话 \"{st.session_state.pending_delete_contract_name}\" 吗？此操作无法撤销。")

            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("确认删除", key="confirm_delete_btn", type="primary"):
                    delete_session_and_refresh(st.session_state.pending_delete_session_id)
                    st.session_state.pending_delete_session_id = None
                    st.session_state.pending_delete_contract_name = None
            with col_cancel:
                if st.button("取消", key="cancel_delete_btn"):
                    st.session_state.pending_delete_session_id = None
                    st.session_state.pending_delete_contract_name = None
                    st.rerun()

        # Rename dialog
        if "pending_rename_session_id" in st.session_state and st.session_state.pending_rename_session_id:
            st.markdown("### 重命名会话")
            new_name = st.text_input("输入新名称", value=st.session_state.pending_rename_contract_name, key="rename_input")

            col_confirm_rename, col_cancel_rename = st.columns(2)
            with col_confirm_rename:
                if st.button("确认", key="confirm_rename_btn", type="primary"):
                    if not new_name or not new_name.strip():
                        st.error("名称不能为空")
                    elif new_name.strip() == st.session_state.pending_rename_contract_name:
                        st.warning("名称未更改")
                        # Clear state and rerun
                        del st.session_state.pending_rename_session_id
                        del st.session_state.pending_rename_contract_name
                        st.rerun()
                    else:
                        try:
                            success = call_api_rename_session(
                                st.session_state.pending_rename_session_id,
                                new_name.strip()
                            )
                            if success:
                                st.success(f"已重命名为: {new_name.strip()}")
                                refresh_sessions()
                                del st.session_state.pending_rename_session_id
                                del st.session_state.pending_rename_contract_name
                                st.rerun()
                            else:
                                st.error("重命名失败")
                        except Exception as e:
                            st.error(f"重命名失败: {str(e)}")
            with col_cancel_rename:
                if st.button("取消", key="cancel_rename_btn"):
                    st.session_state.pending_rename_session_id = None
                    st.session_state.pending_rename_contract_name = None
                    st.rerun()


# ==================== Home Page ====================

if st.session_state.current_view == "home":
    # 检查 API 可用性
    api_available = check_api_available()

    st.markdown("## 欢迎使用智能合同审核系统")

    if not api_available:
        st.error("⚠️ 后端服务未启动或无法连接")
        st.info("请确保后端 API 服务正在运行，然后刷新页面")
        st.code("启动后端: uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload", language="bash")
        st.stop()

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
            # Use streaming API
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name
            try:
                response = call_api_audit_stream(file_bytes, filename)

                if response.status_code != 200:
                    st.error(f"审核启动失败: {response.text}")
                else:
                    # Enter session view with streaming mode
                    st.session_state.current_view = "session"
                    st.session_state.stream_response = response
                    st.session_state.audit_result = None
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
                    try:
                        file_bytes = sample_path.read_bytes()
                        # Use streaming API
                        response = call_api_audit_stream(file_bytes, filename)

                        if response.status_code != 200:
                            st.error(f"审核启动失败: {response.text}")
                        else:
                            st.session_state.current_view = "session"
                            st.session_state.stream_response = response
                            st.session_state.audit_result = None
                            refresh_sessions()
                            st.rerun()
                    except Exception as e:
                        st.error(f"审核失败：{str(e)}")
            else:
                st.caption(f"文件未找到：{filename}")


# ==================== Session Page ====================

elif st.session_state.current_view == "session":
    result = st.session_state.audit_result

    # Check if we have a streaming response
    if st.session_state.get("stream_response"):
        response = st.session_state.stream_response

        try:
            # Process streaming response
            buffer = ""

            # Create placeholders for real-time updates
            progress_bar = st.progress(0)
            status_text = st.empty()
            contract_text_placeholder = st.empty()

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    buffer += chunk.decode("utf-8")

                    # Process SSE events
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
                            event_type = data.get("type")

                            if event_type == "progress":
                                progress = data.get("progress", 0)
                                message = data.get("message", "")
                                progress_bar.progress(progress / 100)
                                status_text.info(f"**{message}**")

                            elif event_type == "contract_text":
                                # Display contract text using placeholder
                                contract_text = data.get("text", "")
                                st.session_state.pending_contract_text = contract_text
                                with contract_text_placeholder.container():
                                    st.markdown('<div class="contract-text-during-audit">', unsafe_allow_html=True)
                                    st.markdown("### 📄 合同原文")
                                    st.text_area(
                                        "原始合同文本",
                                        value=contract_text,
                                        height=250,
                                        disabled=True,
                                        key="contract_text_during_audit",
                                        label_visibility="collapsed"
                                    )
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    st.markdown("---")

                            elif event_type == "complete":
                                result = data.get("result", {})
                                session_id = data.get("session_id")
                                st.session_state.audit_result = result
                                st.session_state.current_session_id = session_id
                                del st.session_state["stream_response"]
                                refresh_sessions()
                                st.rerun()

                            elif event_type == "error":
                                error = data.get("error", "Unknown error")
                                st.error(f"审核失败: {error}")
                                del st.session_state["stream_response"]
                                st.rerun()

                        except json.JSONDecodeError:
                            pass

        except Exception as e:
            st.error(f"流式读取失败: {str(e)}")
            del st.session_state["stream_response"]
            st.rerun()

    # 检测是否有进行中的任务 (polling mode - for backwards compatibility)
    elif st.session_state.get("task_id") and not st.session_state.get("audit_result"):
        task_id = st.session_state.task_id

        with st.spinner("正在获取任务状态..."):
            task_status = call_api_task_status(task_id)

        status = task_status.get("status")
        progress = task_status.get("progress", 0)

        if status == "completed":
            # 任务完成，获取结果
            result_data = task_status.get("result", {})
            st.session_state.audit_result = result_data.get("result")
            st.session_state.current_session_id = result_data.get("session_id")
            del st.session_state["task_id"]
            st.rerun()
        elif status == "failed":
            st.error(f"审核失败: {task_status.get('error', '未知错误')}")
            if st.button("返回首页"):
                navigate_to_home()
            st.stop()
        else:
            # Show progress container
            st.markdown("""
            <div class="progress-container">
                <div class="progress-header">🔄 正在审核合同</div>
            </div>
            """, unsafe_allow_html=True)

            # Determine current step based on progress
            if progress < 20:
                current_step = 0  # Parsing
            elif progress < 50:
                current_step = 1  # Law search
            elif progress < 75:
                current_step = 2  # Risk analysis
            else:
                current_step = 3  # Corrections

            steps = [
                ("📝", "解析合同", current_step == 0),
                ("🔍", "检索依据", current_step == 1),
                ("⚠️", "分析风险", current_step == 2),
                ("💡", "生成建议", current_step == 3),
            ]

            # Build step HTML
            step_html = '<div class="progress-steps">'
            for i, (icon, label, is_active) in enumerate(steps):
                if i < current_step:
                    step_class = "completed"
                elif i == current_step:
                    step_class = "active"
                else:
                    step_class = ""
                step_html += f'''
                <div class="progress-step {step_class}">
                    <div class="progress-step-icon">{icon}</div>
                    <div>{label}</div>
                </div>
                '''
            step_html += '</div>'
            st.markdown(step_html, unsafe_allow_html=True)

            st.progress(progress / 100)

            # Progress message
            message = task_status.get("message", "")
            if message:
                st.info(f"**{message}**")

            # Show percentage
            st.markdown(f"<div style='text-align: center; font-size: 20px; color: #666;'>{progress}%</div>", unsafe_allow_html=True)

            # 自动刷新
            time.sleep(2)
            st.rerun()

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

    # Risk severity is in Chinese: 高/中/低
    high = len([a for a in annotations if a.get("severity", "").strip() == "高"])
    medium = len([a for a in annotations if a.get("severity", "").strip() == "中"])
    low = len([a for a in annotations if a.get("severity", "").strip() == "低"])

    # Header with contract name
    contract_name = result.get("contract_name", "未命名合同")
    st.markdown(f"## 📄 {contract_name}")

    # Tab interface
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 合同概览",
        "📋 合同条款浏览",
        "⚠️ 风险分析",
        "💡 修改建议",
        "📥 导出报告",
        "📄 合同原文"
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

    # ==================== Tab 6: Contract Text ====================

    with tab6:
        st.markdown("### 📄 原始合同文本")

        # Get contract text from session state (during audit) or result (from session)
        contract_text = (
            st.session_state.get("pending_contract_text") or
            result.get("contract_text", "")
        )

        if contract_text:
            st.text_area(
                "合同原文",
                value=contract_text,
                height=500,
                disabled=True,
                key="contract_text_viewer",
                label_visibility="collapsed"
            )
        else:
            st.warning("无法加载合同原文")

# Footer
st.markdown("---")
st.caption("🧠 智能合同审核系统 v2.0 | AI Copilot Workspace")
