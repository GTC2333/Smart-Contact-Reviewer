# API 概览

智能合同审核系统提供 RESTful API 接口，支持通过 HTTP 请求进行合同审核。

## 基础信息

- **Base URL**: `http://127.0.0.1:8000`
- **API 版本**: v1.0.0
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

## 快速开始

### 1. 启动 API 服务

```bash
uvicorn api.server:app --host 127.0.0.1 --port 8000
```

### 2. 访问 API 文档

启动后访问：
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 3. 测试 API

```bash
curl -X POST "http://127.0.0.1:8000/audit" \
  -F "file=@contract.pdf"
```

## API 端点

### 审核合同

**POST** `/audit`

上传合同文件进行审核。

**请求**:
- Content-Type: `multipart/form-data`
- 参数: `file` (文件)

**响应**:
```json
{
  "contract_id": "C20250101-ABCD",
  "metadata": {...},
  "parties": [...],
  "annotations": [...]
}
```

### 健康检查

**GET** `/health`

检查 API 服务状态。

**响应**:
```json
{
  "status": "ok",
  "service": "contract-audit-api"
}
```

## 认证（未来）

未来版本将支持：
- API Key 认证
- OAuth 2.0
- JWT Token

## 错误处理

API 使用标准 HTTP 状态码：

- `200 OK` - 请求成功
- `400 Bad Request` - 请求参数错误
- `500 Internal Server Error` - 服务器错误

错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

## 速率限制（未来）

未来版本将实现：
- 每分钟请求数限制
- 每小时请求数限制
- 基于用户的配额

## 详细文档

查看 [API 端点文档](endpoints.md) 了解详细信息。
