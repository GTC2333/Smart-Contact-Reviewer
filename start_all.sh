#!/bin/bash
# smart_contact_audit/start_all.sh

set -e

# ===== 注入项目根目录到 PYTHONPATH =====
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# ===== 自动清理占用端口 =====
cleanup_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "清理占用端口 $port 的进程: $pids"
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

echo "检查并清理占用端口..."
cleanup_port 8000  # 后端端口
cleanup_port 8501  # 前端端口
# =======================================

# 读取配置（保持原样）
CONFIG_JSON=$(python3 - <<'PY'
import yaml, json, pathlib, sys
cfg_path = pathlib.Path(__file__).resolve().parent / "config" / "settings.yaml"
if not cfg_path.exists():
    print("Error: config/settings.yaml not found", file=sys.stderr)
    sys.exit(1)
data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
print(json.dumps(data))
PY
)

FRONTEND_PORT=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['frontend']['port'])")
BACKEND_HOST=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['backend_api']['host'])")
BACKEND_PORT=$(echo "$CONFIG_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['backend_api']['port'])")

echo "正在启动 智能合同审核系统..."

uvicorn api.server:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!
sleep 3

streamlit run frontend/app.py --server.port="$FRONTEND_PORT" --server.address=0.0.0.0 &
FRONTEND_PID=$!

echo "系统启动成功！"
echo "后端 API 文档: http://${BACKEND_HOST}:${BACKEND_PORT}/docs"
echo "前端界面地址: http://127.0.0.1:${FRONTEND_PORT}"
echo "停止服务：kill $BACKEND_PID $FRONTEND_PID"

trap "echo '正在关闭服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait