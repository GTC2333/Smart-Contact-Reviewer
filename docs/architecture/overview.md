# 架构概览

本文档介绍智能合同审核系统的整体架构设计。

## 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                     前端层 (Frontend)                     │
│                   Streamlit Web UI                        │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────┐
│                    API 层 (API Layer)                    │
│              FastAPI RESTful Service                     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  服务层 (Service Layer)                  │
│            PipelineService, AuditService                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Pipeline 层 (Pipeline)                  │
│         ContractAuditPipeline (步骤编排)                  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  Agent 层    │ │  RAG 层     │ │  核心层    │
│              │ │             │ │           │
│ Formatter    │ │ Embedding   │ │ Config    │
│ LawSearch    │ │ VectorStore │ │ Logger    │
│ RiskAnnotator│ │ Retriever   │ │ LLM       │
│ Correction   │ │             │ │           │
└──────────────┘ └─────────────┘ └───────────┘
```

## 层次结构

### 1. 前端层 (Frontend Layer)

**职责**: 用户界面和交互

- Streamlit Web 应用
- 文件上传和结果展示
- 通过 HTTP 调用后端 API

**技术栈**: Streamlit, Python

### 2. API 层 (API Layer)

**职责**: HTTP 接口和请求处理

- FastAPI 服务
- 文件上传处理
- 请求验证和错误处理
- 调用服务层

**技术栈**: FastAPI, Uvicorn

### 3. 服务层 (Service Layer)

**职责**: 业务逻辑封装

- `PipelineService`: 审核流程服务
- `AuditService`: 审核业务服务
- `KnowledgeBaseService`: 知识库管理

**特点**: 
- 依赖注入
- 易于测试
- 业务逻辑集中

### 4. Pipeline 层 (Pipeline Layer)

**职责**: 流程编排

- `ContractAuditPipeline`: 主审核流程
- 步骤链式执行
- 上下文传递

**步骤**:
1. ContractFormatterStep
2. LawSearchStep
3. RiskAnnotationStep
4. CorrectionStep

### 5. Agent 层 (Agent Layer)

**职责**: 具体任务执行

- `BaseAgent`: 基类，提供通用功能
- `ContractFormatterAgent`: 合同格式化
- `LawSearchAgent`: 法律检索（集成 RAG）
- `RiskAnnotatorAgent`: 风险标注
- `CorrectionAgent`: 修改建议

**特点**:
- 单一职责
- 可扩展
- 依赖注入

### 6. RAG 层 (RAG Layer)

**职责**: 检索增强生成

- `EmbeddingModel`: 嵌入模型接口
- `VectorStore`: 向量存储
- `RAGRetriever`: 检索器

**功能**:
- 文档向量化
- 相似度检索
- 上下文注入

### 7. 核心层 (Core Layer)

**职责**: 基础设施

- `ConfigManager`: 配置管理
- `Logger`: 日志服务
- `LLM Factory`: LLM 客户端工厂

## 数据流

```
用户上传文件
    ↓
API 接收并保存文件
    ↓
提取文本内容
    ↓
PipelineService.audit_contract()
    ↓
ContractAuditPipeline.run()
    ↓
[步骤1] ContractFormatterStep
    ↓ 格式化合同
[步骤2] LawSearchStep
    ↓ 检索法条 (使用 RAG)
[步骤3] RiskAnnotationStep
    ↓ 识别风险
[步骤4] CorrectionStep
    ↓ 生成建议
返回审核结果
    ↓
API 返回 JSON 响应
    ↓
前端展示结果
```

## 设计原则

### 1. 分层架构

- 清晰的层次划分
- 每层只依赖下层
- 便于维护和测试

### 2. 依赖注入

- 减少耦合
- 提高可测试性
- 支持配置化

### 3. 接口抽象

- 定义清晰的接口
- 支持多种实现
- 易于扩展

### 4. 单一职责

- 每个组件职责单一
- 便于理解和维护
- 降低复杂度

## 技术选型

### 后端框架

- **FastAPI**: 现代、快速的 Web 框架
- **Uvicorn**: ASGI 服务器

### AI/ML

- **OpenAI API**: LLM 服务
- **自定义 RAG**: 向量检索

### 数据处理

- **PyMuPDF**: PDF 处理
- **python-docx**: Word 处理
- **Pydantic**: 数据验证

### 前端

- **Streamlit**: 快速构建 Web UI

## 扩展性

### 水平扩展

- API 层可部署多个实例
- 使用负载均衡

### 垂直扩展

- 替换更强的 LLM 模型
- 优化向量存储
- 增加缓存层

### 功能扩展

- 添加新的 Agent
- 扩展 Pipeline 步骤
- 集成新的数据源

## 安全性

### 当前实现

- 文件类型验证
- 错误处理
- 日志记录

### 未来增强

- API 认证
- 速率限制
- 数据加密
- 审计日志

## 性能优化

### 已实现

- 向量存储持久化
- 批处理支持
- 异步处理（部分）

### 计划中

- 结果缓存
- 并行处理
- 数据库优化

## 相关文档

- [设计模式](design-patterns.md)
- [数据流](data-flow.md)
