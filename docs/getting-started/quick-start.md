# 快速开始

5分钟快速上手智能合同审核系统。

## 前置条件

- 已完成[安装](installation.md)
- 已配置 LLM API Key

## 方式一：使用 Web 前端

### 1. 启动后端 API

```bash
# 方式 1: 使用 uvicorn
uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload

# 方式 2: 使用启动脚本
bash start_all.sh
```

### 2. 启动前端（新终端）

```bash
streamlit run frontend/app.py
```

### 3. 使用界面

1. 打开浏览器访问 `http://localhost:8501`
2. 上传合同文件（支持 .txt, .pdf, .docx）
3. 等待审核完成
4. 查看风险标注和建议
5. 下载 JSON 报告

## 方式二：使用 API

### 1. 启动 API 服务

```bash
uvicorn api.server:app --host 127.0.0.1 --port 8000
```

### 2. 调用 API

```bash
curl -X POST "http://127.0.0.1:8000/audit" \
  -F "file=@your_contract.pdf"
```

### 3. 查看 API 文档

访问 `http://127.0.0.1:8000/docs` 查看交互式 API 文档。

## 方式三：使用 Python 代码

### 基本使用

```python
from main import run_pipeline

# 准备合同文本
contract_text = """
合同编号：C2025-001
甲方：示例公司A
乙方：示例公司B

第一条 合同标的
本合同标的为软件开发服务。

第二条 付款方式
乙方应在合同签订后3个工作日内支付全部款项。
"""

# 运行审核
result = run_pipeline({"contract_text": contract_text})

# 查看结果
print(f"合同ID: {result['contract_id']}")
print(f"发现风险: {len(result['annotations'])} 个")

for annotation in result['annotations']:
    print(f"\n条款 {annotation['clause_id']}:")
    print(f"  风险: {annotation['description']}")
    print(f"  严重程度: {annotation['severity']}")
    print(f"  建议: {annotation['recommendation']}")
```

### 使用服务层

```python
from services.pipeline_service import get_pipeline_service

service = get_pipeline_service()
result = service.audit_contract(contract_text)
```

## 输出格式

审核结果是一个 JSON 对象，包含：

```json
{
  "contract_id": "C20250101-ABCD",
  "metadata": {
    "processed_at": "2025-01-01T12:00:00",
    "clause_count": 5,
    "party_count": 2
  },
  "parties": [
    {"role": "甲方", "name": "示例公司A"},
    {"role": "乙方", "name": "示例公司B"}
  ],
  "annotations": [
    {
      "id": "anno-001",
      "clause_id": "2",
      "party": "乙方",
      "issue_type": "Risk",
      "description": "付款期限过短，履约风险较高",
      "severity": "High",
      "recommendation": "建议延长至10个工作日",
      "law_reference": "民法典 第五百一十条",
      "suggested_revision": "修改后的条款文本..."
    }
  ]
}
```

## 下一步

- 了解[详细配置](configuration.md)
- 查看[功能文档](../features/rag.md)
- 阅读[使用示例](../examples/basic-usage.md)
