# Pipeline 说明

Pipeline 是系统的审核流程编排器，负责协调各个 Agents 完成合同审核任务。

## Pipeline 架构

系统采用可扩展的 Pipeline 架构：

```
ContractAuditPipeline
├── ContractFormatterStep (格式化)
├── LawSearchStep (法律检索)
├── RiskAnnotationStep (风险标注)
└── CorrectionStep (修改建议)
```

## Pipeline 接口

### Pipeline 接口

```python
class Pipeline(ABC):
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
```

### PipelineStep 接口

```python
class PipelineStep(ABC):
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
```

## 执行流程

### 1. ContractFormatterStep

**功能**: 将原始合同文本格式化为结构化数据

**输入**: 
```python
{
  "contract_text": "原始合同文本..."
}
```

**输出**: 
```python
{
  "formatted_contract": {
    "clauses": [...],
    "parties": [...]
  }
}
```

### 2. LawSearchStep

**功能**: 为每个条款检索相关法律信息

**输入**: 格式化后的合同

**输出**: 
```python
{
  "law_results": [
    {
      "clause_id": "1",
      "law_info": {...}
    }
  ]
}
```

### 3. RiskAnnotationStep

**功能**: 识别每个条款的风险

**输入**: 条款 + 法律信息

**输出**: 
```python
{
  "annotations": [
    {
      "id": "anno-001",
      "clause_id": "1",
      "description": "...",
      "severity": "High",
      ...
    }
  ]
}
```

### 4. CorrectionStep

**功能**: 为识别的风险生成修改建议

**输入**: 风险标注

**输出**: 
```python
{
  "final_annotations": [
    {
      ...风险信息...,
      "suggested_revision": "修改后的条款"
    }
  ]
}
```

## 使用 Pipeline

### 方式 1: 使用 PipelineService

```python
from services.pipeline_service import get_pipeline_service

service = get_pipeline_service()
result = service.audit_contract(contract_text)
```

### 方式 2: 直接使用 Pipeline

```python
from core.pipeline.contract_pipeline import ContractAuditPipeline
from agents import (
    ContractFormatterAgent,
    LawSearchAgent,
    RiskAnnotatorAgent,
    CorrectionAgent
)

# 创建 Agents
formatter = ContractFormatterAgent()
law_search = LawSearchAgent()
risk_annotator = RiskAnnotatorAgent()
correction = CorrectionAgent()

# 创建 Pipeline
pipeline = ContractAuditPipeline(
    formatter_agent=formatter,
    law_search_agent=law_search,
    risk_annotator_agent=risk_annotator,
    correction_agent=correction
)

# 运行 Pipeline
result = pipeline.run({"contract_text": contract_text})
```

## 扩展 Pipeline

### 添加新步骤

```python
from core.pipeline.interface import PipelineStep

class CustomStep(PipelineStep):
    def __init__(self, custom_service):
        self.service = custom_service
        self.logger = get_logger(self.__class__.__name__)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 实现步骤逻辑
        data = context.get("some_data")
        result = self.service.process(data)
        context["custom_result"] = result
        return context
```

### 修改 Pipeline

```python
class CustomPipeline(ContractAuditPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加自定义步骤
        custom_step = CustomStep(custom_service)
        self.steps.insert(2, custom_step)  # 在指定位置插入
```

## 中间件模式

Pipeline 支持中间件模式（未来扩展）：

- 日志记录
- 错误处理
- 缓存
- 性能监控

## 上下文传递

Pipeline 使用上下文字典在步骤间传递数据：

```python
context = {
    "contract_text": "...",
    "contract_id": "...",
    "formatted_contract": {...},
    "law_results": [...],
    "annotations": [...],
    "final_annotations": [...]
}
```

每个步骤可以：
- 读取上下文中的数据
- 添加新的数据
- 修改现有数据

## 错误处理

Pipeline 包含错误处理机制：

- 步骤失败时记录错误
- 继续执行后续步骤（可选）
- 返回部分结果

## 性能优化

### 并行处理

某些步骤可以并行执行（未来支持）：

```python
# 并行处理多个条款
with ThreadPoolExecutor() as executor:
    results = executor.map(process_clause, clauses)
```

### 缓存

可以缓存中间结果：

```python
# 缓存格式化结果
if "formatted_contract" in cache:
    context["formatted_contract"] = cache["formatted_contract"]
```

## 最佳实践

1. **步骤职责单一**: 每个步骤只做一件事
2. **上下文清晰**: 使用明确的键名
3. **错误处理**: 优雅处理错误，不中断流程
4. **日志记录**: 记录关键操作和结果

## 故障排除

### Pipeline 执行失败

- 检查输入数据格式
- 查看步骤日志
- 验证 Agents 配置

### 步骤顺序问题

- 确认步骤依赖关系
- 检查上下文数据传递

### 性能问题

- 检查 LLM 调用次数
- 优化批处理
- 考虑缓存
