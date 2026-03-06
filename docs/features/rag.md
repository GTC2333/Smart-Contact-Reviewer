# RAG 功能使用指南

## 概述

本系统已集成基础的 RAG (Retrieval-Augmented Generation) 功能，用于增强法律检索和合同审核能力。RAG 通过向量检索相关法律文档，为 LLM 提供上下文信息，从而提高审核准确性。

## 功能特性

- **向量存储**: 使用持久化向量存储保存法律文档
- **语义检索**: 基于嵌入向量的相似度检索
- **自动增强**: 在法条检索时自动注入相关上下文
- **知识库管理**: 支持添加、搜索和管理法律文档

## 配置

在 `config/settings.yaml` 中配置 RAG：

```yaml
rag:
  enabled: true
  embedding_model: "openai"  # openai | simple
  embedding_model_name: "text-embedding-3-small"
  vector_store_path: "outputs/vector_store.pkl"
  retrieval_top_k: 3
```

## 初始化知识库

### 方法 1: 使用初始化脚本

```bash
python utils/init_knowledge_base.py
```

这将创建包含常用民法典条款的知识库。

### 方法 2: 使用 KnowledgeBaseService

```python
from services.knowledge_base import KnowledgeBaseService

service = KnowledgeBaseService()

# 添加单个法条
service.add_law_document(
    law_name="民法典",
    article="第五百一十条",
    content="合同生效后，当事人就质量、价款或者报酬..."
)

# 批量添加
laws = [
    {
        "law_name": "民法典",
        "article": "第五百七十七条",
        "content": "当事人一方不履行合同义务..."
    }
]
service.add_law_documents_batch(laws)

# 从文件加载
from pathlib import Path
service.load_from_file(Path("data/knowledge_base.json"))
```

## 知识库文件格式

创建 `data/knowledge_base.json` 文件：

```json
{
  "laws": [
    {
      "law_name": "民法典",
      "article": "第五百一十条",
      "content": "法条内容..."
    }
  ]
}
```

## 工作原理

1. **文档嵌入**: 法律文档通过嵌入模型转换为向量
2. **向量存储**: 向量保存在持久化存储中
3. **查询检索**: 当审核合同时，查询被转换为向量，检索最相似的法律文档
4. **上下文注入**: 检索到的文档作为上下文注入到 LLM 提示中

## 在 Agent 中使用

`LawSearchAgent` 已自动集成 RAG 功能：

```python
from agents.law_search_agent import LawSearchAgent

agent = LawSearchAgent()
result = agent.check_law("合同条款内容...")
# RAG 会自动检索相关法条并增强结果
```

## 扩展功能

### 添加案例

```python
service.add_case(
    case_id="case_001",
    case_title="某合同纠纷案",
    case_content="案例详情...",
    metadata={"court": "最高人民法院", "year": 2023}
)
```

### 搜索知识库

```python
results = service.search("合同违约责任", top_k=5)
for result in results:
    print(f"相似度: {result['score']}")
    print(f"内容: {result['text']}")
    print(f"来源: {result['metadata']}")
```

## 注意事项

1. **嵌入模型**: 使用 OpenAI 嵌入模型需要配置 API key
2. **存储路径**: 向量存储文件保存在 `outputs/vector_store.pkl`
3. **性能**: 首次检索需要生成嵌入向量，可能需要几秒钟
4. **成本**: 使用 OpenAI 嵌入模型会产生 API 调用费用

## 故障排除

### RAG 未启用

检查配置中 `rag.enabled` 是否为 `true`。

### 嵌入失败

确保 OpenAI API key 已正确配置。

### 知识库为空

运行初始化脚本或手动添加文档。
