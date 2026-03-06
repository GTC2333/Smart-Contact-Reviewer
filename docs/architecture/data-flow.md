# 数据流

本文档描述系统中数据的流转过程。

## 整体数据流

```
用户输入
  ↓
文件上传 (PDF/Word/TXT)
  ↓
文本提取
  ↓
合同文本 (字符串)
  ↓
Pipeline 处理
  ↓
结构化数据 (JSON)
  ↓
审核结果 (JSON)
  ↓
用户输出
```

## 详细数据流

### 阶段 1: 文件上传和提取

```
[用户] 上传文件
  ↓
[API] 接收文件 (multipart/form-data)
  ↓
[FileHandler] 保存文件
  ↓
[TextPreprocess] 提取文本
  ↓
合同文本 (str)
```

**数据格式**:
- 输入: `bytes` (文件内容)
- 输出: `str` (合同文本)

### 阶段 2: 合同格式化

```
合同文本 (str)
  ↓
[ContractFormatterAgent]
  ↓
FormattedContract {
  clauses: [
    {id, title, content}
  ],
  parties: [
    {role, name}
  ]
}
```

**数据转换**:
- 输入: 原始文本字符串
- 输出: 结构化 JSON 对象

### 阶段 3: 法律检索

```
条款内容 (str)
  ↓
[RAG Retriever] 向量检索
  ↓
相关法条 (List[Document])
  ↓
[LawSearchAgent] LLM 分析
  ↓
LawInfo {
  matched: bool,
  law_name: str,
  article: str,
  issue: str
}
```

**数据增强**:
- RAG 检索提供上下文
- LLM 分析生成结果

### 阶段 4: 风险标注

```
条款 + 法律信息
  ↓
[RiskAnnotatorAgent]
  ↓
RiskAnnotation {
  id: str,
  clause_id: str,
  party: str,
  issue_type: str,
  description: str,
  severity: str,
  recommendation: str,
  law_reference: str
} | None
```

**条件处理**:
- 如果发现风险，返回标注对象
- 如果无风险，返回 None

### 阶段 5: 修改建议

```
风险标注
  ↓
[CorrectionAgent]
  ↓
Correction {
  clause_id: str,
  suggested_revision: str,
  note: str
}
```

**数据合并**:
- 风险信息 + 修改建议 = 完整标注

### 阶段 6: 结果聚合

```
所有步骤结果
  ↓
[Pipeline] 聚合
  ↓
AuditResult {
  contract_id: str,
  metadata: {...},
  parties: [...],
  annotations: [...]
}
```

## Pipeline 上下文数据流

Pipeline 使用上下文字典传递数据：

```python
# 初始上下文
context = {
    "contract_text": "...",
    "contract_id": "C20250101-ABCD"
}

# Step 1: ContractFormatterStep
context = {
    "contract_text": "...",
    "contract_id": "...",
    "formatted_contract": {
        "clauses": [...],
        "parties": [...]
    }
}

# Step 2: LawSearchStep
context = {
    ...,
    "law_results": [
        {"clause_id": "1", "law_info": {...}}
    ]
}

# Step 3: RiskAnnotationStep
context = {
    ...,
    "annotations": [
        {"id": "anno-001", ...}
    ]
}

# Step 4: CorrectionStep
context = {
    ...,
    "final_annotations": [
        {...风险信息..., "suggested_revision": "..."}
    ]
}
```

## RAG 数据流

### 文档入库流程

```
法律文档 (文本)
  ↓
[EmbeddingModel] 生成向量
  ↓
向量 (List[float])
  ↓
[VectorStore] 存储
  ↓
持久化存储 (pkl 文件)
```

### 检索流程

```
查询文本 (str)
  ↓
[EmbeddingModel] 生成查询向量
  ↓
查询向量 (List[float])
  ↓
[VectorStore] 相似度搜索
  ↓
相关文档 (List[Document])
  ↓
注入 LLM 上下文
```

## 数据模型转换

### 输入模型

```python
ContractInput {
    contract_text: str
}
```

### 中间模型

```python
FormattedContract {
    clauses: List[Clause],
    parties: List[Party]
}

LawInfo {
    matched: bool,
    law_name: str,
    article: str,
    issue: str
}

RiskAnnotation {
    id: str,
    clause_id: str,
    party: str,
    issue_type: str,
    description: str,
    severity: str,
    recommendation: str,
    law_reference: str
}
```

### 输出模型

```python
AuditResult {
    contract_id: str,
    metadata: {
        processed_at: datetime,
        clause_count: int,
        party_count: int
    },
    parties: List[Party],
    annotations: List[AnnotationResult]
}
```

## 数据验证

### Pydantic 模型验证

所有数据模型使用 Pydantic 进行验证：

```python
class Clause(BaseModel):
    id: str
    title: str = ""
    content: str
```

### 验证点

1. **输入验证**: API 层验证文件格式
2. **模型验证**: Pydantic 验证数据结构
3. **业务验证**: Agents 验证业务逻辑

## 数据持久化

### 临时数据

- 上传的文件: `uploads/` 目录
- 处理完成后自动清理

### 持久化数据

- 向量存储: `outputs/vector_store.pkl`
- 日志文件: `outputs/logs/`
- 审核结果: 可选保存到数据库（未来）

## 数据安全

### 当前措施

- 文件类型验证
- 临时文件自动清理
- 错误信息不泄露敏感数据

### 未来增强

- 数据加密
- 访问控制
- 审计日志

## 性能考虑

### 数据缓存

- 向量存储持久化
- 可缓存格式化结果（未来）

### 批处理

- 批量嵌入生成
- 批量 LLM 调用（未来）

### 数据压缩

- 向量存储压缩（未来）
- 结果压缩传输（未来）
