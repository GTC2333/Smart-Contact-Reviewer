# API 端点详细文档

## POST /audit

上传合同文件进行审核。

### 请求

**URL**: `/audit`

**方法**: `POST`

**Content-Type**: `multipart/form-data`

**参数**:

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| file | File | 是 | 合同文件（.txt, .pdf, .docx） |

**示例**:

```bash
curl -X POST "http://127.0.0.1:8000/audit" \
  -F "file=@contract.pdf"
```

```python
import requests

url = "http://127.0.0.1:8000/audit"
files = {"file": open("contract.pdf", "rb")}
response = requests.post(url, files=files)
result = response.json()
```

### 响应

**成功响应** (200 OK):

```json
{
  "contract_id": "C20250101-ABCD",
  "metadata": {
    "processed_at": "2025-01-01T12:00:00",
    "clause_count": 5,
    "party_count": 2
  },
  "parties": [
    {
      "role": "甲方",
      "name": "示例公司A"
    },
    {
      "role": "乙方",
      "name": "示例公司B"
    }
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
      "suggested_revision": "修改后的条款文本...",
      "note": "修改说明"
    }
  ]
}
```

**错误响应** (400 Bad Request):

```json
{
  "detail": "不支持的文件格式。支持格式: .txt, .pdf, .docx"
}
```

**错误响应** (500 Internal Server Error):

```json
{
  "detail": "审核流程异常: 错误信息"
}
```

### 状态码

- `200 OK` - 审核成功
- `400 Bad Request` - 文件格式不支持或文件名为空
- `500 Internal Server Error` - 服务器内部错误

## GET /health

检查 API 服务健康状态。

### 请求

**URL**: `/health`

**方法**: `GET`

**示例**:

```bash
curl http://127.0.0.1:8000/health
```

```python
import requests

response = requests.get("http://127.0.0.1:8000/health")
print(response.json())
```

### 响应

**成功响应** (200 OK):

```json
{
  "status": "ok",
  "service": "contract-audit-api"
}
```

### 状态码

- `200 OK` - 服务正常

## 使用示例

### Python 示例

```python
import requests

# 审核合同
def audit_contract(file_path):
    url = "http://127.0.0.1:8000/audit"
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

# 使用
result = audit_contract("contract.pdf")
print(f"合同ID: {result['contract_id']}")
print(f"发现风险: {len(result['annotations'])} 个")
```

### JavaScript 示例

```javascript
// 使用 Fetch API
async function auditContract(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://127.0.0.1:8000/audit', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 使用
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const result = await auditContract(file);
  console.log(result);
});
```

### cURL 示例

```bash
# 审核合同
curl -X POST "http://127.0.0.1:8000/audit" \
  -F "file=@contract.pdf" \
  -o result.json

# 查看结果
cat result.json | jq '.contract_id'
```

## 注意事项

1. **文件大小限制**: 建议文件大小不超过 10MB
2. **处理时间**: 审核可能需要几秒到几分钟，取决于合同长度
3. **超时设置**: 建议设置较长的超时时间（如 180 秒）
4. **文件格式**: 仅支持 .txt, .pdf, .docx 格式

## 错误处理

### 常见错误

1. **文件格式错误**
   - 错误码: 400
   - 解决: 确保文件格式为 .txt, .pdf 或 .docx

2. **文件读取失败**
   - 错误码: 500
   - 解决: 检查文件是否损坏

3. **审核流程异常**
   - 错误码: 500
   - 解决: 查看服务器日志，检查配置

## 未来扩展

计划添加的端点：

- `GET /audit/{contract_id}` - 获取审核历史
- `POST /audit/batch` - 批量审核
- `GET /statistics` - 获取统计信息
