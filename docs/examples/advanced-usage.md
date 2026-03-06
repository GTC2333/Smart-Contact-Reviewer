# 高级用法

本文档介绍系统的高级功能和技巧。

## 自定义配置

### 使用不同的 LLM 模型

```python
from core.config_manager import get_config_manager

config = get_config_manager()
# 修改配置（需要重启服务）
# 或使用环境变量
```

### 自定义 Agent 参数

```python
from agents.base_agent import BaseAgent
from core.llm.factory import get_llm_client

class CustomAgent(BaseAgent):
    def __init__(self):
        # 使用自定义参数
        super().__init__(
            agent_name="custom",
            llm_client=get_llm_client()
        )
        # 覆盖默认参数
        self.temperature = 0.3
        self.max_tokens = 3000
```

## 扩展 Pipeline

### 添加自定义步骤

```python
from core.pipeline.interface import PipelineStep
from core.logger import get_logger

class CustomValidationStep(PipelineStep):
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def execute(self, context):
        # 验证合同格式
        formatted = context.get("formatted_contract")
        if not formatted or not formatted.get("clauses"):
            raise ValueError("合同格式无效")
        
        self.logger.info("合同格式验证通过")
        return context
```

### 修改 Pipeline 流程

```python
from core.pipeline.contract_pipeline import ContractAuditPipeline

class CustomPipeline(ContractAuditPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加自定义步骤
        from core.pipeline.interface import PipelineStep
        custom_step = CustomValidationStep()
        self.steps.insert(1, custom_step)  # 在格式化后插入
```

## RAG 高级用法

### 自定义知识库

```python
from services.knowledge_base import KnowledgeBaseService

service = KnowledgeBaseService()

# 添加自定义法条
service.add_law_document(
    law_name="合同法",
    article="第三十二条",
    content="合同内容..."
)

# 添加案例
service.add_case(
    case_id="case_2024_001",
    case_title="某合同纠纷案",
    case_content="案例详情...",
    metadata={
        "court": "最高人民法院",
        "year": 2024,
        "category": "合同纠纷"
    }
)
```

### 搜索知识库

```python
# 搜索相关法条
results = service.search("合同违约责任", top_k=5)

for result in results:
    print(f"相似度: {result['score']:.3f}")
    print(f"内容: {result['text'][:100]}...")
    print(f"来源: {result['metadata']}")
    print()
```

### 批量导入知识库

```python
import json
from pathlib import Path

# 准备数据
laws_data = {
    "laws": [
        {
            "law_name": "民法典",
            "article": "第五百一十条",
            "content": "法条内容..."
        }
        # ... 更多法条
    ]
}

# 保存到文件
kb_file = Path("data/knowledge_base.json")
kb_file.parent.mkdir(exist_ok=True)
with open(kb_file, 'w', encoding='utf-8') as f:
    json.dump(laws_data, f, ensure_ascii=False, indent=2)

# 加载
service = KnowledgeBaseService()
service.load_from_file(kb_file)
```

## 性能优化

### 缓存结果

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_audit(contract_hash):
    """缓存审核结果"""
    # 实现缓存逻辑
    pass

def audit_with_cache(contract_text):
    """带缓存的审核"""
    # 生成哈希
    contract_hash = hashlib.md5(contract_text.encode()).hexdigest()
    
    # 检查缓存
    if contract_hash in cache:
        return cache[contract_hash]
    
    # 执行审核
    result = run_pipeline({"contract_text": contract_text})
    
    # 保存到缓存
    cache[contract_hash] = result
    return result
```

### 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_audit(contract_text):
    """异步审核"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            run_pipeline,
            {"contract_text": contract_text}
        )
    return result

# 使用
result = await async_audit(contract_text)
```

## 错误处理

### 自定义错误处理

```python
from services.pipeline_service import get_pipeline_service

def safe_audit(contract_text):
    """安全的审核函数，包含错误处理"""
    try:
        service = get_pipeline_service()
        result = service.audit_contract(contract_text)
        return {"success": True, "result": result}
    except ValueError as e:
        return {"success": False, "error": f"输入错误: {e}"}
    except Exception as e:
        return {"success": False, "error": f"处理失败: {e}"}

# 使用
response = safe_audit(contract_text)
if response["success"]:
    print(response["result"])
else:
    print(f"错误: {response['error']}")
```

## 日志和监控

### 自定义日志

```python
from core.logger import get_logger

logger = get_logger("custom_module")

def audit_with_logging(contract_text):
    logger.info(f"开始审核合同，长度: {len(contract_text)}")
    
    try:
        result = run_pipeline({"contract_text": contract_text})
        logger.info(f"审核完成，发现 {len(result['annotations'])} 个风险")
        return result
    except Exception as e:
        logger.error(f"审核失败: {e}", exc_info=True)
        raise
```

### 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} 执行时间: {elapsed:.2f} 秒")
        return result
    return wrapper

@monitor_performance
def audited_contract(contract_text):
    return run_pipeline({"contract_text": contract_text})
```

## 集成到其他系统

### Flask 集成

```python
from flask import Flask, request, jsonify
from main import run_pipeline

app = Flask(__name__)

@app.route('/audit', methods=['POST'])
def audit():
    contract_text = request.json.get('contract_text')
    if not contract_text:
        return jsonify({"error": "缺少 contract_text"}), 400
    
    result = run_pipeline({"contract_text": contract_text})
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### Django 集成

```python
from django.http import JsonResponse
from django.views import View
from main import run_pipeline

class AuditView(View):
    def post(self, request):
        contract_text = request.POST.get('contract_text')
        if not contract_text:
            return JsonResponse({"error": "缺少 contract_text"}, status=400)
        
        result = run_pipeline({"contract_text": contract_text})
        return JsonResponse(result)
```

## 最佳实践

1. **使用服务层**: 优先使用 `PipelineService` 而不是直接调用 Pipeline
2. **错误处理**: 始终包含适当的错误处理
3. **日志记录**: 记录关键操作和错误
4. **配置管理**: 使用配置文件而不是硬编码
5. **测试**: 为自定义代码编写测试

## 下一步

- 查看[架构文档](../architecture/overview.md)
- 阅读[开发指南](../development/setup.md)
- 了解[设计模式](../architecture/design-patterns.md)
